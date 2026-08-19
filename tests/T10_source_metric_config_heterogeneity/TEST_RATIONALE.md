# TEST_RATIONALE — T10 Source MetricConfig Heterogeneity

Status: frozen before execution.

## Primary claim C-T10

> At least one of the two T08/T09 product-consequential groups contains more
> than one distinct frozen source non-unit MetricConfig signature among the
> numeric rows used by the variant-divergence arithmetic.

Observable primary quantity:

`affected_groups_with_nonunit_metric_config_heterogeneity`

## Why this test was selected

T08 showed that two production-positive booleans depend on exact-unit
cross-partition arithmetic.

T09 showed that those two booleans affect the frozen product headline.

Before introducing an external semantic reference for unit meaning, the audit
can ask a cheaper source-internal question:

Do the source records already declare different metric definitions beyond the
unit field?

If yes, the affected production group combines rows whose source metric
configuration differs on structured schema fields.

If no, the structured source metric definition is otherwise identical and the
unit field is the remaining structured disagreement.

Either outcome narrows the next semantic test.

## Why this test is run now

The population is only two groups.

All row pointers were already verified by T06.

The required source JSON files are already frozen locally.

This test therefore has near-zero additional external cost and no semantic
judgement.

## Fixed source signature

For every arithmetic score row in the two affected groups, read the frozen
source:

`evaluation_results[result_idx].metric_config`

Primary exact non-unit signature:

- `metric_id`
- `metric_name`
- `metric_kind`
- `metric_parameters`
- `lower_is_better`
- `score_type`
- `min_score`
- `max_score`

`metric_unit` is deliberately excluded from the signature because its
heterogeneity is already established.

Free-text fields are not used in the primary claim.

## Competing predictions

### P1 — unit is the only structured metric-definition disagreement

For both affected groups:

`nonunit_metric_config_signature_count = 1`

Observable result:

`affected_groups_with_nonunit_metric_config_heterogeneity = 0`

### P2 — additional structured metric-definition heterogeneity exists

At least one affected group has:

`nonunit_metric_config_signature_count >= 2`

Observable result:

`affected_groups_with_nonunit_metric_config_heterogeneity >= 1`

## Secondary descriptive outputs

For each affected group T10 reports:

- exact unit set;
- source row count;
- non-unit signature count;
- signatures observed under each exact unit;
- units that contain multiple signatures;
- signatures that occur under multiple units;
- exact field-level values for all primary signature fields;
- source `evaluation_name`;
- source `evaluation_description`;
- source `additional_details`;
- source pointer and result index.

The free-text fields are descriptive only.

## What T10 can establish

T10 can establish whether the product-consequential groups are heterogeneous in
structured source metric-definition fields beyond the already-known unit
difference.

## What T10 cannot establish

T10 cannot establish:

- whether any differing source field is correct;
- whether two signatures denote different real-world estimands;
- whether unit labels are semantically compatible;
- which rows should be grouped;
- whether the original publisher emitted the same metadata;
- whether the product flag is semantically wrong.

Those require a later reference adjudication if still necessary.
