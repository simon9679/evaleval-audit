from __future__ import annotations
import hashlib, json, subprocess
from collections import Counter, defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
T10_ROWS=ROOT/"tests"/"T10_source_metric_config_heterogeneity"/"raw"/"source_metric_configs.jsonl"
FACT=ROOT/"tests"/"T03_corpus_boundary_impact"/"raw"/"fact_results_stage_f.parquet"
BACKEND=ROOT/"freeze"/"repos"/"eval_cards_backend_pipeline"
EXPECTED_COMMIT="9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
EXPECTED_SHA="e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"

RAW_ROWS=HERE/"raw"/"row_identity_trace.jsonl"
RAW_GROUPS=HERE/"raw"/"group_collapse_summary.jsonl"
RAW_COLLAPSE=HERE/"raw"/"collapse_groups.jsonl"
RAW_ERR=HERE/"raw"/"integrity_errors.jsonl"
SUMMARY=HERE/"results"/"summary.json"
ANALYSIS=HERE/"results"/"RESULT_ANALYSIS.md"

def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def hard_error(msg):
    SUMMARY.write_text(json.dumps({"test_id":"T12_source_metric_identity_collapse","verdict":"ERROR","error":msg},indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("T12 ERROR"); print(msg); raise SystemExit(2)

if not (HERE/"raw"/"preflight.json").exists():
    hard_error("Missing T12 preflight evidence.")
head=subprocess.check_output(["git","-C",str(BACKEND),"rev-parse","HEAD"],text=True).strip()
if head!=EXPECTED_COMMIT: hard_error(f"Backend HEAD mismatch: {head}")
if not FACT.exists(): hard_error("Missing Stage F parquet.")
if sha256(FACT)!=EXPECTED_SHA: hard_error("Stage F SHA mismatch.")
if not T10_ROWS.exists(): hard_error("Missing T10 source rows.")

src=[json.loads(line) for line in T10_ROWS.read_text(encoding="utf-8").splitlines() if line.strip()]
if len(src)!=12: hard_error(f"Expected 12 source rows, got {len(src)}")

# Source metric id is already independently traced from frozen EEE by T10.
for r in src:
    if not isinstance(r.get("source_metric_config_primary"),dict):
        hard_error("T10 row missing source_metric_config_primary.")

import duckdb
con=duckdb.connect()
p=FACT.as_posix().replace("'","''")
desc=con.execute(f"DESCRIBE SELECT * FROM read_parquet('{p}')").fetchall()
cols={r[0] for r in desc}
required={"fact_id","comparability_group_id","metric_raw","metric_id","metric_resolution_strategy","metric_key"}
missing=sorted(required-cols)
if missing: hard_error(f"Stage F missing required columns: {missing}")
optional=[c for c in ["metric_id_effective","metric_key_effective"] if c in cols]

fact_ids=[r["fact_id"] for r in src]
if len(set(fact_ids))!=len(fact_ids):
    hard_error("Duplicate fact_id in T10 source rows.")

con.execute("CREATE TEMP TABLE _fids(id VARCHAR)")
con.executemany("INSERT INTO _fids VALUES (?)",[(x,) for x in fact_ids])
select_cols=[
 "fr.fact_id","fr.comparability_group_id","fr.metric_raw","fr.metric_id",
 "fr.metric_resolution_strategy","fr.metric_key"
] + [f"fr.{c}" for c in optional]
q="SELECT "+", ".join(select_cols)+f" FROM read_parquet('{p}') fr JOIN _fids f ON f.id=fr.fact_id ORDER BY fr.fact_id"
stage_tuples=con.execute(q).fetchall()
names=[d[0] for d in con.description]
stage=[dict(zip(names,r)) for r in stage_tuples]

by_fact=defaultdict(list)
for r in stage: by_fact[r["fact_id"]].append(r)

errors=[]
counts=Counter()
traces=[]
by_group=defaultdict(list)

with RAW_ROWS.open("w",encoding="utf-8",newline="\n") as f:
    for s in src:
        fid=s["fact_id"]
        matches=by_fact.get(fid,[])
        if len(matches)!=1:
            counts["row_identity_errors"]+=1
            errors.append({"type":"stage_match_count","fact_id":fid,"count":len(matches)})
            continue
        st=matches[0]
        if st["comparability_group_id"]!=s["comparability_group_id"]:
            counts["row_identity_errors"]+=1
            errors.append({
              "type":"group_id_mismatch","fact_id":fid,
              "source_group":s["comparability_group_id"],
              "stage_group":st["comparability_group_id"]
            })

        source_id=s["source_metric_config_primary"].get("metric_id")
        if source_id is None:
            errors.append({"type":"null_source_metric_id","fact_id":fid})
        rec={
          "fact_id":fid,
          "comparability_group_id":s["comparability_group_id"],
          "source_metric_id":source_id,
          "source_metric_name":s["source_metric_config_primary"].get("metric_name"),
          "source_metric_kind":s["source_metric_config_primary"].get("metric_kind"),
          "source_min_score":s["source_metric_config_primary"].get("min_score"),
          "source_max_score":s["source_metric_config_primary"].get("max_score"),
          "source_lower_is_better":s["source_metric_config_primary"].get("lower_is_better"),
          "source_metric_unit":s.get("source_metric_unit_normalized"),
          "stage_metric_raw":st.get("metric_raw"),
          "stage_metric_id":st.get("metric_id"),
          "stage_metric_resolution_strategy":st.get("metric_resolution_strategy"),
          "stage_metric_key":st.get("metric_key"),
        }
        for c in optional: rec[f"stage_{c}"]=st.get(c)
        traces.append(rec)
        by_group[rec["comparability_group_id"]].append(rec)
        f.write(json.dumps(rec,sort_keys=True,ensure_ascii=True)+"\n")

counts["affected_group_ids"]=len(by_group)
counts["source_rows_scanned"]=len(src)
counts["stage_rows_joined"]=len(traces)
counts["distinct_source_metric_ids_total"]=len({r["source_metric_id"] for r in traces if r["source_metric_id"] is not None})

group_outputs=[]
with RAW_GROUPS.open("w",encoding="utf-8",newline="\n") as fg, RAW_COLLAPSE.open("w",encoding="utf-8",newline="\n") as fc:
    for gid,rs in sorted(by_group.items()):
        source_ids=sorted({r["source_metric_id"] for r in rs if r["source_metric_id"] is not None})
        raws=sorted({r["stage_metric_raw"] for r in rs if r["stage_metric_raw"] is not None})
        mids=sorted({r["stage_metric_id"] for r in rs if r["stage_metric_id"] is not None})
        mkeys=sorted({r["stage_metric_key"] for r in rs if r["stage_metric_key"] is not None})
        strategies=sorted({r["stage_metric_resolution_strategy"] for r in rs if r["stage_metric_resolution_strategy"] is not None})
        structured_rows=sum(1 for r in rs if r["stage_metric_resolution_strategy"]=="metric_id_structured")

        if len(source_ids)>=2: counts["affected_groups_with_multiple_source_metric_ids"]+=1
        if len(raws)==1: counts["affected_groups_with_single_stage_metric_raw"]+=1
        if len(mids)==1: counts["affected_groups_with_single_stage_metric_id"]+=1
        if len(mkeys)==1: counts["affected_groups_with_single_stage_metric_key"]+=1
        if structured_rows>0: counts["affected_groups_with_structured_strategy_rows"]+=1

        mapping=defaultdict(lambda:{"metric_raw":set(),"metric_id":set(),"metric_key":set(),"strategies":set()})
        for r in rs:
            sid=r["source_metric_id"]
            mapping[sid]["metric_raw"].add(r["stage_metric_raw"])
            mapping[sid]["metric_id"].add(r["stage_metric_id"])
            mapping[sid]["metric_key"].add(r["stage_metric_key"])
            mapping[sid]["strategies"].add(r["stage_metric_resolution_strategy"])

        mapping_json={
          str(sid):{
            "metric_raw":sorted(repr(x) for x in v["metric_raw"]),
            "metric_id":sorted(repr(x) for x in v["metric_id"]),
            "metric_key":sorted(repr(x) for x in v["metric_key"]),
            "strategies":sorted(repr(x) for x in v["strategies"]),
          } for sid,v in mapping.items()
        }

        all_source_ids_one_key=(len(source_ids)>=2 and len(mkeys)==1)
        if all_source_ids_one_key:
            counts["source_ids_mapping_to_one_metric_key_groups"]+=1

        collapse=(
          len(source_ids)>=2 and
          len(raws)==1 and
          len(mids)==1 and
          len(mkeys)==1 and
          structured_rows==0
        )
        if collapse:
            counts["affected_groups_with_fallback_source_id_collapse"]+=1

        out={
          "comparability_group_id":gid,
          "source_metric_ids":source_ids,
          "source_metric_id_count":len(source_ids),
          "stage_metric_raws":raws,
          "stage_metric_raw_count":len(raws),
          "stage_metric_ids":mids,
          "stage_metric_id_count":len(mids),
          "stage_metric_keys":mkeys,
          "stage_metric_key_count":len(mkeys),
          "resolution_strategies":strategies,
          "metric_id_structured_row_count":structured_rows,
          "fallback_source_id_collapse":collapse,
          "source_to_stage_mapping":mapping_json,
        }
        for c in optional:
            vals=sorted({r.get(f"stage_{c}") for r in rs if r.get(f"stage_{c}") is not None})
            out[f"stage_{c}_values"]=vals

        group_outputs.append(out)
        fg.write(json.dumps(out,sort_keys=True,ensure_ascii=True)+"\n")
        if collapse:
            fc.write(json.dumps(out,sort_keys=True,ensure_ascii=True)+"\n")

if counts["affected_group_ids"]!=2:
    errors.append({"type":"affected_group_count","got":counts["affected_group_ids"],"expected":2})
if counts["stage_rows_joined"]!=12:
    errors.append({"type":"stage_join_count","got":counts["stage_rows_joined"],"expected":12})

with RAW_ERR.open("w",encoding="utf-8",newline="\n") as f:
    for e in errors: f.write(json.dumps(e,sort_keys=True,ensure_ascii=True)+"\n")

if errors or counts["row_identity_errors"]>0:
    verdict="INCONCLUSIVE"
elif counts["affected_groups_with_fallback_source_id_collapse"]>=1:
    verdict="CONFIRMED"
else:
    verdict="REFUTED"

per_group={
  g["comparability_group_id"]:{
    "source_metric_ids":g["source_metric_ids"],
    "stage_metric_raws":g["stage_metric_raws"],
    "stage_metric_ids":g["stage_metric_ids"],
    "stage_metric_keys":g["stage_metric_keys"],
    "resolution_strategies":g["resolution_strategies"],
    "metric_id_structured_row_count":g["metric_id_structured_row_count"],
    "fallback_source_id_collapse":g["fallback_source_id_collapse"],
  } for g in group_outputs
}

summary={
 "test_id":"T12_source_metric_identity_collapse",
 "verdict":verdict,
 "affected_group_ids":counts["affected_group_ids"],
 "source_rows_scanned":counts["source_rows_scanned"],
 "stage_rows_joined":counts["stage_rows_joined"],
 "distinct_source_metric_ids_total":counts["distinct_source_metric_ids_total"],
 "affected_groups_with_multiple_source_metric_ids":counts["affected_groups_with_multiple_source_metric_ids"],
 "affected_groups_with_single_stage_metric_raw":counts["affected_groups_with_single_stage_metric_raw"],
 "affected_groups_with_single_stage_metric_id":counts["affected_groups_with_single_stage_metric_id"],
 "affected_groups_with_single_stage_metric_key":counts["affected_groups_with_single_stage_metric_key"],
 "affected_groups_with_structured_strategy_rows":counts["affected_groups_with_structured_strategy_rows"],
 "affected_groups_with_fallback_source_id_collapse":counts["affected_groups_with_fallback_source_id_collapse"],
 "source_ids_mapping_to_one_metric_key_groups":counts["source_ids_mapping_to_one_metric_key_groups"],
 "row_identity_errors":counts["row_identity_errors"],
 "integrity_error_records":len(errors),
 "optional_stage_fields":optional,
 "per_group":per_group,
 "competing_predictions":{
   "P1":"affected_groups_with_fallback_source_id_collapse = 0",
   "P2":"affected_groups_with_fallback_source_id_collapse >= 1"
 },
 "limitations":[
   "Source metric-id difference does not automatically prove semantic non-equivalence.",
   "T12 traces the frozen transformation but does not adjudicate resolver alias correctness.",
   "Original-publisher intent is outside T12."
 ],
 "evidence":{
   "input_fact_sha256":sha256(FACT),
   "t10_source_rows_sha256":sha256(T10_ROWS),
   "row_identity_trace_sha256":sha256(RAW_ROWS),
   "group_collapse_summary_sha256":sha256(RAW_GROUPS),
   "collapse_groups_sha256":sha256(RAW_COLLAPSE),
   "integrity_errors_sha256":sha256(RAW_ERR),
 }
}
SUMMARY.write_text(json.dumps(summary,indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")

lines=[
 "# RESULT_ANALYSIS — T12 Source Metric Identity Collapse Trace","",
 "Status: generated after execution from the frozen T12 summary.","",
 f"Primary verdict: `{verdict}`.","",
 "## Raw counts","",
]
for k in [
 "affected_group_ids","source_rows_scanned","stage_rows_joined",
 "distinct_source_metric_ids_total","affected_groups_with_multiple_source_metric_ids",
 "affected_groups_with_single_stage_metric_raw",
 "affected_groups_with_single_stage_metric_id",
 "affected_groups_with_single_stage_metric_key",
 "affected_groups_with_structured_strategy_rows",
 "affected_groups_with_fallback_source_id_collapse",
 "source_ids_mapping_to_one_metric_key_groups",
 "row_identity_errors","integrity_error_records"
]:
    lines.append(f"- `{k}` = {summary[k]}")
lines += ["","## Interpretation",""]
if verdict=="CONFIRMED":
    lines += [
      "P2 was observed: at least one product-consequential group contains multiple source-declared metric ids that collapse to one Stage F raw/canonical metric identity without the structured-id strategy.",
      "",
      "This identifies the downstream identity transformation that makes those source rows eligible for one production metric_key.",
      "",
      "It does not prove the source metric ids are semantically non-equivalent."
    ]
elif verdict=="REFUTED":
    lines += [
      "P1 was observed: the full preregistered fallback source-id collapse predicate is absent.",
      "",
      "Another identity mechanism must explain how the source MetricConfig heterogeneity enters one comparability group."
    ]
else:
    lines += [
      "The transformation trace is not interpretable because a row identity or input invariant failed."
    ]
ANALYSIS.write_text("\n".join(lines)+"\n",encoding="utf-8")

print("T12 COMPLETE")
for k in [
 "verdict","affected_group_ids","source_rows_scanned","stage_rows_joined",
 "distinct_source_metric_ids_total","affected_groups_with_multiple_source_metric_ids",
 "affected_groups_with_single_stage_metric_raw",
 "affected_groups_with_single_stage_metric_id",
 "affected_groups_with_single_stage_metric_key",
 "affected_groups_with_structured_strategy_rows",
 "affected_groups_with_fallback_source_id_collapse",
 "source_ids_mapping_to_one_metric_key_groups",
 "row_identity_errors","integrity_error_records"
]:
    print(f"{k}={summary[k]}")
print("per_group="+json.dumps(summary["per_group"],sort_keys=True,ensure_ascii=True))
print(r"summary=tests\T12_source_metric_identity_collapse\results\summary.json")
print(r"analysis=tests\T12_source_metric_identity_collapse\results\RESULT_ANALYSIS.md")
