from __future__ import annotations
import hashlib, importlib, json, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
T03 = ROOT / "tests" / "T03_corpus_boundary_impact"
T04 = ROOT / "tests" / "T04_comparability_unit_consistency"
FACT = T03 / "raw" / "fact_results_stage_f.parquet"
T04_SUM = T04 / "results" / "summary.json"
BACKEND = ROOT / "freeze" / "repos" / "eval_cards_backend_pipeline"

EXPECTED_COMMIT = "9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
EXPECTED_SHA = "e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"

def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1024*1024), b""): h.update(c)
    return h.hexdigest()

problems=[]
try:
    head=subprocess.check_output(["git","-C",str(BACKEND),"rev-parse","HEAD"],text=True).strip()
except Exception as e:
    head=None; problems.append(f"cannot resolve backend HEAD: {type(e).__name__}: {e}")
if head != EXPECTED_COMMIT:
    problems.append(f"backend HEAD mismatch: {head}")

if not FACT.exists():
    problems.append(f"missing T03 fact parquet: {FACT}")
fact_sha=sha256(FACT) if FACT.exists() else None
if fact_sha and fact_sha != EXPECTED_SHA:
    problems.append(f"T03 fact SHA mismatch: {fact_sha}")

t04={}
if not T04_SUM.exists():
    problems.append(f"missing T04 summary: {T04_SUM}")
else:
    try: t04=json.loads(T04_SUM.read_text(encoding="utf-8"))
    except Exception as e: problems.append(f"cannot parse T04 summary: {type(e).__name__}: {e}")

checks={
    "verdict":"REFUTED",
    "actual_mixed_unit_groups":1234,
    "classification_sensitive_paths":0,
    "production_reconstruction_errors":0,
    "group_consistency_errors":0,
}
for k,v in checks.items():
    if t04 and t04.get(k) != v:
        problems.append(f"T04 summary mismatch {k}: got {t04.get(k)!r}, expected {v!r}")

versions={}
try:
    import duckdb
    versions["duckdb"]=duckdb.__version__
except Exception as e:
    versions["duckdb"]=None
    problems.append(f"missing dependency duckdb: {type(e).__name__}: {e}")

raw=HERE/"raw"; raw.mkdir(exist_ok=True)
(raw/"preflight.json").write_text(json.dumps({
    "test_id":"T05_metric_unit_provenance_decomposition",
    "backend_commit":head,
    "fact_sha256":fact_sha,
    "t04_checks":checks,
    "dependencies":versions,
    "problems":problems,
},indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")

print("T05 PREFLIGHT")
print(f"backend_commit={head}")
print(f"fact_sha256={fact_sha}")
print(f"duckdb={versions.get('duckdb')}")
print(f"problems={len(problems)}")
for p in problems: print(f"PROBLEM {p}")
if problems: raise SystemExit(2)
print("T05 PREFLIGHT OK")
