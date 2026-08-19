from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

FACT=ROOT/"tests"/"T03_corpus_boundary_impact"/"raw"/"fact_results_stage_f.parquet"
T10_ROWS=ROOT/"tests"/"T10_source_metric_config_heterogeneity"/"raw"/"source_metric_configs.jsonl"
T08_FLIPS=ROOT/"tests"/"T08_within_unit_variant_counterfactual"/"raw"/"positive_to_negative_paths.jsonl"
T06ROOT=ROOT/"tests"/"T06_eee_source_unit_trace"/"raw"/"source_root.json"
BACKEND=ROOT/"freeze"/"repos"/"eval_cards_backend_pipeline"

EXPECTED_COMMIT="9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
EXPECTED_SHA="e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"

RAW_SRC=HERE/"raw"/"generation_args_source_trace_fix2.jsonl"
RAW_SUB=HERE/"raw"/"source_id_subgroup_results_fix2.jsonl"
RAW_GROUP=HERE/"raw"/"production_group_counterfactuals_fix2.jsonl"
RAW_ERR=HERE/"raw"/"integrity_errors_fix2.jsonl"
SUMMARY=HERE/"results"/"summary_fix2.json"
ANALYSIS=HERE/"results"/"RESULT_ANALYSIS_FIX2.md"

def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def fail(msg):
    SUMMARY.write_text(
        json.dumps({"test_id":"T14_source_metric_identity_preservation","fix_id":"HARNESS_FIX_02","verdict":"ERROR","error":msg},
                   indent=2,sort_keys=True)+"\n",
        encoding="utf-8"
    )
    print("T14 FIX2 ERROR")
    print(msg)
    raise SystemExit(2)

def canon(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True,default=str)

def float_equal(a,b,tol=1e-12):
    if a is None or b is None: return a is b
    return math.isclose(float(a),float(b),rel_tol=0.0,abs_tol=tol)

def prod_max_nonnull(values):
    vals=[v for v in values if v is not None]
    return max(vals) if vals else None

if not (HERE/"raw"/"preflight_fix2.json").exists():
    fail("Missing Fix2 preflight evidence.")

head=subprocess.check_output(["git","-C",str(BACKEND),"rev-parse","HEAD"],text=True).strip()
if head!=EXPECTED_COMMIT: fail(f"Backend HEAD mismatch: {head}")
if sha256(FACT)!=EXPECTED_SHA: fail("Stage F SHA mismatch.")

sys.path.insert(0,str(BACKEND/"src"))
try:
    from eval_card_backend.signals.comparability import compute_variant_divergence_py
except Exception as e:
    fail(f"cannot import frozen production comparability function: {type(e).__name__}: {e}")

root_payload=json.loads(T06ROOT.read_text(encoding="utf-8"))
EEE=Path(root_payload["selected_root"])
if not EEE.is_dir(): fail(f"Invalid EEE root: {EEE}")

src=[json.loads(x) for x in T10_ROWS.read_text(encoding="utf-8").splitlines() if x.strip()]
flips=[json.loads(x) for x in T08_FLIPS.read_text(encoding="utf-8").splitlines() if x.strip()]
if len(src)!=12: fail(f"Expected 12 T10 rows, got {len(src)}")
if len(flips)!=2: fail(f"Expected 2 T08 groups, got {len(flips)}")

affected_ids=[r["comparability_group_id"] for r in flips]

errors=[]
counts=Counter()
source_by_fact={}
cache={}

def load_record(rel):
    if rel in cache: return cache[rel]
    p=EEE/rel
    if not p.is_file():
        raise FileNotFoundError(str(p))
    obj=json.loads(p.read_text(encoding="utf-8"))
    cache[rel]=obj
    return obj

