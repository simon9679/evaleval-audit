# TEST_RATIONALE — T14 Source Metric Identity Preservation Counterfactual

Status: frozen before execution.

## Primary claim C-T14

> At least one of the two production-positive consequential groups has no
> positive variant-divergence subgroup when the exact frozen source metric id
> is preserved as the metric grouping identity and the frozen production
> variant-divergence function is recomputed within each source-id subgroup.

Primary observable:

`production_positive_groups_losing_all_positive_source_id_subgroups`

## Why this test was selected

T12 and T13 explain how different source metric ids become one production
`score` identity.

That still does not prove the collapse is necessary for the production-positive
variant flags.

T14 tests that consequence directly.

## Why this test is run now

This is the last deterministic causal descendant before semantic/reference
adjudication.

It requires no external source, no human judgement, and no invented metric
alias map.

## Fixed population

Exactly the two T08 positive-to-negative production groups and their twelve
arithmetic rows.

No other corpus rows are modified or regrouped.

## Fixed counterfactual

Within each affected production group:

1. attach the exact frozen source `metric_config.metric_id` to every row;
2. subgroup by that exact source metric id;
3. call the frozen production `compute_variant_divergence_py` separately on
   each subgroup;
4. use the source metric config for threshold semantics;
5. do not merge any source ids;
6. do not convert units;
7. do not change scores or generation setups.

## Group-level outcome

For each affected production group:

- `retains_positive_source_id_subgroup = true`
  if at least one exact source-id subgroup returns
  `has_variant_divergence = true`;
- otherwise false.

A subgroup returning `None` is inapplicable and is not counted as positive.

## Competing predictions

### P1 — collapse not necessary for either production-positive flag

`production_positive_groups_losing_all_positive_source_id_subgroups = 0`

Both affected production groups retain at least one positive exact-source-id
subgroup.

### P2 — identity collapse is necessary for at least one positive flag

`production_positive_groups_losing_all_positive_source_id_subgroups >= 1`

At least one affected production-positive group has no positive exact-source-id
subgroup.

## Primary verdict

- `CONFIRMED` — P2 observed and all integrity/reproduction controls pass.
- `REFUTED` — P1 observed and all integrity/reproduction controls pass.
- `INCONCLUSIVE` — source-id subgroup reconstruction is readable but source
  config consistency, row identity, or production replay does not support a
  valid counterfactual.
- `ERROR` — frozen backend, prerequisite evidence, input artifact, or
  dependency cannot be loaded.

The verdict applies only to C-T14.

## Secondary measurements

Report:

- exact source-id subgroup count;
- applicable source-id subgroups;
- positive source-id subgroups;
- negative source-id subgroups;
- inapplicable source-id subgroups;
- subgroup row counts;
- subgroup divergence magnitudes;
- subgroup thresholds and bases;
- subgroup differing setup fields;
- per-production-group retained-positive status;
- per-source-id metric config.

## Production replay control

Before interpreting the counterfactual, T14 must recompute the original
production variant result for each of the two complete affected production
groups using the frozen production function and the frozen production metric
config.

Both must reproduce `has_variant_divergence = true`.

Failure is an integrity/replay failure.

## What T14 can establish

T14 can establish whether preserving exact source metric identity removes all
positive variant-divergence outcomes from at least one of the two affected
production groups.

## What T14 cannot establish

T14 cannot establish:

- that exact source ids are the correct normative canonical identity;
- that different source ids are semantically non-equivalent;
- that a registry alias must not combine some source ids;
- which canonical identity should be used;
- original-publisher intent.

Those require the next semantic/reference adjudication.
