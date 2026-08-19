from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
(HERE/"raw").mkdir(parents=True,exist_ok=True)
(HERE/"results").mkdir(parents=True,exist_ok=True)

T10=ROOT/"tests"/"T10_source_metric_config_heterogeneity"/"raw"/"source_metric_configs.jsonl"
T06=ROOT/"tests"/"T06_eee_source_unit_trace"/"raw"/"source_root.json"

GID="d38d8f8e547287b6b0fc78f43f310762"
EXPECTED_IDS=[
 "openeval.wildbench.claude-score",
 "openeval.wildbench.gpt-score",
 "openeval.wildbench.llama-score",
 "openeval.wildbench.wildbench-score-rescaled",
]

TRACE=HERE/"raw"/"source_scale_trace.jsonl"
ERR=HERE/"raw"/"integrity_errors.jsonl"
SUMMARY=HERE/"results"/"summary.json"
ANALYSIS=HERE/"results"/"RESULT_ANALYSIS.md"

TRANSFORM_KEY_TOKENS=("normal","rescal","transform","convert","scale")

def canon(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True,default=str)

def parse_jsonish(v):
    if v is None:
        return None
    if isinstance(v,(dict,list,bool,int,float)):
        return v
    if isinstance(v,str):
        s=v.strip()
        try:
            return json.loads(s)
        except Exception:
            return v
    return v

def nonempty_metric_parameters(v):
    v=parse_jsonish(v)
    if v is None:
        return False
    if isinstance(v,dict):
        return len(v)>0
    if isinstance(v,list):
        return len(v)>0
    if isinstance(v,str):
        return bool(v.strip()) and v.strip().lower() not in ("null","{}","[]")
    return True

