from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
T11_SUM=ROOT/"tests"/"T11_metric_config_field_decomposition"/"results"/"summary.json"
T10_ROWS=ROOT/"tests"/"T10_source_metric_config_heterogeneity"/"raw"/"source_metric_configs.jsonl"
FACT=ROOT/"tests"/"T03_corpus_boundary_impact"/"raw"/"fact_results_stage_f.parquet"
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

fact_sha=None
if not FACT.exists():
    problems.append(f"missing Stage F parquet: {FACT}")
else:
    fact_sha=sha256(FACT)
    if fact_sha!=EXPECTED_SHA:
        problems.append(f"Stage F SHA mismatch: {fact_sha}")

s={}
if not T11_SUM.exists():
    problems.append(f"missing T11 summary: {T11_SUM}")
else:
    try: s=json.loads(T11_SUM.read_text(encoding="utf-8"))
    except Exception as e: problems.append(f"cannot parse T11 summary: {type(e).__name__}: {e}")

if s:
    expected={
      "verdict":"CONFIRMED",
      "affected_group_ids":2,
      "source_rows_scanned":12,
      "affected_groups_with_claim_governing_field_variation":2,
      "integrity_error_records":0,
    }
    for k,v in expected.items():
        if s.get(k)!=v:
            problems.append(f"T11 mismatch {k}: got {s.get(k)!r}, expected {v!r}")
    pf=s.get("per_field_varying_group_counts",{})
    if pf.get("metric_id")!=2:
        problems.append(f"T11 metric_id varying-group count mismatch: {pf.get('metric_id')!r}")
    if pf.get("max_score")!=2:
        problems.append(f"T11 max_score varying-group count mismatch: {pf.get('max_score')!r}")

row_count=None
group_count=None
if not T10_ROWS.exists():
    problems.append(f"missing T10 source rows: {T10_ROWS}")
else:
    try:
        rows=[json.loads(line) for line in T10_ROWS.read_text(encoding="utf-8").splitlines() if line.strip()]
        row_count=len(rows)
        group_count=len({r.get("comparability_group_id") for r in rows})
        if row_count!=12: problems.append(f"T10 row count mismatch: {row_count}")
        if group_count!=2: problems.append(f"T10 group count mismatch: {group_count}")
    except Exception as e:
        problems.append(f"cannot parse T10 rows: {type(e).__name__}: {e}")

try:
    import duckdb
    duckdb_version=duckdb.__version__
except Exception as e:
    duckdb_version=None; problems.append(f"missing duckdb: {type(e).__name__}: {e}")

raw=HERE/"raw"; raw.mkdir(exist_ok=True)
(raw/"preflight.json").write_text(json.dumps({
 "test_id":"T12_source_metric_identity_collapse",
 "backend_commit":head,
 "fact_sha256":fact_sha,
 "source_row_count":row_count,
 "source_group_count":group_count,
 "duckdb":duckdb_version,
 "problems":problems,
},indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")

print("T12 PREFLIGHT")
print(f"backend_commit={head}")
print(f"fact_sha256={fact_sha}")
print(f"source_row_count={row_count}")
print(f"source_group_count={group_count}")
print(f"duckdb={duckdb_version}")
print(f"problems={len(problems)}")
for p in problems: print(f"PROBLEM {p}")
if problems: raise SystemExit(2)
print("T12 PREFLIGHT OK")
