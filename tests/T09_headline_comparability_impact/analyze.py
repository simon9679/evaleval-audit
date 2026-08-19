from __future__ import annotations

import hashlib
import json
import math
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FACT=ROOT/"tests"/"T03_corpus_boundary_impact"/"raw"/"fact_results_stage_f.parquet"
T08_FLIPS=ROOT/"tests"/"T08_within_unit_variant_counterfactual"/"raw"/"positive_to_negative_paths.jsonl"
BACKEND=ROOT/"freeze"/"repos"/"eval_cards_backend_pipeline"

EXPECTED_COMMIT="9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
EXPECTED_SHA="e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"

RAW_AFFECTED=HERE/"raw"/"affected_groups.jsonl"
RAW_PROD=HERE/"raw"/"production_headline_comparability.json"
RAW_CF=HERE/"raw"/"counterfactual_headline_comparability.json"
RAW_ERR=HERE/"raw"/"integrity_errors.jsonl"
SUMMARY=HERE/"results"/"summary.json"
ANALYSIS=HERE/"results"/"RESULT_ANALYSIS.md"

def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def hard_error(msg):
    SUMMARY.write_text(json.dumps({"test_id":"T09_headline_comparability_impact","verdict":"ERROR","error":msg},indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("T09 ERROR"); print(msg); raise SystemExit(2)

if not (HERE/"raw"/"preflight.json").exists():
    hard_error("Missing T09 preflight evidence.")
head=subprocess.check_output(["git","-C",str(BACKEND),"rev-parse","HEAD"],text=True).strip()
if head!=EXPECTED_COMMIT: hard_error(f"Backend HEAD mismatch: {head}")
if not FACT.exists(): hard_error("Missing T03 Stage F parquet.")
if sha256(FACT)!=EXPECTED_SHA: hard_error("T03 Stage F parquet SHA mismatch.")
if not T08_FLIPS.exists(): hard_error("Missing T08 positive-to-negative evidence.")

flip_recs=[json.loads(line) for line in T08_FLIPS.read_text(encoding="utf-8").splitlines() if line.strip()]
flip_ids=[r.get("comparability_group_id") for r in flip_recs]
if len(flip_recs)!=2 or None in flip_ids or len(set(flip_ids))!=2:
    hard_error(f"Expected exactly two unique non-null T08 flip ids, got {flip_ids!r}")

import duckdb
con=duckdb.connect()
p=FACT.as_posix().replace("'","''")

cols={r[0] for r in con.execute(f"DESCRIBE SELECT * FROM read_parquet('{p}')").fetchall()}
required={"comparability_group_id","has_variant_divergence","has_cross_party_divergence"}
missing=sorted(required-cols)
if missing: hard_error(f"Stage F schema missing required columns: {missing}")

fact_rows=con.execute(f"SELECT COUNT(*) FROM read_parquet('{p}')").fetchone()[0]
comparability_groups=con.execute(f"""
 SELECT COUNT(DISTINCT comparability_group_id)
 FROM read_parquet('{p}')
 WHERE comparability_group_id IS NOT NULL
""").fetchone()[0]

errors=[]

con.execute("CREATE TEMP TABLE _affected(id VARCHAR)")
con.executemany("INSERT INTO _affected VALUES (?)",[(x,) for x in flip_ids])

affected_rows=con.execute(f"""
 SELECT
   fr.comparability_group_id,
   COUNT(*) AS row_count,
   COUNT(DISTINCT fr.has_variant_divergence) AS distinct_variant_flags,
   MIN(fr.has_variant_divergence::INT) AS min_variant_flag,
   MAX(fr.has_variant_divergence::INT) AS max_variant_flag,
   COUNT(*) FILTER (WHERE fr.has_variant_divergence IS NULL) AS null_variant_rows
 FROM read_parquet('{p}') fr
 JOIN _affected a ON a.id=fr.comparability_group_id
 GROUP BY fr.comparability_group_id
 ORDER BY fr.comparability_group_id
""").fetchall()
an=[d[0] for d in con.description]
affected=[dict(zip(an,r)) for r in affected_rows]

if len(affected)!=2:
    errors.append({"type":"affected_groups_present","got":len(affected),"expected":2})

affected_true=0
with RAW_AFFECTED.open("w",encoding="utf-8",newline="\n") as f:
    byid={r["comparability_group_id"]:r for r in flip_recs}
    for r in affected:
        if (
            r["distinct_variant_flags"]==1
            and r["null_variant_rows"]==0
            and r["min_variant_flag"]==1
            and r["max_variant_flag"]==1
        ):
            affected_true+=1
        else:
            errors.append({"type":"affected_group_not_constant_true","record":r})
        out=dict(r)
        out["t08_counterfactual"]=byid.get(r["comparability_group_id"],{})
        f.write(json.dumps(out,sort_keys=True,ensure_ascii=True)+"\n")

def agg_sql(source_expr):
    return f"""
    SELECT
      COUNT(DISTINCT comparability_group_id) AS total_triples,
      COUNT(DISTINCT comparability_group_id)
        FILTER (WHERE has_variant_divergence) AS variant_divergent_count,
      COUNT(DISTINCT comparability_group_id)
        FILTER (WHERE has_cross_party_divergence) AS cross_party_divergent_count,
      COUNT(DISTINCT comparability_group_id)
        FILTER (WHERE has_variant_divergence IS NOT NULL) AS groups_with_variant_check,
      COUNT(DISTINCT comparability_group_id)
        FILTER (WHERE has_cross_party_divergence IS NOT NULL) AS groups_with_cross_party_check
    FROM ({source_expr}) x
    WHERE comparability_group_id IS NOT NULL
    """

prod_source=f"SELECT comparability_group_id, has_variant_divergence, has_cross_party_divergence FROM read_parquet('{p}')"
row=con.execute(agg_sql(prod_source)).fetchone()
keys=[d[0] for d in con.description]
prod=dict(zip(keys,row))

# Override only the two affected group booleans.
cf_source=f"""
 SELECT
   comparability_group_id,
   CASE
     WHEN comparability_group_id IN (SELECT id FROM _affected)
     THEN FALSE
     ELSE has_variant_divergence
   END AS has_variant_divergence,
   has_cross_party_divergence
 FROM read_parquet('{p}')
"""
row=con.execute(agg_sql(cf_source)).fetchone()
keys=[d[0] for d in con.description]
cf=dict(zip(keys,row))

for obj,path in ((prod,RAW_PROD),(cf,RAW_CF)):
    path.write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")

# Structural invariants.
for k in ["total_triples","cross_party_divergent_count","groups_with_variant_check","groups_with_cross_party_check"]:
    if prod[k]!=cf[k]:
        errors.append({"type":"unexpected_nonvariant_aggregate_change","field":k,"production":prod[k],"counterfactual":cf[k]})

delta=int(cf["variant_divergent_count"])-int(prod["variant_divergent_count"])

# Each affected group should contribute exactly once to distinct group count.
expected_delta=-affected_true
if delta!=expected_delta:
    errors.append({"type":"variant_delta_mismatch","delta":delta,"expected":expected_delta})

with RAW_ERR.open("w",encoding="utf-8",newline="\n") as f:
    for e in errors: f.write(json.dumps(e,sort_keys=True,ensure_ascii=True)+"\n")

def share(num,den):
    return (float(num)/float(den)) if den else None

prod_share_total=share(prod["variant_divergent_count"],prod["total_triples"])
cf_share_total=share(cf["variant_divergent_count"],cf["total_triples"])
prod_share_elig=share(prod["variant_divergent_count"],prod["groups_with_variant_check"])
cf_share_elig=share(cf["variant_divergent_count"],cf["groups_with_variant_check"])

if errors:
    verdict="INCONCLUSIVE"
elif delta<0:
    verdict="CONFIRMED"
elif delta==0:
    verdict="REFUTED"
else:
    # Positive delta contradicts the fixed counterfactual and is an integrity problem.
    verdict="INCONCLUSIVE"
    errors.append({"type":"unexpected_positive_delta","delta":delta})
    RAW_ERR.write_text("\n".join(json.dumps(e,sort_keys=True,ensure_ascii=True) for e in errors)+"\n",encoding="utf-8")

summary={
 "test_id":"T09_headline_comparability_impact",
 "verdict":verdict,
 "fact_rows_scanned":fact_rows,
 "comparability_groups_scanned":comparability_groups,
 "affected_group_ids":len(set(flip_ids)),
 "affected_groups_present":len(affected),
 "affected_groups_production_true":affected_true,
 "production_total_triples":int(prod["total_triples"]),
 "production_variant_divergent_count":int(prod["variant_divergent_count"]),
 "production_cross_party_divergent_count":int(prod["cross_party_divergent_count"]),
 "production_groups_with_variant_check":int(prod["groups_with_variant_check"]),
 "production_groups_with_cross_party_check":int(prod["groups_with_cross_party_check"]),
 "counterfactual_total_triples":int(cf["total_triples"]),
 "counterfactual_variant_divergent_count":int(cf["variant_divergent_count"]),
 "counterfactual_cross_party_divergent_count":int(cf["cross_party_divergent_count"]),
 "counterfactual_groups_with_variant_check":int(cf["groups_with_variant_check"]),
 "counterfactual_groups_with_cross_party_check":int(cf["groups_with_cross_party_check"]),
 "headline_variant_divergent_count_delta":delta,
 "production_variant_divergent_share_of_total":prod_share_total,
 "counterfactual_variant_divergent_share_of_total":cf_share_total,
 "production_variant_divergent_share_of_eligible":prod_share_elig,
 "counterfactual_variant_divergent_share_of_eligible":cf_share_elig,
 "share_of_total_delta":(cf_share_total-prod_share_total) if prod_share_total is not None else None,
 "share_of_eligible_delta":(cf_share_elig-prod_share_elig) if prod_share_elig is not None else None,
 "integrity_error_records":len(errors),
 "competing_predictions":{
   "P1":"headline_variant_divergent_count_delta = 0",
   "P2":"headline_variant_divergent_count_delta < 0"
 },
 "limitations":[
   "T09 measures the frozen backend headline aggregate, not live-site state at another snapshot.",
   "The derived shares are audit diagnostics; exact frontend percentage rendering is not asserted.",
   "T09 does not establish semantic invalidity of the two affected groups.",
   "T09 does not define a materiality threshold for the aggregate change."
 ],
 "evidence":{
   "input_fact_sha256":sha256(FACT),
   "t08_positive_to_negative_sha256":sha256(T08_FLIPS),
   "affected_groups_sha256":sha256(RAW_AFFECTED),
   "production_headline_sha256":sha256(RAW_PROD),
   "counterfactual_headline_sha256":sha256(RAW_CF),
   "integrity_errors_sha256":sha256(RAW_ERR),
 }
}
SUMMARY.write_text(json.dumps(summary,indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")

lines=[
 "# RESULT_ANALYSIS — T09 Headline Comparability Aggregate Impact","",
 "Status: generated after execution from the frozen T09 summary.","",
 f"Primary verdict: `{verdict}`.","",
 "## Raw counts","",
]
for k in [
 "fact_rows_scanned","comparability_groups_scanned","affected_group_ids",
 "affected_groups_present","affected_groups_production_true",
 "production_total_triples","production_variant_divergent_count",
 "production_cross_party_divergent_count","production_groups_with_variant_check",
 "production_groups_with_cross_party_check","counterfactual_total_triples",
 "counterfactual_variant_divergent_count","counterfactual_cross_party_divergent_count",
 "counterfactual_groups_with_variant_check","counterfactual_groups_with_cross_party_check",
 "headline_variant_divergent_count_delta","production_variant_divergent_share_of_total",
 "counterfactual_variant_divergent_share_of_total",
 "production_variant_divergent_share_of_eligible",
 "counterfactual_variant_divergent_share_of_eligible","share_of_total_delta",
 "share_of_eligible_delta","integrity_error_records"
]:
    lines.append(f"- `{k}` = {summary[k]}")

lines += ["","## Interpretation",""]
if verdict=="CONFIRMED":
    lines += [
      "P2 was observed: replacing only the two T08 affected production booleans with their frozen exact-label counterfactual values decreases the frontend-consumed headline comparability `variant_divergent_count`.",
      "",
      "This establishes frozen product-aggregate exposure of the T08 operational consequence.",
      "",
      "It does not establish semantic incorrectness or material user impact."
    ]
elif verdict=="REFUTED":
    lines += [
      "P1 was observed: the two T08 internal boolean transitions do not change the frozen headline comparability count.",
      "",
      "This descendant should stop for headline aggregate impact."
    ]
else:
    lines += [
      "The product aggregate consequence cannot be interpreted because an integrity or reconstruction invariant failed.",
      "",
      "No product-impact attribution is permitted until the measurement is repaired."
    ]

lines += [
 "","## Scope limits","",
 "- Frozen headline aggregate exposure is not semantic invalidity.",
 "- The audit does not define materiality in T09.",
 "- Live-site state outside the frozen snapshot is not measured.",
 "","## Evidence","",
 "- `raw/affected_groups.jsonl`",
 "- `raw/production_headline_comparability.json`",
 "- `raw/counterfactual_headline_comparability.json`",
 "- `raw/integrity_errors.jsonl`",
 "- `results/summary.json`",
]
ANALYSIS.write_text("\n".join(lines)+"\n",encoding="utf-8")

print("T09 COMPLETE")
for k in [
 "verdict","fact_rows_scanned","comparability_groups_scanned","affected_group_ids",
 "affected_groups_present","affected_groups_production_true",
 "production_total_triples","production_variant_divergent_count",
 "production_cross_party_divergent_count","production_groups_with_variant_check",
 "production_groups_with_cross_party_check","counterfactual_total_triples",
 "counterfactual_variant_divergent_count","counterfactual_cross_party_divergent_count",
 "counterfactual_groups_with_variant_check","counterfactual_groups_with_cross_party_check",
 "headline_variant_divergent_count_delta","production_variant_divergent_share_of_total",
 "counterfactual_variant_divergent_share_of_total",
 "production_variant_divergent_share_of_eligible",
 "counterfactual_variant_divergent_share_of_eligible",
 "share_of_total_delta","share_of_eligible_delta","integrity_error_records"
]:
    print(f"{k}={summary[k]}")
print(r"summary=tests\T09_headline_comparability_impact\results\summary.json")
print(r"analysis=tests\T09_headline_comparability_impact\results\RESULT_ANALYSIS.md")
