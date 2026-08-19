from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FACT=ROOT/"tests"/"T03_corpus_boundary_impact"/"raw"/"fact_results_stage_f.parquet"
T08_FLIPS=ROOT/"tests"/"T08_within_unit_variant_counterfactual"/"raw"/"positive_to_negative_paths.jsonl"
SOURCE_ROOT=ROOT/"tests"/"T06_eee_source_unit_trace"/"raw"/"source_root.json"
BACKEND=ROOT/"freeze"/"repos"/"eval_cards_backend_pipeline"
EXPECTED_COMMIT="9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
EXPECTED_SHA="e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"

RAW_ROWS=HERE/"raw"/"source_metric_configs.jsonl"
RAW_GROUPS=HERE/"raw"/"group_signature_summary.jsonl"
RAW_HET=HERE/"raw"/"heterogeneous_groups.jsonl"
RAW_ERR=HERE/"raw"/"integrity_errors.jsonl"
SUMMARY=HERE/"results"/"summary.json"
ANALYSIS=HERE/"results"/"RESULT_ANALYSIS.md"

SIG_FIELDS=[
 "metric_id","metric_name","metric_kind","metric_parameters",
 "lower_is_better","score_type","min_score","max_score"
]

def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def hard_error(msg):
    SUMMARY.write_text(json.dumps({"test_id":"T10_source_metric_config_heterogeneity","verdict":"ERROR","error":msg},indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("T10 ERROR"); print(msg); raise SystemExit(2)

def canonical_signature(mc):
    obj={k:mc.get(k) for k in SIG_FIELDS}
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True),obj

def normalize_unit(v):
    if isinstance(v,str) and v.lower()=="percentage":
        return "percent"
    return v

if not (HERE/"raw"/"preflight.json").exists():
    hard_error("Missing T10 preflight evidence.")
head=subprocess.check_output(["git","-C",str(BACKEND),"rev-parse","HEAD"],text=True).strip()
if head!=EXPECTED_COMMIT: hard_error(f"Backend HEAD mismatch: {head}")
if not FACT.exists(): hard_error("Missing T03 Stage F parquet.")
if sha256(FACT)!=EXPECTED_SHA: hard_error("T03 Stage F parquet SHA mismatch.")
if not T08_FLIPS.exists(): hard_error("Missing T08 affected evidence.")
if not SOURCE_ROOT.exists(): hard_error("Missing T06 source root.")

root_payload=json.loads(SOURCE_ROOT.read_text(encoding="utf-8"))
eee_root=Path(root_payload.get("selected_root") or "")
if not eee_root.is_dir(): hard_error(f"Invalid EEE root: {eee_root}")

flip_recs=[json.loads(line) for line in T08_FLIPS.read_text(encoding="utf-8").splitlines() if line.strip()]
flip_ids=[r.get("comparability_group_id") for r in flip_recs]
if len(flip_recs)!=2 or None in flip_ids or len(set(flip_ids))!=2:
    hard_error(f"Expected two unique affected ids, got {flip_ids!r}")

# Freeze exact arithmetic row ids from T08 evidence for identity checking.
t08_rows={}
for rec in flip_recs:
    gid=rec["comparability_group_id"]
    rows=[]
    for unit,urs in rec.get("unit_rows",{}).items():
        for r in urs:
            rows.append({
                "fact_id":r.get("fact_id"),
                "score":r.get("score"),
                "metric_unit":unit,
                "source_record_path":r.get("source_record_path"),
                "result_idx":r.get("result_idx"),
                "evaluation_id":r.get("evaluation_id"),
                "evaluation_result_id":r.get("evaluation_result_id"),
            })
    t08_rows[gid]=rows

import duckdb
con=duckdb.connect()
p=FACT.as_posix().replace("'","''")
cols={r[0] for r in con.execute(f"DESCRIBE SELECT * FROM read_parquet('{p}')").fetchall()}
required={
 "comparability_group_id","fact_id","score","metric_unit","has_variant_divergence",
 "source_record_path","result_idx","evaluation_id","evaluation_result_id"
}
missing=sorted(required-cols)
if missing: hard_error(f"Stage F schema missing required columns: {missing}")

fact_rows=con.execute(f"SELECT COUNT(*) FROM read_parquet('{p}')").fetchone()[0]

con.execute("CREATE TEMP TABLE _affected(id VARCHAR)")
con.executemany("INSERT INTO _affected VALUES (?)",[(x,) for x in flip_ids])

rows=con.execute(f"""
 SELECT
  fr.comparability_group_id, fr.fact_id, fr.score, fr.metric_unit,
  fr.has_variant_divergence, fr.source_record_path, fr.result_idx,
  fr.evaluation_id, fr.evaluation_result_id
 FROM read_parquet('{p}') fr
 JOIN _affected a ON a.id=fr.comparability_group_id
 WHERE fr.score IS NOT NULL
 ORDER BY fr.comparability_group_id, fr.fact_id
""").fetchall()
names=[d[0] for d in con.description]
stage_rows=[dict(zip(names,r)) for r in rows]

errors=[]
counts=Counter()
by_gid=defaultdict(list)
for r in stage_rows:
    by_gid[r["comparability_group_id"]].append(r)

for gid in flip_ids:
    if gid not in by_gid:
        errors.append({"type":"affected_group_missing","group_id":gid})
    else:
        flags={r["has_variant_divergence"] for r in by_gid[gid]}
        if flags!={True}:
            errors.append({"type":"affected_group_not_production_true","group_id":gid,"flags":sorted(repr(x) for x in flags)})

# Compare row identity to T08 frozen arithmetic evidence.
for gid in flip_ids:
    def key(r):
        return (
            r.get("fact_id"), r.get("source_record_path"), int(r.get("result_idx")),
            r.get("evaluation_id"), r.get("evaluation_result_id")
        )
    stage_set={key(r) for r in by_gid.get(gid,[])}
    t08_set={key(r) for r in t08_rows.get(gid,[])}
    if stage_set!=t08_set:
        counts["arithmetic_row_identity_errors"]+=1
        errors.append({
            "type":"arithmetic_row_identity_mismatch",
            "group_id":gid,
            "stage_only":sorted(repr(x) for x in stage_set-t08_set),
            "t08_only":sorted(repr(x) for x in t08_set-stage_set),
        })

cache={}
def load(rel):
    if rel in cache: return cache[rel]
    path=eee_root/rel
    if not path.is_file():
        raise FileNotFoundError(str(path))
    obj=json.loads(path.read_text(encoding="utf-8"))
    cache[rel]=obj
    return obj

source_records=[]
group_sigs=defaultdict(list)

with RAW_ROWS.open("w",encoding="utf-8",newline="\n") as f:
    for r in stage_rows:
        trace=dict(r)
        trace.update({
            "source_metric_unit":None,
            "source_metric_unit_normalized":None,
            "source_metric_config_signature":None,
            "source_metric_config_primary":None,
            "source_evaluation_name":None,
            "source_evaluation_description":None,
            "source_metric_additional_details":None,
            "trace_error":None,
        })
        try:
            rec=load(r["source_record_path"])
            if not isinstance(rec,dict): raise TypeError("source record is not object")
            rec_eval=rec.get("evaluation_id")
            if rec_eval is not None and rec_eval!=r["evaluation_id"]:
                counts["evaluation_id_mismatches"]+=1
                errors.append({
                    "type":"evaluation_id_mismatch","fact_id":r["fact_id"],
                    "stage":r["evaluation_id"],"source":rec_eval
                })
            ers=rec.get("evaluation_results")
            if not isinstance(ers,list): raise TypeError("evaluation_results is not list")
            idx=int(r["result_idx"])
            if idx<0 or idx>=len(ers): raise IndexError(f"result_idx {idx} out of {len(ers)}")
            sr=ers[idx]
            if not isinstance(sr,dict): raise TypeError("source result is not object")
            mc=sr.get("metric_config")
            if not isinstance(mc,dict): raise TypeError("metric_config is not object")

            su=normalize_unit(mc.get("metric_unit"))
            trace["source_metric_unit"]=mc.get("metric_unit")
            trace["source_metric_unit_normalized"]=su
            if su==r["metric_unit"]:
                counts["source_unit_matches"]+=1
            else:
                counts["source_unit_mismatches"]+=1
                errors.append({
                    "type":"source_unit_mismatch","fact_id":r["fact_id"],
                    "stage_unit":r["metric_unit"],"source_unit":su
                })

            sig,sig_obj=canonical_signature(mc)
            trace["source_metric_config_signature"]=sig
            trace["source_metric_config_primary"]=sig_obj
            trace["source_evaluation_name"]=sr.get("evaluation_name")
            trace["source_evaluation_description"]=mc.get("evaluation_description")
            trace["source_metric_additional_details"]=mc.get("additional_details")
            counts["source_rows_complete"]+=1
            group_sigs[r["comparability_group_id"]].append({
                "unit":su,"signature":sig,"signature_obj":sig_obj,
                "fact_id":r["fact_id"]
            })
        except Exception as e:
            counts["pointer_or_index_errors"]+=1
            trace["trace_error"]=f"{type(e).__name__}: {e}"
            errors.append({"type":"source_trace_error","fact_id":r["fact_id"],"error":trace["trace_error"]})
        f.write(json.dumps(trace,sort_keys=True,ensure_ascii=True)+"\n")
        source_records.append(trace)

heterogeneous=[]
group_outputs=[]
with RAW_GROUPS.open("w",encoding="utf-8",newline="\n") as fg, RAW_HET.open("w",encoding="utf-8",newline="\n") as fh:
    for gid in flip_ids:
        items=group_sigs.get(gid,[])
        units=sorted({x["unit"] for x in items if x["unit"] is not None})
        sigs=sorted({x["signature"] for x in items})
        unit_to_sigs={}
        for u in units:
            unit_to_sigs[u]=sorted({x["signature"] for x in items if x["unit"]==u})
        sig_to_units={}
        for s in sigs:
            sig_to_units[s]=sorted({x["unit"] for x in items if x["signature"]==s and x["unit"] is not None})

        units_multi=sum(1 for v in unit_to_sigs.values() if len(v)>=2)
        sigs_multi=sum(1 for v in sig_to_units.values() if len(v)>=2)
        counts["affected_units_with_multiple_signatures"]+=units_multi
        counts["signatures_shared_across_multiple_units"]+=sigs_multi

        het=len(sigs)>=2
        if het:
            counts["affected_groups_with_nonunit_metric_config_heterogeneity"]+=1
        else:
            counts["affected_groups_with_single_nonunit_signature"]+=1

        out={
            "comparability_group_id":gid,
            "unit_count":len(units),
            "units":units,
            "nonunit_signature_count":len(sigs),
            "heterogeneous_nonunit_metric_config":het,
            "unit_to_signatures":unit_to_sigs,
            "signature_to_units":sig_to_units,
            "signatures":[json.loads(s) for s in sigs],
        }
        group_outputs.append(out)
        fg.write(json.dumps(out,sort_keys=True,ensure_ascii=True)+"\n")
        if het:
            heterogeneous.append(out)
            fh.write(json.dumps(out,sort_keys=True,ensure_ascii=True)+"\n")

counts["affected_group_ids"]=len(set(flip_ids))
counts["affected_groups_present"]=sum(1 for gid in flip_ids if gid in by_gid)
counts["affected_arithmetic_rows"]=len(stage_rows)

with RAW_ERR.open("w",encoding="utf-8",newline="\n") as f:
    for e in errors:
        f.write(json.dumps(e,sort_keys=True,ensure_ascii=True)+"\n")

integrity_bad=(
    len(errors)>0
    or counts["pointer_or_index_errors"]>0
    or counts["evaluation_id_mismatches"]>0
    or counts["arithmetic_row_identity_errors"]>0
    or counts["source_unit_mismatches"]>0
)
if integrity_bad:
    verdict="INCONCLUSIVE"
elif counts["affected_groups_with_nonunit_metric_config_heterogeneity"]>=1:
    verdict="CONFIRMED"
else:
    verdict="REFUTED"

per_group={
    g["comparability_group_id"]:{
        "unit_count":g["unit_count"],
        "units":g["units"],
        "nonunit_signature_count":g["nonunit_signature_count"],
        "heterogeneous_nonunit_metric_config":g["heterogeneous_nonunit_metric_config"],
    } for g in group_outputs
}

summary={
 "test_id":"T10_source_metric_config_heterogeneity",
 "verdict":verdict,
 "fact_rows_scanned":fact_rows,
 "affected_group_ids":counts["affected_group_ids"],
 "affected_groups_present":counts["affected_groups_present"],
 "affected_arithmetic_rows":counts["affected_arithmetic_rows"],
 "source_rows_complete":counts["source_rows_complete"],
 "source_unit_matches":counts["source_unit_matches"],
 "source_unit_mismatches":counts["source_unit_mismatches"],
 "affected_groups_with_single_nonunit_signature":counts["affected_groups_with_single_nonunit_signature"],
 "affected_groups_with_nonunit_metric_config_heterogeneity":counts["affected_groups_with_nonunit_metric_config_heterogeneity"],
 "affected_units_with_multiple_signatures":counts["affected_units_with_multiple_signatures"],
 "signatures_shared_across_multiple_units":counts["signatures_shared_across_multiple_units"],
 "pointer_or_index_errors":counts["pointer_or_index_errors"],
 "evaluation_id_mismatches":counts["evaluation_id_mismatches"],
 "arithmetic_row_identity_errors":counts["arithmetic_row_identity_errors"],
 "integrity_error_records":len(errors),
 "primary_signature_fields":SIG_FIELDS,
 "per_group":per_group,
 "competing_predictions":{
   "P1":"affected_groups_with_nonunit_metric_config_heterogeneity = 0",
   "P2":"affected_groups_with_nonunit_metric_config_heterogeneity >= 1"
 },
 "limitations":[
   "Structured source MetricConfig heterogeneity is not semantic ground truth.",
   "Free-text evaluation_description and additional_details are descriptive only.",
   "T10 does not decide whether differing unit labels are semantically compatible.",
   "T10 remains bounded to the frozen EEE datastore and two product-consequential groups."
 ],
 "evidence":{
   "input_fact_sha256":sha256(FACT),
   "t08_positive_to_negative_sha256":sha256(T08_FLIPS),
   "source_metric_configs_sha256":sha256(RAW_ROWS),
   "group_signature_summary_sha256":sha256(RAW_GROUPS),
   "heterogeneous_groups_sha256":sha256(RAW_HET),
   "integrity_errors_sha256":sha256(RAW_ERR),
 }
}
SUMMARY.write_text(json.dumps(summary,indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")

lines=[
 "# RESULT_ANALYSIS — T10 Source MetricConfig Heterogeneity","",
 "Status: generated after execution from the frozen T10 summary.","",
 f"Primary verdict: `{verdict}`.","",
 "## Raw counts","",
]
for k in [
 "fact_rows_scanned","affected_group_ids","affected_groups_present",
 "affected_arithmetic_rows","source_rows_complete","source_unit_matches",
 "source_unit_mismatches","affected_groups_with_single_nonunit_signature",
 "affected_groups_with_nonunit_metric_config_heterogeneity",
 "affected_units_with_multiple_signatures","signatures_shared_across_multiple_units",
 "pointer_or_index_errors","evaluation_id_mismatches",
 "arithmetic_row_identity_errors","integrity_error_records"
]:
    lines.append(f"- `{k}` = {summary[k]}")
lines += ["","## Interpretation",""]
if verdict=="CONFIRMED":
    lines += [
      "P2 was observed: at least one product-consequential group contains multiple distinct structured source MetricConfig signatures even after `metric_unit` is excluded.",
      "",
      "This localizes additional source-declared metric-definition heterogeneity beyond the already-known unit disagreement.",
      "",
      "It does not yet prove that the signatures denote different real-world estimands."
    ]
elif verdict=="REFUTED":
    lines += [
      "P1 was observed: both affected groups have exactly one structured non-unit MetricConfig signature under the preregistered field set.",
      "",
      "Under this instrument, `metric_unit` is the only structured MetricConfig disagreement among the affected arithmetic rows.",
      "",
      "A later semantic adjudication should therefore focus narrowly on the declared unit disagreement."
    ]
else:
    lines += [
      "The source-configuration question cannot be interpreted because a source trace, row identity, or integrity condition failed.",
      "",
      "No source heterogeneity conclusion is permitted until the measurement is repaired."
    ]
lines += [
 "","## Scope limits","",
 "- Structured metadata are not final semantic authority.",
 "- T10 does not identify a correct grouping rule.",
 "- Original-publisher provenance is outside T10.",
 "","## Evidence","",
 "- `raw/source_metric_configs.jsonl`",
 "- `raw/group_signature_summary.jsonl`",
 "- `raw/heterogeneous_groups.jsonl`",
 "- `raw/integrity_errors.jsonl`",
 "- `results/summary.json`",
]
ANALYSIS.write_text("\n".join(lines)+"\n",encoding="utf-8")

print("T10 COMPLETE")
for k in [
 "verdict","fact_rows_scanned","affected_group_ids","affected_groups_present",
 "affected_arithmetic_rows","source_rows_complete","source_unit_matches",
 "source_unit_mismatches","affected_groups_with_single_nonunit_signature",
 "affected_groups_with_nonunit_metric_config_heterogeneity",
 "affected_units_with_multiple_signatures","signatures_shared_across_multiple_units",
 "pointer_or_index_errors","evaluation_id_mismatches",
 "arithmetic_row_identity_errors","integrity_error_records"
]:
    print(f"{k}={summary[k]}")
print("per_group="+json.dumps(summary["per_group"],sort_keys=True,ensure_ascii=True))
print(r"summary=tests\T10_source_metric_config_heterogeneity\results\summary.json")
print(r"analysis=tests\T10_source_metric_config_heterogeneity\results\RESULT_ANALYSIS.md")
