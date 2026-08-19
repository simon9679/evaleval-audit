from __future__ import annotations
import json, math, sys
from collections import defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
(HERE/"raw").mkdir(parents=True,exist_ok=True)
(HERE/"results").mkdir(parents=True,exist_ok=True)

FACT=ROOT/"tests"/"T03_corpus_boundary_impact"/"raw"/"fact_results_stage_f.parquet"
T16=ROOT/"tests"/"T16_wildbench_common_scale_eligibility"/"results"/"summary.json"
BACKEND=ROOT/"freeze"/"repos"/"eval_cards_backend_pipeline"

GID="d38d8f8e547287b6b0fc78f43f310762"
EXPECTED_IDS=[
 "openeval.wildbench.claude-score",
 "openeval.wildbench.gpt-score",
 "openeval.wildbench.llama-score",
 "openeval.wildbench.wildbench-score-rescaled",
]

TRACE=HERE/"raw"/"source_and_group_config_trace.json"
ERR=HERE/"raw"/"integrity_errors.jsonl"
SUMMARY=HERE/"results"/"summary.json"
ANALYSIS=HERE/"results"/"RESULT_ANALYSIS.md"

def canon(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True,default=str)

def prod_max_nonnull(values):
    vals=[v for v in values if v is not None]
    return max(vals) if vals else None

def close(a,b,tol=1e-12):
    return math.isclose(float(a),float(b),rel_tol=0.0,abs_tol=tol)

errors=[]
pre=json.loads((HERE/"raw"/"preflight.json").read_text(encoding="utf-8"))
if pre.get("problems"):
    print("T17 ERROR")
    print("preflight contains problems")
    raise SystemExit(2)

try:
    import duckdb
    sys.path.insert(0,str(BACKEND/"src"))
    from eval_card_backend.canonicalise.thresholds import compute_threshold
except Exception as e:
    print("T17 ERROR")
    print(f"import failed: {type(e).__name__}: {e}")
    raise SystemExit(2)

t16=json.loads(T16.read_text(encoding="utf-8"))
source_cfg={}
for sid in EXPECTED_IDS:
    item=(t16.get("per_source_metric_id") or {}).get(sid)
    if not item:
        errors.append({"type":"missing_T16_source_id","source_metric_id":sid})
        continue
    scale=item.get("scale_signature")
    if not isinstance(scale,dict):
        errors.append({"type":"missing_T16_scale_signature","source_metric_id":sid})
        continue
    # metric_kind is fixed from T15/T14 source provenance and is common for all
    # four. Read it from Stage-F rows below for exact comparison rather than
    # inventing a value here.
    source_cfg[sid]={
      "metric_unit":scale.get("metric_unit"),
      "min_score":scale.get("min_score"),
      "max_score":scale.get("max_score"),
    }

con=duckdb.connect()
path=FACT.as_posix().replace("'","''")
cursor=con.execute(f"""
SELECT fact_id, metric_kind, metric_unit, min_score, max_score,
       variant_divergence_threshold, variant_threshold_basis
FROM read_parquet('{path}')
WHERE comparability_group_id = ?
ORDER BY fact_id
""",[GID])
cols=[d[0] for d in cursor.description]
rows=[dict(zip(cols,r)) for r in cursor.fetchall()]

if len(rows)!=8:
    errors.append({"type":"affected_row_count","got":len(rows),"expected":8})

# Source-id assignment comes from T16 scale signatures. Because GPT and Llama
# share one scale, use T15 source trace to map each fact id exactly.
T15TRACE=ROOT/"tests"/"T15_wildbench_authoritative_source_identity_trace"/"raw"/"source_identity_trace.jsonl"
fact_to_sid={}
if not T15TRACE.is_file():
    errors.append({"type":"missing_T15_trace","path":str(T15TRACE)})
else:
    for line in T15TRACE.read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        obj=json.loads(line)
        if obj.get("source_metric_id") in EXPECTED_IDS:
            fact_to_sid[obj["fact_id"]]=obj["source_metric_id"]

