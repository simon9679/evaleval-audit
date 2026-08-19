# POSTRUN_DECISION — T06

Status: post-run branch decision.

## Completed result

T06 verdict:

`CONFIRMED`

Key observations:

- mixed-unit groups: 1,234
- mixed-unit rows: 28,196
- source files referenced: 4,278
- source files opened: 4,278
- complete row traces: 28,196
- row unit matches: 28,196
- row unit mismatches: 0
- group unit-set matches: 1,234
- group unit-set mismatches: 0
- pointer/index errors: 0
- evaluation-id mismatches: 0
- integrity errors: 0

## Branch that closes

Close:

`later metric-unit selection layer created the mixed-unit values`

The frozen source records already contain the same unit values.

## Attribution now justified

The audit may state:

`The mixed-unit values are already present in the frozen EEE datastore records referenced by the Stage F rows.`

The audit may not yet state:

`The original publishers supplied incorrect units.`

T06 does not verify the external publisher boundary.

## Branch that remains open

The remaining high-value question is semantic:

`Are different source-unit values under one production comparability identity
legitimate representations of one estimand, or do they represent distinct
estimands that should not be grouped for comparability?`

This requires a new preregistered instrument.

## Cost decision

A 4,278-record external publisher trace is not automatically justified.

First test frozen metric/benchmark semantics and eligibility. Only if that test
cannot resolve the issue, or finds a claim-governing mismatch, should the audit
pay for external source-level tracing.
