from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
T03 = ROOT / "tests" / "T03_corpus_boundary_impact"
T05 = ROOT / "tests" / "T05_metric_unit_provenance_decomposition"
FACT = T03 / "raw" / "fact_results_stage_f.parquet"
T05_SUM = T05 / "results" / "summary.json"
BACKEND = ROOT / "freeze" / "repos" / "eval_cards_backend_pipeline"

EXPECTED_COMMIT = "9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
EXPECTED_SHA = "e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def rel_parts(value: str) -> tuple[str, ...]:
    return tuple(p for p in value.replace("\\", "/").split("/") if p)

def endswith_parts(path: Path, parts: tuple[str, ...]) -> bool:
    pp = path.resolve().parts
    return len(pp) >= len(parts) and tuple(pp[-len(parts):]) == parts

problems = []

# Preserve attempt 01 automatically if it exists and has not been archived yet.
raw = HERE / "raw"
raw.mkdir(exist_ok=True)
old = raw / "preflight.json"
attempt1 = raw / "preflight_attempt_01_marker_not_found.json"
if old.exists() and not attempt1.exists():
    try:
        payload = json.loads(old.read_text(encoding="utf-8"))
    except Exception:
        payload = None
    if isinstance(payload, dict) and payload.get("eee_root") is None:
        attempt1.write_bytes(old.read_bytes())

try:
    head = subprocess.check_output(
        ["git", "-C", str(BACKEND), "rev-parse", "HEAD"], text=True
    ).strip()
except Exception as exc:
    head = None
    problems.append(f"cannot resolve backend HEAD: {type(exc).__name__}: {exc}")

if head != EXPECTED_COMMIT:
    problems.append(f"backend HEAD mismatch: {head}")

if not FACT.exists():
    problems.append(f"missing T03 Stage F parquet: {FACT}")
fact_sha = sha256(FACT) if FACT.exists() else None
if fact_sha and fact_sha != EXPECTED_SHA:
    problems.append(f"T03 fact parquet SHA mismatch: {fact_sha}")

t05 = {}
if not T05_SUM.exists():
    problems.append(f"missing T05 summary: {T05_SUM}")
else:
    try:
        t05 = json.loads(T05_SUM.read_text(encoding="utf-8"))
    except Exception as exc:
        problems.append(f"cannot parse T05 summary: {type(exc).__name__}: {exc}")

expected_t05 = {
    "verdict": "REFUTED",
    "actual_mixed_unit_groups": 1234,
    "single_raw_metric_groups": 1234,
    "multi_raw_metric_groups": 0,
    "groups_with_unresolved_metric_rows": 0,
    "full_resolved_canonical_convergence_groups": 0,
    "integrity_error_records": 0,
}
for key, expected in expected_t05.items():
    if t05 and t05.get(key) != expected:
        problems.append(
            f"T05 summary mismatch {key}: got {t05.get(key)!r}, expected {expected!r}"
        )

if t05:
    if t05.get("resolution_strategy_patterns") != {"exact": 1234}:
        problems.append(
            "T05 resolution_strategy_patterns mismatch: "
            f"{t05.get('resolution_strategy_patterns')!r}"
        )
    if t05.get("metric_unit_provenance_patterns") != {"eee_record": 1234}:
        problems.append(
            "T05 metric_unit_provenance_patterns mismatch: "
            f"{t05.get('metric_unit_provenance_patterns')!r}"
        )

try:
    import duckdb
    duckdb_version = duckdb.__version__
except Exception as exc:
    duckdb_version = None
    problems.append(f"missing dependency duckdb: {type(exc).__name__}: {exc}")
    duckdb = None