if len(fact_to_sid)!=8:
    errors.append({"type":"fact_to_source_id_count","got":len(fact_to_sid),"expected":8})

# Ensure Stage-F row metadata is internally consistent with source signatures.
kinds_by_sid=defaultdict(set)
for r in rows:
    sid=fact_to_sid.get(r["fact_id"])
    if sid is None:
        errors.append({"type":"unmapped_fact_id","fact_id":r["fact_id"]})
        continue
    kinds_by_sid[sid].add(r["metric_kind"])
    expected=source_cfg.get(sid)
    if expected:
        observed={
          "metric_unit":r["metric_unit"],
          "min_score":r["min_score"],
          "max_score":r["max_score"],
        }
        if canon(observed)!=canon(expected):
            errors.append({
              "type":"stage_source_scale_mismatch",
              "fact_id":r["fact_id"],
              "source_metric_id":sid,
              "observed":observed,
              "expected":expected,
            })

for sid in EXPECTED_IDS:
    ks=kinds_by_sid.get(sid,set())
    if len(ks)!=1:
        errors.append({"type":"metric_kind_inconsistent","source_metric_id":sid,"values":sorted(ks,key=str)})
    elif sid in source_cfg:
        source_cfg[sid]["metric_kind"]=next(iter(ks))

production_cfg={
 "metric_kind":prod_max_nonnull([r["metric_kind"] for r in rows]),
 "metric_unit":prod_max_nonnull([r["metric_unit"] for r in rows]),
 "min_score":prod_max_nonnull([r["min_score"] for r in rows]),
 "max_score":prod_max_nonnull([r["max_score"] for r in rows]),
}

missing=[k for k,v in production_cfg.items() if v is None]
if missing:
    errors.append({"type":"production_config_missing_fields","fields":missing})

matches=[
 sid for sid,cfg in source_cfg.items()
 if canon(cfg)==canon(production_cfg)
]

field_provenance={}
for field,value in production_cfg.items():
    field_provenance[field]=sorted([
      sid for sid,cfg in source_cfg.items()
      if cfg.get(field)==value
    ])

threshold_values={canon(r["variant_divergence_threshold"]) for r in rows}
basis_values={canon(r["variant_threshold_basis"]) for r in rows}
if len(threshold_values)!=1:
    errors.append({"type":"frozen_threshold_not_constant","values":sorted(threshold_values)})
if len(basis_values)!=1:
    errors.append({"type":"frozen_basis_not_constant","values":sorted(basis_values)})

frozen_threshold=rows[0]["variant_divergence_threshold"] if rows else None
frozen_basis=rows[0]["variant_threshold_basis"] if rows else None

replay_threshold,replay_basis=compute_threshold(production_cfg)
threshold_replay_exact=(
    frozen_threshold is not None
    and close(replay_threshold,frozen_threshold)
    and replay_basis==frozen_basis
)
if not threshold_replay_exact:
    errors.append({
      "type":"threshold_replay_mismatch",
      "production_config":production_cfg,
      "frozen_threshold":frozen_threshold,
      "frozen_basis":frozen_basis,
      "replay_threshold":replay_threshold,
      "replay_basis":replay_basis,
    })

