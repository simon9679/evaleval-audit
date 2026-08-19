from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

FIX3 = HERE / "results" / "summary_fix3.json"
ERR3 = HERE / "raw" / "integrity_errors_fix3.jsonl"
FACT = ROOT / "tests" / "T03_corpus_boundary_impact" / "raw" / "fact_results_stage_f.parquet"
T10 = ROOT / "tests" / "T10_source_metric_config_heterogeneity" / "raw" / "source_metric_configs.jsonl"
T06ROOT = ROOT / "tests" / "T06_eee_source_unit_trace" / "raw" / "source_root.json"
BACKEND = ROOT / "freeze" / "repos" / "eval_cards_backend_pipeline"

EXPECTED_SHA = "e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"
EXPECTED_COMMIT = "9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
EXPECTED_DUCKDB = "1.5.2"
EXPECTED_PYARROW = "24.0.0"
COCOA_GROUP = "0dc7e803e7438c7faf39dfc4b461faef"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def git_head(path: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None

problems: list[str] = []

head = git_head(BACKEND)
if head != EXPECTED_COMMIT:
    problems.append(f"backend HEAD mismatch: {head}")

fact_sha = sha256(FACT) if FACT.exists() else None
if fact_sha != EXPECTED_SHA:
    problems.append(f"Stage F SHA mismatch: {fact_sha}")

fix3 = {}
if not FIX3.exists():
    problems.append(f"missing Fix3 summary: {FIX3}")
else:
    try:
        fix3 = json.loads(FIX3.read_text(encoding="utf-8"))
        expected = {
            "fix_id": "HARNESS_FIX_03",
            "verdict": "INCONCLUSIVE",
            "affected_production_groups": 2,
            "affected_rows": 12,
            "typed_generation_args_rows_complete": 12,
            "typed_generation_args_errors": 0,
            "production_groups_replayed_exact": 1,
            "production_replay_errors": 1,
            "source_id_subgroups_total": 0,
            "row_identity_errors": 0,
            "integrity_error_records": 1,
        }
        for key, value in expected.items():
            if fix3.get(key) != value:
                problems.append(
                    f"Fix3 mismatch {key}: got {fix3.get(key)!r}, expected {value!r}"
                )
    except Exception as exc:
        problems.append(f"cannot parse Fix3 summary: {type(exc).__name__}: {exc}")

representation_only = False
map_shape_observed = False
if not ERR3.exists():
    problems.append(f"missing Fix3 integrity errors: {ERR3}")
else:
    try:
        errors = [
            json.loads(line)
            for line in ERR3.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if len(errors) != 1:
            problems.append(f"expected exactly one Fix3 error, got {len(errors)}")
        else:
            err = errors[0]
            frozen = err.get("frozen") or {}
            replay = err.get("replay") or {}
            scalar_equal = (
                frozen.get("has_variant_divergence") == replay.get("has_variant_divergence")
                and frozen.get("divergence_magnitude") == replay.get("divergence_magnitude")
                and frozen.get("threshold_used") == replay.get("threshold_used")
                and frozen.get("threshold_basis") == replay.get("threshold_basis")
            )
            fds = frozen.get("differing_setup_fields")
            rds = replay.get("differing_setup_fields")
            representation_only = bool(scalar_equal and fds != rds)

            try:
                fv = fds[0]["values"]
                rv = rds[0]["values"]
                map_shape_observed = (
                    fds[0]["field"] == "agentic_eval_config"
                    and rds[0]["field"] == "agentic_eval_config"
                    and '"additional_details": {' in fv
                    and '"additional_details": [[' in rv
                )
            except Exception:
                map_shape_observed = False

            if not representation_only:
                problems.append("Fix3 mismatch is not representation-only")
            if not map_shape_observed:
                problems.append("Fix3 mismatch does not match the researched MAP shape")
    except Exception as exc:
        problems.append(f"cannot parse Fix3 error: {type(exc).__name__}: {exc}")

eee_root = None
if not T06ROOT.exists():
    problems.append(f"missing T06 source root: {T06ROOT}")
else:
    try:
        root_payload = json.loads(T06ROOT.read_text(encoding="utf-8"))
        eee_root = root_payload.get("selected_root")
        if not eee_root or not Path(eee_root).is_dir():
            problems.append(f"invalid EEE root: {eee_root!r}")
    except Exception as exc:
        problems.append(f"cannot parse EEE root: {type(exc).__name__}: {exc}")

try:
    import duckdb
    duckdb_version = duckdb.__version__
except Exception as exc:
    duckdb_version = None
    problems.append(f"cannot import duckdb: {type(exc).__name__}: {exc}")

try:
    import pyarrow as pa
    pyarrow_version = pa.__version__
except Exception as exc:
    pa = None
    pyarrow_version = None
    problems.append(f"cannot import pyarrow: {type(exc).__name__}: {exc}")

if duckdb_version is not None and duckdb_version != EXPECTED_DUCKDB:
    problems.append(
        f"duckdb version mismatch: got {duckdb_version}, expected {EXPECTED_DUCKDB}"
    )
if pyarrow_version is not None and pyarrow_version != EXPECTED_PYARROW:
    problems.append(
        f"pyarrow version mismatch: got {pyarrow_version}, expected {EXPECTED_PYARROW}"
    )

# Frozen source imports.
schema_fields = None
threshold_factor_value = None
try:
    sys.path.insert(0, str(BACKEND / "src"))
    from eval_card_backend.schemas.eee_arrow import derive_pyarrow_schema, pad_record_for_cast
    from eval_card_backend.schemas.eee_types import EvaluationLog
    from eval_card_backend.canonicalise.thresholds import threshold_factor

    base_schema = derive_pyarrow_schema()
    schema_fields = len(base_schema)
    threshold_factor_value = threshold_factor()
    if threshold_factor_value != 1.0:
        problems.append(
            f"DIVERGENCE_THRESHOLD_FACTOR effective value is {threshold_factor_value}, expected 1.0"
        )
except Exception as exc:
    problems.append(f"cannot load frozen schema/threshold code: {type(exc).__name__}: {exc}")

# Library micro-probe: Arrow MAP -> DuckDB to_json must be an object.
arrow_map_to_json = None
if pa is not None and duckdb_version is not None:
    try:
        probe = pa.table(
            {"m": pa.array([[("duck", "42")]], type=pa.map_(pa.string(), pa.string()))}
        )
        con = duckdb.connect()
        con.register("_map_probe", probe)
        arrow_map_to_json = con.execute(
            "SELECT CAST(to_json(m) AS VARCHAR) FROM _map_probe"
        ).fetchone()[0]
        if arrow_map_to_json != '{"duck":"42"}':
            problems.append(
                f"Arrow MAP -> DuckDB to_json probe mismatch: {arrow_map_to_json!r}"
            )
    except Exception as exc:
        problems.append(f"Arrow MAP/DuckDB micro-probe failed: {type(exc).__name__}: {exc}")

# Actual frozen CocoaBench representation probe.
actual_probe_type = None
actual_probe_json = None
if (
    eee_root
    and T10.exists()
    and pa is not None
    and duckdb_version is not None
    and schema_fields is not None
):
    try:
        rows = [
            json.loads(line)
            for line in T10.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        cocoa = next(r for r in rows if r.get("comparability_group_id") == COCOA_GROUP)
        rel = cocoa["source_record_path"]
        idx0 = int(cocoa["result_idx"])
        cfg = rel.replace("\\", "/").split("/")[1]

        rec = json.loads((Path(eee_root) / rel).read_text(encoding="utf-8"))
        EvaluationLog.model_validate(rec)
        padded = pad_record_for_cast(rec, base_schema)
        padded["source_config"] = cfg
        padded["_record_path"] = rel

        table_schema = pa.schema(
            list(base_schema)
            + [
                pa.field("source_config", pa.string(), nullable=False),
                pa.field("_record_path", pa.string(), nullable=False),
            ]
        )
        table = pa.Table.from_pylist([padded], schema=table_schema)

        con2 = duckdb.connect()
        con2.register("_actual_probe", table)
        idx1 = idx0 + 1

        actual_probe_type, actual_probe_json = con2.execute(
            f"""
            SELECT
              typeof(evaluation_results[{idx1}]
                     .generation_config.generation_args.agentic_eval_config.additional_details),
              CAST(to_json(evaluation_results[{idx1}]
                     .generation_config.generation_args.agentic_eval_config) AS VARCHAR)
            FROM _actual_probe
            """
        ).fetchone()

        if actual_probe_type is None or "MAP" not in actual_probe_type.upper():
            problems.append(
                f"actual CocoaBench additional_details is not DuckDB MAP: {actual_probe_type!r}"
            )
        if actual_probe_json is None:
            problems.append("actual CocoaBench agentic_eval_config to_json is NULL")
        else:
            if '"available_tools":null' not in actual_probe_json:
                problems.append(
                    "actual CocoaBench to_json does not contain available_tools:null"
                )
            if '"additional_details":{' not in actual_probe_json:
                problems.append(
                    "actual CocoaBench to_json does not serialize additional_details as object"
                )
    except Exception as exc:
        problems.append(f"actual CocoaBench representation probe failed: {type(exc).__name__}: {exc}")

payload = {
    "test_id": "T14_source_metric_identity_preservation",
    "fix_id": "HARNESS_FIX_04",
    "fact_sha256": fact_sha,
    "eee_root": eee_root,
    "fix3_representation_only_mismatch": representation_only,
    "fix3_map_shape_observed": map_shape_observed,
    "duckdb": duckdb_version,
    "pyarrow": pyarrow_version,
    "schema_fields": schema_fields,
    "threshold_factor": threshold_factor_value,
    "arrow_map_to_json_probe": arrow_map_to_json,
    "actual_cocoa_additional_details_type": actual_probe_type,
    "actual_cocoa_agentic_eval_config_json": actual_probe_json,
    "problems": problems,
}

(HERE / "raw").mkdir(exist_ok=True)
(HERE / "raw" / "preflight_fix4.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
    encoding="utf-8",
)

print("T14 FIX4 PREFLIGHT")
print(f"fact_sha256={fact_sha}")
print(f"eee_root={eee_root}")
print(f"fix3_representation_only_mismatch={representation_only}")
print(f"fix3_map_shape_observed={map_shape_observed}")
print(f"duckdb={duckdb_version}")
print(f"pyarrow={pyarrow_version}")
print(f"schema_fields={schema_fields}")
print(f"threshold_factor={threshold_factor_value}")
print(f"arrow_map_to_json_probe={arrow_map_to_json}")
print(f"actual_cocoa_additional_details_type={actual_probe_type}")
print(f"actual_cocoa_agentic_eval_config_json={actual_probe_json}")
print(f"problems={len(problems)}")
for problem in problems:
    print(f"PROBLEM {problem}")
if problems:
    raise SystemExit(2)
print("T14 FIX4 PREFLIGHT OK")
