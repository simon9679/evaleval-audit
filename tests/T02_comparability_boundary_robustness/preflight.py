from __future__ import annotations
import subprocess, sys
from pathlib import Path

here = Path(__file__).resolve().parent
audit_root = here.parents[1]
backend = audit_root/"freeze"/"repos"/"eval_cards_backend_pipeline"
expected = "9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
problems=[]

try:
    head=subprocess.check_output(["git","-C",str(backend),"rev-parse","HEAD"],text=True).strip()
    if head!=expected:
        problems.append(f"backend HEAD {head} != {expected}")
except Exception as exc:
    problems.append(f"git check failed: {exc}")

t01= audit_root/"tests"/"T01_signal_calibration"/"results"/"summary.json"
if not t01.exists():
    problems.append("missing T01 summary")
else:
    import json
    s=json.loads(t01.read_text(encoding="utf-8"))
    if s.get("verdict")!="REFUTED" or s.get("fail_count")!=1:
        problems.append(f"unexpected T01 result: {s.get('verdict')} fail_count={s.get('fail_count')}")

sys.path.insert(0,str(backend/"src"))
try:
    from eval_card_backend.signals.comparability import compute_variant_divergence_py
except Exception as exc:
    problems.append(f"comparability import failed: {type(exc).__name__}: {exc}")

if problems:
    print("T02 PREFLIGHT FAIL")
    for p in problems: print(" -",p)
    raise SystemExit(1)
print("T02 PREFLIGHT OK")
print(f"backend_commit={expected}")
print("network_required=false")
