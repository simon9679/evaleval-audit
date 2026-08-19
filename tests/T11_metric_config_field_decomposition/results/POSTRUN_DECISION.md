# POSTRUN_DECISION — T11

Status: post-run branch decision.

## Completed result

T11 verdict:

`CONFIRMED`

Key values:

- affected groups: 2
- source rows: 12
- groups with claim-governing variation: 2
- display-name-only groups: 0
- integrity errors: 0

Field variation:

- metric_id: 2 / 2 groups
- max_score: 2 / 2
- metric_kind: 1 / 2
- lower_is_better: 1 / 2
- min_score: 1 / 2
- metric_parameters: 0 / 2
- score_type: 0 / 2

## Branch that is confirmed

Confirmed:

`product-consequential grouping -> source-declared claim-governing metric
definition heterogeneity`

## Immediate unresolved question

T05 previously observed one Stage F raw/canonical metric identity per mixed
group, while T11 now observes multiple source metric ids in both consequential
groups.

The next test must resolve that transformation.

## Next branch

`source metric ids -> Stage C/F metric_raw -> canonical metric_id -> metric_key`

Do not introduce semantic alias judgement before tracing this path.
