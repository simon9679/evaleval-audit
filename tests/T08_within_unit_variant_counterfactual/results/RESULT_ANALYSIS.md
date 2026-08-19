# RESULT_ANALYSIS — T08 Within-Unit Variant Divergence Counterfactual

Status: post-run analysis written after the completed preregistered T08 execution.

This document interprets the frozen T08 result. It does not modify the
preregistration, test rationale, source attribution, analyzer, or raw evidence.

## 1. Primary preregistered question

C-T08 asked:

> Does at least one production-positive mixed-unit variant-divergence path
> become negative when the raw divergence is constrained to the largest range
> obtainable inside any one exact declared non-null `metric_unit` partition,
> while keeping the frozen production threshold unchanged?

The counterfactual changed exactly one eligibility rule:

- production: one raw `max(score) - min(score)` across all numeric rows in the
  comparability group;
- T08: compute a raw range separately inside each exact stored `metric_unit`
  partition and keep the largest within-unit range.

No unit conversion, semantic equivalence map, preferred unit, or threshold
recomputation was introduced.

## 2. Competing predictions frozen before execution

### P1 — production-positive decisions survive exact-label eligibility

`positive_to_negative_paths = 0`

### P2 — at least one production-positive decision depends on cross-label
arithmetic

`positive_to_negative_paths >= 1`

## 3. Primary verdict

`CONFIRMED`

Observed:

- `production_true_paths = 5`
- `positive_to_positive_paths = 3`
- `positive_to_negative_paths = 2`

Therefore P2 was observed.

Two of the five frozen production-positive variant-divergence paths become
negative when the raw score range is restricted to the largest exact-unit
partition while the production threshold is held fixed.

Observed positive-flag transition fraction:

`2 / 5 = 40%`

This is an operational dependence result.

It does not by itself establish that the exact unit labels are semantically
incompatible or that either production flag is wrong.

## 4. Complete reported counts

### Frozen population

- `fact_rows_scanned = 209382`
- `comparability_groups_scanned = 93495`
- `mixed_unit_groups = 1234`
- `applicable_mixed_variant_paths = 7`

The complete T07 applicable population was reproduced.

### Frozen production outcomes

- `production_true_paths = 5`
- `production_false_paths = 2`

Production therefore marks 5 / 7 applicable mixed-unit paths as
variant-divergent.

### Counterfactual transitions

- `positive_to_positive_paths = 3`
- `positive_to_negative_paths = 2`
- `negative_to_negative_paths = 2`
- `negative_to_positive_paths = 0`

All seven applicable paths are accounted for:

`3 + 2 + 2 + 0 = 7`

The production-positive population is also fully accounted for:

`3 + 2 = 5`

The production-negative population is fully accounted for:

`2 + 0 = 2`

The impossible monotonicity transition did not occur:

`negative_to_positive_paths = 0`

This is consistent with the fact that an exact-unit partition range cannot
exceed the global range computed over all rows.

### Counterfactual final states

- `counterfactual_true_paths = 3`
- `counterfactual_false_paths = 4`

These totals match the transition table:

- true: 3 positive-to-positive;
- false: 2 positive-to-negative + 2 negative-to-negative = 4.

## 5. Magnitude relationship

- `production_divergence_gt_max_within_unit_paths = 4`
- `production_divergence_eq_max_within_unit_paths = 3`
- `production_divergence_lt_max_within_unit_paths = 0`

Therefore:

- in 4 / 7 applicable paths, the global production divergence is strictly
  larger than every exact-unit partition range;
- in 3 / 7 paths, at least one exact-unit partition reproduces the full
  production divergence;
- in 0 / 7 paths does the within-unit range exceed the global range.

This exactly matches the monotonicity expected from the preregistered
counterfactual.

The four `global > max-within` paths are the only paths in which cross-label
membership contributes strictly to the magnitude of the production range.

Two of those four produce a consequential boolean transition.

The other two have a larger production magnitude under cross-label arithmetic
but remain on the same side of the frozen threshold.

## 6. Unit-pattern transition breakdown

Observed transitions:

- `percent | seconds :: positive_to_negative = 1`
- `percent | seconds :: positive_to_positive = 1`
- `points | proportion | score :: positive_to_positive = 1`
- `points | score :: positive_to_negative = 1`
- `proportion | score :: negative_to_negative = 2`
- `proportion | score :: positive_to_positive = 1`

These six pattern-transition cells account for all seven applicable paths:

`1 + 1 + 1 + 1 + 2 + 1 = 7`

The two consequential positive-to-negative transitions occur in:

1. one `percent | seconds` path;
2. one `points | score` path.

This is descriptive label evidence only.

T08 does not assert that either pair is semantically non-convertible.

## 7. Integrity and reconstruction

- `divergence_reconstruction_errors = 0`
- `group_consistency_errors = 0`
- `invariant_errors = 0`
- `integrity_error_records = 0`

Therefore the CONFIRMED verdict is not explained by:

- disagreement with the frozen production divergence magnitude;
- unstable group-level production fields;
- a within-unit range exceeding the global range;
- an impossible negative-to-positive transition;
- an input-evidence failure.

## 8. What T08 establishes

T08 establishes all of the following for the frozen snapshot:

1. seven mixed-unit groups have applicable production variant-divergence
   calculations;
2. five of those seven are production-positive;
3. restricting the score-range calculation to exact declared unit partitions,
   while keeping the frozen threshold fixed, changes two of the five positive
   flags to negative;
4. four of seven global production ranges are strictly larger than every
   within-unit range;
5. three of seven global ranges are reproducible inside at least one exact-unit
   partition;
6. no counterfactual negative-to-positive transition occurs;
7. all reconstruction, consistency, and monotonicity controls pass.

