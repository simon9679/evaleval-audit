# HARNESS_FIX_02 — Exact Stage F group metric_config reconstruction

Status: post-INCONCLUSIVE harness repair.

## Trigger

T14 Fix 1 completed with:

- verdict = INCONCLUSIVE
- generation_args_source_rows_complete = 12
- generation_args_source_errors = 0
- production_groups_replayed_exact = 0
- production_replay_errors = 8
- row_identity_errors = 0
- integrity_error_records = 8

No source-id counterfactual subgroup was executed.

## Root cause

Fix 1 incorrectly required row-level production metric metadata to be constant
inside each affected comparability group.

The frozen Stage F implementation does not require constancy.

It constructs the group-level `metric_config` as:

- `metric_kind := MAX(metric_kind) FILTER (WHERE metric_kind IS NOT NULL)`
- `metric_unit := MAX(metric_unit) FILTER (WHERE metric_unit IS NOT NULL)`
- `min_score := MAX(min_score) FILTER (WHERE min_score IS NOT NULL)`
- `max_score := MAX(max_score) FILTER (WHERE max_score IS NOT NULL)`

The affected groups are already known to be heterogeneous in these fields.

Therefore Fix 1's constancy requirement was incompatible with the frozen
production algorithm.

## Repair

Fix 2 changes only production replay reconstruction.

It keeps unchanged:

- original T14 claim;
- population;
- exact source-id counterfactual;
- source generation-args reconstruction from frozen EEE;
- frozen production divergence function;
- source-id subgroup metric configs;
- competing predictions;
- verdict rule.

For each full affected production group, Fix 2 reconstructs the exact Stage F
group metric_config with the same non-null MAX rule used by production.

## Replay gate

Before counterfactual interpretation, both full affected groups must reproduce
the frozen Stage F values for:

- `has_variant_divergence`;
- divergence magnitude;
- threshold;
- threshold basis;
- differing setup fields.

If either does not reproduce exactly, T14 remains INCONCLUSIVE.

## Attribution

The original T14 error and Fix 1 INCONCLUSIVE are harness failures.

Neither is an EvalEval defect.