with RAW_SRC.open("w",encoding="utf-8",newline="\n") as f:
    for r in src:
        fid=r["fact_id"]
        try:
            rec=load_record(r["source_record_path"])
            idx=int(r["result_idx"])
            ers=rec.get("evaluation_results")
            if not isinstance(ers,list) or idx<0 or idx>=len(ers):
                raise IndexError(f"result_idx={idx}")
            er=ers[idx]
            gc=er.get("generation_config") or {}
            if not isinstance(gc,dict):
                raise TypeError("generation_config is not object")
            ga=gc.get("generation_args") or {}
            if not isinstance(ga,dict):
                raise TypeError("generation_args is not object")
            source_by_fact[fid]={
                "comparability_group_id":r["comparability_group_id"],
                "source_metric_id":r["source_metric_config_primary"]["metric_id"],
                "source_metric_config":{
                    "metric_kind":r["source_metric_config_primary"].get("metric_kind"),
                    "metric_unit":r.get("source_metric_unit_normalized"),
                    "min_score":r["source_metric_config_primary"].get("min_score"),
                    "max_score":r["source_metric_config_primary"].get("max_score"),
                },
                "generation_args":ga,
            }
            counts["generation_args_source_rows_complete"]+=1
            f.write(json.dumps({
                "fact_id":fid,
                "comparability_group_id":r["comparability_group_id"],
                "generation_args":ga,
            },sort_keys=True,ensure_ascii=True)+"\n")
        except Exception as e:
            counts["generation_args_source_errors"]+=1
            errors.append({"type":"generation_args_source_error","fact_id":fid,"error":f"{type(e).__name__}: {e}"})

import duckdb
con=duckdb.connect()
p=FACT.as_posix().replace("'","''")
con.execute("CREATE TEMP TABLE _affected(id VARCHAR)")
con.executemany("INSERT INTO _affected VALUES (?)",[(x,) for x in affected_ids])

rows=con.execute(f"""
 SELECT
   fr.fact_id,
   fr.comparability_group_id,
   fr.evaluation_id,
   fr.score,
   fr.evaluator_relationship,
   fr.org_raw,
   fr.metric_kind,
   fr.metric_unit,
   fr.min_score,
   fr.max_score,
   fr.has_variant_divergence,
   fr.variant_divergence_magnitude,
   fr.variant_divergence_threshold,
   fr.variant_threshold_basis,
   fr.variant_differing_fields
 FROM read_parquet('{p}') fr
 JOIN _affected a ON a.id=fr.comparability_group_id
 ORDER BY fr.comparability_group_id, fr.fact_id
""").fetchall()
names=[d[0] for d in con.description]
stage_all=[dict(zip(names,r)) for r in rows]
stage=[r for r in stage_all if r["fact_id"] in source_by_fact]

if len(stage)!=12:
    errors.append({"type":"stage_affected_row_count","got":len(stage),"expected":12})

by_gid=defaultdict(list)
for r in stage:
    s=source_by_fact.get(r["fact_id"])
    if s is None:
        counts["row_identity_errors"]+=1
        errors.append({"type":"missing_source_fact","fact_id":r["fact_id"]})
        continue
    if s["comparability_group_id"]!=r["comparability_group_id"]:
        counts["row_identity_errors"]+=1
        errors.append({"type":"group_id_mismatch","fact_id":r["fact_id"]})
    rr=dict(r)
    rr["source_metric_id"]=s["source_metric_id"]
    rr["source_metric_config"]=s["source_metric_config"]
    rr["generation_args_source"]=s["generation_args"]
    by_gid[r["comparability_group_id"]].append(rr)

counts["affected_production_groups"]=len(by_gid)
counts["affected_rows"]=len(stage)

production_replay={}
group_prod_cfg={}

