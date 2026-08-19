from __future__ import annotations

import ctypes
import hashlib
import importlib
import importlib.metadata
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT_ROOT = HERE.parents[1]
BACKEND = AUDIT_ROOT / "freeze" / "repos" / "eval_cards_backend_pipeline"
REGISTRY_REPO_CANDIDATES = [
    AUDIT_ROOT / "freeze" / "repos" / "eval-card-registry",
    AUDIT_ROOT / "freeze" / "repos" / "evalcard-registry",
]
EEE = AUDIT_ROOT / "freeze" / "hf" / "EEE_datastore"
CARDS = AUDIT_ROOT / "freeze" / "hf" / "auto-benchmarkcards"
REGISTRY_DATA = AUDIT_ROOT / "freeze" / "hf" / "entity-registry-data"
EXPECTED_COMMIT = "9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"

RAW = HERE / "raw"
RAW.mkdir(exist_ok=True)

def long_path(path: Path) -> str:
    s = str(path.resolve())
    if os.name == "nt" and not s.startswith("\\\\?\\"):
        return "\\\\?\\" + s
    return s

problems = []
info = {}

try:
    head = subprocess.check_output(
        ["git", "-C", str(BACKEND), "rev-parse", "HEAD"],
        text=True,
        stderr=subprocess.STDOUT,
    ).strip()
except Exception as exc:
    head = None
    problems.append(f"backend git check failed: {exc}")
info["backend_commit"] = head
if head != EXPECTED_COMMIT:
    problems.append(f"backend HEAD {head!r} != {EXPECTED_COMMIT}")

for path, markers in [
    (AUDIT_ROOT / "freeze" / "VERIFY_FREEZE.txt", ["bad=0", "missing=0"]),
    (AUDIT_ROOT / "VERIFY_BASELINES.txt", ["bad=0"]),
]:
    if not path.exists():
        problems.append(f"missing prior-gate evidence: {path}")
        continue
    text = path.read_text(encoding="utf-8-sig")
    for marker in markers:
        if marker not in text:
            problems.append(f"{path} lacks {marker}")

for tid, expected in [
    ("T01_signal_calibration", {"verdict": "REFUTED", "fail_count": 1}),
    ("T02_comparability_boundary_robustness", {
        "verdict": "REFUTED",
        "fail_count": 8,
        "boundary_fail_count": 8,
        "below_fail_count": 0,
        "above_fail_count": 0,
    }),
]:
    p = AUDIT_ROOT / "tests" / tid / "results" / "summary.json"
    if not p.exists():
        problems.append(f"missing prior test summary: {p}")
        continue
    payload = json.loads(p.read_text(encoding="utf-8"))
    for k, v in expected.items():
        if payload.get(k) != v:
            problems.append(f"{tid} expected {k}={v!r}, got {payload.get(k)!r}")

registry_repo = next((p for p in REGISTRY_REPO_CANDIDATES if p.exists()), None)
if registry_repo is None:
    problems.append("frozen eval-card-registry checkout not found")
else:
    info["registry_repo"] = str(registry_repo)
    seed = registry_repo / "seed"
    if not seed.exists():
        problems.append(f"registry seed directory missing: {seed}")

for name, p in [("EEE", EEE), ("cards", CARDS), ("registry_data", REGISTRY_DATA)]:
    info[f"{name}_path"] = str(p)
    if not p.exists():
        problems.append(f"missing frozen source directory: {p}")

# Dependency check.
deps = [
    ("duckdb", "duckdb"),
    ("pyarrow", "pyarrow"),
    ("pydantic", "pydantic"),
    ("PyYAML", "yaml"),
    ("pandas", "pandas"),
    ("huggingface-hub", "huggingface_hub"),
]
versions = {}
for dist_name, module_name in deps:
    try:
        importlib.import_module(module_name)
        try:
            versions[dist_name] = importlib.metadata.version(dist_name)
        except Exception:
            versions[dist_name] = "importable"
    except Exception as exc:
        versions[dist_name] = None
        problems.append(f"missing dependency {dist_name}: {type(exc).__name__}: {exc}")
info["dependency_versions"] = versions

