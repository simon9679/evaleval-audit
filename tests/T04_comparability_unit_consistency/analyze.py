from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
AUDIT_ROOT = HERE.parents[1]
T03 = AUDIT_ROOT / "tests" / "T03_corpus_boundary_impact"
FACT = T03 / "raw" / "fact_results_stage_f.parquet"
BACKEND = AUDIT_ROOT / "freeze" / "repos" / "eval_cards_backend_pipeline"
REGISTRY_REPO_CANDIDATES = [
    AUDIT_ROOT / "freeze" / "repos" / "eval-card-registry",
    AUDIT_ROOT / "freeze" / "repos" / "evalcard-registry",
]

EXPECTED_COMMIT = "9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
EXPECTED_FACT_SHA = "e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"
EXPECTED_FACT_ROWS = 209382
EXPECTED_COMPARABILITY_GROUPS = 93495
EXPECTED_WARNING_ROOT_GROUPS = 1425

RAW_WARNING = HERE / "raw" / "warning_root_groups.jsonl"
RAW_MIXED = HERE / "raw" / "mixed_unit_groups.jsonl"
RAW_SENSITIVE = HERE / "raw" / "classification_sensitive_paths.jsonl"
RAW_ERRORS = HERE / "raw" / "integrity_errors.jsonl"
SUMMARY = HERE / "results" / "summary.json"
RESULT_ANALYSIS = HERE / "results" / "RESULT_ANALYSIS.md"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def hard_error(msg: str):
    SUMMARY.parent.mkdir(exist_ok=True)
    SUMMARY.write_text(
        json.dumps(
            {
                "test_id": "T04_comparability_unit_consistency",
                "verdict": "ERROR",
                "error": msg,
            },
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )
    print("T04 ERROR")
    print(msg)
    raise SystemExit(2)

if not (HERE / "raw" / "preflight.json").exists():
    hard_error("Missing T04 preflight evidence; run preflight.py first.")

try:
    head = subprocess.check_output(
        ["git", "-C", str(BACKEND), "rev-parse", "HEAD"], text=True
    ).strip()
except Exception as exc:
    hard_error(f"Cannot resolve backend HEAD: {type(exc).__name__}: {exc}")
if head != EXPECTED_COMMIT:
    hard_error(f"Backend HEAD mismatch: {head}")

if not FACT.exists():
    hard_error("Missing T03 Stage F parquet.")
if sha256(FACT) != EXPECTED_FACT_SHA:
    hard_error("T03 Stage F parquet SHA-256 mismatch.")

registry_repo = next((p for p in REGISTRY_REPO_CANDIDATES if p.exists()), None)
if registry_repo is not None:
    sys.path.insert(0, str(registry_repo / "packages" / "eval-entity-resolver" / "src"))
sys.path.insert(0, str(BACKEND / "src"))

try:
    import duckdb
    from eval_card_backend.canonicalise.thresholds import compute_threshold
except Exception as exc:
    hard_error(f"Analysis import failure: {type(exc).__name__}: {exc}")

os.environ.pop("DIVERGENCE_THRESHOLD_FACTOR", None)

con = duckdb.connect()
fact_sql = FACT.as_posix().replace("'", "''")
cols = {
    r[0]
    for r in con.execute(
        f"DESCRIBE SELECT * FROM read_parquet('{fact_sql}')"
    ).fetchall()
}
required = {
    "comparability_group_id",
    "fact_id",
    "model_aggregation_key",
    "benchmark_key",
    "slice_key",
    "metric_key",
    "metric_unit",
    "min_score",
    "max_score",
    "has_variant_divergence",
    "variant_divergence_magnitude",
    "variant_divergence_threshold",
    "variant_threshold_basis",
    "has_cross_party_divergence",
    "cross_party_divergence_magnitude",
    "cross_party_divergence_threshold",
    "cross_party_threshold_basis",
}
missing = sorted(required - cols)
if missing:
    hard_error(f"Stage F schema missing required columns: {missing}")

optional_cols = [
    c
    for c in ["evaluation_id", "source_record_path", "result_idx", "evaluation_result_id"]
    if c in cols
]

fact_rows = con.execute(
    f"SELECT COUNT(*) FROM read_parquet('{fact_sql}')"
).fetchone()[0]
group_count = con.execute(
    f"""
    SELECT COUNT(DISTINCT comparability_group_id)
    FROM read_parquet('{fact_sql}')
    WHERE comparability_group_id IS NOT NULL
    """
).fetchone()[0]

integrity_errors: list[dict[str, Any]] = []
if fact_rows != EXPECTED_FACT_ROWS:
    integrity_errors.append(
        {"type": "fact_row_count", "got": fact_rows, "expected": EXPECTED_FACT_ROWS}
    )
if group_count != EXPECTED_COMPARABILITY_GROUPS:
    integrity_errors.append(
        {
            "type": "comparability_group_count",
            "got": group_count,
            "expected": EXPECTED_COMPARABILITY_GROUPS,
        }
    )

# Reconstruct the exact population counted by the production Stage F warning:
# root-collapsed (model, benchmark, metric), deliberately omitting slice.
warning_query = f"""
SELECT
    model_aggregation_key,
    benchmark_key,
    metric_key,
    list_sort(list_distinct(list(metric_unit) FILTER (WHERE metric_unit IS NOT NULL))) AS units,
    COUNT(DISTINCT metric_unit) FILTER (WHERE metric_unit IS NOT NULL) AS unit_count,
    COUNT(DISTINCT slice_key) AS slice_count,
    COUNT(*) AS row_count
FROM read_parquet('{fact_sql}')
WHERE comparability_group_id IS NOT NULL
GROUP BY 1,2,3
HAVING COUNT(DISTINCT metric_unit) FILTER (WHERE metric_unit IS NOT NULL) > 1
ORDER BY 1,2,3
"""
warning_rows = con.execute(warning_query).fetchall()
warning_names = [d[0] for d in con.description]
warning_records = [dict(zip(warning_names, r)) for r in warning_rows]

with RAW_WARNING.open("w", encoding="utf-8", newline="\n") as f:
    for r in warning_records:
        f.write(json.dumps(r, ensure_ascii=True, sort_keys=True) + "\n")

warning_root_count = len(warning_records)
if warning_root_count != EXPECTED_WARNING_ROOT_GROUPS:
    integrity_errors.append(
        {
            "type": "warning_root_count_reconstruction",
            "got": warning_root_count,
            "expected": EXPECTED_WARNING_ROOT_GROUPS,
        }
    )

warning_root_keys = {
    (r["model_aggregation_key"], r["benchmark_key"], r["metric_key"])
    for r in warning_records
}

select_cols = [
    "comparability_group_id",
    "fact_id",
    "model_aggregation_key",
    "benchmark_key",
    "slice_key",
    "metric_key",
    "metric_unit",
    "min_score",
    "max_score",
    "has_variant_divergence",
    "variant_divergence_magnitude",
    "variant_divergence_threshold",
    "variant_threshold_basis",
    "has_cross_party_divergence",
    "cross_party_divergence_magnitude",
    "cross_party_divergence_threshold",
    "cross_party_threshold_basis",
] + optional_cols

cur = con.execute(
    f"""
    SELECT {", ".join(select_cols)}
    FROM read_parquet('{fact_sql}')
    WHERE comparability_group_id IS NOT NULL
    ORDER BY comparability_group_id, fact_id
    """
)
names = [d[0] for d in cur.description]

counts = {
    "fact_rows_scanned": 0,
    "comparability_groups_scanned": 0,
    "warning_root_groups": warning_root_count,
    "actual_mixed_unit_groups": 0,
    "warning_roots_with_actual_mixed_group": 0,
    "warning_roots_cross_slice_only": 0,
    "variant_eligible_paths": 0,
    "cross_party_eligible_paths": 0,
    "threshold_sensitive_groups": 0,
    "classification_sensitive_groups": 0,
    "classification_sensitive_paths": 0,
    "variant_classification_sensitive_paths": 0,
    "cross_party_classification_sensitive_paths": 0,
    "production_reconstruction_errors": 0,
    "group_consistency_errors": 0,
}

unit_patterns = Counter()
actual_mixed_root_keys = set()

def one_value(rows: list[dict[str, Any]], key: str):
    vals = {r[key] for r in rows}
    if len(vals) != 1:
        counts["group_consistency_errors"] += 1
        integrity_errors.append(
            {
                "type": "group_field_not_constant",
                "group_id": rows[0]["comparability_group_id"],
                "field": key,
                "values": sorted(repr(v) for v in vals),
            }
        )
        return None, False
    return next(iter(vals)), True

def float_same(a: Any, b: Any) -> bool:
    if a is None or b is None:
        return a is b
    return math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=1e-12)

