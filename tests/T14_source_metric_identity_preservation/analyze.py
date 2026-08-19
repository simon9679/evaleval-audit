from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

T10_ROWS=ROOT/"tests"/"T10_source_metric_config_heterogeneity"/"raw"/"source_metric_configs.jsonl"
T08_FLIPS=ROOT/"tests"/"T08_within_unit_variant_counterfactual"/"raw"/"positive_to_negative_paths.jsonl"
FACT=ROOT/"tests"/"T03_corpus_boundary_impact"/"raw"/"fact_results_stage_f.parquet"
BACKEND=ROOT/"freeze"/"repos"/"eval_cards_backend_pipeline"

EXPECTED_COMMIT="9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
EXPECTED_SHA="e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"

RAW_SUB=HERE/"raw"/"source_id_subgroup_results.jsonl"
RAW_GROUP=HERE/"raw"/"production_group_counterfactuals.jsonl"
RAW_ERR=HERE/"raw"/"integrity_errors.jsonl"
SUMMARY=HERE/"results"/"summary.json"
ANALYSIS=HERE/"results"/"RESULT_ANALYSIS.md"

def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""):
            h.update(c)
    return h.hexdigest()

def hard_error(msg):
    SUMMARY.write_text(
        json.dumps({"test_id":"T14_source_metric_identity_preservation","verdict":"ERROR","error":msg},
                   indent=2,sort_keys=True)+"\n",
        encoding="utf-8"
    )
    print("T14 ERROR")
    print(msg)
    raise SystemExit(2)

def git_head(p):
    return subprocess.check_output(["git","-C",str(p),"rev-parse","HEAD"],text=True).strip()

if not (HERE/"raw"/"preflight.json").exists():
    hard_error("Missing T14 preflight evidence.")

if git_head(BACKEND)!=EXPECTED_COMMIT:
    hard_error("Backend HEAD mismatch.")
if sha256(FACT)!=EXPECTED_SHA:
    hard_error("Stage F SHA mismatch.")

sys.path.insert(0,str(BACKEND/"src"))
try:
    from eval_card_backend.signals.comparability import compute_variant_divergence_py
except Exception as e:
    hard_error(f"cannot import frozen production comparability function: {type(e).__name__}: {e}")

src=[json.loads(x) for x in T10_ROWS.read_text(encoding="utf-8").splitlines() if x.strip()]
flips=[json.loads(x) for x in T08_FLIPS.read_text(encoding="utf-8").splitlines() if x.strip()]
if len(src)!=12:
    hard_error(f"Expected 12 T10 rows, got {len(src)}")
if len(flips)!=2:
    hard_error(f"Expected 2 T08 affected groups, got {len(flips)}")

affected_ids=[x["comparability_group_id"] for x in flips]
if len(set(affected_ids))!=2:
    hard_error("T08 affected group ids are not unique.")

# Map exact source identity/config by fact_id.
src_by_fact={}
for r in src:
    fid=r.get("fact_id")
    if fid in src_by_fact:
        hard_error(f"Duplicate T10 fact_id: {fid}")
    primary=r.get("source_metric_config_primary")
    if not isinstance(primary,dict):
        hard_error(f"Missing source metric config for fact_id {fid}")
    sid=primary.get("metric_id")
    if sid is None:
        hard_error(f"Null source metric id for fact_id {fid}")
    src_by_fact[fid]={
        "comparability_group_id":r.get("comparability_group_id"),
        "source_metric_id":sid,
        "metric_config":{
            "metric_kind":primary.get("metric_kind"),
            "metric_unit":r.get("source_metric_unit_normalized"),
            "min_score":primary.get("min_score"),
            "max_score":primary.get("max_score"),
        }
    }

import duckdb
con=duckdb.connect()
p=FACT.as_posix().replace("'","''")
cols={r[0] for r in con.execute(f"DESCRIBE SELECT * FROM read_parquet('{p}')").fetchall()}

required={
 "fact_id","comparability_group_id","evaluation_id","score","generation_args",
 "evaluator_relationship","source_organization_name",
 "metric_kind","metric_unit","min_score","max_score",
 "has_variant_divergence"
}
missing=sorted(required-cols)
if missing:
    hard_error(f"Stage F missing required columns: {missing}")

con.execute("CREATE TEMP TABLE _affected(id VARCHAR)")
con.executemany("INSERT INTO _affected VALUES (?)",[(x,) for x in affected_ids])

