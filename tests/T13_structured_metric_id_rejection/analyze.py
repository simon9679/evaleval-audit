from __future__ import annotations
import hashlib, json, re, subprocess, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
T12_ROWS=ROOT/"tests"/"T12_source_metric_identity_collapse"/"raw"/"row_identity_trace.jsonl"
FACT=ROOT/"tests"/"T03_corpus_boundary_impact"/"raw"/"fact_results_stage_f.parquet"
DISC=HERE/"raw"/"discovery.json"

RAW_REPLAY=HERE/"raw"/"structured_id_replay.jsonl"
RAW_CLASSES=HERE/"raw"/"rejection_classes.json"
RAW_ERR=HERE/"raw"/"integrity_errors.jsonl"
SUMMARY=HERE/"results"/"summary.json"
ANALYSIS=HERE/"results"/"RESULT_ANALYSIS.md"

EXPECTED_FACT_SHA="e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"

def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def hard_error(msg):
    SUMMARY.write_text(json.dumps({"test_id":"T13_structured_metric_id_rejection","verdict":"ERROR","error":msg},indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("T13 ERROR"); print(msg); raise SystemExit(2)

if not DISC.exists(): hard_error("Missing T13 discovery/preflight evidence.")
d=json.loads(DISC.read_text(encoding="utf-8"))
if d.get("problems"): hard_error(f"Preflight contains problems: {d['problems']}")
resolver_repo=Path(d["resolver_repo"])
registry_root=Path(d["registry_root"])
backend=ROOT/"freeze"/"repos"/"eval_cards_backend_pipeline"

if sha256(FACT)!=EXPECTED_FACT_SHA: hard_error("Stage F SHA mismatch.")

# Import exact frozen resolver source and backend helper code.
sys.path.insert(0,str(resolver_repo/"packages"/"eval-entity-resolver"/"src"))
sys.path.insert(0,str(backend/"src"))

try:
    from eval_entity_resolver import Resolver
    from eval_card_backend.sources import registry as registry_src
    from eval_card_backend.canonicalise.pipeline import _metric_catch_all_ids
except Exception as e:
    hard_error(f"cannot import frozen resolver/backend code: {type(e).__name__}: {e}")

try:
    alias_store=registry_src.load_alias_store(registry_root)
    resolver=Resolver(alias_store)
    catch_all=frozenset(_metric_catch_all_ids(registry_root))
except Exception as e:
    hard_error(f"cannot load frozen resolver registry: {type(e).__name__}: {e}")

src=[json.loads(line) for line in T12_ROWS.read_text(encoding="utf-8").splitlines() if line.strip()]
if len(src)!=12: hard_error(f"Expected 12 T12 rows, got {len(src)}")

import duckdb
con=duckdb.connect()
p=FACT.as_posix().replace("'","''")
cols={r[0] for r in con.execute(f"DESCRIBE SELECT * FROM read_parquet('{p}')").fetchall()}
if "source_config" not in cols:
    hard_error("Stage F does not contain source_config required for frozen resolver replay.")

fact_ids=[r["fact_id"] for r in src]
con.execute("CREATE TEMP TABLE _fids(id VARCHAR)")
con.executemany("INSERT INTO _fids VALUES (?)",[(x,) for x in fact_ids])
rows=con.execute(f"""
 SELECT fact_id, source_config, metric_resolution_strategy
 FROM read_parquet('{p}')
 WHERE fact_id IN (SELECT id FROM _fids)
 ORDER BY fact_id
""").fetchall()
stage={r[0]:{"source_config":r[1],"metric_resolution_strategy":r[2]} for r in rows}

errors=[]
pairs=defaultdict(set)
source_to_rows=defaultdict(list)
for r in src:
    fid=r["fact_id"]
    if fid not in stage:
        errors.append({"type":"missing_stage_fact","fact_id":fid})
        continue
    sid=r["source_metric_id"]
    sc=stage[fid]["source_config"]
    if sid is None or sc is None:
        errors.append({"type":"null_source_id_or_config","fact_id":fid,"source_metric_id":sid,"source_config":sc})
        continue
    pairs[sid].add(sc)
    source_to_rows[(sid,sc)].append(fid)
    if stage[fid]["metric_resolution_strategy"]=="metric_id_structured":
        errors.append({"type":"unexpected_structured_strategy_in_t12_population","fact_id":fid})

multi_config_ids=sum(1 for sid,configs in pairs.items() if len(configs)>1)

counts=Counter()
class_by_id={}
segment_by_id={}

with RAW_REPLAY.open("w",encoding="utf-8",newline="\n") as f:
    for sid in sorted(pairs):
        configs=sorted(pairs[sid])
        for sc in configs:
            segments=[s for s in re.split(r"[./]",sid.strip()) if s]
            segment_results=[]
            hits=[]
            for seg in segments[1:]:
                rr=resolver.resolve(seg,"metric",sc,mode="exact")
                cid=rr.canonical_id
                if cid is not None:
                    hits.append(cid)
                segment_results.append({
                    "segment":seg,
                    "canonical_id":cid,
                    "strategy":rr.strategy,
                    "confidence":rr.confidence,
                    "is_catch_all":bool(cid in catch_all) if cid is not None else False,
                })

            specific=sorted(set(h for h in hits if h not in catch_all))
            direct=resolver.resolve_structured_metric_id(sid,sc,catch_all_ids=catch_all)

            if direct is not None and len(specific)==1 and direct==specific[0]:
                cls="accepted_single_specific"
                counts["structured_accept_ids"]+=1
            elif direct is None and len(hits)==0:
                cls="rejected_no_hits"
                counts["structured_reject_ids"]+=1
                counts["rejected_no_hits"]+=1
                counts["rejected_zero_specific_ids"]+=1
            elif direct is None and len(specific)==0:
                cls="rejected_catch_all_only"
                counts["structured_reject_ids"]+=1
                counts["rejected_catch_all_only"]+=1
                counts["rejected_zero_specific_ids"]+=1
            elif direct is None and len(specific)>=2:
                cls="rejected_conflicting_specific"
                counts["structured_reject_ids"]+=1
                counts["rejected_conflicting_specific_ids"]+=1
            else:
                cls="inconsistent"
                counts["inconsistent_replay_ids"]+=1
                errors.append({
                    "type":"resolver_rule_inconsistency",
                    "source_metric_id":sid,
                    "source_config":sc,
                    "direct":direct,
                    "specific_hits":specific,
                    "all_hits":hits,
                })

            rec={
                "source_metric_id":sid,
                "source_config":sc,
                "fact_ids":sorted(source_to_rows[(sid,sc)]),
                "segments":segments,
                "segment_results":segment_results,
                "all_metric_hits":hits,
                "distinct_specific_hits":specific,
                "direct_structured_result":direct,
                "classification":cls,
            }
            f.write(json.dumps(rec,sort_keys=True,ensure_ascii=True)+"\n")
            class_by_id.setdefault(sid,[]).append({"source_config":sc,"classification":cls,"direct_result":direct})
            segment_by_id.setdefault(sid,[]).append({"source_config":sc,"segment_results":segment_results})

counts["source_rows_scanned"]=len(src)
counts["unique_source_metric_ids"]=len(pairs)
counts["unique_source_metric_id_config_pairs"]=sum(len(x) for x in pairs.values())
counts["affected_ids_with_multiple_source_configs"]=multi_config_ids
counts["catch_all_metric_ids_count"]=len(catch_all)
counts["row_source_config_errors"]=sum(1 for e in errors if e["type"] in {"missing_stage_fact","null_source_id_or_config"})

if counts["unique_source_metric_ids"]!=6:
    errors.append({"type":"unique_source_metric_id_count","got":counts["unique_source_metric_ids"],"expected":6})

# Frozen T12 observation requires all direct structured results null.
if counts["structured_accept_ids"]>0:
    errors.append({"type":"direct_replay_disagrees_with_t12_structured_absence","accepted":counts["structured_accept_ids"]})

if multi_config_ids>0:
    errors.append({"type":"source_id_multiple_configs","count":multi_config_ids})

with RAW_ERR.open("w",encoding="utf-8",newline="\n") as f:
    for e in errors:
        f.write(json.dumps(e,sort_keys=True,ensure_ascii=True)+"\n")

classes={
 "rejection_class_by_source_metric_id":class_by_id,
 "segment_hits_by_source_metric_id":segment_by_id,
 "catch_all_metric_ids":sorted(catch_all),
}
RAW_CLASSES.write_text(json.dumps(classes,indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")

integrity_bad=len(errors)>0 or counts["inconsistent_replay_ids"]>0
if integrity_bad:
    verdict="INCONCLUSIVE"
elif counts["rejected_conflicting_specific_ids"]>=1:
    verdict="REFUTED"
elif counts["rejected_zero_specific_ids"]==6 and counts["structured_reject_ids"]==6:
    verdict="CONFIRMED"
else:
    verdict="INCONCLUSIVE"

summary={
 "test_id":"T13_structured_metric_id_rejection",
 "verdict":verdict,
 "source_rows_scanned":counts["source_rows_scanned"],
 "unique_source_metric_ids":counts["unique_source_metric_ids"],
 "unique_source_metric_id_config_pairs":counts["unique_source_metric_id_config_pairs"],
 "structured_accept_ids":counts["structured_accept_ids"],
 "structured_reject_ids":counts["structured_reject_ids"],
 "rejected_no_hits":counts["rejected_no_hits"],
 "rejected_catch_all_only":counts["rejected_catch_all_only"],
 "rejected_zero_specific_ids":counts["rejected_zero_specific_ids"],
 "rejected_conflicting_specific_ids":counts["rejected_conflicting_specific_ids"],
 "inconsistent_replay_ids":counts["inconsistent_replay_ids"],
 "affected_ids_with_multiple_source_configs":counts["affected_ids_with_multiple_source_configs"],
 "catch_all_metric_ids_count":counts["catch_all_metric_ids_count"],
 "row_source_config_errors":counts["row_source_config_errors"],
 "integrity_error_records":len(errors),
 "rejection_class_by_source_metric_id":class_by_id,
 "segment_hits_by_source_metric_id":segment_by_id,
 "competing_predictions":{
   "P1":"rejected_conflicting_specific_ids >= 1",
   "P2":"rejected_conflicting_specific_ids = 0 and rejected_zero_specific_ids = 6"
 },
 "limitations":[
   "Registry vocabulary rejection is not semantic non-equivalence.",
   "T13 does not determine which aliases should be added.",
   "T13 does not adjudicate whether fallback canonical score is semantically valid."
 ],
 "evidence":{
   "t12_row_trace_sha256":sha256(T12_ROWS),
   "stage_f_sha256":sha256(FACT),
   "structured_id_replay_sha256":sha256(RAW_REPLAY),
   "rejection_classes_sha256":sha256(RAW_CLASSES),
   "integrity_errors_sha256":sha256(RAW_ERR),
 }
}
SUMMARY.write_text(json.dumps(summary,indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")

lines=[
 "# RESULT_ANALYSIS — T13 Structured Metric-ID Rejection Attribution","",
 "Status: generated after execution from the frozen T13 summary.","",
 f"Primary verdict: `{verdict}`.","",
 "## Raw counts","",
]
for k in [
 "source_rows_scanned","unique_source_metric_ids","unique_source_metric_id_config_pairs",
 "structured_accept_ids","structured_reject_ids","rejected_no_hits",
 "rejected_catch_all_only","rejected_zero_specific_ids",
 "rejected_conflicting_specific_ids","inconsistent_replay_ids",
 "affected_ids_with_multiple_source_configs","catch_all_metric_ids_count",
 "row_source_config_errors","integrity_error_records"
]:
    lines.append(f"- `{k}` = {summary[k]}")
lines+=["","## Interpretation",""]
if verdict=="CONFIRMED":
    lines += [
      "P2 was observed: all six consequential source metric ids are rejected by the structured resolver with zero distinct non-catch-all specific metric hits.",
      "",
      "The structured-path deferral is therefore a registry-vocabulary/catch-all outcome rather than a conflict among multiple specific metric candidates.",
      "",
      "Semantic correctness of the later fallback `score` collapse remains unresolved."
    ]
elif verdict=="REFUTED":
    lines += [
      "P1 was observed: at least one consequential source metric id is rejected because multiple distinct specific metric candidates are disclosed.",
      "",
      "The next analysis must distinguish resolver ambiguity from source semantic identity."
    ]
else:
    lines += [
      "The rejection mechanism cannot be interpreted because direct replay or integrity checks do not reproduce the frozen path."
    ]
ANALYSIS.write_text("\n".join(lines)+"\n",encoding="utf-8")

print("T13 COMPLETE")
for k in [
 "verdict","source_rows_scanned","unique_source_metric_ids","unique_source_metric_id_config_pairs",
 "structured_accept_ids","structured_reject_ids","rejected_no_hits",
 "rejected_catch_all_only","rejected_zero_specific_ids",
 "rejected_conflicting_specific_ids","inconsistent_replay_ids",
 "affected_ids_with_multiple_source_configs","catch_all_metric_ids_count",
 "row_source_config_errors","integrity_error_records"
]:
    print(f"{k}={summary[k]}")
print("rejection_class_by_source_metric_id="+json.dumps(summary["rejection_class_by_source_metric_id"],sort_keys=True,ensure_ascii=True))
print(r"summary=tests\T13_structured_metric_id_rejection\results\summary.json")
print(r"analysis=tests\T13_structured_metric_id_rejection\results\RESULT_ANALYSIS.md")