def source_rows(rows):
    out = []
    for r in rows:
        rec = {
            "fact_id": r["fact_id"],
            "metric_unit": r["metric_unit"],
            "min_score": r["min_score"],
            "max_score": r["max_score"],
        }
        for c in optional_cols:
            rec[c] = r.get(c)
        out.append(rec)
    return out

def analyze_path(rows, path, thresholds):
    if path == "variant":
        flag_key = "has_variant_divergence"
        div_key = "variant_divergence_magnitude"
        threshold_key = "variant_divergence_threshold"
        basis_key = "variant_threshold_basis"
        counts["variant_eligible_paths"] += 1
    else:
        flag_key = "has_cross_party_divergence"
        div_key = "cross_party_divergence_magnitude"
        threshold_key = "cross_party_divergence_threshold"
        basis_key = "cross_party_threshold_basis"
        counts["cross_party_eligible_paths"] += 1

    flag, ok1 = one_value(rows, flag_key)
    div, ok2 = one_value(rows, div_key)
    prod_threshold, ok3 = one_value(rows, threshold_key)
    prod_basis, ok4 = one_value(rows, basis_key)

    if not (ok1 and ok2 and ok3 and ok4):
        return None
    if flag is None or div is None:
        # Not actually applicable; undo the optimistic eligible increment.
        if path == "variant":
            counts["variant_eligible_paths"] -= 1
        else:
            counts["cross_party_eligible_paths"] -= 1
        return None

    selected_unit = max(thresholds)
    selected = thresholds[selected_unit]
    reconstructed_flag = float(div) > float(selected["threshold"])

    reconstruction_bad = (
        not float_same(prod_threshold, selected["threshold"])
        or prod_basis != selected["basis"]
        or bool(flag) != bool(reconstructed_flag)
    )
    if reconstruction_bad:
        counts["production_reconstruction_errors"] += 1
        integrity_errors.append(
            {
                "type": "production_threshold_reconstruction",
                "group_id": rows[0]["comparability_group_id"],
                "path": path,
                "production_flag": flag,
                "production_divergence": div,
                "production_threshold": prod_threshold,
                "production_basis": prod_basis,
                "selected_unit": selected_unit,
                "reconstructed_threshold": selected["threshold"],
                "reconstructed_basis": selected["basis"],
                "reconstructed_flag": reconstructed_flag,
            }
        )

    flags_by_unit = {
        unit: bool(float(div) > float(meta["threshold"]))
        for unit, meta in thresholds.items()
    }
    sensitive = len(set(flags_by_unit.values())) > 1

    result = {
        "path": path,
        "production_flag": bool(flag),
        "production_divergence": div,
        "production_threshold": prod_threshold,
        "production_basis": prod_basis,
        "production_selected_unit": selected_unit,
        "counterfactual_flags_by_observed_unit": flags_by_unit,
        "classification_sensitive": sensitive,
    }

    if sensitive:
        counts["classification_sensitive_paths"] += 1
        if path == "variant":
            counts["variant_classification_sensitive_paths"] += 1
        else:
            counts["cross_party_classification_sensitive_paths"] += 1

    return result