if registry_repo is not None:
    resolver_src = registry_repo / "packages" / "eval-entity-resolver" / "src"
    info["resolver_src"] = str(resolver_src)
    if not resolver_src.exists():
        problems.append(f"resolver source missing: {resolver_src}")
    else:
        sys.path.insert(0, str(resolver_src))
        try:
            import eval_entity_resolver
            info["eval_entity_resolver_import"] = "ok"
        except Exception as exc:
            problems.append(f"eval_entity_resolver import failed: {type(exc).__name__}: {exc}")

# Physical memory, descriptive only: no arbitrary RAM pass/fail threshold.
if os.name == "nt":
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]
    mem = MEMORYSTATUSEX()
    mem.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem)):
        info["memory_total_gib"] = round(mem.ullTotalPhys / 1024**3, 3)
        info["memory_available_gib"] = round(mem.ullAvailPhys / 1024**3, 3)
        info["pagefile_available_gib"] = round(mem.ullAvailPageFile / 1024**3, 3)

try:
    du = shutil.disk_usage(AUDIT_ROOT)
    info["disk_free_gib"] = round(du.free / 1024**3, 3)
except Exception as exc:
    info["disk_free_error"] = f"{type(exc).__name__}: {exc}"

# Count only Stage-A aggregate JSON records; JSONL sample companions are not loaded.
aggregate_count = 0
aggregate_bytes = 0
jsonl_count = 0
jsonl_bytes = 0
data_root = Path(long_path(EEE)) / "data"
try:
    for dirpath, _, filenames in os.walk(str(data_root)):
        for name in filenames:
            fp = os.path.join(dirpath, name)
            if name.endswith(".json"):
                aggregate_count += 1
                try:
                    aggregate_bytes += os.path.getsize(fp)
                except OSError:
                    pass
            elif name.endswith(".jsonl"):
                jsonl_count += 1
                try:
                    jsonl_bytes += os.path.getsize(fp)
                except OSError:
                    pass
except Exception as exc:
    problems.append(f"EEE traversal failed: {type(exc).__name__}: {exc}")

info["eee_aggregate_json_files"] = aggregate_count
info["eee_aggregate_json_gib"] = round(aggregate_bytes / 1024**3, 3)
info["eee_jsonl_files"] = jsonl_count
info["eee_jsonl_gib"] = round(jsonl_bytes / 1024**3, 3)

if aggregate_count == 0:
    problems.append("no Stage-A aggregate JSON files found under frozen EEE data/")

# Network-refresh environment must not be enabled.
refresh_vars = {
    "EEE_REFRESH_SNAPSHOT": os.environ.get("EEE_REFRESH_SNAPSHOT"),
    "BENCHMARK_METADATA_REFRESH": os.environ.get("BENCHMARK_METADATA_REFRESH"),
    "ENTITY_REGISTRY_REFRESH": os.environ.get("ENTITY_REGISTRY_REFRESH"),
    "EEE_REVISION": os.environ.get("EEE_REVISION"),
    "BENCHMARK_METADATA_REVISION": os.environ.get("BENCHMARK_METADATA_REVISION"),
    "ENTITY_REGISTRY_REVISION": os.environ.get("ENTITY_REGISTRY_REVISION"),
    "DIVERGENCE_THRESHOLD_FACTOR": os.environ.get("DIVERGENCE_THRESHOLD_FACTOR"),
}
info["relevant_environment_before_run"] = refresh_vars

(RAW / "preflight.json").write_text(
    json.dumps({"problems": problems, "info": info}, indent=2, ensure_ascii=True) + "\n",
    encoding="utf-8",
)

print("T03 PREFLIGHT")
print(f"backend_commit={head}")
print(f"eee_aggregate_json_files={aggregate_count}")
print(f"eee_aggregate_json_gib={info['eee_aggregate_json_gib']}")
print(f"eee_jsonl_files={jsonl_count}")
print(f"eee_jsonl_gib={info['eee_jsonl_gib']}")
print(f"memory_total_gib={info.get('memory_total_gib')}")
print(f"memory_available_gib={info.get('memory_available_gib')}")
print(f"pagefile_available_gib={info.get('pagefile_available_gib')}")
print(f"disk_free_gib={info.get('disk_free_gib')}")
print("dependencies=" + json.dumps(versions, sort_keys=True))
print(f"problems={len(problems)}")
if problems:
    for p in problems:
        print("PROBLEM", p)
    raise SystemExit(1)
print("T03 PREFLIGHT OK")
print("network_refresh_required=false")