The strongest justified operational statement is:

> Two frozen production-positive variant-divergence flags depend on allowing
> numeric scores from different exact declared `metric_unit` partitions to
> contribute to one global range calculation.

## 9. What T08 does not establish

T08 does not establish:

- that exact unit-label equality is the only valid semantic comparability rule;
- that `percent` and `seconds` necessarily represent incompatible estimands in
  the affected source context;
- that `points` and `score` necessarily represent incompatible estimands;
- that any conversion or equivalence relationship is impossible;
- which source unit is correct;
- that the original publisher caused the state;
- that EvalEval should split, normalize, or reject these groups;
- that the two production-positive flags are semantically wrong;
- that either affected flag is visible to a user or governs a published public
  claim.

The last two questions require separate evidence.

## 10. Relationship to T04-T07

### T04 — threshold-choice consequence

T04 found:

- 1,234 actual mixed-unit groups;
- 668 threshold-sensitive groups;
- 7 applicable variant paths;
- 0 final boolean flips when only the threshold unit was varied across observed
  units.

Therefore the relevant consequence did not arise from threshold selection.

### T05 — canonical identity attribution

T05 found:

- one raw metric label in all 1,234 mixed groups;
- one canonical metric id in all 1,234;
- exact metric resolution only;
- EEE-record unit provenance only;
- no canonical-convergence explanation.

### T06 — source verification

T06 independently reproduced:

- 28,196 / 28,196 Stage F unit values from frozen EEE source JSON;
- 1,234 / 1,234 group unit sets;
- zero source-pointer, index, identity, or integrity errors.

Therefore the unit-label heterogeneity is already present at the frozen EEE
datastore boundary.

### T07 — arithmetic-input eligibility

T07 found:

- 7 / 7 applicable mixed-unit variant paths contain multiple exact declared
  unit labels among the numeric score rows;
- 4 / 7 have disjoint unit-label sets at the global score extrema;
- 5 / 7 are production-positive.

### T08 — boolean consequence under fixed threshold

T08 now shows:

- 2 / 5 production-positive flags disappear under the exact-label partition
  counterfactual;
- the effect is not produced by threshold recomputation;
- the effect is specifically due to the row-eligibility boundary of the global
  range operation.

## 11. Branch decision

The arithmetic-consequence branch is now strong enough to justify a
product-surface gate.

The next question should be:

> Are either of the two T08 positive-to-negative paths exposed through a frozen
> public-facing EvalEval output, view, API field, or claim-governing aggregate?

Why this comes next:

- if neither affected path reaches the public/product surface, expensive
  semantic adjudication has low immediate product value;
- if one or both do reach a public surface, semantic/reference adjudication
  becomes claim-governing and justified.

The next test should use the two frozen
`raw/positive_to_negative_paths.jsonl` records as its complete population.

No manual case selection is needed.

## 12. Why semantic adjudication is still not the next immediate step

T08 has produced an operationally consequential counterfactual, but not a
semantic reference result.

A human could look at `percent | seconds` and conclude that the values are
incompatible. That would be an intuitive semantic judgement, not yet a
preregistered reference instrument.

Before paying that adjudication cost, the audit should establish whether the
affected decisions actually reach a product/user-facing surface.

This preserves the Protocol's cheapest-to-more-expensive structure.

## 13. Methodological interpretation

T08 demonstrates a useful distinction between:

- mechanism presence;
- arithmetic participation;
- magnitude consequence;
- boolean consequence;
- semantic invalidity;
- public product impact.

The audit did not collapse these layers.

The branch progressed as:

`mixed units`
`-> source verified`
`-> enter production arithmetic`
`-> alter global range magnitude`
`-> flip 2 production-positive booleans`
`-> public exposure still unknown`

This prevents both underclaiming and overclaiming.

## 14. Relation to the method sources

### Falsification Protocol

The exact T08 counterfactual is not specified by the Protocol.

The Protocol contributed:

- Rule 7: test product/decision consequence rather than stopping at mechanism;
- Rule 8: freeze the counterfactual and competing predictions before the run;
- cheapest-to-more-expensive ordering.

### Validation Handbook

The strongest direct design anchors are:

- B12: comparability eligibility is claim-governing;
- U17: the statistical operation must be evaluated against its scale/design;
- U4: no invented conversion or preferred-unit parameter;
- U8: verdict scope is limited to the exact-label counterfactual;
- U14: comparison claims require a measurement capable of resolving the
  effect;
- U9: T08 is downstream of T07 in the evidence DAG.

### Additional-test catalogue

The closest supporting item is:

- Test 1, Claim–Estimand Boundary.

## 15. Evidence files

Primary T08 evidence:

- `raw/preflight.json`
- `raw/path_counterfactuals.jsonl`
- `raw/positive_to_negative_paths.jsonl`
- `raw/integrity_errors.jsonl`
- `results/summary.json`

Frozen Stage F input:

- `tests/T03_corpus_boundary_impact/raw/fact_results_stage_f.parquet`
- SHA-256:
  `e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196`

Backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

## 16. Final T08 statement

Among seven production-applicable mixed-unit variant-divergence paths in the
frozen EvalEval Stage F corpus, five are production-positive.

Under a preregistered counterfactual that keeps the frozen production
threshold unchanged but restricts the raw score-range calculation to exact
declared `metric_unit` partitions, two of those five positive flags become
negative.

Four of seven production ranges are strictly larger than every within-unit
range; three are exactly reproducible within at least one unit partition.

All reconstruction, consistency, monotonicity, and integrity controls pass.

Therefore C-T08 is CONFIRMED.

The next justified audit gate is product/public exposure of the two affected
positive-to-negative paths. Semantic correctness remains unresolved until a
separate reference instrument is applied.
