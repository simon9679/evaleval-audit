# TEST_RATIONALE — T07 Variant Divergence Unit-Homogeneity Eligibility

Status: frozen before execution.

## Primary claim C-T07

> At least one production-applicable variant-divergence path in the actual
> mixed-unit Stage F population computes its divergence from numeric score rows
> carrying at least two distinct non-null declared `metric_unit` labels.

This is an input-eligibility claim about the frozen production arithmetic.

It is not a claim that two different labels necessarily denote
non-convertible physical dimensions.

## Why this test was selected

T04 found seven production-applicable variant paths inside the mixed-unit
population.

However, group-level mixed metadata does not prove that the rows actually used
by `max(scores) - min(scores)` are themselves mixed-unit. The extra unit label
could belong only to a row without a numeric score or otherwise not contribute
to the production divergence arithmetic.

T07 resolves that ambiguity before any semantic interpretation.

## Why this test is run now

T06 verified that the Stage F unit labels reproduce the frozen EEE source
records exactly.

Therefore the next uncertainty is no longer provenance. It is whether the
actual production arithmetic receives score-bearing rows with more than one
declared unit label.

This can be answered deterministically from the already-hashed Stage F Parquet
without another production run or external source access.

## Production row set

For each actual mixed-unit comparability group:

- production variant applicability is represented by non-null
  `has_variant_divergence`;
- the arithmetic score rows are all group rows with non-null numeric `score`,
  matching the frozen production function's score selection;
- the score-unit set is the set of distinct non-null `metric_unit` labels among
  those arithmetic score rows.

T07 does not select a preferred unit.

## Competing predictions

### P1 — arithmetic input is unit-label homogeneous

For every production-applicable variant path:

`count(distinct non-null metric_unit among arithmetic score rows) <= 1`

Observable result:

`unit_heterogeneous_applicable_variant_paths = 0`

Under P1, the mixed unit labels observed at group level do not enter the same
production `max-min` score operation.

### P2 — arithmetic input is unit-label heterogeneous

At least one production-applicable variant path has:

`count(distinct non-null metric_unit among arithmetic score rows) >= 2`

Observable result:

`unit_heterogeneous_applicable_variant_paths >= 1`

Under P2, production performs one raw variant-divergence operation over numeric
rows carrying multiple declared unit labels.

## Secondary descriptive measurements

For every applicable mixed-unit variant path T07 records:

- full group unit set;
- arithmetic score-row unit set;
- score-row count;
- score rows with null unit;
- minimum score and the unit labels attached to rows at that minimum;
- maximum score and the unit labels attached to rows at that maximum;
- whether minimum and maximum unit-label sets overlap;
- production divergence magnitude;
- recomputed raw `max-min`;
- production threshold and basis;
- production boolean.

T07 also counts paths where the minimum and maximum score are associated only
with disjoint unit-label sets.

That count is descriptive and is not the primary verdict rule.

## Integrity controls

The test must verify:

- backend commit unchanged;
- T03 Stage F Parquet SHA unchanged;
- T04 reports 1,234 mixed groups and 7 variant-applicable paths;
- T06 reports CONFIRMED with 28,196 / 28,196 row matches and 1,234 / 1,234
  group unit-set matches;
- recomputed mixed group count is 1,234;
- recomputed production-applicable mixed variant path count is 7;
- production variant fields are internally constant within each group;
- recomputed `max(score) - min(score)` matches the frozen production divergence
  magnitude for every applicable path.

Integrity failure is not an EvalEval defect.

## What T07 can establish

T07 can establish whether one frozen production variant-divergence arithmetic
operation receives numeric rows with one or multiple declared unit labels.

## What T07 cannot establish

T07 cannot establish:

- whether different unit labels are semantically equivalent;
- whether a conversion between labels exists outside the frozen implementation;
- which unit is correct;
- whether EEE or the original publisher should normalize them;
- whether mixed-label arithmetic changes the final boolean;
- whether the public website exposes a harmful result.

T04 separately tested threshold-unit boolean sensitivity and found zero
classification-sensitive paths.
