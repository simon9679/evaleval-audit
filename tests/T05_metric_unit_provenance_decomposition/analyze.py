from __future__ import annotations
import hashlib, json, subprocess
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FACT=ROOT/"tests"/"T03_corpus_boundary_impact"/"raw"/"fact_results_stage_f.parquet"
BACKEND=ROOT/"freeze"/"repos"/"eval_cards_backend_pipeline"
EXPECTED_COMMIT="9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
EXPECTED_SHA="e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"
EXPECTED_MIXED=1234

RAW_ATTR=HERE/"raw"/"mixed_group_attribution.jsonl"
RAW_FULL=HERE/"raw"/"full_canonical_convergence_groups.jsonl"
RAW_ROWS=HERE/"raw"/"full_canonical_convergence_rows.jsonl"
RAW_ERR=HERE/"raw"/"integrity_errors.jsonl"
SUMMARY=HERE/"results"/"summary.json"
ANALYSIS=HERE/"results"/"RESULT_ANALYSIS.md"

def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def stop_error(msg):
    SUMMARY.write_text(json.dumps({"test_id":"T05_metric_unit_provenance_decomposition","verdict":"ERROR","error":msg},indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("T05 ERROR"); print(msg); raise SystemExit(2)

if not (HERE/"raw"/"preflight.json").exists():
    stop_error("Missing T05 preflight evidence.")
head=subprocess.check_output(["git","-C",str(BACKEND),"rev-parse","HEAD"],text=True).strip()
if head != EXPECTED_COMMIT: stop_error(f"Backend HEAD mismatch: {head}")
if not FACT.exists(): stop_error("Missing T03 fact parquet.")
if sha256(FACT) != EXPECTED_SHA: stop_error("T03 fact parquet SHA mismatch.")

import duckdb
con=duckdb.connect()
p=FACT.as_posix().replace("'","''")
cols={r[0] for r in con.execute(f"DESCRIBE SELECT * FROM read_parquet('{p}')").fetchall()}
required={
 "comparability_group_id","model_aggregation_key","benchmark_key","slice_key",
 "metric_key","metric_key_effective","metric_raw","metric_id",
 "metric_resolution_strategy","metric_unit","metric_unit_provenance",
 "source_config","fact_id","source_record_path","result_idx","evaluation_id",
 "evaluation_result_id"
}
missing=sorted(required-cols)
if missing: stop_error(f"Stage F schema missing required columns: {missing}")

fact_rows=con.execute(f"SELECT COUNT(*) FROM read_parquet('{p}')").fetchone()[0]
all_groups=con.execute(f"SELECT COUNT(DISTINCT comparability_group_id) FROM read_parquet('{p}') WHERE comparability_group_id IS NOT NULL").fetchone()[0]

q=f"""
SELECT
 comparability_group_id,
 any_value(model_aggregation_key) AS model_aggregation_key,
 any_value(benchmark_key) AS benchmark_key,
 any_value(slice_key) AS slice_key,
 any_value(metric_key) AS metric_key,
 list_sort(list_distinct(list(metric_key) FILTER (WHERE metric_key IS NOT NULL))) AS metric_keys,
 list_sort(list_distinct(list(metric_key_effective) FILTER (WHERE metric_key_effective IS NOT NULL))) AS metric_keys_effective,
 list_sort(list_distinct(list(metric_raw) FILTER (WHERE metric_raw IS NOT NULL))) AS metric_raws,
 list_sort(list_distinct(list(metric_id) FILTER (WHERE metric_id IS NOT NULL))) AS metric_ids,
 list_sort(list_distinct(list(metric_resolution_strategy) FILTER (WHERE metric_resolution_strategy IS NOT NULL))) AS resolution_strategies,
 list_sort(list_distinct(list(metric_unit) FILTER (WHERE metric_unit IS NOT NULL))) AS units,
 list_sort(list_distinct(list(metric_unit_provenance) FILTER (WHERE metric_unit_provenance IS NOT NULL))) AS unit_provenances,
 list_sort(list_distinct(list(source_config) FILTER (WHERE source_config IS NOT NULL))) AS source_configs,
 COUNT(*) AS row_count,
 COUNT(*) FILTER (WHERE metric_id IS NULL) AS unresolved_metric_rows,
 COUNT(DISTINCT metric_raw) FILTER (WHERE metric_raw IS NOT NULL) AS raw_count,
 COUNT(DISTINCT metric_id) FILTER (WHERE metric_id IS NOT NULL) AS metric_id_count,
 COUNT(DISTINCT metric_resolution_strategy) FILTER (WHERE metric_resolution_strategy IS NOT NULL) AS strategy_count,
 COUNT(DISTINCT metric_unit_provenance) FILTER (WHERE metric_unit_provenance IS NOT NULL) AS unit_prov_count
FROM read_parquet('{p}')
WHERE comparability_group_id IS NOT NULL
GROUP BY comparability_group_id
HAVING COUNT(DISTINCT metric_unit) FILTER (WHERE metric_unit IS NOT NULL) > 1
ORDER BY comparability_group_id
"""
rows=con.execute(q).fetchall()
names=[d[0] for d in con.description]
records=[dict(zip(names,r)) for r in rows]

errors=[]
if len(records)!=EXPECTED_MIXED:
    errors.append({"type":"mixed_group_count","got":len(records),"expected":EXPECTED_MIXED})

counts=Counter()
res_patterns=Counter()
prov_patterns=Counter()
source_counts=Counter()
unit_patterns=Counter()
full_ids=[]

with RAW_ATTR.open("w",encoding="utf-8",newline="\n") as fa, RAW_FULL.open("w",encoding="utf-8",newline="\n") as ff:
    for r in records:
        counts["actual_mixed_unit_groups"] += 1
        if len(r["metric_keys"]) != 1:
            errors.append({"type":"metric_key_not_stable","group_id":r["comparability_group_id"],"values":r["metric_keys"]})
        if r["raw_count"] <= 1: counts["single_raw_metric_groups"] += 1
        else: counts["multi_raw_metric_groups"] += 1
        if r["unresolved_metric_rows"] > 0: counts["groups_with_unresolved_metric_rows"] += 1
        if r["metric_id_count"] <= 1: counts["single_metric_id_groups"] += 1
        else: counts["multi_metric_id_groups"] += 1
        if r["strategy_count"] > 1: counts["multi_resolution_strategy_groups"] += 1
        if r["unit_prov_count"] > 1: counts["multi_unit_provenance_groups"] += 1

        full = (
            r["raw_count"] >= 2
            and r["unresolved_metric_rows"] == 0
            and r["metric_id_count"] == 1
            and len(r["metric_ids"]) == 1
            and len(r["metric_keys"]) == 1
            and r["metric_ids"][0] == r["metric_keys"][0]
        )
        partial = (
            r["raw_count"] >= 2
            and not full
            and r["metric_id_count"] >= 1
        )
        r["full_resolved_canonical_convergence"] = full
        r["partial_or_mixed_resolution_convergence"] = partial
        if full:
            counts["full_resolved_canonical_convergence_groups"] += 1
            full_ids.append(r["comparability_group_id"])
            ff.write(json.dumps(r,sort_keys=True,ensure_ascii=True)+"\n")
        if partial:
            counts["partial_or_mixed_resolution_convergence_groups"] += 1

        res_patterns[" | ".join(r["resolution_strategies"]) if r["resolution_strategies"] else "<none>"] += 1
        prov_patterns[" | ".join(r["unit_provenances"]) if r["unit_provenances"] else "<none>"] += 1
        unit_patterns[" | ".join(r["units"])] += 1
        for s in r["source_configs"]:
            source_counts[s] += 1
        fa.write(json.dumps(r,sort_keys=True,ensure_ascii=True)+"\n")

# Dump every source-addressable row for the full-convergence subset.
with RAW_ROWS.open("w",encoding="utf-8",newline="\n") as f:
    if full_ids:
        con.execute("CREATE TEMP TABLE _full_ids(id VARCHAR)")
        con.executemany("INSERT INTO _full_ids VALUES (?)", [(x,) for x in full_ids])
        rq=f"""
        SELECT
          fr.comparability_group_id, fr.fact_id, fr.evaluation_id,
          fr.evaluation_result_id, fr.result_idx, fr.source_record_path,
          fr.source_config, fr.model_aggregation_key, fr.benchmark_key,
          fr.slice_key, fr.metric_key, fr.metric_key_effective,
          fr.metric_raw, fr.metric_id, fr.metric_resolution_strategy,
          fr.metric_unit, fr.metric_unit_provenance, fr.min_score, fr.max_score,
          fr.score
        FROM read_parquet('{p}') fr
        JOIN _full_ids x ON x.id=fr.comparability_group_id
        ORDER BY fr.comparability_group_id, fr.fact_id
        """
        rr=con.execute(rq).fetchall()
        rn=[d[0] for d in con.description]
        for row in rr:
            f.write(json.dumps(dict(zip(rn,row)),sort_keys=True,ensure_ascii=True)+"\n")

with RAW_ERR.open("w",encoding="utf-8",newline="\n") as f:
    for e in errors: f.write(json.dumps(e,sort_keys=True,ensure_ascii=True)+"\n")

integrity_bad=bool(errors)
if integrity_bad: verdict="INCONCLUSIVE"
elif counts["full_resolved_canonical_convergence_groups"] >= 1: verdict="CONFIRMED"
else: verdict="REFUTED"

summary={
 "test_id":"T05_metric_unit_provenance_decomposition",
 "verdict":verdict,
 "fact_rows_scanned":fact_rows,
 "comparability_groups_scanned":all_groups,
 "actual_mixed_unit_groups":counts["actual_mixed_unit_groups"],
 "single_raw_metric_groups":counts["single_raw_metric_groups"],
 "multi_raw_metric_groups":counts["multi_raw_metric_groups"],
 "groups_with_unresolved_metric_rows":counts["groups_with_unresolved_metric_rows"],
 "single_metric_id_groups":counts["single_metric_id_groups"],
 "multi_metric_id_groups":counts["multi_metric_id_groups"],
 "multi_resolution_strategy_groups":counts["multi_resolution_strategy_groups"],
 "multi_unit_provenance_groups":counts["multi_unit_provenance_groups"],
 "full_resolved_canonical_convergence_groups":counts["full_resolved_canonical_convergence_groups"],
 "partial_or_mixed_resolution_convergence_groups":counts["partial_or_mixed_resolution_convergence_groups"],
 "integrity_error_records":len(errors),
 "resolution_strategy_patterns":dict(sorted(res_patterns.items())),
 "metric_unit_provenance_patterns":dict(sorted(prov_patterns.items())),
 "source_config_group_counts":dict(sorted(source_counts.items())),
 "unit_patterns":dict(sorted(unit_patterns.items())),
 "competing_predictions":{
   "P1":"full_resolved_canonical_convergence_groups = 0",
   "P2":"full_resolved_canonical_convergence_groups >= 1"
 },
 "limitations":[
   "Structural canonical convergence is not semantic error.",
   "T05 does not decide whether converged raw labels are synonyms or distinct estimands.",
   "T05 does not decide whether upstream metadata or EvalEval is causally responsible for any semantic mismatch.",
   "T05 is snapshot-bound to the frozen T03 Stage F artifact."
 ],
 "evidence":{
   "input_fact_sha256":sha256(FACT),
   "mixed_group_attribution_sha256":sha256(RAW_ATTR),
   "full_canonical_convergence_groups_sha256":sha256(RAW_FULL),
   "full_canonical_convergence_rows_sha256":sha256(RAW_ROWS),
   "integrity_errors_sha256":sha256(RAW_ERR)
 }
}
SUMMARY.write_text(json.dumps(summary,indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")

lines=[
 "# RESULT_ANALYSIS — T05 Metric Unit Provenance Decomposition","",
 "Status: generated after execution from the frozen T05 summary.","",
 f"Primary verdict: `{verdict}`.","",
 "## Raw counts","",
]
for k in [
 "fact_rows_scanned","comparability_groups_scanned","actual_mixed_unit_groups",
 "single_raw_metric_groups","multi_raw_metric_groups",
 "groups_with_unresolved_metric_rows","single_metric_id_groups","multi_metric_id_groups",
 "multi_resolution_strategy_groups","multi_unit_provenance_groups",
 "full_resolved_canonical_convergence_groups",
 "partial_or_mixed_resolution_convergence_groups","integrity_error_records"
]:
    lines.append(f"- `{k}` = {summary[k]}")
lines += ["","## Interpretation",""]
if verdict=="CONFIRMED":
    lines += [
      "P2 was observed: at least one actual mixed-unit group contains multiple raw metric labels that are fully resolved into one shared canonical metric id used as the production metric key.",
      "",
      "This establishes structural participation of canonical metric resolution in part of the mixed-unit population.",
      "",
      "It does not establish that the convergence is semantically wrong. A later source/reference trace must determine whether the converged raw labels represent the same estimand."
    ]
elif verdict=="REFUTED":
    lines += [
      "P1 was observed: no actual mixed-unit group satisfies the strict full resolved canonical-convergence definition.",
      "",
      "The canonical-convergence explanation should not receive an expensive semantic trace solely on this basis. The descriptive provenance breakdown should choose the next attribution layer."
    ]
else:
    lines += [
      "The primary structural attribution cannot be interpreted because an integrity condition failed.",
      "",
      "No EvalEval defect attribution is permitted from this result."
    ]
lines += [
 "","## Scope limits","",
 "- Structural convergence is not semantic correctness or error.",
 "- Unit provenance labels do not substitute for source-level reference authority.",
 "- Public product impact is outside T05.",
 "","## Evidence","",
 "- `raw/mixed_group_attribution.jsonl`",
 "- `raw/full_canonical_convergence_groups.jsonl`",
 "- `raw/full_canonical_convergence_rows.jsonl`",
 "- `raw/integrity_errors.jsonl`",
 "- `results/summary.json`",
]
ANALYSIS.write_text("\n".join(lines)+"\n",encoding="utf-8")

print("T05 COMPLETE")
for k in [
 "verdict","fact_rows_scanned","comparability_groups_scanned","actual_mixed_unit_groups",
 "single_raw_metric_groups","multi_raw_metric_groups","groups_with_unresolved_metric_rows",
 "single_metric_id_groups","multi_metric_id_groups","multi_resolution_strategy_groups",
 "multi_unit_provenance_groups","full_resolved_canonical_convergence_groups",
 "partial_or_mixed_resolution_convergence_groups","integrity_error_records"
]:
    print(f"{k}={summary[k]}")
print("resolution_strategy_patterns="+json.dumps(summary["resolution_strategy_patterns"],sort_keys=True,ensure_ascii=True))
print("metric_unit_provenance_patterns="+json.dumps(summary["metric_unit_provenance_patterns"],sort_keys=True,ensure_ascii=True))
print(r"summary=tests\T05_metric_unit_provenance_decomposition\results\summary.json")
print(r"analysis=tests\T05_metric_unit_provenance_decomposition\results\RESULT_ANALYSIS.md")
