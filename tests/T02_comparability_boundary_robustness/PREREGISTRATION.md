# PREREGISTRATION — T02 Comparability Boundary Robustness

Status: registered before execution.

## Frozen object

Backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

T01 result motivating this branch:

- cases: 24
- pass: 23
- fail: 1
- failed case: V2
- failed signal: comparability

The T01 verdict remains unchanged and is not recomputed by T02.

## Primary hypothesis

H1:

For each frozen threshold basis, all decimal score pairs whose exact decimal difference equals the exact declared threshold are classified as non-divergent by both comparability paths.

Below-threshold controls are non-divergent.

Above-threshold controls are divergent.

Competing prediction H0:

At least one production path classifies an exact-boundary pair as divergent, or misclassifies a below/above control.

## Threshold bases

B1 proportion:
- metric config: `metric_unit=proportion`
- exact threshold: 0.05

B2 percent:
- metric config: `metric_unit=percent`
- exact threshold: 5.0

B3 range_5pct:
- metric config: `min_score=-1`, `max_score=1`
- exact threshold: 0.10

B4 fallback_default:
- metric config: empty
- exact threshold: 0.05

## Decision boundary

Production rule is strict `>`.

Therefore:

- exact difference < threshold => false
- exact difference = threshold => false
- exact difference > threshold => true

## Test paths

Every fixture is evaluated through:

1. variant divergence with two rows whose declared setup differs;
2. cross-party divergence with two distinct named reporting organisations.

## Decimal oracle

The fixture stores score values and thresholds as decimal strings.

Exact classification is computed using `Decimal`.

Production receives `float` values parsed from those same strings.

This allows the test to detect classification changes caused solely by floating-point representation or subtraction.

## Verdict rule

- `CONFIRMED`: zero failed executable cases.
- `REFUTED`: one or more failed executable cases.
- `INCONCLUSIVE`: zero failures but one or more claim-governing cases cannot run.
- `ERROR`: valid execution is prevented by source-integrity, environment, import, or harness failure.

No corpus-level severity conclusion is permitted from T02.
