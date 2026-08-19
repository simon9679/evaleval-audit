from __future__ import annotations
import json, re
from collections import defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

T10=ROOT/"tests"/"T10_source_metric_config_heterogeneity"/"raw"/"source_metric_configs.jsonl"
T06=ROOT/"tests"/"T06_eee_source_unit_trace"/"raw"/"source_root.json"

GID="d38d8f8e547287b6b0fc78f43f310762"
EXPECTED_IDS=[
 "openeval.wildbench.claude-score",
 "openeval.wildbench.gpt-score",
 "openeval.wildbench.llama-score",
 "openeval.wildbench.wildbench-score-rescaled",
]

TRACE=HERE/"raw"/"source_identity_trace.jsonl"
ERR=HERE/"raw"/"integrity_errors.jsonl"
SUMMARY=HERE/"results"/"summary.json"
ANALYSIS=HERE/"results"/"RESULT_ANALYSIS.md"

def canon(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True,default=str)

def parse_jsonish(v):
    if v is None:
        return None
    if isinstance(v,(list,dict,bool,int,float)):
        return v
    if isinstance(v,str):
        try:
            return json.loads(v)
        except Exception:
            return v
    return v

# Sufficient for the observed metric names; no manual aliases.
def observed_metric_slug(raw_name):
    s=str(raw_name).strip().lower()
    s=s.replace("&","and")
    s=re.sub(r"[\s_]+","-",s)
    s=re.sub(r"[^a-z0-9.\-]+","-",s)
    s=re.sub(r"-{2,}","-",s).strip("-")
    return s

errors=[]
pre=json.loads((HERE/"raw"/"preflight.json").read_text(encoding="utf-8"))
if pre.get("problems"):
    print("T15 ERROR")
    print("preflight contains problems")
    raise SystemExit(2)

EEE=Path(json.loads(T06.read_text(encoding="utf-8"))["selected_root"])
t10=[json.loads(x) for x in T10.read_text(encoding="utf-8").splitlines() if x.strip()]
rows=[r for r in t10 if r.get("comparability_group_id")==GID]

if len(rows)!=8:
    errors.append({"type":"affected_row_count","got":len(rows),"expected":8})

cache={}
traces=[]
for r in rows:
    try:
        rel=r["source_record_path"]
        idx=int(r["result_idx"])
        p=EEE/rel
        if not p.is_file():
            raise FileNotFoundError(str(p))
        if rel not in cache:
            cache[rel]=json.loads(p.read_text(encoding="utf-8"))
        ers=cache[rel].get("evaluation_results")
        if not isinstance(ers,list) or not (0 <= idx < len(ers)):
            raise IndexError(idx)
        er=ers[idx]
        mc=er.get("metric_config") or {}
        ad=mc.get("additional_details") or {}
        sid=mc.get("metric_id")
        raw_name=ad.get("raw_metric_name")
        slug=observed_metric_slug(raw_name) if raw_name not in (None,"") else None
        derived=f"openeval.wildbench.{slug}" if slug else None
        models=parse_jsonish(ad.get("metric_models_json"))
        signature={
          "metric_models_json":models,
          "metric_kind":mc.get("metric_kind"),
          "metric_unit":mc.get("metric_unit"),
          "lower_is_better":mc.get("lower_is_better"),
          "score_type":mc.get("score_type"),
          "min_score":mc.get("min_score"),
          "max_score":mc.get("max_score"),
          "metric_parameters":parse_jsonish(mc.get("metric_parameters")),
        }
        traces.append({
          "fact_id":r["fact_id"],
          "source_record_path":rel,
          "result_idx":idx,
          "source_metric_id":sid,
          "raw_metric_name":raw_name,
          "observed_metric_slug":slug,
          "derived_metric_id":derived,
          "exact_adapter_derivation":derived==sid,
          "nonname_signature":signature,
        })
    except Exception as e:
        errors.append({
          "type":"row_trace_error",
          "fact_id":r.get("fact_id"),
          "error":f"{type(e).__name__}: {e}",
        })

by_id=defaultdict(list)
for t in traces:
    by_id[t["source_metric_id"]].append(t)

unique_ids=sorted(by_id.keys())
raw_names=sorted({t["raw_metric_name"] for t in traces if t["raw_metric_name"] is not None})
exact_ids=sorted({
    sid for sid,items in by_id.items()
    if items and all(t["exact_adapter_derivation"] for t in items)
})

signature_by_id={}
for sid,items in by_id.items():
    sigs={canon(t["nonname_signature"]) for t in items}
    if len(sigs)!=1:
        errors.append({
          "type":"nonname_signature_inconsistent_within_source_id",
          "source_metric_id":sid,
          "signature_count":len(sigs),
        })
    else:
        signature_by_id[sid]=next(iter(sigs))

for sid in EXPECTED_IDS:
    items=by_id.get(sid,[])
    if len(items)!=2:
        errors.append({
          "type":"rows_per_source_id",
          "source_metric_id":sid,
          "got":len(items),
          "expected":2,
        })
    for t in items:
        if t["raw_metric_name"] in (None,""):
            errors.append({"type":"missing_raw_metric_name","source_metric_id":sid})

