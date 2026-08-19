# RESULT_ANALYSIS — T14 Source Metric Identity Preservation Counterfactual — Fix 4

Status: generated after the repaired T14 Fix 4 execution.

Primary verdict: `CONFIRMED`.

## Representation repair

Fix 4 reconstructs the frozen Stage-F generation-args input through typed Arrow plus DuckDB `to_json`, avoiding PyArrow `to_pylist()` for Arrow MAP values.

## Raw counts

- `affected_production_groups` = 2
- `affected_rows` = 12
- `duckdb_generation_args_rows_complete` = 12
- `duckdb_generation_args_errors` = 0
- `production_groups_replayed_exact` = 2
- `production_replay_errors` = 0
- `unique_source_metric_ids` = 6
- `source_id_subgroups_total` = 6
- `source_id_subgroups_applicable` = 6
- `source_id_subgroups_positive` = 1
- `source_id_subgroups_negative` = 5
- `source_id_subgroups_inapplicable` = 0
- `production_groups_retaining_positive_source_id_subgroup` = 1
- `production_positive_groups_losing_all_positive_source_id_subgroups` = 1
- `source_metric_config_consistency_errors` = 0
- `row_identity_errors` = 0
- `integrity_error_records` = 0

## Interpretation

Both complete production groups replay exactly before the counterfactual.

P2 was observed: at least one affected production-positive group has no positive exact-source-id subgroup.

Under the preregistered exact-source-id preservation intervention, fallback source-id collapse is operationally necessary for at least one affected production-positive flag.

This does not establish that exact source ids are the normative canonical identity or that all distinct source ids are semantically non-equivalent.
