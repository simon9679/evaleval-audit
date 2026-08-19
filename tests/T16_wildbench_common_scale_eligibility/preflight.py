from __future__ import annotations

import json
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
(HERE/"raw").mkdir(parents=True,exist_ok=True)
(HERE/"results").mkdir(parents=True,exist_ok=True)

T10=ROOT/"tests"/"T10_source_metric_config_heterogeneity"/"raw"/"source_metric_configs.jsonl"
T15=ROOT/"tests"/"T15_wildbench_authoritative_source_identity_trace"/"results"/"summary.json"
T06=ROOT/"tests"/"T06_eee_source_unit_trace"/"raw"/"source_root.json"

EEE_EXPECTED="9bce4136e789ec006c62582f5f9d107d20f8b398"

def head(path):
    try:
        return subprocess.check_output(
            ["git","-C",str(path),"rev-parse","HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None

problems=[]

if not T10.is_file():
    problems.append(f"missing T10 source rows: {T10}")

if not T15.is_file():
    problems.append(f"missing T15 summary: {T15}")
else:
    s=json.loads(T15.read_text(encoding="utf-8"))
    expected={
      "verdict":"CONFIRMED",
      "affected_rows":8,
      "unique_source_metric_ids":4,
      "distinct_raw_metric_names":4,
      "exact_adapter_derivation_ids":4,
      "distinct_nonname_source_signatures":4,
      "source_identity_trace_complete":True,
      "integrity_error_records":0,
    }
    for k,v in expected.items():
        if s.get(k)!=v:
            problems.append(f"T15 dependency mismatch {k}: got {s.get(k)!r}, expected {v!r}")

eee_root=None
if not T06.is_file():
    problems.append(f"missing T06 source root: {T06}")
else:
    r=json.loads(T06.read_text(encoding="utf-8"))
    eee_root=r.get("selected_root")
    if not eee_root or not Path(eee_root).is_dir():
        problems.append(f"invalid EEE root: {eee_root!r}")

repo_candidates=[
  ROOT/"freeze"/"repos"/"every_eval_ever",
  ROOT/"freeze"/"repos"/"every-eval-ever",
]
eee_repo=next((p for p in repo_candidates if p.is_dir()),None)
eee_head=None
adapter=None
if eee_repo is None:
    problems.append("frozen every_eval_ever repo not found")
else:
    eee_head=head(eee_repo)
    if eee_head!=EEE_EXPECTED:
        problems.append(f"every_eval_ever HEAD mismatch: {eee_head}")
    adapter=eee_repo/"every_eval_ever"/"adapters"/"openeval"/"adapter.py"
    if not adapter.is_file():
        problems.append(f"missing frozen OpenEval adapter: {adapter}")

payload={
  "test_id":"T16_wildbench_common_scale_eligibility",
  "eee_root":eee_root,
  "every_eval_ever_repo":str(eee_repo) if eee_repo else None,
  "every_eval_ever_head":eee_head,
  "adapter_path":str(adapter) if adapter else None,
  "problems":problems,
}
(HERE/"raw"/"preflight.json").write_text(
    json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=True)+"\n",
    encoding="utf-8"
)

print("T16 PREFLIGHT")
print(f"eee_root={eee_root}")
print(f"every_eval_ever_repo={eee_repo}")
print(f"every_eval_ever_head={eee_head}")
print(f"adapter_path={adapter}")
print(f"problems={len(problems)}")
for p in problems:
    print(f"PROBLEM {p}")
if problems:
    raise SystemExit(2)
print("T16 PREFLIGHT OK")
