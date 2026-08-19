# TEST_RATIONALE — T02 Comparability Boundary Robustness

Status: frozen before execution.

## Claim being tested

Narrow claim:

> For a fixed frozen threshold basis, mathematically equivalent score differences at the exact declared threshold receive the same non-divergent classification, while controlled below-threshold and above-threshold cases are classified on the correct side of the boundary.

This is a boundary-robustness claim for the frozen comparability instrument.

## Why this test was selected

T01 was preregistered before execution and produced one failure out of 24 cases. The only failed case was comparability case V2 at the exact nominal 0.05 threshold.

A post-hoc three-point diagnostic attributed that failure to binary floating-point subtraction. The next dependency question is whether the effect is isolated to one score pair or affects the comparability decision boundary more generally.

This test follows the defect branch opened by T01. It is not a search for unrelated defects.

## Why this test is run before a full-corpus impact test

A full-corpus canonicalisation is substantially more expensive than a controlled boundary sweep.

If the boundary effect does not generalise across mathematically equivalent pairs, the corpus search can be scoped narrowly. If it does generalise, the corpus-level test must explicitly search all affected threshold bases.

This ordering follows the falsification principle of resolving the cheapest claim-governing uncertainty first.

## Frozen production rules under test

The frozen threshold resolver declares four bases:

- `proportion`: 0.05
- `percent`: 5.0
- `range_5pct`: 0.05 * (max_score - min_score)
- `fallback_default`: 0.05

The frozen divergence rule is strict:

`max(scores) - min(scores) > threshold`

Both variant divergence and cross-party divergence use this rule.

## Instrument and oracle

Production instrument:

- frozen `compute_variant_divergence_py`
- frozen `compute_cross_party_divergence_py`
- frozen `compute_threshold`

Reference oracle:

- score values are specified as decimal strings;
- exact intended differences are computed with Python `Decimal`;
- a case labelled `boundary` has exact decimal difference equal to the exact decimal threshold;
- a boundary case is expected to be non-divergent because the frozen rule is strict `>`.

The oracle does not replace production arithmetic. It defines the preregistered mathematical relation that production output is compared against.

## Controls

For every threshold basis:

- at least one exact-boundary pair that is binary-friendly or expected to remain stable;
- at least one exact-boundary pair chosen independently from a decimal grid;
- one below-threshold control;
- one above-threshold control.

The test includes both variant and cross-party paths.

## Free parameters

No post-run threshold tuning is allowed.

The threshold factor environment variable is removed before execution, fixing the production default factor to 1.0.

The decimal pairs are frozen in `fixtures.json` before execution.

## Possible outcomes

- `CONFIRMED`: all boundary, below, and above cases match the preregistered mathematical classification.
- `REFUTED`: at least one executable case disagrees.
- `INCONCLUSIVE`: no disagreement is observed but a claim-governing threshold basis cannot be instantiated.
- `ERROR`: source-integrity, import, environment, or harness failure prevents valid measurement.

## What the test can establish

It can establish whether the frozen comparability decision boundary is invariant across the tested mathematically equivalent decimal score pairs and threshold bases.

## What the test cannot establish

It cannot establish:

- how often affected pairs occur in the real corpus;
- whether any published aggregate count changes;
- general construct validity of comparability;
- full-pipeline correctness;
- product-level severity.

Those require a later corpus-level test.
