# RESULT_ANALYSIS — T14 Source Metric Identity Preservation Counterfactual — Fix 3

Status: generated after the repaired T14 Fix 3 execution.

Primary verdict: `INCONCLUSIVE`.

## Repair

Fix 3 reconstructs generation args through the frozen Pydantic plus Arrow Stage-A normalization path, rather than reading raw JSON fields directly.

## Raw counts

- `affected_production_groups` = 2
- `affected_rows` = 12
- `typed_generation_args_rows_complete` = 12
- `typed_generation_args_errors` = 0
- `production_groups_replayed_exact` = 1
- `production_replay_errors` = 1
- `unique_source_metric_ids` = 6
- `source_id_subgroups_total` = 0
- `source_id_subgroups_applicable` = 0
- `source_id_subgroups_positive` = 0
- `source_id_subgroups_negative` = 0
- `source_id_subgroups_inapplicable` = 0
- `production_groups_retaining_positive_source_id_subgroup` = 0
- `production_positive_groups_losing_all_positive_source_id_subgroups` = 0
- `source_metric_config_consistency_errors` = 0
- `row_identity_errors` = 0
- `integrity_error_records` = 1

## Interpretation

T14 remains INCONCLUSIVE because exact production replay or another integrity control failed.

No counterfactual attribution is permitted.
