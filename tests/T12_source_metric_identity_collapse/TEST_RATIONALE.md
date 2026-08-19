# TEST_RATIONALE — T12 Source Metric Identity Collapse Trace

Status: frozen before execution.

## Primary claim C-T12

> At least one of the two product-consequential groups contains two or more
> distinct non-null frozen source `metric_config.metric_id` values that are
> represented in Stage F by one `metric_raw`, one canonical `metric_id`, and
> one `metric_key`, with no row using the `metric_id_structured` strategy.

Observable:

`affected_groups_with_fallback_source_id_collapse`

## Why this test was selected

T11 shows multiple source metric ids.

T05 shows one downstream raw/canonical identity at the broader mixed-group
level.

Those facts do not by themselves prove that the exact two consequential groups
underwent source-id collapse.

T12 checks the exact rows and transformation fields.

## Why this test is run now

If the affected source ids remain distinct downstream, then the T11
heterogeneity must enter the same comparability group by another identity
mechanism.

If multiple source ids become one fallback raw/canonical metric identity, that
directly explains how the rows become eligible for one production
comparability group.

This should be resolved before semantic alias adjudication.

## Exact collapse predicate

For one affected group, `fallback_source_id_collapse = true` iff all are true:

1. at least two distinct non-null source `metric_id` values;
2. exactly one distinct non-null Stage F `metric_raw`;
3. exactly one distinct non-null Stage F canonical `metric_id`;
4. exactly one distinct non-null Stage F `metric_key`;
5. no Stage F row has
   `metric_resolution_strategy = metric_id_structured`;
6. every source row maps one-to-one to the frozen Stage F arithmetic row.

No assumption is made about whether the different source ids are semantically
aliases.

## Competing predictions

### P1 — no fallback source-id collapse

`affected_groups_with_fallback_source_id_collapse = 0`

### P2 — fallback source-id collapse exists

`affected_groups_with_fallback_source_id_collapse >= 1`

## Secondary measurements

For each group report:

- source metric-id set;
- Stage F metric-raw set;
- Stage F canonical metric-id set;
- Stage F metric-key set;
- resolution-strategy set;
- optional effective metric-id/key sets if columns exist;
- mapping from each source metric id to Stage F raw/id/key;
- count of source ids mapping to each downstream metric identity.

Also report whether every distinct source metric id maps to the same Stage F
metric key.

## What T12 can establish

T12 can establish whether multiple source-declared metric ids are collapsed
into one production metric identity in the two consequential groups and
whether the structured-id path was bypassed.

## What T12 cannot establish

T12 cannot establish:

- that the source ids are semantically non-equivalent;
- that the fallback resolution is wrong;
- which source id should be canonical;
- whether a resolver alias is normatively correct;
- original-publisher intent.

A later semantic/reference adjudication is required only if the collapse is
confirmed and semantic equivalence remains unresolved.
