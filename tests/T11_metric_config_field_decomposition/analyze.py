from __future__ import annotations
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ROWS=ROOT/"tests"/"T10_source_metric_config_heterogeneity"/"raw"/"source_metric_configs.jsonl"
SUMMARY=HERE/"results"/"summary.json"
ANALYSIS=HERE/"results"/"RESULT_ANALYSIS.md"
RAW_ALL=HERE/"raw"/"field_decomposition.jsonl"
RAW_CLAIM=HERE/"raw"/"claim_governing_variation_groups.jsonl"
RAW_ERR=HERE/"raw"/"integrity_errors.jsonl"

FIELDS=[
 "metric_id","metric_name","metric_kind","metric_parameters",
 "lower_is_better","score_type","min_score","max_score"
]
CLAIM_FIELDS=[
 "metric_id","metric_kind","metric_parameters",
 "lower_is_better","score_type","min_score","max_score"
]

def canon(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True)

if not (HERE/"raw"/"preflight.json").exists():
    SUMMARY.write_text(json.dumps({"test_id":"T11_metric_config_field_decomposition","verdict":"ERROR","error":"Missing preflight evidence."},indent=2)+"\n",encoding="utf-8")
    print("T11 ERROR")
    raise SystemExit(2)

rows=[json.loads(line) for line in ROWS.read_text(encoding="utf-8").splitlines() if line.strip()]
errors=[]
if len(rows)!=12:
    errors.append({"type":"source_row_count","got":len(rows),"expected":12})

by_group=defaultdict(list)
for r in rows:
    gid=r.get("comparability_group_id")
    primary=r.get("source_metric_config_primary")
    unit=r.get("source_metric_unit_normalized")
    if gid is None or not isinstance(primary,dict) or unit is None:
        errors.append({"type":"invalid_source_row","fact_id":r.get("fact_id")})
        continue
    by_group[gid].append(r)

if len(by_group)!=2:
    errors.append({"type":"group_count","got":len(by_group),"expected":2})

field_counts=Counter()
unit_disjoint_counts=Counter()
group_outputs=[]

with RAW_ALL.open("w",encoding="utf-8",newline="\n") as fa, RAW_CLAIM.open("w",encoding="utf-8",newline="\n") as fc:
    for gid,rs in sorted(by_group.items()):
        units=sorted({r["source_metric_unit_normalized"] for r in rs})
        field_info={}
        varying=[]
        claim_varying=[]

        for field in FIELDS:
            values=[r["source_metric_config_primary"].get(field) for r in rs]
            distinct=sorted({canon(v) for v in values})
            varies=len(distinct)>=2
            if varies:
                field_counts[field]+=1
                varying.append(field)
                if field in CLAIM_FIELDS:
                    claim_varying.append(field)

            unit_to_values={}
            for unit in units:
                unit_to_values[unit]=sorted({
                    canon(r["source_metric_config_primary"].get(field))
                    for r in rs
                    if r["source_metric_unit_normalized"]==unit
                })

            disjoint=True
            if len(units)>=2:
                seen=[]
                for unit in units:
                    vals=set(unit_to_values[unit])
                    for prev in seen:
                        if vals & prev:
                            disjoint=False
                    seen.append(vals)
            else:
                disjoint=False

            if varies and disjoint:
                unit_disjoint_counts[field]+=1

            field_info[field]={
                "varies":varies,
                "distinct_value_count":len(distinct),
                "distinct_values":distinct,
                "unit_to_values":unit_to_values,
                "unit_value_sets_disjoint":bool(varies and disjoint),
            }

        if claim_varying:
            classification="claim_governing_variation"
        elif varying==["metric_name"]:
            classification="display_name_only_variation"
        elif not varying:
            classification="no_nonunit_field_variation"
        else:
            classification="nonclaim_mixed_variation"

        out={
            "comparability_group_id":gid,
            "units":units,
            "source_row_count":len(rs),
            "varying_fields":varying,
            "claim_governing_varying_fields":claim_varying,
            "classification":classification,
            "fields":field_info,
        }
        group_outputs.append(out)
        fa.write(json.dumps(out,sort_keys=True,ensure_ascii=True)+"\n")
        if claim_varying:
            fc.write(json.dumps(out,sort_keys=True,ensure_ascii=True)+"\n")

counts=Counter()
for g in group_outputs:
    c=g["classification"]
    if c=="claim_governing_variation":
        counts["affected_groups_with_claim_governing_field_variation"]+=1
    elif c=="display_name_only_variation":
        counts["affected_groups_with_display_name_only_variation"]+=1
    elif c=="no_nonunit_field_variation":
        counts["affected_groups_with_no_nonunit_field_variation"]+=1