for gid,rs in sorted(by_gid.items()):
    # Exact frozen Stage F group_payloads reconstruction:
    cfg={
        "metric_kind":prod_max_nonnull([r["metric_kind"] for r in rs]),
        "metric_unit":prod_max_nonnull([r["metric_unit"] for r in rs]),
        "min_score":prod_max_nonnull([r["min_score"] for r in rs]),
        "max_score":prod_max_nonnull([r["max_score"] for r in rs]),
    }
    group_prod_cfg[gid]=cfg

    frozen_fields={}
    for k in [
        "has_variant_divergence","variant_divergence_magnitude",
        "variant_divergence_threshold","variant_threshold_basis",
        "variant_differing_fields"
    ]:
        vals={canon(r[k]) for r in rs}
        if len(vals)!=1:
            counts["production_replay_errors"]+=1
            errors.append({"type":"frozen_group_signal_not_constant","group_id":gid,"field":k,"values":sorted(vals)})
        else:
            frozen_fields[k]=rs[0][k]

    rows_in=[{
        "fact_id":r["fact_id"],
        "evaluation_id":r["evaluation_id"],
        "score":r["score"],
        "generation_args":deepcopy(r["generation_args_source"]),
        "evaluator_relationship":r["evaluator_relationship"],
        "source_organization_name":r["org_raw"],
    } for r in rs]

    out=compute_variant_divergence_py(rows_in,cfg)
    production_replay[gid]=out

    ok=True
    if out is None:
        ok=False
    else:
        ok &= out.get("has_variant_divergence")==frozen_fields.get("has_variant_divergence")
        ok &= float_equal(out.get("divergence_magnitude"),frozen_fields.get("variant_divergence_magnitude"))
        ok &= float_equal(out.get("threshold_used"),frozen_fields.get("variant_divergence_threshold"))
        ok &= out.get("threshold_basis")==frozen_fields.get("variant_threshold_basis")
        ok &= canon(out.get("differing_setup_fields"))==canon(frozen_fields.get("variant_differing_fields"))

    if not ok:
        counts["production_replay_errors"]+=1
        errors.append({
            "type":"production_replay_mismatch",
            "group_id":gid,
            "production_metric_config_reconstructed":cfg,
            "replay":out,
            "frozen":{
                "has_variant_divergence":frozen_fields.get("has_variant_divergence"),
                "divergence_magnitude":frozen_fields.get("variant_divergence_magnitude"),
                "threshold_used":frozen_fields.get("variant_divergence_threshold"),
                "threshold_basis":frozen_fields.get("variant_threshold_basis"),
                "differing_setup_fields":frozen_fields.get("variant_differing_fields"),
            }
        })
    else:
        counts["production_groups_replayed_exact"]+=1

subgroup_records=[]
group_records=[]

if counts["production_groups_replayed_exact"]==2 and counts["production_replay_errors"]==0:
    with RAW_SUB.open("w",encoding="utf-8",newline="\n") as fs, RAW_GROUP.open("w",encoding="utf-8",newline="\n") as fg:
        for gid,rs in sorted(by_gid.items()):
            by_sid=defaultdict(list)
            for r in rs:
                by_sid[r["source_metric_id"]].append(r)

            positive=negative=inapplicable=0

            for sid,srs in sorted(by_sid.items()):
                cfgs={canon(r["source_metric_config"]) for r in srs}
                if len(cfgs)!=1:
                    counts["source_metric_config_consistency_errors"]+=1
                    errors.append({"type":"source_metric_config_not_constant","group_id":gid,"source_metric_id":sid,"configs":sorted(cfgs)})
                    continue

                cfg=json.loads(next(iter(cfgs)))
                rows_in=[{
                    "fact_id":r["fact_id"],
                    "evaluation_id":r["evaluation_id"],
                    "score":r["score"],
                    "generation_args":deepcopy(r["generation_args_source"]),
                    "evaluator_relationship":r["evaluator_relationship"],
                    "source_organization_name":r["org_raw"],
                } for r in srs]

                out=compute_variant_divergence_py(rows_in,cfg)
                counts["source_id_subgroups_total"]+=1

                if out is None:
                    status="INAPPLICABLE"
                    inapplicable+=1
                    counts["source_id_subgroups_inapplicable"]+=1
                elif out["has_variant_divergence"]:
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
                fs.write(json.dumps(rec,sort_keys=True,ensure_ascii=True)+"\n")

            retains=positive>=1
            if retains:
                counts["production_groups_retaining_positive_source_id_subgroup"]+=1
            else:
                counts["production_positive_groups_losing_all_positive_source_id_subgroups"]+=1

            grec={
                "comparability_group_id":gid,
                "production_metric_config_reconstructed":group_prod_cfg[gid],
                "production_replay":production_replay[gid],
                "source_metric_id_count":len(by_sid),
                "positive_source_id_subgroups":positive,
                "negative_source_id_subgroups":negative,
                "inapplicable_source_id_subgroups":inapplicable,
                "retains_positive_source_id_subgroup":retains,
                "source_metric_ids":sorted(by_sid),
            }
            group_records.append(grec)
            fg.write(json.dumps(grec,sort_keys=True,ensure_ascii=True)+"\n")
