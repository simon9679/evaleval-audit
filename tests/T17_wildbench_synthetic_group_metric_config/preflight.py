from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
(HERE/"raw").mkdir(parents=True,exist_ok=True)
(HERE/"results").mkdir(parents=True,exist_ok=True)

FACT=ROOT/"tests"/"T03_corpus_boundary_impact"/"raw"/"fact_results_stage_f.parquet"
T16=ROOT/"tests"/"T16_wildbench_common_scale_eligibility"/"results"/"summary.json"
BACKEND=ROOT/"freeze"/"repos"/"eval_cards_backend_pipeline"

EXPECTED_FACT_SHA="e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"
EXPECTED_BACKEND="9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"

def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def head(p):
    try:
        return subprocess.check_output(["git","-C",str(p),"rev-parse","HEAD"],text=True,stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None

problems=[]
fact_sha=sha256(FACT) if FACT.is_file() else None
if fact_sha!=EXPECTED_FACT_SHA:
    problems.append(f"Stage F SHA mismatch: {fact_sha}")

backend_head=head(BACKEND)
if backend_head!=EXPECTED_BACKEND:
    problems.append(f"backend HEAD mismatch: {backend_head}")

if not T16.is_file():
    problems.append(f"missing T16 summary: {T16}")
else:
    s=json.loads(T16.read_text(encoding="utf-8"))
    expected={
      "verdict":"CONFIRMED",
      "affected_rows":8,
      "unique_source_metric_ids":4,
      "distinct_scale_signatures":3,
      "common_scale_eligible":False,
      "integrity_error_records":0,
    }
    for k,v in expected.items():
        if s.get(k)!=v:
            problems.append(f"T16 dependency mismatch {k}: got {s.get(k)!r}, expected {v!r}")

try:
    import duckdb
    duckdb_version=duckdb.__version__
except Exception as e:
    duckdb_version=None
    problems.append(f"duckdb import failed: {type(e).__name__}: {e}")

# Verify threshold module is importable from the frozen backend.
threshold_probe=None
try:
    import sys
    sys.path.insert(0,str(BACKEND/"src"))
    from eval_card_backend.canonicalise.thresholds import compute_threshold, threshold_factor
    threshold_probe=compute_threshold({"metric_unit":"score","min_score":0.0,"max_score":10.0})
    if threshold_factor()!=1.0:
        problems.append(f"threshold factor is {threshold_factor()}, expected 1.0")
except Exception as e:
    problems.append(f"threshold import/probe failed: {type(e).__name__}: {e}")

payload={
 "test_id":"T17_wildbench_synthetic_group_metric_config",
 "fact_sha256":fact_sha,
 "backend_head":backend_head,
 "duckdb":duckdb_version,
 "threshold_probe":threshold_probe,
 "problems":problems,
}
(HERE/"raw"/"preflight.json").write_text(
    json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=True)+"\n",
    encoding="utf-8"
)

print("T17 PREFLIGHT")
print(f"fact_sha256={fact_sha}")
print(f"backend_head={backend_head}")
print(f"duckdb={duckdb_version}")
print(f"threshold_probe={threshold_probe}")
print(f"problems={len(problems)}")
for p in problems: print(f"PROBLEM {p}")
if problems: raise SystemExit(2)
print("T17 PREFLIGHT OK")
