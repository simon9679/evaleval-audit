# POSTRUN_DECISION — T05

Status: post-run branch decision.

## Completed result

T05 verdict:

`REFUTED`

Key observations:

- actual mixed-unit groups: 1,234
- single raw metric groups: 1,234
- multi raw metric groups: 0
- unresolved metric groups: 0
- single canonical metric id groups: 1,234
- multi canonical metric id groups: 0
- multi resolution-strategy groups: 0
- resolution strategy pattern: `exact` in all 1,234 groups
- multi unit-provenance groups: 0
- unit provenance pattern: `eee_record` in all 1,234 groups
- full canonical-convergence groups: 0
- partial/mixed convergence groups: 0
- integrity errors: 0

## Branch that stops

Stop:

`multiple raw metric labels -> canonical resolution convergence -> mixed units`

The preregistered structural condition never occurred.

## Branch that continues

Continue:

`pipeline reports eee_record unit provenance -> verify frozen source records`

The next test should independently confirm whether the source records pointed to
by Stage F contain the unit values attributed to them.

## Why a source trace is now justified

Before T05, source tracing all mixed-unit groups would have been premature
because the variation could have been introduced by:

- raw metric extraction;
- canonical metric resolution;
- mixed resolution strategies;
- heuristic unit inference;
- registry metadata;
- upstream record metadata.

T05 removes several of those branches simultaneously.

The remaining high-information branch can now be tested directly against the
frozen source records without a new full production run.

## Forbidden inference

Do not yet state:

`upstream EEE caused the mixed units`

T05 only establishes that the frozen EvalEval pipeline labels all unit values in
the mixed population as `eee_record` provenance.

Independent source verification is still required.