source_paths = []
if FACT.exists() and duckdb is not None:
    try:
        fact_sql = FACT.as_posix().replace("'", "''")
        con = duckdb.connect()
        source_paths = [
            r[0]
            for r in con.execute(
                f"""
                SELECT DISTINCT source_record_path
                FROM read_parquet('{fact_sql}')
                WHERE source_record_path IS NOT NULL
                  AND source_record_path <> ''
                ORDER BY source_record_path
                LIMIT 32
                """
            ).fetchall()
        ]
    except Exception as exc:
        problems.append(
            f"cannot read source_record_path values: {type(exc).__name__}: {exc}"
        )

eee_root = None
discovery = {
    "method": "exact source_record_path suffix discovery",
    "probe_path": source_paths[0] if source_paths else None,
    "leaf_matches": [],
    "candidate_roots": [],
    "verification_paths_checked": 0,
    "verification_paths_missing": [],
}

if source_paths:
    probe = source_paths[0]
    parts = rel_parts(probe)
    leaf = parts[-1]
    matches = []
    # Search only the frozen material first. This tree contains the large
    # immutable source snapshots and avoids unrelated user files.
    freeze_root = ROOT / "freeze"
    if freeze_root.is_dir():
        for hit in freeze_root.rglob(leaf):
            if hit.is_file() and endswith_parts(hit, parts):
                matches.append(hit.resolve())

    discovery["leaf_matches"] = [str(x) for x in matches]

    candidate_roots = []
    for hit in matches:
        candidate = hit
        for _ in parts:
            candidate = candidate.parent
        candidate_roots.append(candidate.resolve())

    # Exact dedupe.
    unique_roots = []
    seen = set()
    for x in candidate_roots:
        sx = str(x)
        if sx not in seen:
            seen.add(sx)
            unique_roots.append(x)
    discovery["candidate_roots"] = [str(x) for x in unique_roots]

    verified_roots = []
    for candidate in unique_roots:
        missing = []
        for rel in source_paths:
            path = candidate.joinpath(*rel_parts(rel))
            if not path.is_file():
                missing.append(rel)
        if not missing:
            verified_roots.append(candidate)

    if len(verified_roots) == 1:
        eee_root = str(verified_roots[0])
        discovery["verification_paths_checked"] = len(source_paths)
    elif len(verified_roots) == 0:
        problems.append(
            "no candidate EEE root satisfied all deterministic source_record_path probes"
        )
    else:
        problems.append(
            f"multiple EEE roots satisfied all probes: {[str(x) for x in verified_roots]}"
        )
else:
    problems.append("no non-null source_record_path probes found")

(raw / "source_root.json").write_text(
    json.dumps(
        {
            "selected_root": eee_root,
            "discovery": discovery,
            "source_path_probe_count": len(source_paths),
        },
        indent=2,
        ensure_ascii=True,
        sort_keys=True,
    ) + "\n",
    encoding="utf-8",
)

(raw / "preflight.json").write_text(
    json.dumps(
        {
            "test_id": "T06_eee_source_unit_trace",
            "setup_amendment": "SETUP_AMENDMENT_01",
            "backend_commit": head,
            "fact_sha256": fact_sha,
            "t05_checks": expected_t05,
            "duckdb": duckdb_version,
            "eee_root": eee_root,
            "source_path_probe_count": len(source_paths),
            "problems": problems,
        },
        indent=2,
        ensure_ascii=True,
        sort_keys=True,
    ) + "\n",
    encoding="utf-8",
)

print("T06 PREFLIGHT FIX1")
print(f"backend_commit={head}")
print(f"fact_sha256={fact_sha}")
print(f"duckdb={duckdb_version}")
print(f"source_path_probe_count={len(source_paths)}")
print(f"probe_path={discovery['probe_path']}")
print(f"exact_probe_matches={len(discovery['leaf_matches'])}")
print(f"candidate_roots={len(discovery['candidate_roots'])}")
print(f"eee_root={eee_root}")
print(f"problems={len(problems)}")
for problem in problems:
    print(f"PROBLEM {problem}")
if problems:
    raise SystemExit(2)
print("T06 PREFLIGHT FIX1 OK")
