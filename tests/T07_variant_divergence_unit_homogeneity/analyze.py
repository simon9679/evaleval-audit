from __future__ import annotations

import hashlib
import json
import math
import subprocess
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FACT=ROOT/"tests"/"T03_corpus_boundary_impact"/"raw"/"fact_results_stage_f.parquet"
BACKEND=ROOT/"freeze"/"repos"/"eval_cards_backend_pipeline"
EXPECTED_COMMIT="9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
EXPECTED_SHA="e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"
EXPECTED_MIXED=1234
EXPECTED_APPLICABLE=7

RAW_ALL=HERE/"raw"/"applicable_variant_paths.jsonl"
RAW_HET=HERE/"raw"/"unit_heterogeneous_paths.jsonl"
RAW_ERR=HERE/"raw"/"integrity_errors.jsonl"
SUMMARY=HERE/"results"/"summary.json"
ANALYSIS=HERE/"results"/"RESULT_ANALYSIS.md"

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def hard_error(msg):
    SUMMARY.write_text(json.dumps({"test_id":"T07_variant_divergence_unit_homogeneity","verdict":"ERROR","error":msg},indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("T07 ERROR"); print(msg); raise SystemExit(2)

if not (HERE/"raw"/"preflight.json").exists():
    hard_error("Missing T07 preflight evidence.")
head=subprocess.check_output(["git","-C",str(BACKEND),"rev-parse","HEAD"],text=True).strip()
if head != EXPECTED_COMMIT: hard_error(f"Backend HEAD mismatch: {head}")
if not FACT.exists(): hard_error("Missing T03 Stage F parquet.")
if sha256(FACT) != EXPECTED_SHA: hard_error("T03 Stage F parquet SHA mismatch.")

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

groups={}
for tup in rows:
    r=dict(zip(names,tup))
    groups.setdefault(r["comparability_group_id"],[]).append(r)

counts=Counter()
patterns=Counter()

def constant(rows,key):
    vals={r[key] for r in rows}
    if len(vals)!=1:
        counts["group_consistency_errors"]+=1
        errors.append({"type":"group_field_not_constant","group_id":rows[0]["comparability_group_id"],"field":key,"values":sorted(repr(v) for v in vals)})
        return None,False
    return next(iter(vals)),True

def score_rows(rows):
    out=[]
    for r in rows:
        v=r["score"]
        if isinstance(v,(int,float)) and not isinstance(v,bool):
            out.append(r)
    return out

with RAW_ALL.open("w",encoding="utf-8",newline="\n") as fa, RAW_HET.open("w",encoding="utf-8",newline="\n") as fh:
    for gid,rs in groups.items():
        flag,ok1=constant(rs,"has_variant_divergence")
        div,ok2=constant(rs,"variant_divergence_magnitude")
        thr,ok3=constant(rs,"variant_divergence_threshold")
        basis,ok4=constant(rs,"variant_threshold_basis")
        if not (ok1 and ok2 and ok3 and ok4):
            continue
        if flag is None:
            continue

        counts["applicable_mixed_variant_paths"]+=1
        srows=score_rows(rs)
        if len(srows)<2:
            errors.append({"type":"applicable_path_has_fewer_than_two_numeric_scores","group_id":gid,"score_rows":len(srows)})
            counts["divergence_reconstruction_errors"]+=1
            continue

        values=[float(r["score"]) for r in srows]
        recomputed=max(values)-min(values)
        if div is None or not math.isclose(float(div),recomputed,rel_tol=0.0,abs_tol=1e-12):
            counts["divergence_reconstruction_errors"]+=1
            errors.append({"type":"divergence_reconstruction","group_id":gid,"production":div,"recomputed":recomputed})

        group_units=sorted({r["metric_unit"] for r in rs if r["metric_unit"] is not None})
        scored_units=sorted({r["metric_unit"] for r in srows if r["metric_unit"] is not None})
        null_unit_score_rows=sum(1 for r in srows if r["metric_unit"] is None)
        if null_unit_score_rows:
            counts["applicable_paths_with_null_unit_score_rows"]+=1

        heterogeneous=len(scored_units)>=2
        if heterogeneous:
            counts["unit_heterogeneous_applicable_variant_paths"]+=1
        else:
            counts["unit_homogeneous_applicable_variant_paths"]+=1

        min_score=min(values)
        max_score=max(values)
        min_units=sorted({r["metric_unit"] for r in srows if float(r["score"])==min_score and r["metric_unit"] is not None})
        max_units=sorted({r["metric_unit"] for r in srows if float(r["score"])==max_score and r["metric_unit"] is not None})
        overlap=sorted(set(min_units)&set(max_units))
        if heterogeneous:
            if min_units and max_units and not overlap:
                counts["extrema_disjoint_unit_paths"]+=1
            else:
                counts["extrema_overlapping_unit_paths"]+=1

        if bool(flag):
            counts["production_true_paths"]+=1
        else:
            counts["production_false_paths"]+=1

        patterns[" | ".join(scored_units) if scored_units else "<none>"]+=1

        record={
         "comparability_group_id":gid,
         "production_flag":bool(flag),
         "production_divergence_magnitude":div,
         "recomputed_divergence":recomputed,
         "production_threshold":thr,
         "production_threshold_basis":basis,
         "group_units":group_units,
         "arithmetic_score_units":scored_units,
         "arithmetic_score_row_count":len(srows),
         "null_unit_score_rows":null_unit_score_rows,
         "unit_heterogeneous_arithmetic":heterogeneous,
         "min_score":min_score,
         "min_score_units":min_units,
         "max_score":max_score,
         "max_score_units":max_units,
         "extrema_unit_overlap":overlap,
         "score_rows":[{
           "fact_id":r["fact_id"],
           "score":r["score"],
           "metric_unit":r["metric_unit"],
           "source_record_path":r["source_record_path"],
           "result_idx":r["result_idx"],
           "evaluation_id":r["evaluation_id"],
           "evaluation_result_id":r["evaluation_result_id"],
         } for r in srows],
        }
        fa.write(json.dumps(record,sort_keys=True,ensure_ascii=True)+"\n")
        if heterogeneous:
            fh.write(json.dumps(record,sort_keys=True,ensure_ascii=True)+"\n")

if counts["applicable_mixed_variant_paths"]!=EXPECTED_APPLICABLE:
    errors.append({"type":"applicable_variant_count","got":counts["applicable_mixed_variant_paths"],"expected":EXPECTED_APPLICABLE})

with RAW_ERR.open("w",encoding="utf-8",newline="\n") as f:
    for e in errors: f.write(json.dumps(e,sort_keys=True,ensure_ascii=True)+"\n")

integrity_bad=(
    len(errors)>0
    or counts["divergence_reconstruction_errors"]>0
    or counts["group_consistency_errors"]>0
)
if integrity_bad:
    verdict="INCONCLUSIVE"
elif counts["unit_heterogeneous_applicable_variant_paths"]>=1:
    verdict="CONFIRMED"
else:
    verdict="REFUTED"

summary={
 "test_id":"T07_variant_divergence_unit_homogeneity",
 "verdict":verdict,
 "fact_rows_scanned":fact_rows,
 "comparability_groups_scanned":all_groups,
 "mixed_unit_groups":len(mixed_ids),
 "applicable_mixed_variant_paths":counts["applicable_mixed_variant_paths"],
 "unit_homogeneous_applicable_variant_paths":counts["unit_homogeneous_applicable_variant_paths"],
 "unit_heterogeneous_applicable_variant_paths":counts["unit_heterogeneous_applicable_variant_paths"],
 "applicable_paths_with_null_unit_score_rows":counts["applicable_paths_with_null_unit_score_rows"],
 "extrema_disjoint_unit_paths":counts["extrema_disjoint_unit_paths"],
 "extrema_overlapping_unit_paths":counts["extrema_overlapping_unit_paths"],
 "production_true_paths":counts["production_true_paths"],
 "production_false_paths":counts["production_false_paths"],
 "divergence_reconstruction_errors":counts["divergence_reconstruction_errors"],
 "group_consistency_errors":counts["group_consistency_errors"],
 "integrity_error_records":len(errors),
 "arithmetic_score_unit_patterns":dict(sorted(patterns.items())),
 "competing_predictions":{
   "P1":"unit_heterogeneous_applicable_variant_paths = 0",
   "P2":"unit_heterogeneous_applicable_variant_paths >= 1"
 },
 "limitations":[
   "Different declared unit labels are not automatically semantically incompatible.",
   "T07 introduces no conversion or equivalence map.",
   "T07 tests arithmetic input eligibility, not public product impact.",
   "T07 does not retest T04 threshold-unit boolean sensitivity."
 ],
 "evidence":{
   "input_fact_sha256":sha256(FACT),
   "applicable_variant_paths_sha256":sha256(RAW_ALL),
   "unit_heterogeneous_paths_sha256":sha256(RAW_HET),
   "integrity_errors_sha256":sha256(RAW_ERR)
 }
}
SUMMARY.write_text(json.dumps(summary,indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")

lines=[
 "# RESULT_ANALYSIS — T07 Variant Divergence Unit-Homogeneity Eligibility","",
 "Status: generated after execution from the frozen T07 summary.","",
 f"Primary verdict: `{verdict}`.","",
 "## Raw counts","",
]
for k in [
 "fact_rows_scanned","comparability_groups_scanned","mixed_unit_groups",
 "applicable_mixed_variant_paths","unit_homogeneous_applicable_variant_paths",
 "unit_heterogeneous_applicable_variant_paths",
 "applicable_paths_with_null_unit_score_rows","extrema_disjoint_unit_paths",
 "extrema_overlapping_unit_paths","production_true_paths","production_false_paths",
 "divergence_reconstruction_errors","group_consistency_errors","integrity_error_records"
]:
    lines.append(f"- `{k}` = {summary[k]}")
lines+=["","## Interpretation",""]
if verdict=="CONFIRMED":
    lines += [
      "P2 was observed: at least one production-applicable variant-divergence calculation receives numeric score rows carrying multiple distinct declared unit labels.",
      "",
      "This establishes unit-label heterogeneity in the arithmetic input to the frozen raw max-minus-min operation.",
      "",
      "It does not by itself establish that the labels are semantically non-convertible or that the final boolean is wrong."
    ]
elif verdict=="REFUTED":
    lines += [
      "P1 was observed: every production-applicable mixed-unit variant path is unit-label homogeneous over the numeric score rows actually used by the divergence arithmetic.",
      "",
      "The broader group-level mixed-unit metadata therefore does not enter one production max-minus-min operation in this snapshot."
    ]
else:
    lines += [
      "Neither competing prediction can be interpreted because a reconstruction or group-integrity condition failed.",
      "",
      "No EvalEval defect attribution is permitted from this result."
    ]
lines += [
 "","## Scope limits","",
 "- Unit-label difference is not semantic incompatibility.",
 "- No unit conversion rule was invented.",
 "- Final boolean correctness is outside C-T07.",
 "- Public-site impact is outside C-T07.",
 "","## Evidence","",
 "- `raw/applicable_variant_paths.jsonl`",
 "- `raw/unit_heterogeneous_paths.jsonl`",
 "- `raw/integrity_errors.jsonl`",
 "- `results/summary.json`",
]
ANALYSIS.write_text("\n".join(lines)+"\n",encoding="utf-8")

print("T07 COMPLETE")
for k in [
 "verdict","fact_rows_scanned","comparability_groups_scanned","mixed_unit_groups",
 "applicable_mixed_variant_paths","unit_homogeneous_applicable_variant_paths",
 "unit_heterogeneous_applicable_variant_paths",
 "applicable_paths_with_null_unit_score_rows","extrema_disjoint_unit_paths",
 "extrema_overlapping_unit_paths","production_true_paths","production_false_paths",
 "divergence_reconstruction_errors","group_consistency_errors","integrity_error_records"
]:
    print(f"{k}={summary[k]}")
print("arithmetic_score_unit_patterns="+json.dumps(summary["arithmetic_score_unit_patterns"],sort_keys=True,ensure_ascii=True))
print(r"summary=tests\T07_variant_divergence_unit_homogeneity\results\summary.json")
print(r"analysis=tests\T07_variant_divergence_unit_homogeneity\results\RESULT_ANALYSIS.md")