trace={
 "group_id":GID,
 "production_group_config":production_cfg,
 "source_configs":source_cfg,
 "production_signature_source_matches":matches,
 "production_signature_source_match_count":len(matches),
 "field_provenance":field_provenance,
 "frozen_threshold":frozen_threshold,
 "frozen_threshold_basis":frozen_basis,
 "replay_threshold":replay_threshold,
 "replay_threshold_basis":replay_basis,
 "threshold_replay_exact":threshold_replay_exact,
}
TRACE.write_text(json.dumps(trace,indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")
with ERR.open("w",encoding="utf-8",newline="\n") as f:
    for e in errors:
        f.write(json.dumps(e,sort_keys=True,ensure_ascii=True)+"\n")

if errors:
    verdict="INCONCLUSIVE"
elif len(matches)==0:
    verdict="CONFIRMED"
else:
    verdict="REFUTED"

summary={
 "test_id":"T17_wildbench_synthetic_group_metric_config",
 "verdict":verdict,
 "affected_group_id":GID,
 "affected_rows":len(rows),
 "exact_source_metric_ids":len(source_cfg),
 "production_group_config":production_cfg,
 "production_signature_source_match_count":len(matches),
 "production_signature_source_matches":matches,
 "field_provenance":field_provenance,
 "frozen_threshold":frozen_threshold,
 "frozen_threshold_basis":frozen_basis,
 "replay_threshold":replay_threshold,
 "replay_threshold_basis":replay_basis,
 "threshold_replay_exact":threshold_replay_exact,
 "integrity_error_records":len(errors),
 "source_configs":source_cfg,
 "limitations":[
   "A synthetic group config is not automatically invalid in every application.",
   "T17 does not establish semantic non-equivalence of all source channels.",
   "T17 does not prescribe a repair."
 ],
}
SUMMARY.write_text(json.dumps(summary,indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")

lines=[
 "# RESULT_ANALYSIS — T17 WildBench Synthetic Group MetricConfig Provenance",
 "",
 f"Primary verdict: `{verdict}`.",
 "",
 "## Raw values",
 "",
 f"- affected_rows = {summary['affected_rows']}",
 f"- exact_source_metric_ids = {summary['exact_source_metric_ids']}",
 f"- production_signature_source_match_count = {summary['production_signature_source_match_count']}",
 f"- threshold_replay_exact = {str(summary['threshold_replay_exact']).lower()}",
 f"- frozen_threshold = {summary['frozen_threshold']}",
 f"- frozen_threshold_basis = `{summary['frozen_threshold_basis']}`",
 f"- integrity_error_records = {summary['integrity_error_records']}",
 "",
 "## Production group config",
 "",
 f"`{canon(production_cfg)}`",
 "",
 "## Interpretation",
 "",
]
if verdict=="CONFIRMED":
    lines += [
      "The reconstructed production group metric configuration matches no exact source metric configuration.",
      "",
      "The frozen production threshold and basis are exactly reproduced from that reconstructed configuration.",
      "",
      "Therefore this claim-governing group uses a synthetic field-wise group metric configuration for threshold selection.",
      "",
      "This is a provenance/representation result and does not by itself prove that every synthetic group config is invalid."
    ]
elif verdict=="REFUTED":
    lines += [
      "The reconstructed production group metric configuration exactly matches at least one source metric configuration.",
      "",
      "The synthetic-config claim is refuted."
    ]
else:
    lines += [
      "An integrity or replay condition failed.",
      "",
      "No synthetic-config verdict is admissible."
    ]
ANALYSIS.write_text("\n".join(lines)+"\n",encoding="utf-8")

print("T17 COMPLETE")
for k in [
 "verdict","affected_rows","exact_source_metric_ids",
 "production_signature_source_match_count","threshold_replay_exact",
 "frozen_threshold","frozen_threshold_basis",
 "replay_threshold","replay_threshold_basis","integrity_error_records"
]:
    print(f"{k}={summary[k]}")
print("production_group_config="+json.dumps(summary["production_group_config"],sort_keys=True,ensure_ascii=True))
print("production_signature_source_matches="+json.dumps(summary["production_signature_source_matches"],sort_keys=True,ensure_ascii=True))
print("field_provenance="+json.dumps(summary["field_provenance"],sort_keys=True,ensure_ascii=True))
print("source_configs="+json.dumps(summary["source_configs"],sort_keys=True,ensure_ascii=True))
print(r"summary=tests\T17_wildbench_synthetic_group_metric_config\results\summary.json")
print(r"analysis=tests\T17_wildbench_synthetic_group_metric_config\results\RESULT_ANALYSIS.md")
