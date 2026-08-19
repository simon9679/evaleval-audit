from __future__ import annotations
import json, hashlib
from pathlib import Path
import duckdb

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

FACT=ROOT/"tests"/"T03_corpus_boundary_impact"/"raw"/"fact_results_stage_f.parquet"
T10=ROOT/"tests"/"T10_source_metric_config_heterogeneity"/"raw"/"source_metric_configs.jsonl"
T06ROOT=ROOT/"tests"/"T06_eee_source_unit_trace"/"raw"/"source_root.json"
ORIG_SUM=HERE/"results"/"summary.json"

EXPECTED_SHA="e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"

def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

problems=[]

if not FACT.exists():
    problems.append(f"missing Stage F parquet: {FACT}")
elif sha256(FACT)!=EXPECTED_SHA:
    problems.append(f"Stage F SHA mismatch: {sha256(FACT)}")

if not T10.exists():
    problems.append(f"missing T10 source rows: {T10}")

eee_root=None
if not T06ROOT.exists():
    problems.append(f"missing T06 source_root.json: {T06ROOT}")
else:
    try:
        x=json.loads(T06ROOT.read_text(encoding="utf-8"))
        eee_root=x.get("selected_root")
        if not eee_root or not Path(eee_root).is_dir():
            problems.append(f"invalid selected EEE root: {eee_root!r}")
    except Exception as e:
        problems.append(f"cannot parse T06 source root: {type(e).__name__}: {e}")

orig_error=None
if ORIG_SUM.exists():
    try:
        s=json.loads(ORIG_SUM.read_text(encoding="utf-8"))
        orig_error=s.get("error")
        if s.get("verdict")!="ERROR":
            problems.append(f"original T14 summary verdict is not ERROR: {s.get('verdict')!r}")
    except Exception as e:
        problems.append(f"cannot parse original T14 summary: {type(e).__name__}: {e}")
else:
    problems.append("missing original T14 ERROR summary")

try:
    con=duckdb.connect()
    p=FACT.as_posix().replace("'","''")
    cols=[r[0] for r in con.execute(f"DESCRIBE SELECT * FROM read_parquet('{p}')").fetchall()]
except Exception as e:
    cols=[]
    problems.append(f"cannot inspect Stage F schema: {type(e).__name__}: {e}")

required=[
 "fact_id","comparability_group_id","evaluation_id","score",
 "evaluator_relationship","org_raw",
 "metric_kind","metric_unit","min_score","max_score",
 "has_variant_divergence","variant_divergence_magnitude",
 "variant_divergence_threshold","variant_threshold_basis",
 "variant_differing_fields"
]
missing=[c for c in required if c not in cols]
if missing:
    problems.append(f"Stage F missing fix1 required columns: {missing}")

if "generation_args_json" in cols:
    problems.append("unexpected generation_args_json present in final Stage F; fix1 assumption no longer matches artifact")

row_count=None
if T10.exists():
    try:
        rows=[json.loads(x) for x in T10.read_text(encoding="utf-8").splitlines() if x.strip()]
        row_count=len(rows)
        for r in rows:
            for k in ["fact_id","comparability_group_id","source_record_path","result_idx","source_metric_config_primary"]:
                if k not in r:
                    problems.append(f"T10 row missing {k}")
                    break
        if row_count!=12:
            problems.append(f"T10 source row count mismatch: {row_count}")
    except Exception as e:
        problems.append(f"cannot parse T10 rows: {type(e).__name__}: {e}")

payload={
 "test_id":"T14_source_metric_identity_preservation",
 "fix_id":"HARNESS_FIX_01",
 "fact_sha256":sha256(FACT) if FACT.exists() else None,
 "eee_root":eee_root,
 "t10_source_rows":row_count,
 "original_error":orig_error,
 "stage_f_has_org_raw":"org_raw" in cols,
 "stage_f_has_generation_args_json":"generation_args_json" in cols,
 "problems":problems,
}
(HERE/"raw"/"preflight_fix1.json").parent.mkdir(exist_ok=True)
(HERE/"raw"/"preflight_fix1.json").write_text(
    json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=True)+"\n",
    encoding="utf-8"
)

print("T14 FIX1 PREFLIGHT")
print(f"fact_sha256={payload['fact_sha256']}")
print(f"eee_root={eee_root}")
print(f"t10_source_rows={row_count}")
print(f"stage_f_has_org_raw={payload['stage_f_has_org_raw']}")
print(f"stage_f_has_generation_args_json={payload['stage_f_has_generation_args_json']}")
print(f"original_error={orig_error}")
print(f"problems={len(problems)}")
for p in problems: print(f"PROBLEM {p}")
if problems: raise SystemExit(2)
print("T14 FIX1 PREFLIGHT OK")
