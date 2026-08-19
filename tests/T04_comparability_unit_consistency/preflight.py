from __future__ import annotations

import hashlib
import importlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT_ROOT = HERE.parents[1]
T03 = AUDIT_ROOT / "tests" / "T03_corpus_boundary_impact"
FACT = T03 / "raw" / "fact_results_stage_f.parquet"
T03_SUMMARY = T03 / "results" / "summary.json"
BACKEND = AUDIT_ROOT / "freeze" / "repos" / "eval_cards_backend_pipeline"

EXPECTED_COMMIT = "9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
EXPECTED_FACT_SHA = "e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"

problems = []

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

try:
    head = subprocess.check_output(
        ["git", "-C", str(BACKEND), "rev-parse", "HEAD"], text=True
    ).strip()
except Exception as exc:
    head = None
    problems.append(f"cannot resolve backend HEAD: {type(exc).__name__}: {exc}")

if head != EXPECTED_COMMIT:
    problems.append(f"backend HEAD mismatch: {head}")

for p, label in [(FACT, "T03 Stage F parquet"), (T03_SUMMARY, "T03 summary")]:
    if not p.exists():
        problems.append(f"missing {label}: {p}")

fact_sha = sha256(FACT) if FACT.exists() else None
if fact_sha is not None and fact_sha != EXPECTED_FACT_SHA:
    problems.append(f"T03 fact parquet SHA mismatch: {fact_sha}")

t03 = {}
if T03_SUMMARY.exists():
    try:
        t03 = json.loads(T03_SUMMARY.read_text(encoding="utf-8"))
    except Exception as exc:
        problems.append(f"cannot parse T03 summary: {type(exc).__name__}: {exc}")

expected_t03 = {
    "verdict": "REFUTED",
    "fact_rows_scanned": 209382,
    "comparability_groups": 93495,
    "variant_mismatches": 0,
    "cross_party_mismatches": 0,
}
for key, expected in expected_t03.items():
    if t03 and t03.get(key) != expected:
        problems.append(
            f"T03 summary mismatch {key}: got {t03.get(key)!r}, expected {expected!r}"
        )

versions = {}
for pkg, mod in [("duckdb", "duckdb")]:
    try:
        m = importlib.import_module(mod)
        versions[pkg] = getattr(m, "__version__", "unknown")
    except Exception as exc:
        versions[pkg] = None
        problems.append(f"missing dependency {pkg}: {type(exc).__name__}: {exc}")

raw = HERE / "raw"
raw.mkdir(exist_ok=True)
record = {
    "test_id": "T04_comparability_unit_consistency",
    "backend_commit": head,
    "fact_sha256": fact_sha,
    "t03_summary_checked": expected_t03,
    "dependencies": versions,
    "problems": problems,
}
(raw / "preflight.json").write_text(
    json.dumps(record, indent=2, ensure_ascii=True, sort_keys=True) + "\n",
    encoding="utf-8",
)

print("T04 PREFLIGHT")
print(f"backend_commit={head}")
print(f"fact_sha256={fact_sha}")
print(f"duckdb={versions.get('duckdb')}")
print(f"problems={len(problems)}")
for p in problems:
    print(f"PROBLEM {p}")
if problems:
    raise SystemExit(2)
print("T04 PREFLIGHT OK")