else:
    RAW_SUB.write_text("",encoding="utf-8")
    RAW_GROUP.write_text("",encoding="utf-8")

counts["unique_source_metric_ids"]=len({s["source_metric_id"] for s in source_by_fact.values()})

with RAW_ERR.open("w",encoding="utf-8",newline="\n") as f:
    for e in errors:
        f.write(json.dumps(e,sort_keys=True,ensure_ascii=True)+"\n")

integrity_bad=(
    len(errors)>0
    or counts["generation_args_source_errors"]>0
    or counts["row_identity_errors"]>0
    or counts["production_replay_errors"]>0
    or counts["source_metric_config_consistency_errors"]>0
)

if integrity_bad:
    verdict="INCONCLUSIVE"
elif counts["production_positive_groups_losing_all_positive_source_id_subgroups"]>=1:
    verdict="CONFIRMED"
else:
    verdict="REFUTED"

per_group={
    g["comparability_group_id"]:{
        "production_metric_config_reconstructed":g["production_metric_config_reconstructed"],
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
 "fix_id":"HARNESS_FIX_02",
 "verdict":verdict,
 "affected_production_groups":counts["affected_production_groups"],
 "affected_rows":counts["affected_rows"],
 "generation_args_source_rows_complete":counts["generation_args_source_rows_complete"],
 "generation_args_source_errors":counts["generation_args_source_errors"],
 "production_groups_replayed_exact":counts["production_groups_replayed_exact"],
 "production_replay_errors":counts["production_replay_errors"],
 "unique_source_metric_ids":counts["unique_source_metric_ids"],
 "source_id_subgroups_total":counts["source_id_subgroups_total"],
 "source_id_subgroups_applicable":counts["source_id_subgroups_applicable"],
 "source_id_subgroups_positive":counts["source_id_subgroups_positive"],
 "source_id_subgroups_negative":counts["source_id_subgroups_negative"],
 "source_id_subgroups_inapplicable":counts["source_id_subgroups_inapplicable"],
 "production_groups_retaining_positive_source_id_subgroup":counts["production_groups_retaining_positive_source_id_subgroup"],
 "production_positive_groups_losing_all_positive_source_id_subgroups":counts["production_positive_groups_losing_all_positive_source_id_subgroups"],
 "source_metric_config_consistency_errors":counts["source_metric_config_consistency_errors"],
 "row_identity_errors":counts["row_identity_errors"],
 "integrity_error_records":len(errors),
 "per_group":per_group,
 "per_source_metric_id":per_source_id,
 "competing_predictions":{
   "P1":"production_positive_groups_losing_all_positive_source_id_subgroups = 0",
   "P2":"production_positive_groups_losing_all_positive_source_id_subgroups >= 1"
 },
 "limitations":[
   "Fix 2 repairs production group metric_config reconstruction after Fix 1 INCONCLUSIVE.",
   "Exact source-id preservation is an operational counterfactual, not a normative canonicalization rule.",
   "T14 does not establish semantic non-equivalence of distinct source ids."
 ],
 "evidence":{
   "stage_f_sha256":sha256(FACT),
   "t10_source_rows_sha256":sha256(T10_ROWS),
   "t08_positive_to_negative_sha256":sha256(T08_FLIPS),
   "generation_args_source_trace_sha256":sha256(RAW_SRC),
   "source_id_subgroup_results_sha256":sha256(RAW_SUB),
   "production_group_counterfactuals_sha256":sha256(RAW_GROUP),
   "integrity_errors_sha256":sha256(RAW_ERR),
 }
}
SUMMARY.write_text(json.dumps(summary,indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")

lines=[
 "# RESULT_ANALYSIS — T14 Source Metric Identity Preservation Counterfactual — Fix 2",
 "",
 "Status: generated after the repaired T14 Fix 2 execution.",
 "",
 f"Primary verdict: `{verdict}`.",
 "",
 "## Repair",
 "",
 "Fix 2 reconstructs the full-group production metric_config with the exact frozen Stage F non-null MAX rule instead of incorrectly requiring row-level metric metadata constancy.",
 "",
 "## Raw counts",
 "",
]
for k in [
 "affected_production_groups","affected_rows",
 "generation_args_source_rows_complete","generation_args_source_errors",
 "production_groups_replayed_exact","production_replay_errors",
 "unique_source_metric_ids","source_id_subgroups_total",
 "source_id_subgroups_applicable","source_id_subgroups_positive",
 "source_id_subgroups_negative","source_id_subgroups_inapplicable",
 "production_groups_retaining_positive_source_id_subgroup",
 "production_positive_groups_losing_all_positive_source_id_subgroups",
 "source_metric_config_consistency_errors","row_identity_errors",
 "integrity_error_records"
]:
    lines.append(f"- `{k}` = {summary[k]}")

lines += ["","## Interpretation",""]
if verdict=="CONFIRMED":
    lines += [
      "P2 was observed: at least one affected production-positive group has no positive exact-source-id subgroup.",
      "",
      "Both original production groups replay exactly under the frozen Stage F group metric_config construction before the counterfactual is interpreted.",
      "",
      "This supports operational dependence on fallback source-id collapse under the preregistered identity-preservation intervention."
    ]
elif verdict=="REFUTED":
    lines += [
      "P1 was observed: both affected production-positive groups retain at least one positive exact-source-id subgroup.",
      "",
      "The production-positive decisions cannot be attributed solely to fallback source-id collapse."
    ]
else:
    lines += [
      "T14 remains INCONCLUSIVE because exact production replay or another integrity control failed.",
      "",
      "No counterfactual attribution is permitted."
    ]

ANALYSIS.write_text("\n".join(lines)+"\n",encoding="utf-8")

print("T14 FIX2 COMPLETE")
for k in [
 "verdict","affected_production_groups","affected_rows",
 "generation_args_source_rows_complete","generation_args_source_errors",
 "production_groups_replayed_exact","production_replay_errors",
 "unique_source_metric_ids","source_id_subgroups_total",
 "source_id_subgroups_applicable","source_id_subgroups_positive",
 "source_id_subgroups_negative","source_id_subgroups_inapplicable",
 "production_groups_retaining_positive_source_id_subgroup",
 "production_positive_groups_losing_all_positive_source_id_subgroups",
 "source_metric_config_consistency_errors","row_identity_errors",
 "integrity_error_records"
]:
    print(f"{k}={summary[k]}")
print("per_group="+json.dumps(summary["per_group"],sort_keys=True,ensure_ascii=True))
print("per_source_metric_id="+json.dumps(summary["per_source_metric_id"],sort_keys=True,ensure_ascii=True))
print(r"summary=tests\T14_source_metric_identity_preservation\results\summary_fix2.json")
print(r"analysis=tests\T14_source_metric_identity_preservation\results\RESULT_ANALYSIS_FIX2.md")
