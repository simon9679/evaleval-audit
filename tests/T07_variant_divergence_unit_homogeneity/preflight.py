from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
T03 = ROOT / "tests" / "T03_corpus_boundary_impact"
T04 = ROOT / "tests" / "T04_comparability_unit_consistency"
T06 = ROOT / "tests" / "T06_eee_source_unit_trace"
FACT = T03 / "raw" / "fact_results_stage_f.parquet"
BACKEND = ROOT / "freeze" / "repos" / "eval_cards_backend_pipeline"
EXPECTED_COMMIT = "9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
EXPECTED_SHA = "e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""):
            h.update(c)
    return h.hexdigest()

problems=[]

try:
    head=subprocess.check_output(["git","-C",str(BACKEND),"rev-parse","HEAD"],text=True).strip()
except Exception as exc:
    head=None
    problems.append(f"cannot resolve backend HEAD: {type(exc).__name__}: {exc}")
if head != EXPECTED_COMMIT:
    problems.append(f"backend HEAD mismatch: {head}")

if not FACT.exists():
    problems.append(f"missing T03 Stage F parquet: {FACT}")
fact_sha=sha256(FACT) if FACT.exists() else None
if fact_sha and fact_sha != EXPECTED_SHA:
    problems.append(f"T03 fact SHA mismatch: {fact_sha}")

def load_summary(path, label):
    if not path.exists():
        problems.append(f"missing {label}: {path}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        problems.append(f"cannot parse {label}: {type(exc).__name__}: {exc}")
        return {}

t04=load_summary(T04/"results"/"summary.json","T04 summary")
t06=load_summary(T06/"results"/"summary.json","T06 summary")

checks04={
 "actual_mixed_unit_groups":1234,
 "variant_eligible_paths":7,
 "cross_party_eligible_paths":0,
 "classification_sensitive_paths":0,
 "integrity_error_records":0,
}
for k,v in checks04.items():
    if t04 and t04.get(k) != v:
        problems.append(f"T04 mismatch {k}: got {t04.get(k)!r}, expected {v!r}")

checks06={
 "verdict":"CONFIRMED",
 "mixed_unit_groups":1234,
 "mixed_unit_rows":28196,
 "row_traces_complete":28196,
 "row_unit_matches":28196,
 "row_unit_mismatches":0,
 "group_unit_set_matches":1234,
 "group_unit_set_mismatches":0,
 "pointer_or_index_errors":0,
 "integrity_error_records":0,
}
for k,v in checks06.items():
    if t06 and t06.get(k) != v:
        problems.append(f"T06 mismatch {k}: got {t06.get(k)!r}, expected {v!r}")

try:
    import duckdb
    duckdb_version=duckdb.__version__
except Exception as exc:
    duckdb_version=None
    problems.append(f"missing dependency duckdb: {type(exc).__name__}: {exc}")

raw=HERE/"raw"; raw.mkdir(exist_ok=True)
(raw/"preflight.json").write_text(json.dumps({
 "test_id":"T07_variant_divergence_unit_homogeneity",
 "backend_commit":head,
 "fact_sha256":fact_sha,
 "t04_checks":checks04,
 "t06_checks":checks06,
 "duckdb":duckdb_version,
 "problems":problems,
},indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")

print("T07 PREFLIGHT")
print(f"backend_commit={head}")
print(f"fact_sha256={fact_sha}")
print(f"duckdb={duckdb_version}")
print(f"problems={len(problems)}")
for p in problems: print(f"PROBLEM {p}")
if problems: raise SystemExit(2)
print("T07 PREFLIGHT OK")
