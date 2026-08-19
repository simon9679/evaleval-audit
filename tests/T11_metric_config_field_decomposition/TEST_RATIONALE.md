# TEST_RATIONALE — T11 MetricConfig Field-Level Decomposition

Status: frozen before execution.

## Primary claim C-T11

> At least one product-consequential group varies in at least one
> claim-governing structured MetricConfig field other than display-only
> `metric_name`.

The claim-governing field subset is preregistered as:

- `metric_id`
- `metric_kind`
- `metric_parameters`
- `lower_is_better`
- `score_type`
- `min_score`
- `max_score`

`metric_name` is still fully measured and reported, but a difference only in
`metric_name` is not sufficient for C-T11.

## Why this test was selected

T10 proved non-unit signature heterogeneity but did not identify the fields.

A display-name-only difference would be much weaker evidence than a difference
in stable metric id, normalized metric family, parameters, direction, score
type, or scale bounds.

T11 separates those cases without subjective semantic interpretation.

## Why this test is run now

The source rows and signatures are already frozen by T10.

The population is only two groups and twelve rows.

This is the cheapest remaining deterministic test before external/reference
adjudication.

## Exact field variation rule

For each affected group and each primary field:

`field_varies = count(distinct canonical exact values) >= 2`

Rules:

- missing -> null;
- dictionaries -> canonical JSON with sorted keys;
- list order preserved;
- strings case-sensitive;
- no trimming;
- no synonym mapping;
- no numeric conversion.

## Unit-partition alignment

For each varying field T11 also reports:

- whether each exact unit has one or multiple values for that field;
- whether any exact field value is shared across multiple units;
- whether the field's value sets are disjoint across unit partitions.

This is descriptive and not part of the primary verdict.

## Competing predictions

### P1 — only display-name-level non-unit heterogeneity

Across both affected groups, all claim-governing fields are constant.

Observable:

`affected_groups_with_claim_governing_field_variation = 0`

### P2 — claim-governing structured heterogeneity exists

At least one affected group varies in at least one claim-governing field.

Observable:

`affected_groups_with_claim_governing_field_variation >= 1`

## What T11 can establish

T11 can establish which structured source fields differ inside the two
product-consequential groups and whether those differences extend beyond
display naming.

## What T11 cannot establish

T11 cannot establish:

- that a varying field necessarily denotes a different semantic estimand;
- that any source value is correct;
- which rows should be grouped;
- whether unit labels are semantically compatible;
- original-publisher provenance;
- semantic correctness of the production flags.

Those remain reference-adjudication questions.
