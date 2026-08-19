# POSTRUN_DECISION — T12

Status: post-run branch decision.

## Completed result

T12 verdict:

`CONFIRMED`

Key values:

- affected groups: 2
- source rows: 12
- joined Stage F rows: 12
- distinct source metric ids: 6
- groups with multiple source metric ids: 2
- groups with one Stage F metric raw: 2
- groups with one Stage F canonical metric id: 2
- groups with one Stage F metric key: 2
- groups with structured-strategy rows: 0
- groups with fallback source-id collapse: 2
- row identity errors: 0
- integrity errors: 0

## Confirmed transformation

Both consequential groups follow:

`multiple source metric ids -> fallback raw "score" -> canonical "score" ->
metric_key "score"`

## Next unresolved component

Why did the structured metric-id pre-step reject all six source ids?

Next test:

`structured source id -> registry segment hits -> rejection class`

Do not perform semantic alias adjudication before this deterministic component
attribution.
