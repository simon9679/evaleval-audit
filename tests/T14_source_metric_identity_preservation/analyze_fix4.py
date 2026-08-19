from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

FACT = ROOT / "tests" / "T03_corpus_boundary_impact" / "raw" / "fact_results_stage_f.parquet"
T10_ROWS = ROOT / "tests" / "T10_source_metric_config_heterogeneity" / "raw" / "source_metric_configs.jsonl"
T08_FLIPS = ROOT / "tests" / "T08_within_unit_variant_counterfactual" / "raw" / "positive_to_negative_paths.jsonl"
T06ROOT = ROOT / "tests" / "T06_eee_source_unit_trace" / "raw" / "source_root.json"
BACKEND = ROOT / "freeze" / "repos" / "eval_cards_backend_pipeline"

EXPECTED_COMMIT = "9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
EXPECTED_SHA = "e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"
EXPECTED_DUCKDB = "1.5.2"
EXPECTED_PYARROW = "24.0.0"

RAW_SRC = HERE / "raw" / "generation_args_duckdb_trace_fix4.jsonl"
RAW_SUB = HERE / "raw" / "source_id_subgroup_results_fix4.jsonl"
RAW_GROUP = HERE / "raw" / "production_group_counterfactuals_fix4.jsonl"
RAW_ERR = HERE / "raw" / "integrity_errors_fix4.jsonl"
SUMMARY = HERE / "results" / "summary_fix4.json"
ANALYSIS = HERE / "results" / "RESULT_ANALYSIS_FIX4.md"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def fail(message: str):
    SUMMARY.parent.mkdir(exist_ok=True)
    SUMMARY.write_text(
        json.dumps(
            {
                "test_id": "T14_source_metric_identity_preservation",
                "fix_id": "HARNESS_FIX_04",
                "verdict": "ERROR",
                "error": message,
            },
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print("T14 FIX4 ERROR")
    print(message)
    raise SystemExit(2)

def canon(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )

def float_equal(a, b, tol=1e-12):
    if a is None or b is None:
        return a is b
    return math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=tol)

def prod_max_nonnull(values):
    values = [v for v in values if v is not None]
    return max(values) if values else None

if not (HERE / "raw" / "preflight_fix4.json").exists():
    fail("Missing Fix4 preflight evidence.")

head = subprocess.check_output(
    ["git", "-C", str(BACKEND), "rev-parse", "HEAD"], text=True
).strip()
if head != EXPECTED_COMMIT:
    fail(f"Backend HEAD mismatch: {head}")
if sha256(FACT) != EXPECTED_SHA:
    fail("Stage F SHA mismatch.")

sys.path.insert(0, str(BACKEND / "src"))

try:
    import duckdb
    import pyarrow as pa
    from eval_card_backend.canonicalise.thresholds import threshold_factor
    from eval_card_backend.schemas.eee_arrow import derive_pyarrow_schema, pad_record_for_cast
    from eval_card_backend.schemas.eee_types import EvaluationLog
    from eval_card_backend.signals.comparability import compute_variant_divergence_py
except Exception as exc:
    fail(f"cannot import frozen/library code: {type(exc).__name__}: {exc}")

if duckdb.__version__ != EXPECTED_DUCKDB:
    fail(f"duckdb version mismatch: {duckdb.__version__}")
if pa.__version__ != EXPECTED_PYARROW:
    fail(f"pyarrow version mismatch: {pa.__version__}")
if threshold_factor() != 1.0:
    fail(f"effective divergence threshold factor is {threshold_factor()}, expected 1.0")

base_schema = derive_pyarrow_schema()
table_schema = pa.schema(
    list(base_schema)
    + [
        pa.field("source_config", pa.string(), nullable=False),
        pa.field("_record_path", pa.string(), nullable=False),
    ]
)

root_payload = json.loads(T06ROOT.read_text(encoding="utf-8"))
EEE = Path(root_payload["selected_root"])
if not EEE.is_dir():
    fail(f"Invalid EEE root: {EEE}")

src = [
    json.loads(line)
    for line in T10_ROWS.read_text(encoding="utf-8").splitlines()
    if line.strip()
]
flips = [
    json.loads(line)
    for line in T08_FLIPS.read_text(encoding="utf-8").splitlines()
    if line.strip()
]
if len(src) != 12:
    fail(f"Expected 12 T10 rows, got {len(src)}")
if len(flips) != 2:
    fail(f"Expected 2 T08 groups, got {len(flips)}")

affected_ids = [row["comparability_group_id"] for row in flips]

errors = []
counts = Counter()
source_by_fact = {}
record_cache = {}

def load_raw_record(rel: str):
    if rel not in record_cache:
        path = EEE / rel
        if not path.is_file():
            raise FileNotFoundError(str(path))
        record_cache[rel] = json.loads(path.read_text(encoding="utf-8"))
    return record_cache[rel]

# Exact Stage-A typed Arrow -> DuckDB -> Stage-D to_json reconstruction.
with RAW_SRC.open("w", encoding="utf-8", newline="\n") as trace:
    for ordinal, row in enumerate(src):
        fid = row["fact_id"]
        try:
            rel = row["source_record_path"]
            idx0 = int(row["result_idx"])
            path_parts = rel.replace("\\", "/").split("/")
            if len(path_parts) < 2 or path_parts[0] != "data":
                raise ValueError(f"unexpected EEE record path: {rel}")
            source_config = path_parts[1]

            rec = load_raw_record(rel)
            EvaluationLog.model_validate(rec)
            padded = pad_record_for_cast(rec, base_schema)
            padded["source_config"] = source_config
            padded["_record_path"] = rel

            arrow_table = pa.Table.from_pylist([padded], schema=table_schema)

            con_src = duckdb.connect()
            relation_name = f"_typed_source_{ordinal}"
            con_src.register(relation_name, arrow_table)
            idx1 = idx0 + 1

            generation_args_json = con_src.execute(
                f"""
                SELECT CAST(
                    to_json(
                        evaluation_results[{idx1}]
                        .generation_config.generation_args
                    ) AS VARCHAR
                )
                FROM {relation_name}
                """
            ).fetchone()[0]

            source_by_fact[fid] = {
                "comparability_group_id": row["comparability_group_id"],
                "source_metric_id": row["source_metric_config_primary"]["metric_id"],
                "source_metric_config": {
                    "metric_kind": row["source_metric_config_primary"].get("metric_kind"),
                    "metric_unit": row.get("source_metric_unit_normalized"),
                    "min_score": row["source_metric_config_primary"].get("min_score"),
                    "max_score": row["source_metric_config_primary"].get("max_score"),
                },
                "generation_args_json": generation_args_json,
                "source_record_path": rel,
                "result_idx": idx0,
            }

            counts["duckdb_generation_args_rows_complete"] += 1
            trace.write(
                json.dumps(
                    {
                        "fact_id": fid,
                        "comparability_group_id": row["comparability_group_id"],
                        "source_record_path": rel,
                        "result_idx": idx0,
                        "generation_args_json": generation_args_json,
                    },
                    sort_keys=True,
                    ensure_ascii=True,
                )
                + "\n"
            )
        except Exception as exc:
            counts["duckdb_generation_args_errors"] += 1
            errors.append(
                {
                    "type": "duckdb_generation_args_error",
                    "fact_id": fid,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

# Frozen Stage F rows.
con = duckdb.connect()
fact_path = FACT.as_posix().replace("'", "''")
con.execute("CREATE TEMP TABLE _affected(id VARCHAR)")
con.executemany("INSERT INTO _affected VALUES (?)", [(gid,) for gid in affected_ids])

rows = con.execute(
    f"""
    SELECT
      fr.fact_id,
      fr.comparability_group_id,
      fr.evaluation_id,
      fr.score,
      fr.evaluator_relationship,
      fr.org_raw,
      fr.metric_kind,
      fr.metric_unit,
      fr.min_score,
      fr.max_score,
      fr.has_variant_divergence,
      fr.variant_divergence_magnitude,
      fr.variant_divergence_threshold,
      fr.variant_threshold_basis,
      fr.variant_differing_fields
    FROM read_parquet('{fact_path}') fr
    JOIN _affected a ON a.id = fr.comparability_group_id
    ORDER BY fr.comparability_group_id, fr.fact_id
    """
).fetchall()
names = [desc[0] for desc in con.description]
stage_all = [dict(zip(names, row)) for row in rows]

stage = [row for row in stage_all if row["fact_id"] in source_by_fact]
if len(stage) != 12:
    errors.append(
        {"type": "stage_affected_row_count", "got": len(stage), "expected": 12}
    )

by_gid = defaultdict(list)
for row in stage:
    source = source_by_fact.get(row["fact_id"])
    if source is None:
        counts["row_identity_errors"] += 1
        errors.append({"type": "missing_source_fact", "fact_id": row["fact_id"]})
        continue
    if source["comparability_group_id"] != row["comparability_group_id"]:
        counts["row_identity_errors"] += 1
        errors.append(
            {
                "type": "group_id_mismatch",
                "fact_id": row["fact_id"],
                "source_group": source["comparability_group_id"],
                "stage_group": row["comparability_group_id"],
            }
        )

    merged = dict(row)
    merged["source_metric_id"] = source["source_metric_id"]
    merged["source_metric_config"] = source["source_metric_config"]
    merged["generation_args_json_reconstructed"] = source["generation_args_json"]
    by_gid[row["comparability_group_id"]].append(merged)

counts["affected_production_groups"] = len(by_gid)
counts["affected_rows"] = len(stage)

# Exact production replay.
production_replay = {}
group_prod_cfg = {}

for gid, group_rows in sorted(by_gid.items()):
    cfg = {
        "metric_kind": prod_max_nonnull([r["metric_kind"] for r in group_rows]),
        "metric_unit": prod_max_nonnull([r["metric_unit"] for r in group_rows]),
        "min_score": prod_max_nonnull([r["min_score"] for r in group_rows]),
        "max_score": prod_max_nonnull([r["max_score"] for r in group_rows]),
    }
    group_prod_cfg[gid] = cfg

    frozen_fields = {}
    for field in [
        "has_variant_divergence",
        "variant_divergence_magnitude",
        "variant_divergence_threshold",
        "variant_threshold_basis",
        "variant_differing_fields",
    ]:
        values = {canon(r[field]) for r in group_rows}
        if len(values) != 1:
            counts["production_replay_errors"] += 1
            errors.append(
                {
                    "type": "frozen_group_signal_not_constant",
                    "group_id": gid,
                    "field": field,
                    "values": sorted(values),
                }
            )
        else:
            frozen_fields[field] = group_rows[0][field]

    production_rows = [
        {
            "fact_id": r["fact_id"],
            "evaluation_id": r["evaluation_id"],
            "score": r["score"],
            # Pass the DuckDB-produced JSON string exactly as Stage F does.
            "generation_args": r["generation_args_json_reconstructed"],
            "evaluator_relationship": r["evaluator_relationship"],
            "source_organization_name": r["org_raw"],
        }
        for r in group_rows
    ]

    replay = compute_variant_divergence_py(production_rows, cfg)
    production_replay[gid] = replay

    ok = True
    if replay is None:
        ok = False
    else:
        ok &= (
            replay.get("has_variant_divergence")
            == frozen_fields.get("has_variant_divergence")
        )
        ok &= float_equal(
            replay.get("divergence_magnitude"),
            frozen_fields.get("variant_divergence_magnitude"),
        )
        ok &= float_equal(
            replay.get("threshold_used"),
            frozen_fields.get("variant_divergence_threshold"),
        )
        ok &= (
            replay.get("threshold_basis")
            == frozen_fields.get("variant_threshold_basis")
        )
        ok &= (
            canon(replay.get("differing_setup_fields"))
            == canon(frozen_fields.get("variant_differing_fields"))
        )

    if not ok:
        counts["production_replay_errors"] += 1
        errors.append(
            {
                "type": "production_replay_mismatch",
                "group_id": gid,
                "production_metric_config_reconstructed": cfg,
                "replay": replay,
                "frozen": {
                    "has_variant_divergence": frozen_fields.get(
                        "has_variant_divergence"
                    ),
                    "divergence_magnitude": frozen_fields.get(
                        "variant_divergence_magnitude"
                    ),
                    "threshold_used": frozen_fields.get(
                        "variant_divergence_threshold"
                    ),
                    "threshold_basis": frozen_fields.get(
                        "variant_threshold_basis"
                    ),
                    "differing_setup_fields": frozen_fields.get(
                        "variant_differing_fields"
                    ),
                },
            }
        )
    else:
        counts["production_groups_replayed_exact"] += 1

# Counterfactual runs only after an exact 2/2 replay.
subgroup_records = []
group_records = []

if (
    counts["production_groups_replayed_exact"] == 2
    and counts["production_replay_errors"] == 0
):
    with RAW_SUB.open("w", encoding="utf-8", newline="\n") as fs, RAW_GROUP.open(
        "w", encoding="utf-8", newline="\n"
    ) as fg:
        for gid, group_rows in sorted(by_gid.items()):
            by_source_id = defaultdict(list)
            for row in group_rows:
                by_source_id[row["source_metric_id"]].append(row)

            positive = 0
            negative = 0
            inapplicable = 0

            for source_id, source_rows in sorted(by_source_id.items()):
                configs = {
                    canon(row["source_metric_config"]) for row in source_rows
                }
                if len(configs) != 1:
                    counts["source_metric_config_consistency_errors"] += 1
                    errors.append(
                        {
                            "type": "source_metric_config_not_constant",
                            "group_id": gid,
                            "source_metric_id": source_id,
                            "configs": sorted(configs),
                        }
                    )
                    continue

                cfg = json.loads(next(iter(configs)))
                subgroup_input = [
                    {
                        "fact_id": row["fact_id"],
                        "evaluation_id": row["evaluation_id"],
                        "score": row["score"],
                        "generation_args": row[
                            "generation_args_json_reconstructed"
                        ],
                        "evaluator_relationship": row["evaluator_relationship"],
                        "source_organization_name": row["org_raw"],
                    }
                    for row in source_rows
                ]

                result = compute_variant_divergence_py(subgroup_input, cfg)
                counts["source_id_subgroups_total"] += 1

                if result is None:
                    status = "INAPPLICABLE"
                    inapplicable += 1
                    counts["source_id_subgroups_inapplicable"] += 1
                elif result["has_variant_divergence"]:
                    status = "POSITIVE"
                    positive += 1
                    counts["source_id_subgroups_applicable"] += 1
                    counts["source_id_subgroups_positive"] += 1
                else:
                    status = "NEGATIVE"
                    negative += 1
                    counts["source_id_subgroups_applicable"] += 1
                    counts["source_id_subgroups_negative"] += 1

                record = {
                    "comparability_group_id": gid,
                    "source_metric_id": source_id,
                    "row_count": len(source_rows),
                    "fact_ids": sorted(r["fact_id"] for r in source_rows),
                    "metric_config": cfg,
                    "status": status,
                    "variant_result": result,
                }
                subgroup_records.append(record)
                fs.write(
                    json.dumps(record, sort_keys=True, ensure_ascii=True) + "\n"
                )

            retains_positive = positive >= 1
            if retains_positive:
                counts[
                    "production_groups_retaining_positive_source_id_subgroup"
                ] += 1
            else:
                counts[
                    "production_positive_groups_losing_all_positive_source_id_subgroups"
                ] += 1

            group_record = {
                "comparability_group_id": gid,
                "production_metric_config_reconstructed": group_prod_cfg[gid],
                "production_replay": production_replay[gid],
                "source_metric_id_count": len(by_source_id),
                "positive_source_id_subgroups": positive,
                "negative_source_id_subgroups": negative,
                "inapplicable_source_id_subgroups": inapplicable,
                "retains_positive_source_id_subgroup": retains_positive,
                "source_metric_ids": sorted(by_source_id),
            }
            group_records.append(group_record)
            fg.write(
                json.dumps(group_record, sort_keys=True, ensure_ascii=True)
                + "\n"
            )
else:
    RAW_SUB.write_text("", encoding="utf-8")
    RAW_GROUP.write_text("", encoding="utf-8")

counts["unique_source_metric_ids"] = len(
    {source["source_metric_id"] for source in source_by_fact.values()}
)

with RAW_ERR.open("w", encoding="utf-8", newline="\n") as f:
    for error in errors:
        f.write(json.dumps(error, sort_keys=True, ensure_ascii=True) + "\n")

integrity_bad = (
    len(errors) > 0
    or counts["duckdb_generation_args_errors"] > 0
    or counts["row_identity_errors"] > 0
    or counts["production_replay_errors"] > 0
    or counts["source_metric_config_consistency_errors"] > 0
)

if integrity_bad:
    verdict = "INCONCLUSIVE"
elif (
    counts[
        "production_positive_groups_losing_all_positive_source_id_subgroups"
    ]
    >= 1
):
    verdict = "CONFIRMED"
else:
    verdict = "REFUTED"

per_group = {
    record["comparability_group_id"]: {
        "production_metric_config_reconstructed": record[
            "production_metric_config_reconstructed"
        ],
        "source_metric_id_count": record["source_metric_id_count"],
        "positive_source_id_subgroups": record["positive_source_id_subgroups"],
        "negative_source_id_subgroups": record["negative_source_id_subgroups"],
        "inapplicable_source_id_subgroups": record[
            "inapplicable_source_id_subgroups"
        ],
        "retains_positive_source_id_subgroup": record[
            "retains_positive_source_id_subgroup"
        ],
        "source_metric_ids": record["source_metric_ids"],
    }
    for record in group_records
}

per_source_id = {
    record["source_metric_id"]: {
        "comparability_group_id": record["comparability_group_id"],
        "row_count": record["row_count"],
        "status": record["status"],
        "metric_config": record["metric_config"],
        "variant_result": record["variant_result"],
    }
    for record in subgroup_records
}

summary = {
    "test_id": "T14_source_metric_identity_preservation",
    "fix_id": "HARNESS_FIX_04",
    "verdict": verdict,
    "affected_production_groups": counts["affected_production_groups"],
    "affected_rows": counts["affected_rows"],
    "duckdb_generation_args_rows_complete": counts[
        "duckdb_generation_args_rows_complete"
    ],
    "duckdb_generation_args_errors": counts["duckdb_generation_args_errors"],
    "production_groups_replayed_exact": counts[
        "production_groups_replayed_exact"
    ],
    "production_replay_errors": counts["production_replay_errors"],
    "unique_source_metric_ids": counts["unique_source_metric_ids"],
    "source_id_subgroups_total": counts["source_id_subgroups_total"],
    "source_id_subgroups_applicable": counts["source_id_subgroups_applicable"],
    "source_id_subgroups_positive": counts["source_id_subgroups_positive"],
    "source_id_subgroups_negative": counts["source_id_subgroups_negative"],
    "source_id_subgroups_inapplicable": counts[
        "source_id_subgroups_inapplicable"
    ],
    "production_groups_retaining_positive_source_id_subgroup": counts[
        "production_groups_retaining_positive_source_id_subgroup"
    ],
    "production_positive_groups_losing_all_positive_source_id_subgroups": counts[
        "production_positive_groups_losing_all_positive_source_id_subgroups"
    ],
    "source_metric_config_consistency_errors": counts[
        "source_metric_config_consistency_errors"
    ],
    "row_identity_errors": counts["row_identity_errors"],
    "integrity_error_records": len(errors),
    "per_group": per_group,
    "per_source_metric_id": per_source_id,
    "competing_predictions": {
        "P1": "production_positive_groups_losing_all_positive_source_id_subgroups = 0",
        "P2": "production_positive_groups_losing_all_positive_source_id_subgroups >= 1",
    },
    "limitations": [
        "Fix 4 repairs only the typed Arrow-to-DuckDB representation path after Fix 3.",
        "Exact source-id preservation is an operational counterfactual, not a normative canonicalization rule.",
        "T14 does not establish semantic non-equivalence of distinct source ids.",
    ],
    "evidence": {
        "stage_f_sha256": sha256(FACT),
        "t10_source_rows_sha256": sha256(T10_ROWS),
        "t08_positive_to_negative_sha256": sha256(T08_FLIPS),
        "generation_args_duckdb_trace_sha256": sha256(RAW_SRC),
        "source_id_subgroup_results_sha256": sha256(RAW_SUB),
        "production_group_counterfactuals_sha256": sha256(RAW_GROUP),
        "integrity_errors_sha256": sha256(RAW_ERR),
    },
}

SUMMARY.parent.mkdir(exist_ok=True)
SUMMARY.write_text(
    json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
    encoding="utf-8",
)

lines = [
    "# RESULT_ANALYSIS — T14 Source Metric Identity Preservation Counterfactual — Fix 4",
    "",
    "Status: generated after the repaired T14 Fix 4 execution.",
    "",
    f"Primary verdict: `{verdict}`.",
    "",
    "## Representation repair",
    "",
    "Fix 4 reconstructs the frozen Stage-F generation-args input through typed Arrow plus DuckDB `to_json`, avoiding PyArrow `to_pylist()` for Arrow MAP values.",
    "",
    "## Raw counts",
    "",
]

for key in [
    "affected_production_groups",
    "affected_rows",
    "duckdb_generation_args_rows_complete",
    "duckdb_generation_args_errors",
    "production_groups_replayed_exact",
    "production_replay_errors",
    "unique_source_metric_ids",
    "source_id_subgroups_total",
    "source_id_subgroups_applicable",
    "source_id_subgroups_positive",
    "source_id_subgroups_negative",
    "source_id_subgroups_inapplicable",
    "production_groups_retaining_positive_source_id_subgroup",
    "production_positive_groups_losing_all_positive_source_id_subgroups",
    "source_metric_config_consistency_errors",
    "row_identity_errors",
    "integrity_error_records",
]:
    lines.append(f"- `{key}` = {summary[key]}")

lines += ["", "## Interpretation", ""]

if verdict == "CONFIRMED":
    lines += [
        "Both complete production groups replay exactly before the counterfactual.",
        "",
        "P2 was observed: at least one affected production-positive group has no positive exact-source-id subgroup.",
        "",
        "Under the preregistered exact-source-id preservation intervention, fallback source-id collapse is operationally necessary for at least one affected production-positive flag.",
        "",
        "This does not establish that exact source ids are the normative canonical identity or that all distinct source ids are semantically non-equivalent.",
    ]
elif verdict == "REFUTED":
    lines += [
        "Both complete production groups replay exactly before the counterfactual.",
        "",
        "P1 was observed: both affected production-positive groups retain at least one positive exact-source-id subgroup.",
        "",
        "The production-positive decisions therefore cannot be attributed solely to fallback source-id collapse.",
    ]
else:
    lines += [
        "T14 remains INCONCLUSIVE because exact production replay or another integrity control failed.",
        "",
        "No source-id counterfactual attribution is permitted.",
    ]

ANALYSIS.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("T14 FIX4 COMPLETE")
for key in [
    "verdict",
    "affected_production_groups",
    "affected_rows",
    "duckdb_generation_args_rows_complete",
    "duckdb_generation_args_errors",
    "production_groups_replayed_exact",
    "production_replay_errors",
    "unique_source_metric_ids",
    "source_id_subgroups_total",
    "source_id_subgroups_applicable",
    "source_id_subgroups_positive",
    "source_id_subgroups_negative",
    "source_id_subgroups_inapplicable",
    "production_groups_retaining_positive_source_id_subgroup",
    "production_positive_groups_losing_all_positive_source_id_subgroups",
    "source_metric_config_consistency_errors",
    "row_identity_errors",
    "integrity_error_records",
]:
    print(f"{key}={summary[key]}")

print(
    "per_group="
    + json.dumps(summary["per_group"], sort_keys=True, ensure_ascii=True)
)
print(
    "per_source_metric_id="
    + json.dumps(
        summary["per_source_metric_id"], sort_keys=True, ensure_ascii=True
    )
)
print(
    r"summary=tests\T14_source_metric_identity_preservation\results\summary_fix4.json"
)
print(
    r"analysis=tests\T14_source_metric_identity_preservation\results\RESULT_ANALYSIS_FIX4.md"
)
