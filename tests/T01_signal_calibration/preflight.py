from __future__ import annotations
import subprocess
import sys
from pathlib import Path

test_dir = Path(__file__).resolve().parent
audit_root = test_dir.parents[1]
backend = audit_root / "freeze" / "repos" / "eval_cards_backend_pipeline"
expected = "9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"

problems = []

if not backend.exists():
    problems.append(f"missing backend: {backend}")
else:
    try:
        head = subprocess.check_output(["git", "-C", str(backend), "rev-parse", "HEAD"], text=True).strip()
        if head != expected:
            problems.append(f"backend HEAD {head} != {expected}")
    except Exception as exc:
        problems.append(f"git check failed: {exc}")

for p, markers in [
    (audit_root / "freeze" / "VERIFY_FREEZE.txt", ["bad=0", "missing=0"]),
    (audit_root / "VERIFY_BASELINES.txt", ["bad=0"]),
]:
    if not p.exists():
        problems.append(f"missing gate evidence: {p}")
    else:
        text = p.read_text(encoding="utf-8-sig")
        for marker in markers:
            if marker not in text:
                problems.append(f"{p} lacks {marker}")

sys.path.insert(0, str(backend / "src"))
for module in [
    "eval_card_backend.signals.reproducibility",
    "eval_card_backend.signals.completeness",
    "eval_card_backend.signals.comparability",
    "eval_card_backend.signals.setup",
]:
    try:
        __import__(module)
    except Exception as exc:
        problems.append(f"cannot import {module}: {type(exc).__name__}: {exc}")

if problems:
    print("T01 PREFLIGHT FAIL")
    for p in problems:
        print(" -", p)
    raise SystemExit(1)

print("T01 PREFLIGHT OK")
print(f"backend_commit={expected}")
print("network_required=false")
