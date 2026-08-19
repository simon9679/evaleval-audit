# RESULT_ANALYSIS — T07 Variant Divergence Unit-Homogeneity Eligibility

Status: post-run analysis written after the completed preregistered T07 execution.

This document interprets the frozen T07 result. It does not modify the
preregistration, test rationale, source attribution, analyzer, or raw evidence.

## 1. Primary preregistered question

C-T07 asked:

> Does at least one production-applicable variant-divergence path in the actual
> mixed-unit Stage F population compute its divergence from numeric score rows
> carrying at least two distinct non-null declared `metric_unit` labels?

This is an arithmetic-input eligibility claim.

It does not decide whether two different unit labels are semantically
equivalent, convertible, correct, or incorrect.

## 2. Competing predictions frozen before execution

### P1 — arithmetic input is unit-label homogeneous

`unit_heterogeneous_applicable_variant_paths = 0`

### P2 — arithmetic input is unit-label heterogeneous

`unit_heterogeneous_applicable_variant_paths >= 1`

## 3. Primary verdict

`CONFIRMED`

Observed:

- `applicable_mixed_variant_paths = 7`
- `unit_homogeneous_applicable_variant_paths = 0`
- `unit_heterogeneous_applicable_variant_paths = 7`

Therefore P2 was observed.

All seven production-applicable mixed-unit variant-divergence paths use numeric
score rows carrying more than one distinct declared non-null unit label.

## 4. Complete reported counts

### Frozen population

- `fact_rows_scanned = 209382`
- `comparability_groups_scanned = 93495`
- `mixed_unit_groups = 1234`

The T04/T05/T06 mixed-unit population is reproduced.

### Applicable variant paths

- `applicable_mixed_variant_paths = 7`
- `unit_homogeneous_applicable_variant_paths = 0`
- `unit_heterogeneous_applicable_variant_paths = 7`

Observed heterogeneous fraction:

`7 / 7 = 100%`

The group-level unit heterogeneity is therefore present in the numeric
arithmetic input of every applicable variant path in this frozen snapshot.

### Null-unit control

- `applicable_paths_with_null_unit_score_rows = 0`

The result is not caused by an ambiguous null-unit row participating in the
score arithmetic. Every applicable path's score-bearing input is composed of
non-null declared unit labels.

### Extrema relationship

- `extrema_disjoint_unit_paths = 4`
- `extrema_overlapping_unit_paths = 3`

In four of seven paths, the unit-label set attached to the minimum-score rows
and the unit-label set attached to the maximum-score rows are disjoint.

This means that, for those four paths, the two extrema used directly in the
production raw `max(score) - min(score)` operation are associated with
different declared unit labels.

In three of seven paths, the minimum and maximum unit-label sets overlap. This
can occur when tied extrema or repeated score values are present across unit
labels. T07 does not infer a semantic relationship from that overlap.

### Production boolean outcomes

- `production_true_paths = 5`
- `production_false_paths = 2`

Five of the seven applicable mixed-unit paths are flagged by production as
variant-divergent.

Two are applicable but do not cross the production threshold.

This does not establish that any of the five positive flags are wrong. T07
tests unit-label composition of the arithmetic input, not semantic validity or
counterfactual correctness of the boolean.

### Divergence reconstruction and integrity

- `divergence_reconstruction_errors = 0`
- `group_consistency_errors = 0`
- `integrity_error_records = 0`

The frozen production `variant_divergence_magnitude` was reproducible as raw
`max(score) - min(score)` for every applicable path within the preregistered
tolerance.

The CONFIRMED verdict is therefore not caused by a reconstruction failure or
group inconsistency.

## 5. Arithmetic score-unit patterns

The seven applicable paths had these declared unit-label sets among the
numeric score rows:

- `percent | seconds = 2`
- `points | proportion | score = 1`
- `points | score = 1`
- `proportion | score = 3`

Total:

`2 + 1 + 1 + 3 = 7`

These are descriptive labels from the frozen source-backed Stage F rows.

T07 does not apply any conversion or equivalence rule between them.

## 6. What T07 establishes

T07 establishes all of the following for the frozen snapshot:

1. exactly seven actual mixed-unit groups have an applicable production
   variant-divergence path;
2. all seven arithmetic inputs contain at least two distinct non-null declared
   unit labels among numeric score rows;
3. none of the seven relies on null-unit score rows;
4. in four paths, the minimum and maximum score extrema are associated with
   disjoint unit-label sets;
5. five paths are production-positive and two production-negative;
6. production divergence magnitude is exactly reconstructable from the frozen
   numeric rows under the preregistered tolerance;
7. no integrity or group-consistency errors were observed.

## 7. What T07 does not establish

T07 does not establish:

