from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
from decimal import Decimal
from pathlib import Path
from statistics import median
from typing import Any

HERE = Path(__file__).resolve().parent
AUDIT_ROOT = HERE.parents[1]
BACKEND = AUDIT_ROOT / "freeze" / "repos" / "eval_cards_backend_pipeline"
REGISTRY_REPO_CANDIDATES = [
    AUDIT_ROOT / "freeze" / "repos" / "eval-card-registry",
    AUDIT_ROOT / "freeze" / "repos" / "evalcard-registry",
]
EXPECTED_COMMIT = "9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
FACT = HERE / "raw" / "fact_results_stage_f.parquet"
RAW_GROUPS = HERE / "raw" / "group_scan.jsonl"
RAW_MISMATCH = HERE / "raw" / "mismatches.jsonl"
SUMMARY = HERE / "results" / "summary.json"

def fail(msg: str):
    SUMMARY.write_text(
        json.dumps({"test_id":"T03_corpus_boundary_impact","verdict":"ERROR","error":msg}, indent=2)+"\n",
        encoding="utf-8",
    )
    print("T03 ANALYSIS ERROR")
    print(msg)
    raise SystemExit(2)

try:
    head = subprocess.check_output(["git","-C",str(BACKEND),"rev-parse","HEAD"], text=True).strip()
except Exception as exc:
    fail(f"Cannot resolve backend HEAD: {exc}")
if head != EXPECTED_COMMIT:
    fail(f"Backend HEAD mismatch: {head}")
if not FACT.exists():
    fail("Missing Stage F fact_results evidence; run run_pipeline.py first.")

registry_repo = next((p for p in REGISTRY_REPO_CANDIDATES if p.exists()), None)
if registry_repo is not None:
    sys.path.insert(0, str(registry_repo/"packages"/"eval-entity-resolver"/"src"))
sys.path.insert(0, str(BACKEND/"src"))

try:
    import duckdb
    from eval_card_backend.signals.comparability import normalize_org_name
except Exception as exc:
    fail(f"Analysis import failure: {type(exc).__name__}: {exc}")

os.environ.pop("DIVERGENCE_THRESHOLD_FACTOR", None)

con = duckdb.connect()
fact_sql = FACT.as_posix().replace("'", "''")
cols = {
    r[0] for r in con.execute(
        f"DESCRIBE SELECT * FROM read_parquet('{fact_sql}')"
    ).fetchall()
}

required = {
    "comparability_group_id","fact_id","score","org_raw",
    "metric_unit","min_score","max_score",
    "has_variant_divergence","variant_divergence_magnitude",
    "variant_divergence_threshold","variant_threshold_basis",
    "has_cross_party_divergence","cross_party_divergence_magnitude",
    "cross_party_divergence_threshold","cross_party_threshold_basis",
    "model_aggregation_key","benchmark_key","slice_key","metric_key",
}
missing = sorted(required - cols)
if missing:
    fail(f"Stage F schema missing required columns: {missing}")

optional_exprs = []
for c in ["evaluation_id","source_record_path","result_idx","evaluation_result_id"]:
    optional_exprs.append(c if c in cols else f"NULL AS {c}")

query = f"""
SELECT
    comparability_group_id,
    fact_id,
    model_aggregation_key,
    benchmark_key,
    slice_key,
    metric_key,
    score,
    org_raw,
    metric_unit,
    min_score,
    max_score,
    has_variant_divergence,
    variant_divergence_magnitude,
    variant_divergence_threshold,
    variant_threshold_basis,
    has_cross_party_divergence,
    cross_party_divergence_magnitude,
    cross_party_divergence_threshold,
    cross_party_threshold_basis,
    {", ".join(optional_exprs)}
FROM read_parquet('{fact_sql}')
WHERE comparability_group_id IS NOT NULL
ORDER BY comparability_group_id, fact_id
"""

cur = con.execute(query)
names = [d[0] for d in cur.description]

def D(v: Any) -> Decimal:
    return Decimal(str(v))