rows=con.execute(f"""
 SELECT
   fr.fact_id,
   fr.comparability_group_id,
   fr.evaluation_id,
   fr.score,
   fr.generation_args,
   fr.evaluator_relationship,
   fr.source_organization_name,
   fr.metric_kind,
   fr.metric_unit,
   fr.min_score,
   fr.max_score,
   fr.has_variant_divergence
 FROM read_parquet('{p}') fr
 JOIN _affected a ON a.id=fr.comparability_group_id
 ORDER BY fr.comparability_group_id, fr.fact_id
""").fetchall()
names=[d[0] for d in con.description]
stage=[dict(zip(names,r)) for r in rows]

errors=[]
counts=Counter()

# Restrict to the exact 12 arithmetic rows frozen by T10.
stage=[r for r in stage if r["fact_id"] in src_by_fact]
counts["affected_rows"]=len(stage)
if len(stage)!=12:
    errors.append({"type":"affected_row_count","got":len(stage),"expected":12})

by_gid=defaultdict(list)
for r in stage:
    fid=r["fact_id"]
    s=src_by_fact.get(fid)
    if s is None:
        counts["row_identity_errors"]+=1
        errors.append({"type":"missing_source_row","fact_id":fid})
        continue
    if s["comparability_group_id"]!=r["comparability_group_id"]:
        counts["row_identity_errors"]+=1
        errors.append({
            "type":"group_id_mismatch",
            "fact_id":fid,
            "stage":r["comparability_group_id"],
            "source":s["comparability_group_id"],
        })
    rr=dict(r)
    rr["source_metric_id"]=s["source_metric_id"]
    rr["source_metric_config"]=s["metric_config"]
    by_gid[rr["comparability_group_id"]].append(rr)

counts["affected_production_groups"]=len(by_gid)

# Reproduce original production TRUE for each affected full group.
production_replay={}
for gid,rs in by_gid.items():
    group_fields={}
    for k in ["metric_kind","metric_unit","min_score","max_score","has_variant_divergence"]:
        vals={r[k] for r in rs}
        if len(vals)!=1:
            errors.append({"type":"production_group_field_not_constant","group_id":gid,"field":k,"values":sorted(repr(x) for x in vals)})
            continue
        group_fields[k]=next(iter(vals))
    if set(group_fields)!={"metric_kind","metric_unit","min_score","max_score","has_variant_divergence"}:
        counts["production_replay_errors"]+=1
        continue

    prod_rows=[{
        "fact_id":r["fact_id"],
        "evaluation_id":r["evaluation_id"],
        "score":r["score"],
        "generation_args":deepcopy(r["generation_args"]),
        "evaluator_relationship":r["evaluator_relationship"],
        "source_organization_name":r["source_organization_name"],
    } for r in rs]
    cfg={k:group_fields[k] for k in ["metric_kind","metric_unit","min_score","max_score"]}
    out=compute_variant_divergence_py(prod_rows,cfg)
    production_replay[gid]=out
    if out is None or out.get("has_variant_divergence") is not True or group_fields["has_variant_divergence"] is not True:
        counts["production_replay_errors"]+=1
        errors.append({
            "type":"production_replay_not_true",
            "group_id":gid,
            "stage_flag":group_fields["has_variant_divergence"],
            "replay":out,
        })
    else:
        counts["production_groups_replayed_true"]+=1

# Exact source-id config consistency and counterfactual subgroup replay.
subgroup_records=[]
group_records=[]

