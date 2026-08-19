# RESULT_ANALYSIS — T14 Source Metric Identity Preservation Counterfactual — Fix 1

Status: generated after the repaired T14 execution.

Primary verdict: `INCONCLUSIVE`.

## Harness repair

The original analyzer stopped with ERROR because final Stage F excludes the generation-args payload used internally by the production divergence UDF.

Fix 1 reconstructs generation args from the frozen EEE source pointer and requires exact full-group production replay before interpreting the counterfactual.

## Raw counts

- `affected_production_groups` = 2
- `affected_rows` = 12
- `generation_args_source_rows_complete` = 12
- `generation_args_source_errors` = 0
- `production_groups_replayed_exact` = 0
- `production_replay_errors` = 8
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
- `integrity_error_records` = 8

## Interpretation

T14 remains INCONCLUSIVE because source reconstruction or exact production replay failed.

No counterfactual attribution is permitted.
