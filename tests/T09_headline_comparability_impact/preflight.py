from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FACT=ROOT/"tests"/"T03_corpus_boundary_impact"/"raw"/"fact_results_stage_f.parquet"
T08=ROOT/"tests"/"T08_within_unit_variant_counterfactual"
T08_SUM=T08/"results"/"summary.json"
T08_FLIPS=T08/"raw"/"positive_to_negative_paths.jsonl"
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

t08={}
if not T08_SUM.exists():
    problems.append(f"missing T08 summary: {T08_SUM}")
else:
    try: t08=json.loads(T08_SUM.read_text(encoding="utf-8"))
    except Exception as e: problems.append(f"cannot parse T08 summary: {type(e).__name__}: {e}")

checks={
 "verdict":"CONFIRMED",
 "applicable_mixed_variant_paths":7,
 "production_true_paths":5,
 "production_false_paths":2,
 "positive_to_positive_paths":3,
 "positive_to_negative_paths":2,
 "negative_to_negative_paths":2,
 "negative_to_positive_paths":0,
 "divergence_reconstruction_errors":0,
 "group_consistency_errors":0,
 "invariant_errors":0,
 "integrity_error_records":0,
}
for k,v in checks.items():
    if t08 and t08.get(k)!=v:
        problems.append(f"T08 mismatch {k}: got {t08.get(k)!r}, expected {v!r}")

flip_count=None
flip_ids=[]
if not T08_FLIPS.exists():
    problems.append(f"missing T08 flip evidence: {T08_FLIPS}")
else:
    try:
        recs=[json.loads(line) for line in T08_FLIPS.read_text(encoding="utf-8").splitlines() if line.strip()]
        flip_count=len(recs)
        flip_ids=[r.get("comparability_group_id") for r in recs]
        if flip_count!=2:
            problems.append(f"T08 flip record count mismatch: {flip_count}")
        if None in flip_ids or len(set(flip_ids))!=2:
            problems.append(f"T08 flip ids are not two unique non-null ids: {flip_ids!r}")
    except Exception as e:
        problems.append(f"cannot parse T08 flip evidence: {type(e).__name__}: {e}")

try:
    import duckdb
    duckdb_version=duckdb.__version__
except Exception as e:
    duckdb_version=None
    problems.append(f"missing dependency duckdb: {type(e).__name__}: {e}")

raw=HERE/"raw"; raw.mkdir(exist_ok=True)
(raw/"preflight.json").write_text(json.dumps({
 "test_id":"T09_headline_comparability_impact",
 "backend_commit":head,
 "fact_sha256":fact_sha,
 "t08_checks":checks,
 "t08_flip_record_count":flip_count,
 "t08_flip_ids":flip_ids,
 "duckdb":duckdb_version,
 "problems":problems,
},indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")

print("T09 PREFLIGHT")
print(f"backend_commit={head}")
print(f"fact_sha256={fact_sha}")
print(f"duckdb={duckdb_version}")
print(f"t08_flip_record_count={flip_count}")
print(f"t08_unique_flip_ids={len(set(flip_ids)) if flip_ids else 0}")
print(f"problems={len(problems)}")
for p in problems: print(f"PROBLEM {p}")
if problems: raise SystemExit(2)
print("T09 PREFLIGHT OK")
