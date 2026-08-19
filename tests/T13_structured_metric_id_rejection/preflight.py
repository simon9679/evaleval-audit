from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
T12_SUM=ROOT/"tests"/"T12_source_metric_identity_collapse"/"results"/"summary.json"
T12_ROWS=ROOT/"tests"/"T12_source_metric_identity_collapse"/"raw"/"row_identity_trace.jsonl"
FACT=ROOT/"tests"/"T03_corpus_boundary_impact"/"raw"/"fact_results_stage_f.parquet"
BACKEND=ROOT/"freeze"/"repos"/"eval_cards_backend_pipeline"

EXPECTED_BACKEND="9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
EXPECTED_RESOLVER="6fb026d7483467f063da465c15a76733b3d25f4c"
EXPECTED_FACT_SHA="e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"

def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def git_head(p):
    try:
        return subprocess.check_output(["git","-C",str(p),"rev-parse","HEAD"],text=True,stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None

problems=[]

backend_head=git_head(BACKEND)
if backend_head!=EXPECTED_BACKEND:
    problems.append(f"backend HEAD mismatch: {backend_head}")

fact_sha=sha256(FACT) if FACT.exists() else None
if fact_sha!=EXPECTED_FACT_SHA:
    problems.append(f"Stage F SHA mismatch: {fact_sha}")

s={}
if not T12_SUM.exists():
    problems.append(f"missing T12 summary: {T12_SUM}")
else:
    try:s=json.loads(T12_SUM.read_text(encoding="utf-8"))
    except Exception as e:problems.append(f"cannot parse T12 summary: {type(e).__name__}: {e}")

expected={
 "verdict":"CONFIRMED",
 "affected_group_ids":2,
 "source_rows_scanned":12,
 "stage_rows_joined":12,
 "distinct_source_metric_ids_total":6,
 "affected_groups_with_multiple_source_metric_ids":2,
 "affected_groups_with_structured_strategy_rows":0,
 "affected_groups_with_fallback_source_id_collapse":2,
 "row_identity_errors":0,
 "integrity_error_records":0,
}
for k,v in expected.items():
    if s and s.get(k)!=v:
        problems.append(f"T12 mismatch {k}: got {s.get(k)!r}, expected {v!r}")

if not T12_ROWS.exists():
    problems.append(f"missing T12 rows: {T12_ROWS}")

# Resolver checkout discovery by commit, not folder name.
resolver_candidates=[]
repos_root=ROOT/"freeze"/"repos"
if repos_root.is_dir():
    for p in repos_root.iterdir():
        if p.is_dir() and git_head(p)==EXPECTED_RESOLVER:
            marker=p/"packages"/"eval-entity-resolver"/"src"/"eval_entity_resolver"/"resolver.py"
            if marker.exists():
                resolver_candidates.append(p)
if len(resolver_candidates)!=1:
    problems.append(f"expected exactly one resolver repo at frozen commit, found {len(resolver_candidates)}")
resolver_repo=str(resolver_candidates[0]) if len(resolver_candidates)==1 else None

# Registry data discovery by required tables, not marker filename assumptions.
def has_table(root,name):
    return (root/f"{name}.parquet").is_file() or ((root/name).is_dir() and any((root/name).glob("*.parquet")))

registry_candidates=[]
hf_root=ROOT/"freeze"/"hf"
if hf_root.is_dir():
    for p in [hf_root]+[x for x in hf_root.rglob("*") if x.is_dir()]:
        if has_table(p,"aliases") and has_table(p,"canonical_metrics"):
            registry_candidates.append(p)
# remove nested duplicates if any path repeats
registry_candidates=sorted(set(registry_candidates))
if len(registry_candidates)!=1:
    problems.append(f"expected exactly one registry data root, found {len(registry_candidates)}")
registry_root=str(registry_candidates[0]) if len(registry_candidates)==1 else None

try:
    import duckdb
    duckdb_version=duckdb.__version__
except Exception as e:
    duckdb_version=None
    problems.append(f"missing duckdb: {type(e).__name__}: {e}")

raw=HERE/"raw"; raw.mkdir(exist_ok=True)
payload={
 "test_id":"T13_structured_metric_id_rejection",
 "backend_commit":backend_head,
 "resolver_commit":EXPECTED_RESOLVER,
 "fact_sha256":fact_sha,
 "resolver_repo":resolver_repo,
 "registry_root":registry_root,
 "duckdb":duckdb_version,
 "problems":problems,
}
(raw/"discovery.json").write_text(json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")
(raw/"preflight.json").write_text(json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")

print("T13 PREFLIGHT")
print(f"backend_commit={backend_head}")
print(f"resolver_commit={EXPECTED_RESOLVER}")
print(f"fact_sha256={fact_sha}")
print(f"resolver_repo={resolver_repo}")
print(f"registry_root={registry_root}")
print(f"duckdb={duckdb_version}")
print(f"problems={len(problems)}")
for p in problems: print(f"PROBLEM {p}")
if problems: raise SystemExit(2)
print("T13 PREFLIGHT OK")
