from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FACT=ROOT/"tests"/"T03_corpus_boundary_impact"/"raw"/"fact_results_stage_f.parquet"
T07_SUM=ROOT/"tests"/"T07_variant_divergence_unit_homogeneity"/"results"/"summary.json"
BACKEND=ROOT/"freeze"/"repos"/"eval_cards_backend_pipeline"

EXPECTED_COMMIT="9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
EXPECTED_SHA="e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"

def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

problems=[]
try:
    head=subprocess.check_output(["git","-C",str(BACKEND),"rev-parse","HEAD"],text=True).strip()
except Exception as e:
    head=None; problems.append(f"cannot resolve backend HEAD: {type(e).__name__}: {e}")
if head!=EXPECTED_COMMIT:
    problems.append(f"backend HEAD mismatch: {head}")

if not FACT.exists():
    problems.append(f"missing T03 Stage F parquet: {FACT}")
fact_sha=sha256(FACT) if FACT.exists() else None
if fact_sha and fact_sha!=EXPECTED_SHA:
    problems.append(f"T03 fact SHA mismatch: {fact_sha}")

t07={}
if not T07_SUM.exists():
    problems.append(f"missing T07 summary: {T07_SUM}")
else:
    try: t07=json.loads(T07_SUM.read_text(encoding="utf-8"))
    except Exception as e: problems.append(f"cannot parse T07 summary: {type(e).__name__}: {e}")

checks={
 "verdict":"CONFIRMED",
 "mixed_unit_groups":1234,
 "applicable_mixed_variant_paths":7,
 "unit_homogeneous_applicable_variant_paths":0,
 "unit_heterogeneous_applicable_variant_paths":7,
 "production_true_paths":5,
 "production_false_paths":2,
 "divergence_reconstruction_errors":0,
 "group_consistency_errors":0,
 "integrity_error_records":0,
}
for k,v in checks.items():
    if t07 and t07.get(k)!=v:
        problems.append(f"T07 mismatch {k}: got {t07.get(k)!r}, expected {v!r}")

try:
    import duckdb
    duckdb_version=duckdb.__version__
except Exception as e:
    duckdb_version=None
    problems.append(f"missing dependency duckdb: {type(e).__name__}: {e}")

raw=HERE/"raw"; raw.mkdir(exist_ok=True)
(raw/"preflight.json").write_text(json.dumps({
 "test_id":"T08_within_unit_variant_counterfactual",
 "backend_commit":head,
 "fact_sha256":fact_sha,
 "t07_checks":checks,
 "duckdb":duckdb_version,
 "problems":problems,
},indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")

print("T08 PREFLIGHT")
print(f"backend_commit={head}")
print(f"fact_sha256={fact_sha}")
print(f"duckdb={duckdb_version}")
print(f"problems={len(problems)}")
for p in problems: print(f"PROBLEM {p}")
if problems: raise SystemExit(2)
print("T08 PREFLIGHT OK")