def emit_group(rows, mixed_f, sensitive_f):
    counts["comparability_groups_scanned"] += 1
    counts["fact_rows_scanned"] += len(rows)

    units = sorted({r["metric_unit"] for r in rows if r["metric_unit"] is not None})
    if len(units) <= 1:
        return

    counts["actual_mixed_unit_groups"] += 1
    root_key = (
        rows[0]["model_aggregation_key"],
        rows[0]["benchmark_key"],
        rows[0]["metric_key"],
    )
    actual_mixed_root_keys.add(root_key)
    unit_patterns[" | ".join(units)] += 1

    mins = [r["min_score"] for r in rows if r["min_score"] is not None]
    maxs = [r["max_score"] for r in rows if r["max_score"] is not None]
    agg_min = max(mins) if mins else None
    agg_max = max(maxs) if maxs else None

    thresholds = {}
    for unit in units:
        threshold, basis = compute_threshold(
            {
                "metric_unit": unit,
                "min_score": agg_min,
                "max_score": agg_max,
            }
        )
        thresholds[unit] = {"threshold": threshold, "basis": basis}

    threshold_signatures = {
        (round(float(v["threshold"]), 15), v["basis"]) for v in thresholds.values()
    }
    threshold_sensitive = len(threshold_signatures) > 1
    if threshold_sensitive:
        counts["threshold_sensitive_groups"] += 1

    identity_fields = [
        "comparability_group_id",
        "model_aggregation_key",
        "benchmark_key",
        "slice_key",
        "metric_key",
    ]
    identity = {}
    for key in identity_fields:
        val, ok = one_value(rows, key)
        identity[key] = val

    variant = analyze_path(rows, "variant", thresholds)
    cross = analyze_path(rows, "cross_party", thresholds)

    group_sensitive = bool(
        (variant and variant["classification_sensitive"])
        or (cross and cross["classification_sensitive"])
    )
    if group_sensitive:
        counts["classification_sensitive_groups"] += 1

    record = {
        **identity,
        "row_count": len(rows),
        "observed_units": units,
        "production_selected_unit_by_MAX": max(units),
        "group_max_min_score": agg_min,
        "group_max_max_score": agg_max,
        "thresholds_by_observed_unit": thresholds,
        "threshold_sensitive": threshold_sensitive,
        "classification_sensitive": group_sensitive,
        "variant": variant,
        "cross_party": cross,
        "rows": source_rows(rows),
    }
    mixed_f.write(json.dumps(record, ensure_ascii=True, sort_keys=True) + "\n")

    if group_sensitive:
        sensitive_f.write(json.dumps(record, ensure_ascii=True, sort_keys=True) + "\n")