def exact_threshold(rows: list[dict[str,Any]]) -> tuple[Decimal,str]:
    units = [r["metric_unit"] for r in rows if r["metric_unit"] is not None]
    unit = max(units) if units else None

    mins = [r["min_score"] for r in rows if r["min_score"] is not None]
    maxs = [r["max_score"] for r in rows if r["max_score"] is not None]
    min_v = max(mins) if mins else None
    max_v = max(maxs) if maxs else None

    if unit == "proportion":
        return Decimal("0.05"), "proportion"
    if unit == "percent":
        return Decimal("5.0"), "percent"
    if min_v is not None and max_v is not None and float(max_v) > float(min_v):
        return Decimal("0.05") * (D(max_v) - D(min_v)), "range_5pct"
    return Decimal("0.05"), "fallback_default"

def dec_median(values: list[Decimal]) -> Decimal:
    vals = sorted(values)
    n = len(vals)
    if n == 0:
        raise ValueError("median of empty list")
    if n % 2:
        return vals[n//2]
    return (vals[n//2-1] + vals[n//2]) / Decimal(2)

counts = {
    "fact_rows_scanned": 0,
    "comparability_groups": 0,
    "variant_applicable_groups": 0,
    "cross_party_applicable_groups": 0,
    "variant_production_true": 0,
    "cross_party_production_true": 0,
    "variant_decimal_true": 0,
    "cross_party_decimal_true": 0,
    "variant_mismatches": 0,
    "cross_party_mismatches": 0,
    "exact_boundary_mismatches": 0,
    "nonboundary_mismatches": 0,
    "production_true_decimal_false": 0,
    "production_false_decimal_true": 0,
    "group_consistency_errors": 0,
}
by_basis = {}
mismatches = []

def one_value(rows, key):
    vals = {r[key] for r in rows}
    if len(vals) > 1:
        counts["group_consistency_errors"] += 1
        return None, False
    return next(iter(vals)), True

def emit_group(rows: list[dict[str,Any]], out_f, mm_f):
    counts["comparability_groups"] += 1
    counts["fact_rows_scanned"] += len(rows)

    group_id = rows[0]["comparability_group_id"]
    threshold_dec, oracle_basis = exact_threshold(rows)

    identity = {
        "comparability_group_id": group_id,
        "model_aggregation_key": rows[0]["model_aggregation_key"],
        "benchmark_key": rows[0]["benchmark_key"],
        "slice_key": rows[0]["slice_key"],
        "metric_key": rows[0]["metric_key"],
        "row_count": len(rows),
    }

    group_record = {**identity, "oracle_threshold": str(threshold_dec), "oracle_basis": oracle_basis}

    # Variant
    vflag, vok = one_value(rows, "has_variant_divergence")
    if vok and vflag is not None:
        counts["variant_applicable_groups"] += 1
        prod = bool(vflag)
        if prod:
            counts["variant_production_true"] += 1
        scores = [D(r["score"]) for r in rows]
        exact_div = max(scores) - min(scores)
        expected = exact_div > threshold_dec
        if expected:
            counts["variant_decimal_true"] += 1
        relation = "boundary" if exact_div == threshold_dec else ("above" if exact_div > threshold_dec else "below")
        mismatch = prod != expected
        group_record["variant"] = {
            "production_flag": prod,
            "decimal_flag": expected,
            "exact_divergence": str(exact_div),
            "relation": relation,
            "production_divergence": rows[0]["variant_divergence_magnitude"],
            "production_threshold": rows[0]["variant_divergence_threshold"],
            "production_basis": rows[0]["variant_threshold_basis"],
            "mismatch": mismatch,
        }
        if mismatch:
            counts["variant_mismatches"] += 1
            if relation == "boundary":
                counts["exact_boundary_mismatches"] += 1
            else:
                counts["nonboundary_mismatches"] += 1
            if prod and not expected:
                counts["production_true_decimal_false"] += 1
            elif (not prod) and expected:
                counts["production_false_decimal_true"] += 1
            item = {
                **identity,
                "path": "variant",
                "oracle_basis": oracle_basis,
                "oracle_threshold": str(threshold_dec),
                "exact_divergence": str(exact_div),
                "relation": relation,
                "production_flag": prod,
                "decimal_flag": expected,
                "production_divergence": rows[0]["variant_divergence_magnitude"],
                "production_threshold": rows[0]["variant_divergence_threshold"],
                "rows": [
                    {
                        "fact_id": r["fact_id"],
                        "score": r["score"],
                        "score_decimal": str(D(r["score"])),
                        "org_raw": r["org_raw"],
                        "evaluation_id": r.get("evaluation_id"),
                        "source_record_path": r.get("source_record_path"),
                        "result_idx": r.get("result_idx"),
                        "evaluation_result_id": r.get("evaluation_result_id"),
                    } for r in rows
                ],
            }
            mm_f.write(json.dumps(item, ensure_ascii=True, sort_keys=True)+"\n")

    # Cross-party
    xflag, xok = one_value(rows, "has_cross_party_divergence")
    if xok and xflag is not None:
        counts["cross_party_applicable_groups"] += 1
        prod = bool(xflag)
        if prod:
            counts["cross_party_production_true"] += 1

        by_org = {}
        for r in rows:
            org = normalize_org_name(r["org_raw"])
            if org:
                by_org.setdefault(org, []).append(D(r["score"]))
        medians = {org: dec_median(vals) for org, vals in by_org.items()}
        if len(medians) < 2:
            counts["group_consistency_errors"] += 1
            group_record["cross_party"] = {
                "analysis_error": "production applicable but decimal reconstruction has fewer than two named organisations"
            }
        else:
            exact_div = max(medians.values()) - min(medians.values())
            expected = exact_div > threshold_dec
            if expected:
                counts["cross_party_decimal_true"] += 1
            relation = "boundary" if exact_div == threshold_dec else ("above" if exact_div > threshold_dec else "below")
            mismatch = prod != expected
            group_record["cross_party"] = {
                "production_flag": prod,
                "decimal_flag": expected,
                "exact_divergence": str(exact_div),
                "relation": relation,
                "production_divergence": rows[0]["cross_party_divergence_magnitude"],
                "production_threshold": rows[0]["cross_party_divergence_threshold"],
                "production_basis": rows[0]["cross_party_threshold_basis"],
                "organization_count_decimal": len(medians),
                "org_medians_decimal": {k: str(v) for k,v in sorted(medians.items())},
                "mismatch": mismatch,
            }
            if mismatch:
                counts["cross_party_mismatches"] += 1
                if relation == "boundary":
                    counts["exact_boundary_mismatches"] += 1
                else:
                    counts["nonboundary_mismatches"] += 1
                if prod and not expected:
                    counts["production_true_decimal_false"] += 1
                elif (not prod) and expected:
                    counts["production_false_decimal_true"] += 1
                item = {
                    **identity,
                    "path": "cross_party",
                    "oracle_basis": oracle_basis,
                    "oracle_threshold": str(threshold_dec),
                    "exact_divergence": str(exact_div),
                    "relation": relation,
                    "production_flag": prod,
                    "decimal_flag": expected,
                    "production_divergence": rows[0]["cross_party_divergence_magnitude"],
                    "production_threshold": rows[0]["cross_party_divergence_threshold"],
                    "org_medians_decimal": {k: str(v) for k,v in sorted(medians.items())},
                    "rows": [
                        {
                            "fact_id": r["fact_id"],
                            "score": r["score"],
                            "score_decimal": str(D(r["score"])),
                            "org_raw": r["org_raw"],
                            "evaluation_id": r.get("evaluation_id"),
                            "source_record_path": r.get("source_record_path"),
                            "result_idx": r.get("result_idx"),
                            "evaluation_result_id": r.get("evaluation_result_id"),
                        } for r in rows
                    ],
                }
                mm_f.write(json.dumps(item, ensure_ascii=True, sort_keys=True)+"\n")

    b = by_basis.setdefault(oracle_basis, {
        "groups": 0,
        "variant_mismatches": 0,
        "cross_party_mismatches": 0,
        "exact_boundary_mismatches": 0,
    })
    b["groups"] += 1
    if group_record.get("variant",{}).get("mismatch"):
        b["variant_mismatches"] += 1
        if group_record["variant"]["relation"] == "boundary":
            b["exact_boundary_mismatches"] += 1
    if group_record.get("cross_party",{}).get("mismatch"):
        b["cross_party_mismatches"] += 1
        if group_record["cross_party"]["relation"] == "boundary":
            b["exact_boundary_mismatches"] += 1

    out_f.write(json.dumps(group_record, ensure_ascii=True, sort_keys=True)+"\n")

current_id = None
group_rows = []

with RAW_GROUPS.open("w", encoding="utf-8", newline="\n") as out_f, \
     RAW_MISMATCH.open("w", encoding="utf-8", newline="\n") as mm_f:
    while True:
        batch = cur.fetchmany(10000)
        if not batch:
            break
        for tup in batch:
            r = dict(zip(names, tup))
            gid = r["comparability_group_id"]
            if current_id is None:
                current_id = gid
            if gid != current_id:
                emit_group(group_rows, out_f, mm_f)
                group_rows = []
                current_id = gid
            group_rows.append(r)
    if group_rows:
        emit_group(group_rows, out_f, mm_f)

total_mismatches = counts["variant_mismatches"] + counts["cross_party_mismatches"]

if counts["group_consistency_errors"] > 0:
    verdict = "INCONCLUSIVE"
elif counts["exact_boundary_mismatches"] > 0:
    verdict = "CONFIRMED"
else:
    verdict = "REFUTED"

capture_path = HERE/"raw"/"pipeline_capture.json"
capture = json.loads(capture_path.read_text(encoding="utf-8")) if capture_path.exists() else {}

summary = {
    "test_id": "T03_corpus_boundary_impact",
    "backend_commit": head,
    "claim": "At least one exact-boundary float classification mismatch exists in the full frozen Stage F corpus.",
    "verdict": verdict,
    **counts,
    "total_mismatches": total_mismatches,
    "by_basis": by_basis,
    "pipeline_capture": capture,
    "evidence": {
        "fact_results_sha256": hashlib.sha256(FACT.read_bytes()).hexdigest(),
        "group_scan_sha256": hashlib.sha256(RAW_GROUPS.read_bytes()).hexdigest(),
        "mismatches_sha256": hashlib.sha256(RAW_MISMATCH.read_bytes()).hexdigest(),
    },
    "limitations": [
        "Decimal(str(score)) uses the canonical stored score representation, not the original source JSON lexical token.",
        "Any affected real group must be traced to frozen source records before a final public product-level finding.",
        "The verdict is snapshot-bound to this frozen corpus and Stage F implementation.",
    ],
}
SUMMARY.write_text(
    json.dumps(summary, indent=2, ensure_ascii=True, sort_keys=True)+"\n",
    encoding="utf-8",
)

print("T03 COMPLETE")
print(f"verdict={verdict}")
for k in [
    "fact_rows_scanned",
    "comparability_groups",
    "variant_applicable_groups",
    "cross_party_applicable_groups",
    "variant_production_true",
    "variant_decimal_true",
    "cross_party_production_true",
    "cross_party_decimal_true",
    "variant_mismatches",
    "cross_party_mismatches",
    "exact_boundary_mismatches",
    "nonboundary_mismatches",
    "production_true_decimal_false",
    "production_false_decimal_true",
    "group_consistency_errors",
]:
    print(f"{k}={counts[k]}")
for basis, vals in sorted(by_basis.items()):
    print(
        f"{basis}: groups={vals['groups']} "
        f"variant_mismatches={vals['variant_mismatches']} "
        f"cross_party_mismatches={vals['cross_party_mismatches']} "
        f"exact_boundary_mismatches={vals['exact_boundary_mismatches']}"
    )
print(r"raw_groups=tests\T03_corpus_boundary_impact\raw\group_scan.jsonl")
print(r"raw_mismatches=tests\T03_corpus_boundary_impact\raw\mismatches.jsonl")
print(r"summary=tests\T03_corpus_boundary_impact\results\summary.json")
