# PREREGISTRATION — T14 Source Metric Identity Preservation Counterfactual

Status: registered before T14 execution.

## Frozen prerequisites

Required T13 result:

- verdict = `CONFIRMED`;
- source_rows_scanned = 12;
- unique_source_metric_ids = 6;
- structured_accept_ids = 0;
- structured_reject_ids = 6;
- rejected_no_hits = 4;
- rejected_catch_all_only = 2;
- rejected_zero_specific_ids = 6;
- rejected_conflicting_specific_ids = 0;
- inconsistent_replay_ids = 0;
- integrity_error_records = 0.

Required T12 result:

- affected_group_ids = 2;
- source_rows_scanned = 12;
- stage_rows_joined = 12;
- affected_groups_with_fallback_source_id_collapse = 2;
- integrity_error_records = 0.

Required production-positive T08 population:

- exactly 2 positive-to-negative groups;
- both are production-positive.

Frozen backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

Frozen Stage F SHA-256:

`e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196`

## Inputs

- T10 frozen source metric configs:
  `tests/T10_source_metric_config_heterogeneity/raw/source_metric_configs.jsonl`
- T08 affected groups:
  `tests/T08_within_unit_variant_counterfactual/raw/positive_to_negative_paths.jsonl`
- frozen Stage F Parquet:
  `tests/T03_corpus_boundary_impact/raw/fact_results_stage_f.parquet`

## Population

Exactly twelve rows in exactly two affected production groups.

Every row must join one-to-one by `fact_id` across T10 and Stage F.

## Counterfactual identity

Exact source metric id string.

No transformation is allowed.

## Source metric config consistency

For all rows with one source metric id, the following tuple must be constant:

- `metric_kind`
- normalized source `metric_unit`
- `min_score`
- `max_score`

If not constant, T14 is INCONCLUSIVE.

## Frozen production variant function

Import from the frozen backend:

`eval_card_backend.signals.comparability.compute_variant_divergence_py`

No copy or reimplementation of the core production function is permitted.

## Production replay

For each full affected production group, call the frozen function using all
group rows and this frozen production metric config:

- `metric_kind`
- `metric_unit`
- `min_score`
- `max_score`

taken from Stage F group fields.

The recomputed result must be non-null and
`has_variant_divergence = true`.

## Counterfactual replay

For each exact source metric id subgroup:

- call the same frozen production function;
- pass only rows with that source metric id;
- pass that source id's frozen source metric config.

## Primary quantity

`production_positive_groups_losing_all_positive_source_id_subgroups`

## Competing predictions

### P1

`production_positive_groups_losing_all_positive_source_id_subgroups = 0`

### P2

`production_positive_groups_losing_all_positive_source_id_subgroups >= 1`

## Required counts

At minimum:

- affected_production_groups;
- affected_rows;
- unique_source_metric_ids;
- source_id_subgroups_total;
- source_id_subgroups_applicable;
- source_id_subgroups_positive;
- source_id_subgroups_negative;
- source_id_subgroups_inapplicable;
- production_groups_replayed_true;
- production_groups_retaining_positive_source_id_subgroup;
- production_positive_groups_losing_all_positive_source_id_subgroups;
- source_metric_config_consistency_errors;
- production_replay_errors;
- row_identity_errors;
- integrity_error_records;
- per-production-group outcomes;
- per-source-id subgroup outcomes.

All counts must be printed.

## Branch decision

If `CONFIRMED`:

- the audit may state that fallback source-id collapse is operationally
  necessary for at least one of the two consequential production-positive
  flags under the exact-source-id preservation counterfactual;
- proceed to semantic/reference adjudication only for the affected source-id
  sets.

If `REFUTED`:

- the affected production-positive flags survive inside at least one exact
  source-id subgroup in both groups;
- source-id collapse is not necessary for the positive decisions;
- semantic analysis must not attribute the flags solely to identity collapse.

If `INCONCLUSIVE` or `ERROR`:

- repair the counterfactual measurement before semantic attribution.