current_id = None
group_rows = []

with RAW_MIXED.open("w", encoding="utf-8", newline="\n") as mixed_f, \
     RAW_SENSITIVE.open("w", encoding="utf-8", newline="\n") as sensitive_f:
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
                emit_group(group_rows, mixed_f, sensitive_f)
                group_rows = []
                current_id = gid
            group_rows.append(r)
    if group_rows:
        emit_group(group_rows, mixed_f, sensitive_f)

counts["warning_roots_with_actual_mixed_group"] = len(
    warning_root_keys & actual_mixed_root_keys
)
counts["warning_roots_cross_slice_only"] = len(
    warning_root_keys - actual_mixed_root_keys
)

# Any actual mixed root should necessarily be inside the warning population.
orphan_actual_roots = actual_mixed_root_keys - warning_root_keys
if orphan_actual_roots:
    integrity_errors.append(
        {
            "type": "actual_mixed_root_missing_from_warning_population",
            "count": len(orphan_actual_roots),
        }
    )

with RAW_ERRORS.open("w", encoding="utf-8", newline="\n") as f:
    for e in integrity_errors:
        f.write(json.dumps(e, ensure_ascii=True, sort_keys=True) + "\n")

integrity_bad = (
    len(integrity_errors) > 0
    or counts["production_reconstruction_errors"] > 0
    or counts["group_consistency_errors"] > 0
)

if integrity_bad:
    verdict = "INCONCLUSIVE"
elif counts["classification_sensitive_paths"] >= 1:
    verdict = "CONFIRMED"
else:
    verdict = "REFUTED"

summary = {
    "test_id": "T04_comparability_unit_consistency",
    "backend_commit": head,
    "claim": (
        "At least one production-applicable Stage F comparability path changes "
        "boolean classification across metric_unit values actually observed "
        "inside that same comparability group."
    ),
    "verdict": verdict,
    **counts,
    "integrity_error_records": len(integrity_errors),
    "unit_patterns": dict(sorted(unit_patterns.items())),
    "competing_predictions": {
        "P1": "classification_sensitive_paths = 0",
        "P2": "classification_sensitive_paths >= 1",
    },
    "stop_rule": (
        "Stop unit-choice consequence branch on REFUTED; source-trace "
        "classification-sensitive groups on CONFIRMED."
    ),
    "evidence": {
        "input_fact_sha256": sha256(FACT),
        "warning_root_groups_sha256": sha256(RAW_WARNING),
        "mixed_unit_groups_sha256": sha256(RAW_MIXED),
        "classification_sensitive_paths_sha256": sha256(RAW_SENSITIVE),
        "integrity_errors_sha256": sha256(RAW_ERRORS),
    },
    "limitations": [
        "T04 tests sensitivity to observed unit choices; it does not decide which unit is semantically correct.",
        "T04 reuses frozen production divergence magnitudes to isolate threshold-unit choice.",
        "The verdict is snapshot-bound to the frozen T03 Stage F artifact.",
        "A CONFIRMED verdict requires later source tracing before any root-cause or public-product claim.",
    ],
}
SUMMARY.write_text(
    json.dumps(summary, indent=2, ensure_ascii=True, sort_keys=True) + "\n",
    encoding="utf-8",
)