- that different declared unit labels are semantically incompatible;
- that the source labels are correct;
- that a conversion between labels does or does not exist;
- that the production divergence magnitude is numerically wrong;
- that any of the five production-positive booleans should be false;
- that either of the two production-negative booleans should be true;
- that a public website user sees a misleading result;
- that the original publisher caused the mixed-unit state.

T04 already showed that changing only the threshold unit among observed units
did not flip any final comparability boolean.

T07 addresses a different issue: the composition of the score rows entering
the raw divergence magnitude itself.

## 8. Relationship to T04-T06

### T04

T04 established:

- 1,234 actual mixed-unit groups;
- 668 threshold-sensitive groups;
- 7 applicable mixed variant paths;
- 0 threshold-choice boolean flips.

Therefore threshold selection across observed units did not change a final
boolean in the frozen snapshot.

### T05

T05 established:

- one raw metric label per mixed group;
- one canonical metric id per mixed group;
- exact metric resolution only;
- `eee_record` unit provenance only;
- no canonical-convergence explanation.

### T06

T06 independently verified:

- 28,196 / 28,196 Stage F unit values against frozen EEE records;
- 1,234 / 1,234 group unit sets;
- zero source-pointer or identity errors.

Therefore the declared unit heterogeneity seen by T07 is source-backed at the
frozen EEE datastore boundary.

### T07

T07 now establishes that the mixed unit labels are not merely passive metadata
elsewhere in the group. They are present on the numeric rows used in the
production variant-divergence arithmetic in all seven applicable paths.

## 9. Branch decision

The following hypothesis is now confirmed:

`mixed declared units -> same production variant max-minus-min arithmetic`

The next unresolved question is narrower:

> Does the production mixed-unit divergence magnitude depend on comparing
> extrema across different declared-unit partitions, rather than being
> reproducible inside at least one single declared-unit partition?

This is the correct next descendant because it measures consequence without
inventing a unit conversion or semantic equivalence map.

## 10. Why a semantic judgement is still deferred

The labels `percent`, `seconds`, `points`, `proportion`, and `score` have
different ordinary meanings, but T07 is intentionally not a human semantic
adjudication test.

The audit has not yet established a reference rule saying which label is
correct or whether the labels can legitimately encode one source-specific
estimand.

Therefore the defensible statement is:

`production arithmetic combines numeric rows carrying different declared unit labels`

not:

`production arithmetic combines mathematically incomparable quantities`

The latter requires an additional reference or no-free-parameter operational
test.

## 11. Methodological interpretation

T07 demonstrates why group-level metadata inconsistency alone was insufficient.

Before T07, 1,234 mixed groups existed, but only seven were relevant to the
actual variant-divergence operation.

T07 then showed that all seven relevant paths are themselves unit-label
heterogeneous at the arithmetic-input level.

This is a useful narrowing sequence:

- broad corpus warning;
- actual group reconstruction;
- provenance attribution;
- source verification;
- operation-level eligibility.

Each step reduces the claim scope before a stronger conclusion is considered.

## 12. Relation to the method sources

### Falsification Protocol

The exact T07 test is not specified by the Protocol.

The Protocol contributed:

- Rule 7: test the actual product/measurement operation;
- Rule 8: freeze competing predictions before inspecting the applicable paths;
- cheapest-to-more-expensive ordering.

### Validation Handbook

The strongest direct design anchors are:

- B12: comparability eligibility must match the object's own comparison
  operation;
- U17: a statistical operation must be evaluated against the scale/design of
  the rows it operates on;
- U4: no invented unit conversion or preferred unit;
- U8: verdict granularity must not exceed measurement granularity;
- U9: the T07 branch is downstream of T04-T06;
- U11: provenance attribution is already separated from arithmetic
  eligibility.

### Additional-test catalogue

The closest supporting item is:

- Test 1, Claim–Estimand Boundary.

## 13. Evidence files

Primary T07 evidence:

- `raw/preflight.json`
- `raw/applicable_variant_paths.jsonl`
- `raw/unit_heterogeneous_paths.jsonl`
- `raw/integrity_errors.jsonl`
- `results/summary.json`

Frozen Stage F input:

- `tests/T03_corpus_boundary_impact/raw/fact_results_stage_f.parquet`
- SHA-256:
  `e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196`

Backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

## 14. Final T07 statement

All seven production-applicable variant-divergence paths inside the frozen
mixed-unit population compute their raw divergence from numeric score rows
carrying multiple distinct declared non-null `metric_unit` labels.

Four of the seven paths have minimum- and maximum-score extrema associated with
disjoint unit-label sets.

Five paths are production-positive and two are production-negative.

The production divergence magnitude is fully reconstructable in all seven
paths, with zero reconstruction, group-consistency, or integrity errors.

Therefore C-T07 is CONFIRMED.

The next justified question is whether the mixed-unit raw divergence magnitude
can be reproduced within any single declared-unit partition, without inventing
a conversion or semantic equivalence rule.
