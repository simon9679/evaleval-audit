from __future__ import annotations

import hashlib
import json
import math
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FACT=ROOT/"tests"/"T03_corpus_boundary_impact"/"raw"/"fact_results_stage_f.parquet"
BACKEND=ROOT/"freeze"/"repos"/"eval_cards_backend_pipeline"
EXPECTED_COMMIT="9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
EXPECTED_SHA="e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"
EXPECTED_MIXED=1234
EXPECTED_APPLICABLE=7
EXPECTED_TRUE=5
EXPECTED_FALSE=2
TOL=1e-12

RAW_ALL=HERE/"raw"/"path_counterfactuals.jsonl"
RAW_FLIP=HERE/"raw"/"positive_to_negative_paths.jsonl"
RAW_ERR=HERE/"raw"/"integrity_errors.jsonl"
SUMMARY=HERE/"results"/"summary.json"
ANALYSIS=HERE/"results"/"RESULT_ANALYSIS.md"

def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def hard_error(msg):
    SUMMARY.write_text(json.dumps({"test_id":"T08_within_unit_variant_counterfactual","verdict":"ERROR","error":msg},indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("T08 ERROR"); print(msg); raise SystemExit(2)

if not (HERE/"raw"/"preflight.json").exists():
    hard_error("Missing T08 preflight evidence.")
head=subprocess.check_output(["git","-C",str(BACKEND),"rev-parse","HEAD"],text=True).strip()
if head!=EXPECTED_COMMIT: hard_error(f"Backend HEAD mismatch: {head}")
if not FACT.exists(): hard_error("Missing T03 Stage F parquet.")
if sha256(FACT)!=EXPECTED_SHA: hard_error("T03 Stage F parquet SHA mismatch.")

import duckdb
con=duckdb.connect()
p=FACT.as_posix().replace("'","''")
cols={r[0] for r in con.execute(f"DESCRIBE SELECT * FROM read_parquet('{p}')").fetchall()}
required={
 "comparability_group_id","fact_id","score","metric_unit",
 "has_variant_divergence","variant_divergence_magnitude",
 "variant_divergence_threshold","variant_threshold_basis",
 "source_record_path","result_idx","evaluation_id","evaluation_result_id"
}
missing=sorted(required-cols)
if missing: hard_error(f"Stage F schema missing required columns: {missing}")

fact_rows=con.execute(f"SELECT COUNT(*) FROM read_parquet('{p}')").fetchone()[0]
all_groups=con.execute(f"SELECT COUNT(DISTINCT comparability_group_id) FROM read_parquet('{p}') WHERE comparability_group_id IS NOT NULL").fetchone()[0]

mixed_ids=[r[0] for r in con.execute(f"""
 SELECT comparability_group_id
 FROM read_parquet('{p}')
 WHERE comparability_group_id IS NOT NULL
 GROUP BY comparability_group_id
 HAVING COUNT(DISTINCT metric_unit) FILTER (WHERE metric_unit IS NOT NULL) > 1
 ORDER BY comparability_group_id
""").fetchall()]

errors=[]
counts=Counter()
patterns=Counter()

if len(mixed_ids)!=EXPECTED_MIXED:
    errors.append({"type":"mixed_group_count","got":len(mixed_ids),"expected":EXPECTED_MIXED})

con.execute("CREATE TEMP TABLE _mixed(id VARCHAR)")
con.executemany("INSERT INTO _mixed VALUES (?)",[(x,) for x in mixed_ids])
rows=con.execute(f"""
 SELECT
  fr.comparability_group_id, fr.fact_id, fr.score, fr.metric_unit,
  fr.has_variant_divergence, fr.variant_divergence_magnitude,
  fr.variant_divergence_threshold, fr.variant_threshold_basis,
  fr.source_record_path, fr.result_idx, fr.evaluation_id,
  fr.evaluation_result_id
 FROM read_parquet('{p}') fr
 JOIN _mixed m ON m.id=fr.comparability_group_id
 ORDER BY fr.comparability_group_id, fr.fact_id
""").fetchall()
names=[d[0] for d in con.description]

groups=defaultdict(list)
for row in rows:
    r=dict(zip(names,row))
    groups[r["comparability_group_id"]].append(r)

def constant(rs,key):
    vals={r[key] for r in rs}
    if len(vals)!=1:
        counts["group_consistency_errors"]+=1
        errors.append({"type":"group_field_not_constant","group_id":rs[0]["comparability_group_id"],"field":key,"values":sorted(repr(v) for v in vals)})
        return None,False
    return next(iter(vals)),True

def is_num(v):
    return isinstance(v,(int,float)) and not isinstance(v,bool)

with RAW_ALL.open("w",encoding="utf-8",newline="\n") as fa, RAW_FLIP.open("w",encoding="utf-8",newline="\n") as ff:
    for gid,rs in groups.items():
        prod_flag,ok1=constant(rs,"has_variant_divergence")
        prod_div,ok2=constant(rs,"variant_divergence_magnitude")
        threshold,ok3=constant(rs,"variant_divergence_threshold")
        basis,ok4=constant(rs,"variant_threshold_basis")
        if not (ok1 and ok2 and ok3 and ok4):
            continue
        if prod_flag is None:
            continue

        counts["applicable_mixed_variant_paths"]+=1
        if bool(prod_flag): counts["production_true_paths"]+=1
        else: counts["production_false_paths"]+=1

        srows=[r for r in rs if is_num(r["score"])]
        if len(srows)<2:
            counts["divergence_reconstruction_errors"]+=1
            errors.append({"type":"fewer_than_two_numeric_scores","group_id":gid,"count":len(srows)})
            continue
        if any(r["metric_unit"] is None for r in srows):
            counts["invariant_errors"]+=1
            errors.append({"type":"null_unit_score_row","group_id":gid})
            continue

        vals=[float(r["score"]) for r in srows]
        global_div=max(vals)-min(vals)
        if prod_div is None or not math.isclose(float(prod_div),global_div,rel_tol=0.0,abs_tol=TOL):
            counts["divergence_reconstruction_errors"]+=1
            errors.append({"type":"production_divergence_mismatch","group_id":gid,"production":prod_div,"recomputed":global_div})

        by_unit=defaultdict(list)
        for r in srows:
            by_unit[r["metric_unit"]].append(r)

        unit_ranges={}
        unit_rows={}
        for unit,urs in sorted(by_unit.items()):
            uvals=[float(r["score"]) for r in urs]
            urange=max(uvals)-min(uvals) if len(uvals)>=2 else 0.0
            unit_ranges[unit]=urange
            unit_rows[unit]=[{
                "fact_id":r["fact_id"],
                "score":r["score"],
                "source_record_path":r["source_record_path"],
                "result_idx":r["result_idx"],
                "evaluation_id":r["evaluation_id"],
                "evaluation_result_id":r["evaluation_result_id"],
            } for r in urs]

        max_within=max(unit_ranges.values()) if unit_ranges else 0.0
        if max_within > global_div + TOL:
            counts["invariant_errors"]+=1
            counts["production_divergence_lt_max_within_unit_paths"]+=1
            errors.append({"type":"within_range_exceeds_global_range","group_id":gid,"global":global_div,"max_within":max_within})
        elif math.isclose(max_within,global_div,rel_tol=0.0,abs_tol=TOL):
            counts["production_divergence_eq_max_within_unit_paths"]+=1
        else:
            counts["production_divergence_gt_max_within_unit_paths"]+=1

        cf_flag=max_within > float(threshold)
        if cf_flag: counts["counterfactual_true_paths"]+=1
        else: counts["counterfactual_false_paths"]+=1

        if bool(prod_flag) and cf_flag:
            transition="positive_to_positive"
            counts["positive_to_positive_paths"]+=1
        elif bool(prod_flag) and not cf_flag:
            transition="positive_to_negative"
            counts["positive_to_negative_paths"]+=1
        elif (not bool(prod_flag)) and (not cf_flag):
            transition="negative_to_negative"
            counts["negative_to_negative_paths"]+=1
        else:
            transition="negative_to_positive"
            counts["negative_to_positive_paths"]+=1
            counts["invariant_errors"]+=1
            errors.append({"type":"negative_to_positive_impossible_transition","group_id":gid})

        units=sorted(by_unit)
        patterns[f"{' | '.join(units)} :: {transition}"]+=1

        record={
            "comparability_group_id":gid,
            "units":units,
            "production_divergence":global_div,
            "production_threshold":threshold,
            "production_threshold_basis":basis,
            "production_flag":bool(prod_flag),
            "unit_ranges":unit_ranges,
            "max_within_unit_range":max_within,
            "cross_label_excess":global_div-max_within,
            "counterfactual_flag":cf_flag,
            "transition":transition,
            "unit_rows":unit_rows,
        }
        fa.write(json.dumps(record,sort_keys=True,ensure_ascii=True)+"\n")
        if transition=="positive_to_negative":
            ff.write(json.dumps(record,sort_keys=True,ensure_ascii=True)+"\n")

# prereg population controls
if counts["applicable_mixed_variant_paths"]!=EXPECTED_APPLICABLE:
    errors.append({"type":"applicable_count","got":counts["applicable_mixed_variant_paths"],"expected":EXPECTED_APPLICABLE})
if counts["production_true_paths"]!=EXPECTED_TRUE:
    errors.append({"type":"production_true_count","got":counts["production_true_paths"],"expected":EXPECTED_TRUE})
if counts["production_false_paths"]!=EXPECTED_FALSE:
    errors.append({"type":"production_false_count","got":counts["production_false_paths"],"expected":EXPECTED_FALSE})

with RAW_ERR.open("w",encoding="utf-8",newline="\n") as f:
    for e in errors: f.write(json.dumps(e,sort_keys=True,ensure_ascii=True)+"\n")

integrity_bad=(
    len(errors)>0
    or counts["divergence_reconstruction_errors"]>0
    or counts["group_consistency_errors"]>0
    or counts["invariant_errors"]>0
)
if integrity_bad:
    verdict="INCONCLUSIVE"
elif counts["positive_to_negative_paths"]>=1:
    verdict="CONFIRMED"
else:
    verdict="REFUTED"

summary={
 "test_id":"T08_within_unit_variant_counterfactual",
 "verdict":verdict,
 "fact_rows_scanned":fact_rows,
 "comparability_groups_scanned":all_groups,
 "mixed_unit_groups":len(mixed_ids),
 "applicable_mixed_variant_paths":counts["applicable_mixed_variant_paths"],
 "production_true_paths":counts["production_true_paths"],
 "production_false_paths":counts["production_false_paths"],
 "positive_to_positive_paths":counts["positive_to_positive_paths"],
 "positive_to_negative_paths":counts["positive_to_negative_paths"],
 "negative_to_negative_paths":counts["negative_to_negative_paths"],
 "negative_to_positive_paths":counts["negative_to_positive_paths"],
 "production_divergence_gt_max_within_unit_paths":counts["production_divergence_gt_max_within_unit_paths"],
 "production_divergence_eq_max_within_unit_paths":counts["production_divergence_eq_max_within_unit_paths"],
 "production_divergence_lt_max_within_unit_paths":counts["production_divergence_lt_max_within_unit_paths"],
 "counterfactual_true_paths":counts["counterfactual_true_paths"],
 "counterfactual_false_paths":counts["counterfactual_false_paths"],
 "divergence_reconstruction_errors":counts["divergence_reconstruction_errors"],
 "group_consistency_errors":counts["group_consistency_errors"],
 "invariant_errors":counts["invariant_errors"],
 "integrity_error_records":len(errors),
 "unit_pattern_transitions":dict(sorted(patterns.items())),
 "competing_predictions":{
   "P1":"positive_to_negative_paths = 0",
   "P2":"positive_to_negative_paths >= 1"
 },
 "limitations":[
   "Exact unit-label partitioning is an operational counterfactual, not a semantic equivalence judgement.",
   "The frozen production threshold is held fixed to isolate row-eligibility effects.",
   "T08 does not establish which unit label is correct.",
   "T08 does not establish public-product impact."
 ],
 "evidence":{
   "input_fact_sha256":sha256(FACT),
   "path_counterfactuals_sha256":sha256(RAW_ALL),
   "positive_to_negative_paths_sha256":sha256(RAW_FLIP),
   "integrity_errors_sha256":sha256(RAW_ERR),
 }
}
SUMMARY.write_text(json.dumps(summary,indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")

lines=[
 "# RESULT_ANALYSIS — T08 Within-Unit Variant Divergence Counterfactual","",
 "Status: generated after execution from the frozen T08 summary.","",
 f"Primary verdict: `{verdict}`.","",
 "## Raw counts","",
]
for k in [
 "fact_rows_scanned","comparability_groups_scanned","mixed_unit_groups",
 "applicable_mixed_variant_paths","production_true_paths","production_false_paths",
 "positive_to_positive_paths","positive_to_negative_paths",
 "negative_to_negative_paths","negative_to_positive_paths",
 "production_divergence_gt_max_within_unit_paths",
 "production_divergence_eq_max_within_unit_paths",
 "production_divergence_lt_max_within_unit_paths",
 "counterfactual_true_paths","counterfactual_false_paths",
 "divergence_reconstruction_errors","group_consistency_errors",
 "invariant_errors","integrity_error_records"
]:
    lines.append(f"- `{k}` = {summary[k]}")

lines+=["","## Interpretation",""]
if verdict=="CONFIRMED":
    lines += [
      "P2 was observed: at least one production-positive mixed-unit variant path becomes negative when the raw range is constrained to the most permissive exact-unit partition and the frozen production threshold is held fixed.",
      "",
      "For each such path, the production positive decision depends on allowing score values from different exact declared unit-label partitions to contribute to one global range.",
      "",
      "This is an operational counterfactual result, not a semantic judgement that the unit labels are necessarily incompatible."
    ]
elif verdict=="REFUTED":
    lines += [
      "P1 was observed: every production-positive path remains positive using the maximum exact-unit range under the same frozen threshold.",
      "",
      "The mixed-label arithmetic therefore has no observed positive-boolean consequence under this exact-label eligibility counterfactual."
    ]
else:
    lines += [
      "Neither competing prediction can be interpreted because an integrity, reconstruction, or monotonicity invariant failed.",
      "",
      "No EvalEval defect attribution is permitted from this result."
    ]

lines += [
 "","## Scope limits","",
 "- Exact label equality is not asserted to be the only semantically valid equivalence rule.",
 "- The production threshold is intentionally held fixed.",
 "- The result does not identify the correct source unit.",
 "- Public-product exposure is outside T08.",
 "","## Evidence","",
 "- `raw/path_counterfactuals.jsonl`",
 "- `raw/positive_to_negative_paths.jsonl`",
 "- `raw/integrity_errors.jsonl`",
 "- `results/summary.json`",
]
ANALYSIS.write_text("\n".join(lines)+"\n",encoding="utf-8")

print("T08 COMPLETE")
for k in [
 "verdict","fact_rows_scanned","comparability_groups_scanned","mixed_unit_groups",
 "applicable_mixed_variant_paths","production_true_paths","production_false_paths",
 "positive_to_positive_paths","positive_to_negative_paths",
 "negative_to_negative_paths","negative_to_positive_paths",
 "production_divergence_gt_max_within_unit_paths",
 "production_divergence_eq_max_within_unit_paths",
 "production_divergence_lt_max_within_unit_paths",
 "counterfactual_true_paths","counterfactual_false_paths",
 "divergence_reconstruction_errors","group_consistency_errors",
 "invariant_errors","integrity_error_records"
]:
    print(f"{k}={summary[k]}")
print("unit_pattern_transitions="+json.dumps(summary["unit_pattern_transitions"],sort_keys=True,ensure_ascii=True))
print(r"summary=tests\T08_within_unit_variant_counterfactual\results\summary.json")
print(r"analysis=tests\T08_within_unit_variant_counterfactual\results\RESULT_ANALYSIS.md")
