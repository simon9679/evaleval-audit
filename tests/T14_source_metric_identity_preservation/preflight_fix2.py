from __future__ import annotations
import json, hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

FIX1=HERE/"results"/"summary_fix1.json"
FACT=ROOT/"tests"/"T03_corpus_boundary_impact"/"raw"/"fact_results_stage_f.parquet"
T10=ROOT/"tests"/"T10_source_metric_config_heterogeneity"/"raw"/"source_metric_configs.jsonl"
T06ROOT=ROOT/"tests"/"T06_eee_source_unit_trace"/"raw"/"source_root.json"

EXPECTED_SHA="e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"

def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

problems=[]

if not FIX1.exists():
    problems.append(f"missing Fix1 summary: {FIX1}")
else:
    try:
        s=json.loads(FIX1.read_text(encoding="utf-8"))
        expected={
          "fix_id":"HARNESS_FIX_01",
          "verdict":"INCONCLUSIVE",
          "affected_production_groups":2,
          "affected_rows":12,
          "generation_args_source_rows_complete":12,
          "generation_args_source_errors":0,
          "production_groups_replayed_exact":0,
          "production_replay_errors":8,
          "source_id_subgroups_total":0,
          "row_identity_errors":0,
          "integrity_error_records":8,
        }
        for k,v in expected.items():
            if s.get(k)!=v:
                problems.append(f"Fix1 mismatch {k}: got {s.get(k)!r}, expected {v!r}")
    except Exception as e:
        problems.append(f"cannot parse Fix1 summary: {type(e).__name__}: {e}")

if not FACT.exists():
    problems.append(f"missing Stage F: {FACT}")
elif sha256(FACT)!=EXPECTED_SHA:
    problems.append(f"Stage F SHA mismatch: {sha256(FACT)}")

eee_root=None
if not T06ROOT.exists():
    problems.append(f"missing T06 source root: {T06ROOT}")
else:
    try:
        x=json.loads(T06ROOT.read_text(encoding="utf-8"))
        eee_root=x.get("selected_root")
        if not eee_root or not Path(eee_root).is_dir():
            problems.append(f"invalid EEE root: {eee_root!r}")
    except Exception as e:
        problems.append(f"cannot parse EEE root: {type(e).__name__}: {e}")

if not T10.exists():
    problems.append(f"missing T10 source rows: {T10}")

payload={
 "test_id":"T14_source_metric_identity_preservation",
 "fix_id":"HARNESS_FIX_02",
 "fact_sha256":sha256(FACT) if FACT.exists() else None,
 "eee_root":eee_root,
 "problems":problems,
}
(HERE/"raw"/"preflight_fix2.json").parent.mkdir(exist_ok=True)
(HERE/"raw"/"preflight_fix2.json").write_text(
    json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=True)+"\n",
    encoding="utf-8"
)

print("T14 FIX2 PREFLIGHT")
print(f"fact_sha256={payload['fact_sha256']}")
print(f"eee_root={eee_root}")
print(f"fix1_expected_inconclusive={not any('Fix1' in p for p in problems)}")
print(f"problems={len(problems)}")
for p in problems: print(f"PROBLEM {p}")
if problems: raise SystemExit(2)
print("T14 FIX2 PREFLIGHT OK")
