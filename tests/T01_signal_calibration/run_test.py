from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

TEST_DIR = Path(__file__).resolve().parent
AUDIT_ROOT = TEST_DIR.parents[1]
BACKEND = AUDIT_ROOT / "freeze" / "repos" / "eval_cards_backend_pipeline"
EXPECTED_COMMIT = "9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
RAW_DIR = TEST_DIR / "raw"
RESULTS_DIR = TEST_DIR / "results"
RAW_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

def fail_error(message: str) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    payload = {"test_id": "T01_signal_calibration", "verdict": "ERROR", "error": message}
    (RESULTS_DIR / "summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("T01 ERROR")
    print(message)
    raise SystemExit(2)

def git_head(repo: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    except Exception as exc:
        fail_error(f"Cannot resolve frozen backend HEAD: {exc}")

if not BACKEND.exists():
    fail_error(f"Frozen backend repository missing: {BACKEND}")

head = git_head(BACKEND)
if head != EXPECTED_COMMIT:
    fail_error(f"Frozen backend HEAD mismatch: {head}")

verify_freeze = AUDIT_ROOT / "freeze" / "VERIFY_FREEZE.txt"
verify_baselines = AUDIT_ROOT / "VERIFY_BASELINES.txt"

for path, required in [
    (verify_freeze, ["bad=0", "missing=0"]),
    (verify_baselines, ["bad=0"]),
]:
    if not path.exists():
        fail_error(f"Required prior-gate evidence missing: {path}")
    text = path.read_text(encoding="utf-8-sig")
    for marker in required:
        if marker not in text:
            fail_error(f"Prior gate is not clean: {path} lacks {marker}")

sys.path.insert(0, str(BACKEND / "src"))

try:
    from eval_card_backend.signals.reproducibility import required_repro_fields
    from eval_card_backend.signals.completeness import (
        COMPLETENESS_FIELD_SET,
        compute_completeness_py,
    )
    from eval_card_backend.signals.comparability import (
        compute_cross_party_divergence_py,
        compute_variant_divergence_py,
        normalize_org_name,
    )
    from eval_card_backend.signals.setup import differing_setup_fields
except Exception as exc:
    fail_error(f"Cannot import frozen signal primitives: {type(exc).__name__}: {exc}")

os.environ.pop("DIVERGENCE_THRESHOLD_FACTOR", None)

source_paths = [
    "src/eval_card_backend/signals/reproducibility.py",
    "src/eval_card_backend/signals/completeness.py",
    "src/eval_card_backend/signals/comparability.py",
    "src/eval_card_backend/signals/setup.py",
    "src/eval_card_backend/canonicalise/thresholds.py",
    "src/eval_card_backend/canonicalise/stages.py",
    "src/eval_card_backend/registry/completeness_fields.json",
]
source_hashes = {}
for rel in source_paths:
    p = BACKEND / rel
    if not p.exists():
        fail_error(f"Frozen source file missing: {rel}")
    source_hashes[rel] = hashlib.sha256(p.read_bytes()).hexdigest()

(TEST_DIR / "raw" / "source_hashes.json").write_text(
    json.dumps({"backend_commit": head, "files": source_hashes}, indent=2) + "\n",
    encoding="utf-8",
)

cases: list[dict[str, Any]] = []

def same(a: Any, b: Any, tol: float = 1e-12) -> bool:
    if isinstance(a, float) or isinstance(b, float):
        try:
            return math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=tol)
        except Exception:
            return False
    return a == b

def add_case(
    case_id: str,
    signal: str,
    description: str,
    expected: Any,
    actual: Any,
    status_if_unavailable: str | None = None,
) -> None:
    if status_if_unavailable:
        status = status_if_unavailable
        passed = None
    else:
        passed = same(actual, expected)
        status = "PASS" if passed else "FAIL"
    cases.append({
        "case_id": case_id,
        "signal": signal,
        "description": description,
        "expected": expected,
        "actual": actual,
        "status": status,
        "passed": passed,
    })

# ------------------------------------------------------------------
# R — reproducibility
# ------------------------------------------------------------------

def repro_state(agentic: bool, values: dict[str, Any]) -> dict[str, Any]:
    required = list(required_repro_fields(agentic))
    missing = [f for f in required if values.get(f) is None]
    return {"required": required, "missing": missing, "gap": bool(missing)}

add_case(
    "R1", "reproducibility", "Non-agentic active fields fully populated.",
    {"required": ["temperature", "max_tokens"], "missing": [], "gap": False},
    repro_state(False, {"temperature": 0.0, "max_tokens": 2048}),
)
add_case(
    "R2", "reproducibility", "Non-agentic temperature missing.",
    {"required": ["temperature", "max_tokens"], "missing": ["temperature"], "gap": True},
    repro_state(False, {"temperature": None, "max_tokens": 2048}),
)
add_case(
    "R3", "reproducibility", "Non-agentic max_tokens missing.",
    {"required": ["temperature", "max_tokens"], "missing": ["max_tokens"], "gap": True},
    repro_state(False, {"temperature": 0.0, "max_tokens": None}),
)
add_case(
    "R4", "reproducibility", "Agentic active fields fully populated.",
    {"required": ["temperature", "max_tokens", "eval_plan", "eval_limits"], "missing": [], "gap": False},
    repro_state(True, {
        "temperature": 0.0, "max_tokens": 2048,
        "eval_plan": {"steps": 2}, "eval_limits": {"turns": 4},
    }),
)
add_case(
    "R5", "reproducibility", "Agentic eval_plan missing.",
    {"required": ["temperature", "max_tokens", "eval_plan", "eval_limits"], "missing": ["eval_plan"], "gap": True},
    repro_state(True, {
        "temperature": 0.0, "max_tokens": 2048,
        "eval_plan": None, "eval_limits": {"turns": 4},
    }),
)
r6a = repro_state(False, {
    "temperature": 0.0, "max_tokens": 2048,
    "top_p": 0.1, "prompt_template": "A",
})
r6b = repro_state(False, {
    "temperature": 0.0, "max_tokens": 2048,
    "top_p": 0.99, "prompt_template": "B",
})
add_case("R6", "reproducibility", "Nuisance top_p/prompt_template changes do not affect active rule.", r6a, r6b)

# ------------------------------------------------------------------
# C — completeness
# ------------------------------------------------------------------

def set_path(obj: dict, path: str, value: Any) -> None:
    parts = path.split(".")
    cur = obj
    for part in parts[:-1]:
        cur = cur.setdefault(part, {})
    cur[parts[-1]] = value

def del_path(obj: dict, path: str) -> None:
    parts = path.split(".")
    cur = obj
    for part in parts[:-1]:
        nxt = cur.get(part)
        if not isinstance(nxt, dict):
            return
        cur = nxt
    cur.pop(parts[-1], None)

def build_complete_inputs():
    record = {"autobenchmarkcard": {}, "eee_eval": {"source_metadata": {}}, "evalcards": {}}
    for field in COMPLETENESS_FIELD_SET:
        coverage = field["coverage"]
        if coverage in ("full", "reserved"):
            set_path(record, field["path"], "x")
        elif coverage == "partial":
            for sp in field.get("subitem_paths") or []:
                set_path(record, sp, "x")
    card = record["autobenchmarkcard"]
    sm = record["eee_eval"]["source_metadata"]
    ev = record["evalcards"]
    return card, {
        "source_type": sm.get("source_type"),
        "source_organization_name": sm.get("source_organization_name"),
        "evaluator_relationship": sm.get("evaluator_relationship"),
        "lifecycle_status": ev.get("lifecycle_status"),
        "preregistration_url": ev.get("preregistration_url"),
    }

card_full, kwargs_full = build_complete_inputs()
full = compute_completeness_py(card_full, **kwargs_full)
add_case("C1", "completeness", "All registry-declared fields populated.", 1.0, full["completeness_score"])

empty = compute_completeness_py({}, None, None, None, None, None)
add_case("C2", "completeness", "Empty declared record.", 0.0, empty["completeness_score"])

N = len(COMPLETENESS_FIELD_SET)
full_candidates = [
    f for f in COMPLETENESS_FIELD_SET
    if f.get("coverage") in ("full", "reserved")
]
# Prefer a card field that is not a prefix of another declared field.
all_paths = [f["path"] for f in COMPLETENESS_FIELD_SET]
selected_full = None
for f in full_candidates:
    p = f["path"]
    if p.startswith("autobenchmarkcard.") and not any(q != p and q.startswith(p + ".") for q in all_paths):
        selected_full = f
        break

if selected_full is None:
    add_case("C3", "completeness", "Remove one full declared field.", None, None, "INCONCLUSIVE")
else:
    c = copy.deepcopy(card_full)
    k = copy.deepcopy(kwargs_full)
    rel = selected_full["path"].removeprefix("autobenchmarkcard.")
    del_path(c, rel)
    out = compute_completeness_py(c, **k)
    expected = 1.0 - (1.0 / N)
    add_case("C3", "completeness", f"Remove full field {selected_full['path']}.", expected, out["completeness_score"])

partial_candidates = [f for f in COMPLETENESS_FIELD_SET if f.get("coverage") == "partial" and (f.get("subitem_paths") or [])]
if not partial_candidates:
    add_case("C4", "completeness", "Remove one partial-field subitem.", None, None, "INCONCLUSIVE")
else:
    pf = partial_candidates[0]
    sp = list(pf["subitem_paths"])[0]
    k_count = len(pf["subitem_paths"])
    c = copy.deepcopy(card_full)
    k = copy.deepcopy(kwargs_full)
    if sp.startswith("autobenchmarkcard."):
        del_path(c, sp.removeprefix("autobenchmarkcard."))
    elif sp == "eee_eval.source_metadata.source_type":
        k["source_type"] = None
    elif sp == "eee_eval.source_metadata.source_organization_name":
        k["source_organization_name"] = None
    elif sp == "eee_eval.source_metadata.evaluator_relationship":
        k["evaluator_relationship"] = None
    elif sp == "evalcards.lifecycle_status":
        k["lifecycle_status"] = None
    elif sp == "evalcards.preregistration_url":
        k["preregistration_url"] = None
    else:
        add_case("C4", "completeness", f"Remove partial subitem {sp}.", None, None, "INCONCLUSIVE")
        pf = None
    if pf is not None:
        out = compute_completeness_py(c, **k)
        expected = 1.0 - (1.0 / (N * k_count))
        add_case("C4", "completeness", f"Remove one of {k_count} subitems from {pf['path']}.", expected, out["completeness_score"])

c_nuisance = copy.deepcopy(card_full)
c_nuisance["audit_only_undeclared_field"] = {"value": 999}
nuisance = compute_completeness_py(c_nuisance, **kwargs_full)
add_case("C5", "completeness", "Undeclared extra field is a nuisance mutation.", full["completeness_score"], nuisance["completeness_score"])

# ------------------------------------------------------------------
# P — provenance: source-anchored Stage E / F.1 formula
# ------------------------------------------------------------------

ASCII_WS = re.compile(r"[ \t\n\r\f\v]+")

def stage_f_org_normalize(name: Any) -> str | None:
    if not isinstance(name, str):
        return None
    s = ASCII_WS.sub(" ", name.lower()).strip()
    return s or None

def provenance_fixture(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = [stage_f_org_normalize(r.get("org_raw")) for r in rows]
    distinct = len({x for x in normalized if x is not None})
    out = []
    for row in rows:
        raw_type = row.get("evaluator_relationship")
        provenance_source_type = "unspecified" if raw_type in (None, "other") else raw_type
        out.append({
            "distinct_reporting_orgs": distinct,
            "is_multi_source": distinct > 1,
            "first_party_only": provenance_source_type == "first_party" and distinct == 1,
            "provenance_source_type": provenance_source_type,
        })
    return out

p1 = provenance_fixture([{"org_raw": "Example Org", "evaluator_relationship": "first_party"}])[0]
add_case("P1", "provenance", "One first-party reporting organisation.",
         {"distinct_reporting_orgs": 1, "is_multi_source": False, "first_party_only": True, "provenance_source_type": "first_party"}, p1)

p2 = provenance_fixture([{"org_raw": "Example Org", "evaluator_relationship": "third_party"}])[0]
add_case("P2", "provenance", "One third-party reporting organisation.",
         {"distinct_reporting_orgs": 1, "is_multi_source": False, "first_party_only": False, "provenance_source_type": "third_party"}, p2)

p3 = provenance_fixture([
    {"org_raw": "Org A", "evaluator_relationship": "first_party"},
    {"org_raw": "Org B", "evaluator_relationship": "third_party"},
])
add_case("P3", "provenance", "Two distinct reporting organisations.",
         [
             {"distinct_reporting_orgs": 2, "is_multi_source": True, "first_party_only": False, "provenance_source_type": "first_party"},
             {"distinct_reporting_orgs": 2, "is_multi_source": True, "first_party_only": False, "provenance_source_type": "third_party"},
         ], p3)

p4 = provenance_fixture([
    {"org_raw": "Example Org", "evaluator_relationship": "first_party"},
    {"org_raw": "  example   org  ", "evaluator_relationship": "first_party"},
])
add_case("P4", "provenance", "Case and ASCII-whitespace nuisance collapses to one organisation.",
         [1, 1], [x["distinct_reporting_orgs"] for x in p4])

p5 = provenance_fixture([{"org_raw": "Example Org", "evaluator_relationship": "other"}])[0]
add_case("P5", "provenance", "Stage E collapses source type other to unspecified.", "unspecified", p5["provenance_source_type"])

# ------------------------------------------------------------------
# V / X — comparability
# ------------------------------------------------------------------

metric = {"metric_unit": "proportion"}

def row(eid: str, score: float, org: str, ga: dict[str, Any]) -> dict[str, Any]:
    return {
        "fact_id": eid,
        "evaluation_id": eid,
        "score": score,
        "generation_args": ga,
        "evaluator_relationship": "third_party",
        "source_organization_name": org,
    }

def variant_actual(delta: float):
    rows = [
        row("a", 0.50, "Org A", {"temperature": 0.0, "max_tokens": 100}),
        row("b", 0.50 + delta, "Org A", {"temperature": 1.0, "max_tokens": 100}),
    ]
    return compute_variant_divergence_py(rows, metric)

for cid, delta, expected_flag in [
    ("V1", 0.04, False),
    ("V2", 0.05, False),
    ("V3", 0.050001, True),
]:
    out = variant_actual(delta)
    add_case(
        cid, "comparability",
        f"Variant setup differs; score divergence={delta}.",
        {"applicable": True, "threshold": 0.05, "flag": expected_flag},
        {
            "applicable": out is not None,
            "threshold": None if out is None else out["threshold_used"],
            "flag": None if out is None else out["has_variant_divergence"],
        },
    )

v4rows = [
    row("a", 0.50, "Org A", {"temperature": 0.0, "max_tokens": 100, "seed": 1}),
    row("b", 0.60, "Org A", {"temperature": 0.0, "max_tokens": 100, "seed": 999}),
]
v4 = compute_variant_divergence_py(v4rows, metric)
add_case("V4", "comparability", "Undeclared generation key seed is nuisance; no setup difference.", None, v4)

v5diff = differing_setup_fields([
    {"temperature": 0.0, "max_tokens": 100, "prompt_template": "  hello\r\nworld  "},
    {"temperature": 0.0, "max_tokens": 100, "prompt_template": "hello\nworld"},
])
add_case("V5", "comparability", "Prompt-template cosmetic whitespace normalises away.", [], v5diff)

x1 = compute_cross_party_divergence_py([
    row("a", 0.50, "Org A", {"temperature": 0.0})
], metric)
add_case("X1", "comparability", "One named organisation makes cross-party divergence N/A.", None, x1)

x2 = compute_cross_party_divergence_py([
    row("a", 0.50, "Org A", {"temperature": 0.0}),
    row("b", 0.56, "Org B", {"temperature": 0.0}),
], metric)
add_case(
    "X2", "comparability", "Two organisations separated by 0.06.",
    {"applicable": True, "organization_count": 2, "threshold": 0.05, "flag": True},
    {
        "applicable": x2 is not None,
        "organization_count": None if x2 is None else x2["organization_count"],
        "threshold": None if x2 is None else x2["threshold_used"],
        "flag": None if x2 is None else x2["has_cross_party_divergence"],
    },
)

x3 = compute_cross_party_divergence_py([
    row("a", 0.50, "Example Org", {"temperature": 0.0}),
    row("b", 0.60, "  example   org  ", {"temperature": 0.0}),
], metric)
add_case("X3", "comparability", "Organisation case/whitespace nuisance collapses to one party.", None, x3)

# Raw first, summary second.
raw_path = RAW_DIR / "cases.jsonl"
with raw_path.open("w", encoding="utf-8", newline="\n") as f:
    for case in cases:
        f.write(json.dumps(case, ensure_ascii=True, sort_keys=True) + "\n")

fails = [c for c in cases if c["status"] == "FAIL"]
incs = [c for c in cases if c["status"] == "INCONCLUSIVE"]
errors = [c for c in cases if c["status"] == "ERROR"]

by_signal = {}
for c in cases:
    d = by_signal.setdefault(c["signal"], {"total": 0, "pass": 0, "fail": 0, "inconclusive": 0})
    d["total"] += 1
    if c["status"] == "PASS":
        d["pass"] += 1
    elif c["status"] == "FAIL":
        d["fail"] += 1
    elif c["status"] == "INCONCLUSIVE":
        d["inconclusive"] += 1

if errors:
    verdict = "ERROR"
elif fails:
    verdict = "REFUTED"
elif incs:
    verdict = "INCONCLUSIVE"
else:
    verdict = "CONFIRMED"

summary = {
    "test_id": "T01_signal_calibration",
    "backend_commit": head,
    "claim_scope": "controlled-fixture discrimination and nuisance invariance only",
    "verdict": verdict,
    "case_count": len(cases),
    "pass_count": sum(c["status"] == "PASS" for c in cases),
    "fail_count": len(fails),
    "inconclusive_count": len(incs),
    "by_signal": by_signal,
    "limitations": [
        "A positive result does not establish real-world construct validity.",
        "Provenance is formula-calibrated in T01 and still requires an end-to-end Stage F.1 test.",
        "No corpus-level accuracy or long-tail claim is tested here.",
        "No public-claim scope verdict is produced here.",
    ],
}
(RESULTS_DIR / "summary.json").write_text(
    json.dumps(summary, indent=2, ensure_ascii=True, sort_keys=True) + "\n",
    encoding="utf-8",
)

print("T01 COMPLETE")
print(f"verdict={verdict}")
print(f"cases={len(cases)}")
print(f"pass={summary['pass_count']}")
print(f"fail={summary['fail_count']}")
print(f"inconclusive={summary['inconclusive_count']}")
for sig, counts in sorted(by_signal.items()):
    print(f"{sig}: total={counts['total']} pass={counts['pass']} fail={counts['fail']} inconclusive={counts['inconclusive']}")
print(r"raw=tests\T01_signal_calibration\raw\cases.jsonl")
print(r"summary=tests\T01_signal_calibration\results\summary.json")