analysis_lines = [
    "# RESULT_ANALYSIS — T04 Comparability Unit Consistency and Threshold-Choice Sensitivity",
    "",
    "Status: generated after execution from the frozen T04 summary.",
    "",
    f"Primary verdict: `{verdict}`.",
    "",
    "## Raw counts",
    "",
]
for key in [
    "fact_rows_scanned",
    "comparability_groups_scanned",
    "warning_root_groups",
    "actual_mixed_unit_groups",
    "warning_roots_with_actual_mixed_group",
    "warning_roots_cross_slice_only",
    "variant_eligible_paths",
    "cross_party_eligible_paths",
    "threshold_sensitive_groups",
    "classification_sensitive_groups",
    "classification_sensitive_paths",
    "variant_classification_sensitive_paths",
    "cross_party_classification_sensitive_paths",
    "production_reconstruction_errors",
    "group_consistency_errors",
]:
    analysis_lines.append(f"- `{key}` = {counts[key]}")
analysis_lines += [
    "",
    "## Interpretation",
    "",
]
if verdict == "CONFIRMED":
    analysis_lines += [
        "P2 was observed: at least one production-applicable comparability boolean changes across unit values already present inside the same frozen comparability group.",
        "",
        "This establishes a frozen-corpus threshold-choice sensitivity, not semantic correctness of either unit and not a global EvalEval comparability failure.",
        "",
        "Per the preregistered stop/continue rule, the next descendant test must trace the classification-sensitive groups to frozen source records before any root-cause or public-product claim.",
    ]
elif verdict == "REFUTED":
    analysis_lines += [
        "P1 was observed: no production-applicable comparability boolean changes across the unit values present inside the same frozen comparability group.",
        "",
        "Any observed mixed-unit or threshold-only heterogeneity therefore has no demonstrated boolean-classification consequence in this frozen Stage F snapshot.",
        "",
        "Per the preregistered stop rule, this consequence branch stops here; source tracing is not justified solely by the Stage F warning.",
    ]
else:
    analysis_lines += [
        "Neither competing prediction can be interpreted because an integrity or reconstruction condition failed.",
        "",
        "No EvalEval defect attribution is permitted from this result. The measurement step must be repaired or replaced first.",
    ]
analysis_lines += [
    "",
    "## Scope limits",
    "",
    "- This result does not identify the semantically correct unit.",
    "- It does not establish upstream root cause.",
    "- It does not establish public-site impact.",
    "- It does not generalize beyond the frozen snapshot.",
    "",
    "## Evidence",
    "",
    "- `raw/warning_root_groups.jsonl`",
    "- `raw/mixed_unit_groups.jsonl`",
    "- `raw/classification_sensitive_paths.jsonl`",
    "- `raw/integrity_errors.jsonl`",
    "- `results/summary.json`",
]
RESULT_ANALYSIS.write_text("\n".join(analysis_lines) + "\n", encoding="utf-8")

print("T04 COMPLETE")
print(f"verdict={verdict}")
for key in [
    "fact_rows_scanned",
    "comparability_groups_scanned",
    "warning_root_groups",
    "actual_mixed_unit_groups",
    "warning_roots_with_actual_mixed_group",
    "warning_roots_cross_slice_only",
    "variant_eligible_paths",
    "cross_party_eligible_paths",
    "threshold_sensitive_groups",
    "classification_sensitive_groups",
    "classification_sensitive_paths",
    "variant_classification_sensitive_paths",
    "cross_party_classification_sensitive_paths",
    "production_reconstruction_errors",
    "group_consistency_errors",
]:
    print(f"{key}={counts[key]}")
print(f"integrity_error_records={len(integrity_errors)}")
for pattern, n in sorted(unit_patterns.items()):
    print(f"unit_pattern[{pattern}]={n}")
print(r"raw_warning=tests\T04_comparability_unit_consistency\raw\warning_root_groups.jsonl")
print(r"raw_mixed=tests\T04_comparability_unit_consistency\raw\mixed_unit_groups.jsonl")
print(r"raw_sensitive=tests\T04_comparability_unit_consistency\raw\classification_sensitive_paths.jsonl")
print(r"summary=tests\T04_comparability_unit_consistency\results\summary.json")
print(r"analysis=tests\T04_comparability_unit_consistency\results\RESULT_ANALYSIS.md")
