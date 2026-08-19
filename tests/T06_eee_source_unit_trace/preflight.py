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

problems = []

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

# Resolve the frozen EEE root without opening T06 outcome cases.
# Candidate roots are directories under the audit tree that have
# `.eee_file_listing.json` and a `data/` directory.
candidates = []
for listing in ROOT.rglob(".eee_file_listing.json"):
    candidate = listing.parent
    if (candidate / "data").is_dir():
        try:
            payload = json.loads(listing.read_text(encoding="utf-8"))
            paths = payload.get("paths", [])
            revision = payload.get("revision")
        except Exception as exc:
            problems.append(
                f"cannot parse EEE listing {listing}: {type(exc).__name__}: {exc}"
            )
            continue
        candidates.append(
            {
                "root": str(candidate.resolve()),
                "revision": revision,
                "path_count": len(paths),
            }
        )

# Prefer the exact T03 population size. Do not require a particular revision
# here because the full freeze may preserve revision identity in a separate
# marker rather than the listing payload.
matching = [c for c in candidates if c["path_count"] == 24787]
if len(matching) != 1:
    problems.append(
        f"expected exactly one EEE root with 24787 aggregate paths, found {len(matching)}"
    )
    eee_root = None
else:
    eee_root = matching[0]["root"]

raw = HERE / "raw"
raw.mkdir(exist_ok=True)
(raw / "source_root.json").write_text(
    json.dumps(
        {
            "candidates": candidates,
            "selected_root": eee_root,
            "selection_rule": "unique .eee_file_listing.json root with 24787 aggregate paths",
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
            "backend_commit": head,
            "fact_sha256": fact_sha,
            "t05_checks": expected_t05,
            "duckdb": duckdb_version,
            "eee_root": eee_root,
            "problems": problems,
        },
        indent=2,
        ensure_ascii=True,
        sort_keys=True,
    ) + "\n",
    encoding="utf-8",
)

print("T06 PREFLIGHT")
print(f"backend_commit={head}")
print(f"fact_sha256={fact_sha}")
print(f"duckdb={duckdb_version}")
print(f"eee_root_candidates={len(candidates)}")
print(f"eee_root_matching_24787={len(matching)}")
print(f"eee_root={eee_root}")
print(f"problems={len(problems)}")
for problem in problems:
    print(f"PROBLEM {problem}")
if problems:
    raise SystemExit(2)
print("T06 PREFLIGHT OK")
