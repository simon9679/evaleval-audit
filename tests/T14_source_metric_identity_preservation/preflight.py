from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

T13_SUM=ROOT/"tests"/"T13_structured_metric_id_rejection"/"results"/"summary.json"
T12_SUM=ROOT/"tests"/"T12_source_metric_identity_collapse"/"results"/"summary.json"
T10_ROWS=ROOT/"tests"/"T10_source_metric_config_heterogeneity"/"raw"/"source_metric_configs.jsonl"
T08_FLIPS=ROOT/"tests"/"T08_within_unit_variant_counterfactual"/"raw"/"positive_to_negative_paths.jsonl"
FACT=ROOT/"tests"/"T03_corpus_boundary_impact"/"raw"/"fact_results_stage_f.parquet"
BACKEND=ROOT/"freeze"/"repos"/"eval_cards_backend_pipeline"

EXPECTED_COMMIT="9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
EXPECTED_SHA="e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"

def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""):
            h.update(c)
    return h.hexdigest()

def git_head(p):
    try:
        return subprocess.check_output(
            ["git","-C",str(p),"rev-parse","HEAD"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return None

problems=[]

head=git_head(BACKEND)
if head!=EXPECTED_COMMIT:
    problems.append(f"backend HEAD mismatch: {head}")

fact_sha=sha256(FACT) if FACT.exists() else None
if fact_sha!=EXPECTED_SHA:
    problems.append(f"Stage F SHA mismatch: {fact_sha}")

def load_summary(path,label):
    if not path.exists():
        problems.append(f"missing {label} summary: {path}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        problems.append(f"cannot parse {label} summary: {type(e).__name__}: {e}")
        return {}

t13=load_summary(T13_SUM,"T13")
t12=load_summary(T12_SUM,"T12")

expected13={
 "verdict":"CONFIRMED",
 "source_rows_scanned":12,
 "unique_source_metric_ids":6,
 "structured_accept_ids":0,
 "structured_reject_ids":6,
 "rejected_no_hits":4,
 "rejected_catch_all_only":2,
 "rejected_zero_specific_ids":6,
 "rejected_conflicting_specific_ids":0,
 "inconsistent_replay_ids":0,
 "integrity_error_records":0,
}
for k,v in expected13.items():
    if t13 and t13.get(k)!=v:
        problems.append(f"T13 mismatch {k}: got {t13.get(k)!r}, expected {v!r}")

expected12={
 "affected_group_ids":2,
 "source_rows_scanned":12,
 "stage_rows_joined":12,
 "affected_groups_with_fallback_source_id_collapse":2,
 "integrity_error_records":0,
}
for k,v in expected12.items():
    if t12 and t12.get(k)!=v:
        problems.append(f"T12 mismatch {k}: got {t12.get(k)!r}, expected {v!r}")

for path,label in [(T10_ROWS,"T10 source rows"),(T08_FLIPS,"T08 flips"),(FACT,"Stage F")]:
    if not path.exists():
        problems.append(f"missing {label}: {path}")

source_rows=None
source_ids=None
if T10_ROWS.exists():
    try:
        rows=[json.loads(x) for x in T10_ROWS.read_text(encoding="utf-8").splitlines() if x.strip()]
        source_rows=len(rows)
        source_ids=len({
            r.get("source_metric_config_primary",{}).get("metric_id")
            for r in rows
            if r.get("source_metric_config_primary",{}).get("metric_id") is not None
        })
        if source_rows!=12:
            problems.append(f"T10 source row count mismatch: {source_rows}")
        if source_ids!=6:
            problems.append(f"T10 source metric id count mismatch: {source_ids}")
    except Exception as e:
        problems.append(f"cannot parse T10 source rows: {type(e).__name__}: {e}")

flip_count=None
if T08_FLIPS.exists():
    try:
        flips=[json.loads(x) for x in T08_FLIPS.read_text(encoding="utf-8").splitlines() if x.strip()]
        flip_count=len(flips)
        if flip_count!=2:
            problems.append(f"T08 flip count mismatch: {flip_count}")
    except Exception as e:
        problems.append(f"cannot parse T08 flips: {type(e).__name__}: {e}")

try:
    import duckdb
    duckdb_version=duckdb.__version__
except Exception as e:
    duckdb_version=None
    problems.append(f"missing duckdb: {type(e).__name__}: {e}")

raw=HERE/"raw"; raw.mkdir(exist_ok=True)
payload={
 "test_id":"T14_source_metric_identity_preservation",
 "backend_commit":head,
 "fact_sha256":fact_sha,
 "source_rows":source_rows,
 "unique_source_metric_ids":source_ids,
 "affected_flip_groups":flip_count,
 "duckdb":duckdb_version,
 "problems":problems,
}
(raw/"preflight.json").write_text(
    json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=True)+"\n",
    encoding="utf-8"
)

print("T14 PREFLIGHT")
print(f"backend_commit={head}")
print(f"fact_sha256={fact_sha}")
print(f"source_rows={source_rows}")
print(f"unique_source_metric_ids={source_ids}")
print(f"affected_flip_groups={flip_count}")
print(f"duckdb={duckdb_version}")
print(f"problems={len(problems)}")
for p in problems:
    print(f"PROBLEM {p}")
if problems:
    raise SystemExit(2)
print("T14 PREFLIGHT OK")