errors=[]
pre=json.loads((HERE/"raw"/"preflight.json").read_text(encoding="utf-8"))
if pre.get("problems"):
    print("T16 ERROR")
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
        if not isinstance(ers,list) or not (0<=idx<len(ers)):
            raise IndexError(idx)
        er=ers[idx]
        mc=er.get("metric_config") or {}
        ad=mc.get("additional_details") or {}
        sid=mc.get("metric_id")
        mp=parse_jsonish(mc.get("metric_parameters"))

        transform_keys=[]
        if isinstance(ad,dict):
            for key in ad:
                kl=str(key).lower()
                if key=="raw_metric_name":
                    continue
                if any(tok in kl for tok in TRANSFORM_KEY_TOKENS):
                    transform_keys.append(str(key))

        scale_signature={
          "metric_unit":mc.get("metric_unit"),
          "min_score":mc.get("min_score"),
          "max_score":mc.get("max_score"),
        }
        traces.append({
          "fact_id":r["fact_id"],
          "source_record_path":rel,
          "result_idx":idx,
          "source_metric_id":sid,
          "raw_metric_name":ad.get("raw_metric_name") if isinstance(ad,dict) else None,
          "metric_kind":mc.get("metric_kind"),
          "score_type":mc.get("score_type"),
          "lower_is_better":mc.get("lower_is_better"),
          "scale_signature":scale_signature,
          "metric_parameters":mp,
          "metric_parameters_nonempty":nonempty_metric_parameters(mp),
          "additional_details_transform_keys":sorted(transform_keys),
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

for sid in EXPECTED_IDS:
    items=by_id.get(sid,[])
    if len(items)!=2:
        errors.append({
          "type":"rows_per_source_id",
          "source_metric_id":sid,
          "got":len(items),
          "expected":2,
        })

per_source={}
for sid in EXPECTED_IDS:
    items=by_id.get(sid,[])
    if not items:
        continue
    sigs={canon(x["scale_signature"]) for x in items}
    mps={canon(x["metric_parameters"]) for x in items}
    tks={canon(x["additional_details_transform_keys"]) for x in items}
    if len(sigs)!=1:
        errors.append({
          "type":"scale_signature_inconsistent_within_source_id",
          "source_metric_id":sid,
          "signature_count":len(sigs),
        })
    if len(mps)!=1:
        errors.append({
          "type":"metric_parameters_inconsistent_within_source_id",
          "source_metric_id":sid,
          "value_count":len(mps),
        })
    if len(tks)!=1:
        errors.append({
          "type":"transform_keys_inconsistent_within_source_id",
          "source_metric_id":sid,
          "value_count":len(tks),
        })
    per_source[sid]={
      "row_count":len(items),
      "scale_signature":json.loads(next(iter(sigs))) if len(sigs)==1 else None,
      "metric_parameters":json.loads(next(iter(mps))) if len(mps)==1 else None,
      "metric_parameters_nonempty_all":all(x["metric_parameters_nonempty"] for x in items),
      "additional_details_transform_keys":json.loads(next(iter(tks))) if len(tks)==1 else None,
    }

scale_sigs=[
    canon(per_source[sid]["scale_signature"])
    for sid in EXPECTED_IDS
    if sid in per_source and per_source[sid]["scale_signature"] is not None
]
distinct_scale_signatures=len(set(scale_sigs))
units=sorted({
    per_source[sid]["scale_signature"].get("metric_unit")
    for sid in EXPECTED_IDS
    if sid in per_source and per_source[sid]["scale_signature"] is not None
}, key=lambda x: "" if x is None else str(x))
bounds=sorted({
    canon({
      "min_score":per_source[sid]["scale_signature"].get("min_score"),
      "max_score":per_source[sid]["scale_signature"].get("max_score"),
    })
    for sid in EXPECTED_IDS
    if sid in per_source and per_source[sid]["scale_signature"] is not None
})

nonempty_parameter_ids=[
    sid for sid in EXPECTED_IDS
    if sid in per_source and per_source[sid]["metric_parameters_nonempty_all"]
]
transform_key_ids=[
    sid for sid in EXPECTED_IDS
    if sid in per_source and per_source[sid]["additional_details_transform_keys"]
]

# Modal scale: deterministic lexicographic tie break after count.
counter=Counter(scale_sigs)
modal_scale=None
if counter:
    max_count=max(counter.values())
    modal_scale=sorted(k for k,v in counter.items() if v==max_count)[0]

different_from_modal=[
    sid for sid in EXPECTED_IDS
    if sid in per_source
    and canon(per_source[sid]["scale_signature"]) != modal_scale
]

case_a=(distinct_scale_signatures==1)
case_b=(
    bool(different_from_modal)
    and all(sid in nonempty_parameter_ids for sid in different_from_modal)
)
common_scale_eligible=bool(case_a or case_b)

with TRACE.open("w",encoding="utf-8",newline="\n") as f:
    for t in sorted(traces,key=lambda x:(x["source_metric_id"] or "",x["fact_id"])):
        f.write(json.dumps(t,sort_keys=True,ensure_ascii=True)+"\n")
with ERR.open("w",encoding="utf-8",newline="\n") as f:
    for e in errors:
        f.write(json.dumps(e,sort_keys=True,ensure_ascii=True)+"\n")

if errors:
    verdict="INCONCLUSIVE"
elif common_scale_eligible:
    verdict="REFUTED"
else:
    verdict="CONFIRMED"

summary={
 "test_id":"T16_wildbench_common_scale_eligibility",
 "verdict":verdict,
 "affected_group_id":GID,
 "affected_rows":len(rows),
 "unique_source_metric_ids":len(by_id),
 "distinct_declared_units":len(units),
 "declared_units":units,
 "distinct_bound_signatures":len(bounds),
 "bound_signatures":[json.loads(x) for x in bounds],
 "distinct_scale_signatures":distinct_scale_signatures,
 "nonempty_metric_parameters_ids":len(nonempty_parameter_ids),
 "nonempty_metric_parameters_source_ids":nonempty_parameter_ids,
 "structured_transform_key_ids":len(transform_key_ids),
 "structured_transform_key_source_ids":transform_key_ids,
 "modal_scale_signature":json.loads(modal_scale) if modal_scale else None,
 "source_ids_different_from_modal_scale":different_from_modal,
 "eligibility_case_identical_scale":case_a,
 "eligibility_case_explicit_transform":case_b,
 "common_scale_eligible":common_scale_eligible,
 "integrity_error_records":len(errors),
 "per_source_metric_id":per_source,
 "limitations":[
   "This verdict concerns the frozen structured source representation, not undocumented upstream transformations.",
   "Different declared scales do not by themselves prove different latent constructs.",
   "The test does not prescribe the canonical repair."
 ],
}
SUMMARY.write_text(
    json.dumps(summary,indent=2,sort_keys=True,ensure_ascii=True)+"\n",
    encoding="utf-8"
)

lines=[
 "# RESULT_ANALYSIS — T16 WildBench Common-Scale Eligibility",
 "",
 f"Primary verdict: `{verdict}`.",
 "",
 "## Raw counts",
 "",
 f"- affected_rows = {summary['affected_rows']}",
 f"- unique_source_metric_ids = {summary['unique_source_metric_ids']}",
 f"- distinct_declared_units = {summary['distinct_declared_units']}",
 f"- distinct_bound_signatures = {summary['distinct_bound_signatures']}",
 f"- distinct_scale_signatures = {summary['distinct_scale_signatures']}",
 f"- nonempty_metric_parameters_ids = {summary['nonempty_metric_parameters_ids']}",
 f"- structured_transform_key_ids = {summary['structured_transform_key_ids']}",
 f"- common_scale_eligible = {str(summary['common_scale_eligible']).lower()}",
 f"- integrity_error_records = {summary['integrity_error_records']}",
 "",
 "## Interpretation",
 "",
]
if verdict=="CONFIRMED":
    lines += [
      "The four source channels are represented with multiple declared raw scales.",
      "",
      "The preregistered structured representation does not provide the explicit per-channel transformation metadata required by the common-scale eligibility predicate.",
      "",
      "Therefore direct raw-range arithmetic across all four channels is not justified by the frozen structured source representation itself.",
      "",
      "This does not prove that no undocumented upstream transformation exists."
    ]
elif verdict=="REFUTED":
    lines += [
      "The frozen structured source representation satisfies the preregistered common-scale eligibility predicate.",
      "",
      "The branch claiming absent represented commensurability stops."
    ]
else:
    lines += [
      "A claim-governing source or integrity condition failed.",
      "",
      "No common-scale verdict is admissible."
    ]
ANALYSIS.write_text("\n".join(lines)+"\n",encoding="utf-8")

print("T16 COMPLETE")
for k in [
 "verdict","affected_rows","unique_source_metric_ids","distinct_declared_units",
 "distinct_bound_signatures","distinct_scale_signatures",
 "nonempty_metric_parameters_ids","structured_transform_key_ids",
 "common_scale_eligible","integrity_error_records"
]:
    print(f"{k}={summary[k]}")
print("declared_units="+json.dumps(summary["declared_units"],sort_keys=True,ensure_ascii=True))
print("bound_signatures="+json.dumps(summary["bound_signatures"],sort_keys=True,ensure_ascii=True))
print("source_ids_different_from_modal_scale="+json.dumps(summary["source_ids_different_from_modal_scale"],sort_keys=True,ensure_ascii=True))
print("per_source_metric_id="+json.dumps(summary["per_source_metric_id"],sort_keys=True,ensure_ascii=True))
print(r"summary=tests\T16_wildbench_common_scale_eligibility\results\summary.json")
print(r"analysis=tests\T16_wildbench_common_scale_eligibility\results\RESULT_ANALYSIS.md")