distinct_signatures=len(set(signature_by_id.values()))

complete=(
    len(rows)==8
    and unique_ids==EXPECTED_IDS
    and len(raw_names)==4
    and exact_ids==EXPECTED_IDS
    and distinct_signatures>=2
)

verdict="INCONCLUSIVE" if errors else ("CONFIRMED" if complete else "REFUTED")

with TRACE.open("w",encoding="utf-8",newline="\n") as f:
    for t in sorted(traces,key=lambda x:(x["source_metric_id"] or "",x["fact_id"])):
        f.write(json.dumps(t,sort_keys=True,ensure_ascii=True)+"\n")
with ERR.open("w",encoding="utf-8",newline="\n") as f:
    for e in errors:
        f.write(json.dumps(e,sort_keys=True,ensure_ascii=True)+"\n")

per_source={}
for sid in EXPECTED_IDS:
    items=by_id.get(sid,[])
    per_source[sid]={
      "row_count":len(items),
      "raw_metric_names":sorted({x["raw_metric_name"] for x in items if x["raw_metric_name"] is not None}),
      "exact_adapter_derivation_all":bool(items) and all(x["exact_adapter_derivation"] for x in items),
      "nonname_signature":json.loads(signature_by_id[sid]) if sid in signature_by_id else None,
    }

summary={
 "test_id":"T15_wildbench_authoritative_source_identity_trace",
 "verdict":verdict,
 "affected_group_id":GID,
 "affected_rows":len(rows),
 "unique_source_metric_ids":len(unique_ids),
 "source_metric_ids":unique_ids,
 "distinct_raw_metric_names":len(raw_names),
 "raw_metric_names":raw_names,
 "exact_adapter_derivation_ids":len(exact_ids),
 "exact_adapter_derivation_source_ids":exact_ids,
 "distinct_nonname_source_signatures":distinct_signatures,
 "source_identity_trace_complete":complete,
 "integrity_error_records":len(errors),
 "per_source_metric_id":per_source,
 "limitations":[
   "Distinct raw metric names do not establish semantic non-equivalence.",
   "This test does not map source names to official WildBench procedures from names alone.",
   "A later authoritative semantic adjudication is required."
 ],
}
SUMMARY.write_text(
    json.dumps(summary,indent=2,sort_keys=True,ensure_ascii=True)+"\n",
    encoding="utf-8"
)

lines=[
 "# RESULT_ANALYSIS — T15 WildBench Authoritative Source-Identity Trace",
 "",
 f"Primary verdict: `{verdict}`.",
 "",
 "## Raw counts",
 "",
 f"- affected_rows = {summary['affected_rows']}",
 f"- unique_source_metric_ids = {summary['unique_source_metric_ids']}",
 f"- distinct_raw_metric_names = {summary['distinct_raw_metric_names']}",
 f"- exact_adapter_derivation_ids = {summary['exact_adapter_derivation_ids']}",
 f"- distinct_nonname_source_signatures = {summary['distinct_nonname_source_signatures']}",
 f"- source_identity_trace_complete = {str(summary['source_identity_trace_complete']).lower()}",
 f"- integrity_error_records = {summary['integrity_error_records']}",
 "",
 "## Interpretation",
 "",
]
if verdict=="CONFIRMED":
    lines += [
      "All four claim-governing EEE source metric ids trace to four distinct preserved raw OpenEval metric names under the frozen adapter naming rule.",
      "",
      "At least two structured source signatures remain after excluding metric id and raw metric name.",
      "",
      "Therefore the four source identities are not merely downstream aliases generated from one raw OpenEval metric name.",
      "",
      "This remains a provenance result, not a semantic non-equivalence verdict."
    ]
elif verdict=="REFUTED":
    lines += [
      "The complete frozen trace does not support four independently traceable source-defined metric identities under the preregistered rule."
    ]
else:
    lines += [
      "The source-identity trace has an integrity or authority gap.",
      "",
      "No semantic inference is permitted."
    ]
ANALYSIS.write_text("\n".join(lines)+"\n",encoding="utf-8")

print("T15 COMPLETE")
for k in [
 "verdict","affected_rows","unique_source_metric_ids","distinct_raw_metric_names",
 "exact_adapter_derivation_ids","distinct_nonname_source_signatures",
 "source_identity_trace_complete","integrity_error_records"
]:
    print(f"{k}={summary[k]}")
print("raw_metric_names="+json.dumps(summary["raw_metric_names"],sort_keys=True,ensure_ascii=True))
print("per_source_metric_id="+json.dumps(summary["per_source_metric_id"],sort_keys=True,ensure_ascii=True))
print(r"summary=tests\T15_wildbench_authoritative_source_identity_trace\results\summary.json")
print(r"analysis=tests\T15_wildbench_authoritative_source_identity_trace\results\RESULT_ANALYSIS.md")
