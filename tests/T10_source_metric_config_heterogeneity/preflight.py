from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FACT=ROOT/"tests"/"T03_corpus_boundary_impact"/"raw"/"fact_results_stage_f.parquet"
T08_FLIPS=ROOT/"tests"/"T08_within_unit_variant_counterfactual"/"raw"/"positive_to_negative_paths.jsonl"
T09_SUM=ROOT/"tests"/"T09_headline_comparability_impact"/"results"/"summary.json"
SOURCE_ROOT=ROOT/"tests"/"T06_eee_source_unit_trace"/"raw"/"source_root.json"
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

t09={}
if not T09_SUM.exists():
    problems.append(f"missing T09 summary: {T09_SUM}")
else:
    try: t09=json.loads(T09_SUM.read_text(encoding="utf-8"))
    except Exception as e: problems.append(f"cannot parse T09 summary: {type(e).__name__}: {e}")

checks={
 "verdict":"CONFIRMED",
 "affected_group_ids":2,
 "affected_groups_present":2,
 "affected_groups_production_true":2,
 "production_variant_divergent_count":343,
 "counterfactual_variant_divergent_count":341,
 "headline_variant_divergent_count_delta":-2,
 "integrity_error_records":0,
}
for k,v in checks.items():
    if t09 and t09.get(k)!=v:
        problems.append(f"T09 mismatch {k}: got {t09.get(k)!r}, expected {v!r}")

flip_ids=[]
if not T08_FLIPS.exists():
    problems.append(f"missing T08 flip evidence: {T08_FLIPS}")
else:
    try:
        recs=[json.loads(line) for line in T08_FLIPS.read_text(encoding="utf-8").splitlines() if line.strip()]
        flip_ids=[r.get("comparability_group_id") for r in recs]
        if len(recs)!=2 or None in flip_ids or len(set(flip_ids))!=2:
            problems.append(f"T08 flip ids invalid: {flip_ids!r}")
    except Exception as e:
        problems.append(f"cannot parse T08 flip evidence: {type(e).__name__}: {e}")

eee_root=None
if not SOURCE_ROOT.exists():
    problems.append(f"missing T06 source root: {SOURCE_ROOT}")
else:
    try:
        payload=json.loads(SOURCE_ROOT.read_text(encoding="utf-8"))
        eee_root=payload.get("selected_root")
        if not eee_root or not Path(eee_root).is_dir():
            problems.append(f"invalid selected EEE root: {eee_root!r}")
    except Exception as e:
        problems.append(f"cannot parse T06 source root: {type(e).__name__}: {e}")

try:
    import duckdb
    duckdb_version=duckdb.__version__
except Exception as e:
    duckdb_version=None
    problems.append(f"missing dependency duckdb: {type(e).__name__}: {e}")

raw=HERE/"raw"; raw.mkdir(exist_ok=True)
(raw/"preflight.json").write_text(json.dumps({
 "test_id":"T10_source_metric_config_heterogeneity",
 "backend_commit":head,
 "fact_sha256":fact_sha,
 "t09_checks":checks,
 "affected_group_ids":flip_ids,
 "eee_root":eee_root,
 "duckdb":duckdb_version,
 "problems":problems,
},indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")

print("T10 PREFLIGHT")
print(f"backend_commit={head}")
print(f"fact_sha256={fact_sha}")
print(f"duckdb={duckdb_version}")
print(f"affected_group_ids={len(set(flip_ids)) if flip_ids else 0}")
print(f"eee_root={eee_root}")
print(f"problems={len(problems)}")
for p in problems: print(f"PROBLEM {p}")
if problems: raise SystemExit(2)
print("T10 PREFLIGHT OK")