with RAW_ERR.open("w",encoding="utf-8",newline="\n") as f:
    for e in errors:
        f.write(json.dumps(e,sort_keys=True,ensure_ascii=True)+"\n")

if errors:
    verdict="INCONCLUSIVE"
elif counts["affected_groups_with_claim_governing_field_variation"]>=1:
    verdict="CONFIRMED"
else:
    verdict="REFUTED"

per_group={
    g["comparability_group_id"]:{
        "units":g["units"],
        "varying_fields":g["varying_fields"],
        "claim_governing_varying_fields":g["claim_governing_varying_fields"],
        "classification":g["classification"],
    } for g in group_outputs
}

summary={
 "test_id":"T11_metric_config_field_decomposition",
 "verdict":verdict,
 "affected_group_ids":len(by_group),
 "source_rows_scanned":len(rows),
 "affected_groups_with_claim_governing_field_variation":counts["affected_groups_with_claim_governing_field_variation"],
 "affected_groups_with_display_name_only_variation":counts["affected_groups_with_display_name_only_variation"],
 "affected_groups_with_no_nonunit_field_variation":counts["affected_groups_with_no_nonunit_field_variation"],
 "per_field_varying_group_counts":{f:field_counts[f] for f in FIELDS},
 "per_field_unit_disjoint_value_group_counts":{f:unit_disjoint_counts[f] for f in FIELDS},
 "per_group":per_group,
 "integrity_error_records":len(errors),
 "competing_predictions":{
   "P1":"affected_groups_with_claim_governing_field_variation = 0",
   "P2":"affected_groups_with_claim_governing_field_variation >= 1"
 },
 "limitations":[
   "Field variation does not itself prove different semantic estimands.",
   "Structured source metadata are not final semantic authority.",
   "T11 does not adjudicate original-publisher provenance or correct grouping."
 ]
}
SUMMARY.write_text(json.dumps(summary,indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")

lines=[
 "# RESULT_ANALYSIS — T11 MetricConfig Field-Level Decomposition","",
 "Status: generated after execution from the frozen T11 summary.","",
 f"Primary verdict: `{verdict}`.","",
 "## Raw counts","",
 f"- `affected_group_ids` = {summary['affected_group_ids']}",
 f"- `source_rows_scanned` = {summary['source_rows_scanned']}",
 f"- `affected_groups_with_claim_governing_field_variation` = {summary['affected_groups_with_claim_governing_field_variation']}",
 f"- `affected_groups_with_display_name_only_variation` = {summary['affected_groups_with_display_name_only_variation']}",
 f"- `affected_groups_with_no_nonunit_field_variation` = {summary['affected_groups_with_no_nonunit_field_variation']}",
 f"- `integrity_error_records` = {summary['integrity_error_records']}",
 "",
 "## Per-field varying group counts","",
]
for f in FIELDS:
    lines.append(f"- `{f}` = {summary['per_field_varying_group_counts'][f]}")
lines += ["","## Interpretation",""]
if verdict=="CONFIRMED":
    lines += [
      "P2 was observed: at least one consequential group varies in one or more claim-governing structured MetricConfig fields beyond display naming.",
      "",
      "The exact varying fields are reported in `per_group` and the raw field decomposition.",
      "",
      "A later semantic/reference test should be restricted to those fields."
    ]
elif verdict=="REFUTED":
    lines += [
      "P1 was observed: no consequential group varies in the preregistered claim-governing fields.",
      "",
      "Any remaining non-unit heterogeneity is therefore limited to display naming under this instrument."
    ]
else:
    lines += [
      "The field decomposition cannot be interpreted because an integrity invariant failed."
    ]
ANALYSIS.write_text("\n".join(lines)+"\n",encoding="utf-8")

print("T11 COMPLETE")
for k in [
 "verdict","affected_group_ids","source_rows_scanned",
 "affected_groups_with_claim_governing_field_variation",
 "affected_groups_with_display_name_only_variation",
 "affected_groups_with_no_nonunit_field_variation",
 "integrity_error_records"
]:
    print(f"{k}={summary[k]}")
print("per_field_varying_group_counts="+json.dumps(summary["per_field_varying_group_counts"],sort_keys=True,ensure_ascii=True))
print("per_field_unit_disjoint_value_group_counts="+json.dumps(summary["per_field_unit_disjoint_value_group_counts"],sort_keys=True,ensure_ascii=True))
print("per_group="+json.dumps(summary["per_group"],sort_keys=True,ensure_ascii=True))
print(r"summary=tests\T11_metric_config_field_decomposition\results\summary.json")
print(r"analysis=tests\T11_metric_config_field_decomposition\results\RESULT_ANALYSIS.md")