with RAW_SUB.open("w",encoding="utf-8",newline="\n") as fs, RAW_GROUP.open("w",encoding="utf-8",newline="\n") as fg:
    for gid,rs in sorted(by_gid.items()):
        by_sid=defaultdict(list)
        for r in rs:
            by_sid[r["source_metric_id"]].append(r)

        positive=0
        negative=0
        inapplicable=0
        subgroup_summaries=[]

        for sid,srs in sorted(by_sid.items()):
            cfg_jsons={
                json.dumps(r["source_metric_config"],sort_keys=True,separators=(",",":"),ensure_ascii=True)
                for r in srs
            }
            if len(cfg_jsons)!=1:
                counts["source_metric_config_consistency_errors"]+=1
                errors.append({
                    "type":"source_metric_config_not_constant",
                    "group_id":gid,
                    "source_metric_id":sid,
                    "configs":sorted(cfg_jsons),
                })
                continue

            cfg=json.loads(next(iter(cfg_jsons)))
            sub_rows=[{
                "fact_id":r["fact_id"],
                "evaluation_id":r["evaluation_id"],
                "score":r["score"],
                "generation_args":deepcopy(r["generation_args"]),
                "evaluator_relationship":r["evaluator_relationship"],
                "source_organization_name":r["source_organization_name"],
            } for r in srs]

            out=compute_variant_divergence_py(sub_rows,cfg)
            counts["source_id_subgroups_total"]+=1

            if out is None:
                status="INAPPLICABLE"
                inapplicable+=1
                counts["source_id_subgroups_inapplicable"]+=1
            elif out.get("has_variant_divergence") is True:
                status="POSITIVE"
                positive+=1
                counts["source_id_subgroups_applicable"]+=1
                counts["source_id_subgroups_positive"]+=1
            else:
                status="NEGATIVE"
                negative+=1
                counts["source_id_subgroups_applicable"]+=1
                counts["source_id_subgroups_negative"]+=1

            rec={
                "comparability_group_id":gid,
                "source_metric_id":sid,
                "row_count":len(srs),
                "fact_ids":sorted(r["fact_id"] for r in srs),
                "metric_config":cfg,
                "status":status,
                "variant_result":out,
            }
            subgroup_records.append(rec)
            subgroup_summaries.append(rec)
            fs.write(json.dumps(rec,sort_keys=True,ensure_ascii=True)+"\n")

        retains=positive>=1
        if retains:
            counts["production_groups_retaining_positive_source_id_subgroup"]+=1
        else:
            counts["production_positive_groups_losing_all_positive_source_id_subgroups"]+=1

        grec={
            "comparability_group_id":gid,
            "production_replay":production_replay.get(gid),
            "source_metric_id_count":len(by_sid),
            "positive_source_id_subgroups":positive,
            "negative_source_id_subgroups":negative,
            "inapplicable_source_id_subgroups":inapplicable,
            "retains_positive_source_id_subgroup":retains,
            "source_metric_ids":sorted(by_sid),
        }
        group_records.append(grec)
        fg.write(json.dumps(grec,sort_keys=True,ensure_ascii=True)+"\n")

counts["unique_source_metric_ids"]=len({r["source_metric_id"] for r in subgroup_records})

if counts["affected_production_groups"]!=2:
    errors.append({"type":"affected_group_count","got":counts["affected_production_groups"],"expected":2})
if counts["production_groups_replayed_true"]!=2:
    errors.append({"type":"production_replay_true_count","got":counts["production_groups_replayed_true"],"expected":2})
if counts["unique_source_metric_ids"]!=6:
    errors.append({"type":"unique_source_metric_ids","got":counts["unique_source_metric_ids"],"expected":6})

with RAW_ERR.open("w",encoding="utf-8",newline="\n") as f:
    for e in errors:
        f.write(json.dumps(e,sort_keys=True,ensure_ascii=True)+"\n")

integrity_bad=(
    len(errors)>0
    or counts["source_metric_config_consistency_errors"]>0
    or counts["production_replay_errors"]>0
    or counts["row_identity_errors"]>0
)

if integrity_bad:
    verdict="INCONCLUSIVE"
elif counts["production_positive_groups_losing_all_positive_source_id_subgroups"]>=1:
    verdict="CONFIRMED"
else:
    verdict="REFUTED"

per_group={
    g["comparability_group_id"]:{
        "source_metric_id_count":g["source_metric_id_count"],
        "positive_source_id_subgroups":g["positive_source_id_subgroups"],
        "negative_source_id_subgroups":g["negative_source_id_subgroups"],
        "inapplicable_source_id_subgroups":g["inapplicable_source_id_subgroups"],
        "retains_positive_source_id_subgroup":g["retains_positive_source_id_subgroup"],
        "source_metric_ids":g["source_metric_ids"],
    } for g in group_records
}

per_source_id={
    r["source_metric_id"]:{
        "comparability_group_id":r["comparability_group_id"],
        "row_count":r["row_count"],
        "status":r["status"],
        "metric_config":r["metric_config"],
        "variant_result":r["variant_result"],
    } for r in subgroup_records
}

