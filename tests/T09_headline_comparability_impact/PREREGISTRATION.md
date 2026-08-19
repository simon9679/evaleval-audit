# PREREGISTRATION — T09 Headline Comparability Aggregate Impact

Status: registered before T09 execution.

## Frozen prerequisites

Backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

T03 Stage F Parquet SHA-256:

`e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196`

Required T08 result:

- verdict = `CONFIRMED`;
- applicable_mixed_variant_paths = 7;
- production_true_paths = 5;
- production_false_paths = 2;
- positive_to_positive_paths = 3;
- positive_to_negative_paths = 2;
- negative_to_negative_paths = 2;
- negative_to_positive_paths = 0;
- divergence_reconstruction_errors = 0;
- group_consistency_errors = 0;
- invariant_errors = 0;
- integrity_error_records = 0.

Required T08 raw evidence:

`raw/positive_to_negative_paths.jsonl`

must contain exactly two records with two unique non-null
`comparability_group_id` values.

## Production aggregate

Reproduce the frozen overall comparability block over all non-null
`comparability_group_id` values:

- `total_triples` =
  count distinct group id;
- `variant_divergent_count` =
  count distinct group id where `has_variant_divergence` is true;
- `cross_party_divergent_count` =
  count distinct group id where `has_cross_party_divergence` is true;
- `groups_with_variant_check` =
  count distinct group id where `has_variant_divergence` is not null;
- `groups_with_cross_party_check` =
  count distinct group id where `has_cross_party_divergence` is not null.

## Counterfactual aggregate

For exactly the two T08 positive-to-negative ids:

`has_variant_divergence := FALSE`

All other Stage F values remain frozen.

Recompute the same five aggregate counts.

## Primary quantity

`headline_variant_divergent_count_delta =
 counterfactual_variant_divergent_count
 - production_variant_divergent_count`

## Competing predictions

### P1

`headline_variant_divergent_count_delta = 0`

### P2

`headline_variant_divergent_count_delta < 0`

## Primary verdict

- `CONFIRMED` — P2 is observed and all integrity controls pass.
- `REFUTED` — P1 is observed and all integrity controls pass.
- `INCONCLUSIVE` — the frozen artifact is readable but the affected groups,
  group flags, or aggregate reconstruction are inconsistent.
- `ERROR` — prerequisite evidence, dependency, backend commit, or Stage F
  artifact cannot be verified/read.

The verdict applies only to C-T09.

## Integrity controls

The test must verify:

- exactly two unique T08 affected group ids;
- both ids exist in Stage F;
- both have internally constant production `has_variant_divergence = TRUE`;
- neither has null production variant applicability;
- changing those booleans does not change:
  - total group count;
  - variant-eligible group count;
  - cross-party divergent count;
  - cross-party eligible count;
- no unaffected group's variant flag changes.

Any violation is an integrity failure, not an EvalEval defect.

## Required raw outputs

- `raw/affected_groups.jsonl`
- `raw/production_headline_comparability.json`
- `raw/counterfactual_headline_comparability.json`
- `raw/integrity_errors.jsonl`

## Required summary counts

At minimum:

- fact_rows_scanned;
- comparability_groups_scanned;
- affected_group_ids;
- affected_groups_present;
- affected_groups_production_true;
- production_total_triples;
- production_variant_divergent_count;
- production_cross_party_divergent_count;
- production_groups_with_variant_check;
- production_groups_with_cross_party_check;
- counterfactual_total_triples;
- counterfactual_variant_divergent_count;
- counterfactual_cross_party_divergent_count;
- counterfactual_groups_with_variant_check;
- counterfactual_groups_with_cross_party_check;
- headline_variant_divergent_count_delta;
- production_variant_divergent_share_of_total;
- counterfactual_variant_divergent_share_of_total;
- production_variant_divergent_share_of_eligible;
- counterfactual_variant_divergent_share_of_eligible;
- integrity_error_records.

All counts and rates must be printed.

## Branch decision

If `CONFIRMED`:

- the audit may state that the T08 operational counterfactual changes a frozen
  frontend-consumed headline comparability aggregate;
- do not call the aggregate semantically wrong;
- semantic/reference adjudication is now justified for only the two affected
  product-consequential paths.

If `REFUTED`:

- the T08 internal flips do not affect the frozen headline comparability
  aggregate;
- stop this descendant for headline/public aggregate impact.

If `INCONCLUSIVE` or `ERROR`:

- repair the measurement;
- do not attribute harness failure to EvalEval.
