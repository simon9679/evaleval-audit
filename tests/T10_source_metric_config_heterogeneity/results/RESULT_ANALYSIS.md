# RESULT_ANALYSIS — T10 Source MetricConfig Heterogeneity

Status: post-run analysis written after the completed preregistered T10 execution.

This document interprets the completed T10 result. It does not modify the
preregistration, test rationale, source attribution, analyzer, or raw evidence.

## 1. Primary preregistered question

C-T10 asked whether at least one of the two T08/T09 product-consequential
groups contains more than one distinct frozen source non-unit MetricConfig
signature among the numeric rows used by the variant-divergence arithmetic.

The primary signature excluded `metric_unit` and used exact values for:

- `metric_id`
- `metric_name`
- `metric_kind`
- `metric_parameters`
- `lower_is_better`
- `score_type`
- `min_score`
- `max_score`

## 2. Competing predictions frozen before execution

### P1 — unit is the only structured MetricConfig disagreement

`affected_groups_with_nonunit_metric_config_heterogeneity = 0`

### P2 — additional structured MetricConfig heterogeneity exists

`affected_groups_with_nonunit_metric_config_heterogeneity >= 1`

## 3. Primary verdict

`CONFIRMED`

Observed:

- `affected_groups_with_single_nonunit_signature = 0`
- `affected_groups_with_nonunit_metric_config_heterogeneity = 2`

Therefore P2 was observed.

Both product-consequential groups contain multiple distinct structured source
MetricConfig signatures even after `metric_unit` is excluded.

## 4. Complete reported counts

### Frozen population

- `fact_rows_scanned = 209382`
- `affected_group_ids = 2`
- `affected_groups_present = 2`
- `affected_arithmetic_rows = 12`

The complete consequential population contains 12 arithmetic score rows.

### Source trace

- `source_rows_complete = 12`
- `source_unit_matches = 12`
- `source_unit_mismatches = 0`
- `pointer_or_index_errors = 0`
- `evaluation_id_mismatches = 0`
- `arithmetic_row_identity_errors = 0`

Every affected arithmetic row was source-traceable and reproduced its unit
without any identity or pointer error.

### Non-unit source signatures

- `affected_groups_with_single_nonunit_signature = 0`
- `affected_groups_with_nonunit_metric_config_heterogeneity = 2`
- `affected_units_with_multiple_signatures = 1`
- `signatures_shared_across_multiple_units = 0`

The last count is especially informative.

No exact non-unit MetricConfig signature is shared across more than one unit
label in the two consequential groups.

Thus the unit partition is not floating independently over an otherwise
identical structured metric definition.

At least one exact unit partition contains multiple distinct non-unit
signatures, as shown by:

`affected_units_with_multiple_signatures = 1`

## 5. Per-group structure

### Group `0dc7e803e7438c7faf39dfc4b461faef`

- `unit_count = 2`
- units: `percent`, `seconds`
- `nonunit_signature_count = 2`
- heterogeneous non-unit MetricConfig: true

This group has two exact unit labels and two distinct non-unit MetricConfig
signatures.

T10 does not yet identify which signature fields differ.

### Group `d38d8f8e547287b6b0fc78f43f310762`

- `unit_count = 2`
- units: `points`, `score`
- `nonunit_signature_count = 4`
- heterogeneous non-unit MetricConfig: true

This group has two exact unit labels and four distinct non-unit MetricConfig
signatures.

Therefore its source metric-definition heterogeneity is more complex than a
simple one-signature-per-unit split.

## 6. Integrity

- `integrity_error_records = 0`

The result is therefore interpretable under the preregistered rules.

## 7. What T10 establishes

T10 establishes:

1. both product-consequential groups are heterogeneous in structured source
   metric-definition fields beyond `metric_unit`;
2. the first group contains 2 units and 2 non-unit signatures;
3. the second group contains 2 units and 4 non-unit signatures;
4. no exact non-unit signature is shared across multiple unit labels;
5. one exact unit partition contains multiple non-unit signatures;
6. all 12 affected arithmetic rows reproduce their frozen source identity and
   unit;
7. no pointer, source-unit, evaluation-id, row-identity, or integrity error was
   observed.

The strongest justified statement is:

> The two product-consequential mixed-unit groups are not merely inconsistent
> in `metric_unit`; their frozen EEE source rows also differ in other structured
> MetricConfig fields.

## 8. What T10 does not establish

T10 does not establish:

- which of the eight primary signature fields differ;
- whether the differing fields define distinct real-world estimands;
- whether any source field is correct or incorrect;
- whether exact unit labels are semantically compatible;
- which rows should be grouped or split;
- whether the original publisher emitted the same metadata;
- whether the production divergence flags are semantically wrong.

A field-level deterministic decomposition is required before semantic
adjudication.

## 9. Relationship to T08 and T09

T08 established that two production-positive variant-divergence flags become
negative under the exact-unit within-partition counterfactual.

T09 established that those two flags change the frozen frontend-consumed
headline count from 343 to 341.

T10 now establishes that those same two product-consequential groups also
contain structured source metric-definition heterogeneity beyond unit.

This makes the unresolved issue narrower and stronger:

`product-consequential grouping`
`-> multiple exact unit labels`
`-> multiple structured source metric definitions`

The next question is which exact schema fields create that split.

## 10. Branch decision

Proceed to a field-level decomposition over the same 12 source rows.

The next test should not introduce any semantic judgement.

It should report, for each consequential group and exact unit partition,
whether the following fields vary:

- `metric_id`
- `metric_name`
- `metric_kind`
- `metric_parameters`
- `lower_is_better`
- `score_type`
- `min_score`
- `max_score`

The field-level result will determine whether a later semantic/reference
instrument is needed and what exactly it must adjudicate.

## 11. Methodological interpretation

T10 is another example of delaying semantic judgement until structured
evidence is exhausted.

After T09, the audit already had a product-level consequence. It could have
jumped directly to interpreting `percent`, `seconds`, `points`, and `score`.

Instead, T10 asked whether the source itself already declares additional
metric-definition distinctions.

Both consequential groups do.

This reduces the semantic burden and prevents a human unit judgement from
absorbing a source-identity problem that may already be explicit in structured
metadata.

## 12. Final T10 statement

Across the 12 arithmetic rows in the two T08/T09 product-consequential groups,
all source traces completed and all source units matched Stage F.

Both groups contain multiple distinct non-unit MetricConfig signatures:

- group `0dc7e803e7438c7faf39dfc4b461faef`: 2 units, 2 signatures;
- group `d38d8f8e547287b6b0fc78f43f310762`: 2 units, 4 signatures.

No exact non-unit signature is shared across multiple unit labels.

Therefore C-T10 is CONFIRMED.

The next justified test is a deterministic field-level decomposition of the
structured MetricConfig differences in these two groups.
