from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
bad = 0

def ok(cond: bool, msg: str) -> None:
    global bad
    if cond:
        print(f"OK {msg}")
    else:
        print(f"BAD {msg}")
        bad += 1

def require(base: Path, rels: list[str]) -> None:
    for rel in rels:
        p = base / rel
        ok(p.exists(), rel)

def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"BAD JSON {path}: {type(exc).__name__}: {exc}")
        global bad
        bad += 1
        return {}

def line_count(path: Path) -> int:
    with path.open("rb") as f:
        return sum(1 for _ in f)

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

print("COMPLETED TEST ARTIFACT VERIFY")

# T01
base = ROOT / "tests" / "T01_signal_calibration"
print("[T01_signal_calibration]")
require(base, [
    "README.md", "TEST_RATIONALE.md", "PREREGISTRATION.md", "SOURCE_ATTRIBUTION.md",
    "run_test.py", "verify_prereg.py", "raw/source_hashes.json", "raw/cases.jsonl",
    "results/summary.json", "results/RESULT_ANALYSIS.md",
    "posthoc/V2_BOUNDARY_DIAGNOSTIC.md", "posthoc/capture_v2_boundary.py",
])
s = read_json(base / "results" / "summary.json") if (base / "results" / "summary.json").exists() else {}
ok(s.get("verdict") == "REFUTED", "T01 verdict=REFUTED")
ok(s.get("case_count") == 24, "T01 case_count=24")
ok(s.get("pass_count") == 23, "T01 pass_count=23")
ok(s.get("fail_count") == 1, "T01 fail_count=1")
if (base / "raw" / "cases.jsonl").exists():
    ok(line_count(base / "raw" / "cases.jsonl") == 24, "T01 raw cases lines=24")
print()

# T02
base = ROOT / "tests" / "T02_comparability_boundary_robustness"
print("[T02_comparability_boundary_robustness]")
require(base, [
    "README.md", "TEST_RATIONALE.md", "PREREGISTRATION.md", "SOURCE_ATTRIBUTION.md",
    "run_test.py", "verify_prereg.py", "fixtures.json", "raw/cases.jsonl",
    "results/summary.json", "results/RESULT_ANALYSIS.md",
])
s = read_json(base / "results" / "summary.json") if (base / "results" / "summary.json").exists() else {}
for key, expected in {
    "verdict": "REFUTED", "case_count": 48, "pass_count": 40, "fail_count": 8,
    "boundary_fail_count": 8, "below_fail_count": 0, "above_fail_count": 0,
}.items():
    ok(s.get(key) == expected, f"T02 {key}={expected}")
if (base / "raw" / "cases.jsonl").exists():
    ok(line_count(base / "raw" / "cases.jsonl") == 48, "T02 raw cases lines=48")
print()

# T03
base = ROOT / "tests" / "T03_corpus_boundary_impact"
print("[T03_corpus_boundary_impact]")
require(base, [
    "README.md", "TEST_RATIONALE.md", "PREREGISTRATION.md", "SOURCE_ATTRIBUTION.md",
    "preflight.py", "run_pipeline.py", "analyze.py", "verify_prereg.py",
    "raw/preflight.json", "raw/preflight_attempt_01_missing_duckdb.json",
    "raw/pipeline_capture.json", "raw/pipeline_transcript.txt",
    "raw/fact_results_stage_f.parquet", "raw/group_scan.jsonl", "raw/mismatches.jsonl",
    "results/pipeline_status.json", "results/summary.json", "results/RESULT_ANALYSIS.md",
])
s = read_json(base / "results" / "summary.json") if (base / "results" / "summary.json").exists() else {}
for key, expected in {
    "verdict": "REFUTED",
    "fact_rows_scanned": 209382,
    "comparability_groups": 93495,
    "variant_applicable_groups": 862,
    "cross_party_applicable_groups": 886,
    "variant_production_true": 343,
    "variant_decimal_true": 343,
    "cross_party_production_true": 57,
    "cross_party_decimal_true": 57,
    "variant_mismatches": 0,
    "cross_party_mismatches": 0,
    "exact_boundary_mismatches": 0,
    "nonboundary_mismatches": 0,
    "production_true_decimal_false": 0,
    "production_false_decimal_true": 0,
    "group_consistency_errors": 0,
}.items():
    ok(s.get(key) == expected, f"T03 {key}={expected}")
if (base / "raw" / "group_scan.jsonl").exists():
    ok(line_count(base / "raw" / "group_scan.jsonl") == 93495, "T03 raw group_scan lines=93495")
if (base / "raw" / "mismatches.jsonl").exists():
    ok(line_count(base / "raw" / "mismatches.jsonl") == 0, "T03 raw mismatches lines=0")
if (base / "raw" / "fact_results_stage_f.parquet").exists():
    expected_hash = "e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"
    ok(sha256(base / "raw" / "fact_results_stage_f.parquet") == expected_hash,
       f"T03 fact_results SHA256={expected_hash}")
if (base / "results" / "pipeline_status.json").exists():
    ps = read_json(base / "results" / "pipeline_status.json")
    ok(ps.get("status") == "COMPLETE", "T03 pipeline status=COMPLETE")
print()

print(f"VERIFY_COMPLETED_TESTS bad={bad}")
raise SystemExit(1 if bad else 0)