summary={
 "test_id":"T14_source_metric_identity_preservation",
 "verdict":verdict,
 "affected_production_groups":counts["affected_production_groups"],
 "affected_rows":counts["affected_rows"],
 "unique_source_metric_ids":counts["unique_source_metric_ids"],
 "source_id_subgroups_total":counts["source_id_subgroups_total"],
 "source_id_subgroups_applicable":counts["source_id_subgroups_applicable"],
 "source_id_subgroups_positive":counts["source_id_subgroups_positive"],
 "source_id_subgroups_negative":counts["source_id_subgroups_negative"],
 "source_id_subgroups_inapplicable":counts["source_id_subgroups_inapplicable"],
 "production_groups_replayed_true":counts["production_groups_replayed_true"],
 "production_groups_retaining_positive_source_id_subgroup":counts["production_groups_retaining_positive_source_id_subgroup"],
 "production_positive_groups_losing_all_positive_source_id_subgroups":counts["production_positive_groups_losing_all_positive_source_id_subgroups"],
 "source_metric_config_consistency_errors":counts["source_metric_config_consistency_errors"],
 "production_replay_errors":counts["production_replay_errors"],
 "row_identity_errors":counts["row_identity_errors"],
 "integrity_error_records":len(errors),
 "per_group":per_group,
 "per_source_metric_id":per_source_id,
 "competing_predictions":{
   "P1":"production_positive_groups_losing_all_positive_source_id_subgroups = 0",
   "P2":"production_positive_groups_losing_all_positive_source_id_subgroups >= 1"
 },
 "limitations":[
   "Exact source-id preservation is an operational counterfactual, not a normative canonicalization rule.",
   "T14 does not establish semantic non-equivalence of distinct source ids.",
   "T14 does not prescribe registry aliases or product fixes."
 ],
 "evidence":{
   "stage_f_sha256":sha256(FACT),
   "t10_source_rows_sha256":sha256(T10_ROWS),
   "t08_positive_to_negative_sha256":sha256(T08_FLIPS),
   "source_id_subgroup_results_sha256":sha256(RAW_SUB),
   "production_group_counterfactuals_sha256":sha256(RAW_GROUP),
   "integrity_errors_sha256":sha256(RAW_ERR),
 }
}

SUMMARY.write_text(
    json.dumps(summary,indent=2,sort_keys=True,ensure_ascii=True)+"\n",
    encoding="utf-8"
)

lines=[
 "# RESULT_ANALYSIS — T14 Source Metric Identity Preservation Counterfactual",
 "",
 "Status: generated after execution from the frozen T14 summary.",
 "",
 f"Primary verdict: `{verdict}`.",
 "",
 "## Raw counts",
 "",
]
for k in [
 "affected_production_groups","affected_rows","unique_source_metric_ids",
 "source_id_subgroups_total","source_id_subgroups_applicable",
 "source_id_subgroups_positive","source_id_subgroups_negative",
 "source_id_subgroups_inapplicable","production_groups_replayed_true",
 "production_groups_retaining_positive_source_id_subgroup",
 "production_positive_groups_losing_all_positive_source_id_subgroups",
 "source_metric_config_consistency_errors","production_replay_errors",
 "row_identity_errors","integrity_error_records"
]:
    lines.append(f"- `{k}` = {summary[k]}")

lines += ["","## Interpretation",""]
if verdict=="CONFIRMED":
    lines += [
      "P2 was observed: at least one production-positive consequential group has no positive variant-divergence subgroup when exact source metric identity is preserved.",
      "",
      "The fallback source-id collapse is therefore operationally necessary for at least one affected production-positive flag under this preregistered counterfactual.",
      "",
      "This does not establish that exact source-id preservation is the normative canonicalization rule."
    ]
elif verdict=="REFUTED":
    lines += [
      "P1 was observed: both affected production-positive groups retain at least one positive exact-source-id subgroup.",
      "",
      "The production-positive decisions cannot be attributed solely to source-id collapse."
    ]
else:
    lines += [
      "The counterfactual cannot be interpreted because row identity, source metric config, or production replay integrity failed."
    ]

ANALYSIS.write_text("\n".join(lines)+"\n",encoding="utf-8")

print("T14 COMPLETE")
for k in [
 "verdict","affected_production_groups","affected_rows","unique_source_metric_ids",
 "source_id_subgroups_total","source_id_subgroups_applicable",
 "source_id_subgroups_positive","source_id_subgroups_negative",
 "source_id_subgroups_inapplicable","production_groups_replayed_true",
 "production_groups_retaining_positive_source_id_subgroup",
 "production_positive_groups_losing_all_positive_source_id_subgroups",
 "source_metric_config_consistency_errors","production_replay_errors",
 "row_identity_errors","integrity_error_records"
]:
    print(f"{k}={summary[k]}")
print("per_group="+json.dumps(summary["per_group"],sort_keys=True,ensure_ascii=True))
print("per_source_metric_id="+json.dumps(summary["per_source_metric_id"],sort_keys=True,ensure_ascii=True))
print(r"summary=tests\T14_source_metric_identity_preservation\results\summary.json")
print(r"analysis=tests\T14_source_metric_identity_preservation\results\RESULT_ANALYSIS.md")
