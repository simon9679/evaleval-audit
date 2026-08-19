# RESULT_ANALYSIS — T09 Headline Comparability Aggregate Impact

Status: post-run analysis written after the completed preregistered T09 execution.

This document interprets the completed T09 result. It does not modify the
preregistration, test rationale, source attribution, analyzer, or raw evidence.

## 1. Primary preregistered question

C-T09 asked whether replacing only the two T08 positive-to-negative
`has_variant_divergence` group booleans with their frozen T08 counterfactual
values decreases the frozen overall `headline.json` comparability
`variant_divergent_count`.

Primary quantity:

`headline_variant_divergent_count_delta =
 counterfactual_variant_divergent_count
 - production_variant_divergent_count`

## 2. Competing predictions frozen before execution

### P1 — no headline aggregate consequence

`headline_variant_divergent_count_delta = 0`

### P2 — headline aggregate consequence exists

`headline_variant_divergent_count_delta < 0`

## 3. Primary verdict

`CONFIRMED`

Observed:

- production `variant_divergent_count = 343`
- counterfactual `variant_divergent_count = 341`
- `headline_variant_divergent_count_delta = -2`

Therefore P2 was observed.

The two T08 consequential group booleans contribute directly to the frozen
frontend-consumed headline comparability aggregate.

## 4. Complete reported counts

### Frozen corpus

- `fact_rows_scanned = 209382`
- `comparability_groups_scanned = 93495`
- `affected_group_ids = 2`
- `affected_groups_present = 2`
- `affected_groups_production_true = 2`

Both T08 affected group ids are present in Stage F and both are production
positive before the counterfactual.

### Production headline comparability block

- `production_total_triples = 93495`
- `production_variant_divergent_count = 343`
- `production_cross_party_divergent_count = 57`
- `production_groups_with_variant_check = 862`
- `production_groups_with_cross_party_check = 886`

### Counterfactual headline comparability block

- `counterfactual_total_triples = 93495`
- `counterfactual_variant_divergent_count = 341`
- `counterfactual_cross_party_divergent_count = 57`
- `counterfactual_groups_with_variant_check = 862`
- `counterfactual_groups_with_cross_party_check = 886`

Only the preregistered variant-positive count changes.

The following remain exactly invariant:

- total comparability groups;
- variant eligibility;
- cross-party positive count;
- cross-party eligibility.

This is the expected isolation behavior.

## 5. Aggregate effect size

### Share of all comparability groups

Production:

`343 / 93495 = 0.003668645382105995`

Counterfactual:

`341 / 93495 = 0.0036472538638429863`

Absolute delta:

`-0.000021391518263008842`

Expressed in percentage points:

`-0.0021391518263008842 percentage points`

### Share of variant-eligible groups

Production:

`343 / 862 = 0.39791183294663574`

Counterfactual:

`341 / 862 = 0.39559164733178653`

Absolute delta:

`-0.0023201856148492017`

Expressed in percentage points:

`-0.23201856148492017 percentage points`

### Relative change in the positive count

The positive count changes from 343 to 341:

`2 / 343 = 0.0058309037900874635`

Relative decrease:

`0.5830903790087464%`

These values describe magnitude. T09 preregistered no materiality threshold,
so no material / immaterial verdict is assigned.

## 6. Integrity

- `integrity_error_records = 0`

The result is not explained by a missing affected id, inconsistent production
flag, eligibility change, cross-party change, or aggregate reconstruction
failure.

## 7. What T09 establishes

T09 establishes that:

1. both T08 positive-to-negative groups are present in the frozen Stage F
   product population;
2. both are production `has_variant_divergence = TRUE`;
3. the frozen headline aggregate counts both groups among the 343
   variant-divergent groups;
4. replacing only those two booleans by the T08 counterfactual values changes
   the headline count to 341;
5. no other headline comparability count changes;
6. the exact aggregate delta is -2.

The strongest justified statement is:

> The two T08 operationally consequential variant-divergence flags change the
> frozen product-facing headline variant-divergent count from 343 to 341.

## 8. What T09 does not establish

T09 does not establish:

- that either affected group is semantically invalid;
- that exact unit-label partitioning is the correct normative comparability
  rule;
- that the original publisher is responsible;
- that the live site at another point in time has the same counts;
- that users were materially misled;
- that a 2-count or 0.232-percentage-point eligible-share change is materially
  important.

No materiality threshold was preregistered.

## 9. Relationship to T04-T08

The branch now has the following evidence chain:

1. T04: 1,234 actual mixed-unit groups; zero threshold-choice boolean flips.
2. T05: canonical metric convergence does not explain the mixed-unit state.
3. T06: all mixed-unit values reproduce from frozen EEE source JSON.
4. T07: all 7 applicable mixed-unit variant paths use multiple declared units
   in the numeric range input.
5. T08: 2 of 5 production-positive paths become negative under exact-label
   within-unit arithmetic with the same threshold.
6. T09: those two booleans change the frozen headline positive count from
   343 to 341.

Thus the branch has progressed from metadata heterogeneity to a small but
measurable product-aggregate consequence.

## 10. Branch decision

Product aggregate exposure is confirmed.

Semantic/reference adjudication is now justified, but only for the two affected
groups rather than for all 1,234 mixed-unit groups.

Before introducing an external semantic unit ontology, the cheapest remaining
question is source-internal:

> Do the two affected groups contain different source-declared metric
> configurations beyond `metric_unit`, or is `metric_unit` the only
> claim-governing MetricConfig field that varies?

That is the recommended T10 gate.

## 11. Why source MetricConfig comes before external semantic adjudication

The frozen EEE schema gives structured fields intended to define the metric,
including:

- stable metric id;
- metric display name;
- normalized metric kind;
- metric parameters;
- direction;
- score type;
- score bounds;
- metric unit.

If different unit partitions also carry different structured metric
definitions, the grouping problem can be localized without inventing a
semantic conversion rule.

If those fields are otherwise identical, the audit can then proceed to a
narrow external-reference unit adjudication.

## 12. Methodological interpretation

T09 demonstrates why public/product exposure should be measured before
expensive semantic adjudication.

The T08 effect is real but small at corpus scale:

- two groups out of 93,495 total;
- two out of 862 variant-eligible;
- two out of 343 production-positive.

This prevents a local defect candidate from being rhetorically inflated into a
large corpus-wide effect.

At the same time, the effect is not zero and it reaches a product-facing
aggregate, so the branch remains worth resolving.

## 13. Evidence files

Primary T09 evidence:

- `raw/preflight.json`
- `raw/affected_groups.jsonl`
- `raw/production_headline_comparability.json`
- `raw/counterfactual_headline_comparability.json`
- `raw/integrity_errors.jsonl`
- `results/summary.json`

Frozen Stage F input:

- `tests/T03_corpus_boundary_impact/raw/fact_results_stage_f.parquet`
- SHA-256:
  `e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196`

Backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

## 14. Final T09 statement

The two T08 positive-to-negative groups are both counted in the frozen
production headline comparability aggregate.

Replacing only those two production-positive booleans with their T08
counterfactual values changes `variant_divergent_count` from 343 to 341, with
all other headline comparability counts unchanged.

The relative decrease in the positive count is approximately 0.5831%. The
eligible-group share decreases by approximately 0.2320 percentage points, and
the all-group share decreases by approximately 0.002139 percentage points.

All integrity controls pass.

Therefore C-T09 is CONFIRMED.

This establishes a real but small frozen product-aggregate consequence.
Semantic correctness of the two affected groups remains unresolved.
