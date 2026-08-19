from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
AUDIT_ROOT = HERE.parents[1]
BACKEND = AUDIT_ROOT / "freeze" / "repos" / "eval_cards_backend_pipeline"
EXPECTED_COMMIT = "9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
RAW = HERE / "raw"
RESULTS = HERE / "results"
RAW.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)

def error(msg: str):
    payload = {"test_id": "T02_comparability_boundary_robustness", "verdict": "ERROR", "error": msg}
    (RESULTS/"summary.json").write_text(json.dumps(payload, indent=2)+"\n", encoding="utf-8")
    print("T02 ERROR")
    print(msg)
    raise SystemExit(2)

try:
    head = subprocess.check_output(["git","-C",str(BACKEND),"rev-parse","HEAD"], text=True).strip()
except Exception as exc:
    error(f"Cannot resolve backend HEAD: {exc}")
if head != EXPECTED_COMMIT:
    error(f"Backend HEAD mismatch: {head}")

sys.path.insert(0, str(BACKEND/"src"))
try:
    from eval_card_backend.signals.comparability import (
        compute_variant_divergence_py,
        compute_cross_party_divergence_py,
        compute_threshold,
    )
except Exception as exc:
    error(f"Cannot import frozen comparability functions: {type(exc).__name__}: {exc}")

os.environ.pop("DIVERGENCE_THRESHOLD_FACTOR", None)

fixture_path = HERE/"fixtures.json"
fx = json.loads(fixture_path.read_text(encoding="utf-8"))

def row(eid: str, score: float, org: str, temp: float) -> dict[str, Any]:
    return {
        "fact_id": eid,
        "evaluation_id": eid,
        "score": score,
        "generation_args": {"temperature": temp, "max_tokens": 100},
        "evaluator_relationship": "third_party",
        "source_organization_name": org,
    }

records = []
for basis in fx["threshold_bases"]:
    metric = basis["metric_config"]
    exact_threshold = Decimal(basis["threshold"])
    prod_threshold, prod_basis = compute_threshold(metric)

    for case in basis["cases"]:
        a_dec = Decimal(case["a"])
        b_dec = Decimal(case["b"])
        exact_delta = b_dec - a_dec
        relation = case["relation"]
        if relation == "boundary":
            expected = False
            assert exact_delta == exact_threshold, (case["id"], exact_delta, exact_threshold)
        elif relation == "below":
            expected = False
            assert exact_delta < exact_threshold, (case["id"], exact_delta, exact_threshold)
        elif relation == "above":
            expected = True
            assert exact_delta > exact_threshold, (case["id"], exact_delta, exact_threshold)
        else:
            error(f"Unknown relation: {relation}")

        a = float(case["a"])
        b = float(case["b"])

        variant = compute_variant_divergence_py(
            [row("a", a, "Org A", 0.0), row("b", b, "Org A", 1.0)],
            metric,
        )
        cross = compute_cross_party_divergence_py(
            [row("a", a, "Org A", 0.0), row("b", b, "Org B", 0.0)],
            metric,
        )

        for path_name, out, flag_key in [
            ("variant", variant, "has_variant_divergence"),
            ("cross_party", cross, "has_cross_party_divergence"),
        ]:
            actual = None if out is None else bool(out[flag_key])
            records.append({
                "case_id": case["id"],
                "basis_id": basis["id"],
                "production_basis": prod_basis,
                "path": path_name,
                "relation": relation,
                "score_a_decimal": case["a"],
                "score_b_decimal": case["b"],
                "score_a_float_repr": repr(a),
                "score_b_float_repr": repr(b),
                "exact_decimal_delta": str(exact_delta),
                "exact_decimal_threshold": str(exact_threshold),
                "production_divergence_repr": None if out is None else repr(out["divergence_magnitude"]),
                "production_threshold_repr": repr(prod_threshold),
                "expected_flag": expected,
                "actual_flag": actual,
                "status": "PASS" if actual == expected else "FAIL",
            })

raw_path = RAW/"cases.jsonl"
with raw_path.open("w", encoding="utf-8", newline="\n") as f:
    for r in records:
        f.write(json.dumps(r, sort_keys=True, ensure_ascii=True)+"\n")

fails = [r for r in records if r["status"]=="FAIL"]
by_basis = {}
by_path = {}
for r in records:
    b = by_basis.setdefault(r["basis_id"], {"total":0,"pass":0,"fail":0})
    p = by_path.setdefault(r["path"], {"total":0,"pass":0,"fail":0})
    for d in [b,p]:
        d["total"] += 1
        d["pass" if r["status"]=="PASS" else "fail"] += 1

verdict = "REFUTED" if fails else "CONFIRMED"
summary = {
    "test_id": "T02_comparability_boundary_robustness",
    "backend_commit": head,
    "verdict": verdict,
    "case_count": len(records),
    "pass_count": len(records)-len(fails),
    "fail_count": len(fails),
    "boundary_fail_count": sum(r["status"]=="FAIL" and r["relation"]=="boundary" for r in records),
    "below_fail_count": sum(r["status"]=="FAIL" and r["relation"]=="below" for r in records),
    "above_fail_count": sum(r["status"]=="FAIL" and r["relation"]=="above" for r in records),
    "by_basis": by_basis,
    "by_path": by_path,
    "limitations": [
        "This test does not estimate real-corpus prevalence.",
        "This test does not establish product-level severity.",
        "This test tests exact decimal relations mapped through production float arithmetic.",
    ],
}
(RESULTS/"summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True)+"\n", encoding="utf-8")

print("T02 COMPLETE")
print(f"verdict={verdict}")
print(f"cases={summary['case_count']}")
print(f"pass={summary['pass_count']}")
print(f"fail={summary['fail_count']}")
print(f"boundary_fail={summary['boundary_fail_count']}")
print(f"below_fail={summary['below_fail_count']}")
print(f"above_fail={summary['above_fail_count']}")
for k,v in sorted(by_basis.items()):
    print(f"{k}: total={v['total']} pass={v['pass']} fail={v['fail']}")
for k,v in sorted(by_path.items()):
    print(f"{k}: total={v['total']} pass={v['pass']} fail={v['fail']}")
print(r"raw=tests\T02_comparability_boundary_robustness\raw\cases.jsonl")
print(r"summary=tests\T02_comparability_boundary_robustness\results\summary.json")
