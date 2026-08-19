# RESULT_ANALYSIS — T11 MetricConfig Field-Level Decomposition

Status: post-run analysis written after the completed preregistered T11 execution.

This document interprets the completed T11 result. It does not modify the
preregistration, test rationale, source attribution, analyzer, or raw evidence.

## 1. Primary preregistered question

C-T11 asked whether at least one of the two product-consequential groups varies
in at least one claim-governing structured MetricConfig field other than the
display-only `metric_name`.

Claim-governing field subset:

- `metric_id`
- `metric_kind`
- `metric_parameters`
- `lower_is_better`
- `score_type`
- `min_score`
- `max_score`

## 2. Competing predictions frozen before execution

### P1 — only display-name-level non-unit heterogeneity

`affected_groups_with_claim_governing_field_variation = 0`

### P2 — claim-governing structured heterogeneity exists

`affected_groups_with_claim_governing_field_variation >= 1`

## 3. Primary verdict

`CONFIRMED`

Observed:

- `affected_groups_with_claim_governing_field_variation = 2`
- `affected_groups_with_display_name_only_variation = 0`
- `affected_groups_with_no_nonunit_field_variation = 0`

Therefore P2 was observed in both product-consequential groups.

The source MetricConfig differences extend beyond display naming in both
groups.

## 4. Complete reported counts

- `affected_group_ids = 2`
- `source_rows_scanned = 12`
- `integrity_error_records = 0`

All twelve T10 source rows were included.

## 5. Per-field varying-group counts

Across the two affected groups:

- `metric_id = 2`
- `metric_name = 2`
- `metric_kind = 1`
- `metric_parameters = 0`
- `lower_is_better = 1`
- `score_type = 0`
- `min_score = 1`
- `max_score = 2`

The most important structural facts are:

1. source `metric_id` varies in both groups;
2. source `max_score` varies in both groups;
3. source `metric_kind` varies in one group;
4. source `lower_is_better` varies in one group;
5. source `min_score` varies in one group;
6. `metric_parameters` and `score_type` are constant in both groups.

## 6. Unit-disjoint value counts

Per-field counts where the varying field's exact value sets are disjoint across
the exact unit partitions:

- `metric_id = 2`
- `metric_name = 2`
- `metric_kind = 1`
- `metric_parameters = 0`
- `lower_is_better = 1`
- `score_type = 0`
- `min_score = 0`
- `max_score = 2`

Thus, in both groups, the source `metric_id` values are completely separated
by exact unit partition.

The same is true for `max_score`.

In the first group, `metric_kind` and `lower_is_better` are also completely
separated by unit partition.

`min_score` varies in the second group but its value sets are not fully
disjoint across unit partitions.

## 7. Per-group decomposition

### Group `0dc7e803e7438c7faf39dfc4b461faef`

Units:

- `percent`
- `seconds`

Varying fields:

- `metric_id`
- `metric_name`
- `metric_kind`
- `lower_is_better`
- `max_score`

Claim-governing varying fields:

- `metric_id`
- `metric_kind`
- `lower_is_better`
- `max_score`

Classification:

`claim_governing_variation`

This is the stronger of the two groups structurally because source metric
identity, metric family, score direction, and maximum score all vary.

### Group `d38d8f8e547287b6b0fc78f43f310762`

Units:

- `points`
- `score`

Varying fields:

- `metric_id`
- `metric_name`
- `min_score`
- `max_score`

Claim-governing varying fields:

- `metric_id`
- `min_score`
- `max_score`

Classification:

`claim_governing_variation`

This group has source metric identity and score-bound differences, but no
observed difference in metric family, score direction, score type, or metric
parameters.

## 8. What T11 establishes

T11 establishes, for the two product-consequential groups:

1. both vary in source-declared `metric_id`;
2. both vary in source-declared `max_score`;
3. one also varies in `metric_kind` and `lower_is_better`;
4. one also varies in `min_score`;
5. these differences are not display-name-only;
6. source `metric_id` value sets are disjoint across exact unit partitions in
   both groups;
7. all field decomposition integrity controls pass.

The strongest justified statement is:

> Both product-consequential comparability groups combine source rows that
> differ in claim-governing structured MetricConfig fields, including the
> source-declared metric identifier.

## 9. What T11 does not establish

T11 does not establish:

- that every different source `metric_id` is semantically a different estimand;
- that any source field is correct;
- that the source publisher intended the field exactly as stored;
- that the canonical resolver is necessarily wrong to map two source ids to
  one canonical metric;
- which source rows should be grouped;
- whether a semantic alias relationship exists between the source metric ids;
- original-publisher provenance.

Those questions require tracing the identity transformation and, only if still
needed, a narrow reference adjudication.

## 10. Relationship to T05

T11 creates an important unresolved transformation question.

T05 reported, across the actual mixed-unit population:

- one Stage F `metric_raw` per group;
- one Stage F canonical `metric_id` per group;
- `metric_resolution_strategy = exact`.

T11 now shows that, in both product-consequential groups, the frozen source EEE
rows contain multiple source `metric_id` values.

Therefore the next test must trace how multiple source-declared metric ids
become one Stage F raw/canonical metric identity.

This is a transformation/provenance question, not yet a semantic judgement.

## 11. Branch decision

Proceed to a source-to-canonical metric identity trace over the same twelve
rows.

The next test should compare, row by row:

- source `metric_config.metric_id`;
- source metric name/kind/bounds;
- Stage F `metric_raw`;
- Stage F `metric_id`;
- Stage F `metric_resolution_strategy`;
- Stage F `metric_key`;
- optional `metric_id_effective` / `metric_key_effective` when present.

The central question is whether different source-declared metric ids collapse
into one production metric identity through the non-structured fallback path.

## 12. Methodological interpretation

T11 shows why field-level decomposition should precede semantic adjudication.

The finding is no longer merely:

`different unit labels`

It is now:

`different unit labels + different source metric ids + different score bounds`

and, in one group:

`different metric kind + different score direction`

That materially changes what the next audit step must explain.

The cheapest next step is not a human judgement. It is tracing the
canonicalization path that produced one production metric identity from these
source definitions.

## 13. Final T11 statement

Both product-consequential groups contain claim-governing MetricConfig
variation.

Source `metric_id` and `max_score` vary in both groups. The `percent | seconds`
group additionally varies in `metric_kind` and `lower_is_better`; the
`points | score` group additionally varies in `min_score`.

All twelve rows were included and `integrity_error_records = 0`.

Therefore C-T11 is CONFIRMED.

The next justified test is a deterministic source-metric-id to Stage F
canonical-identity trace.
