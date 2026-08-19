# POSTRUN_DECISION — T10

Status: post-run branch decision.

## Completed result

T10 verdict:

`CONFIRMED`

Key values:

- affected groups: 2
- affected arithmetic rows: 12
- complete source rows: 12
- source unit matches: 12
- source unit mismatches: 0
- affected groups with non-unit heterogeneity: 2
- affected groups with a single non-unit signature: 0
- units with multiple signatures: 1
- signatures shared across multiple units: 0
- integrity errors: 0

## Branch that is confirmed

Confirmed:

`product-consequential mixed-unit groups -> additional structured source
MetricConfig heterogeneity beyond metric_unit`

## Next branch

Next:

`non-unit signature heterogeneity -> exact field-level decomposition`

No semantic unit adjudication should be introduced before this decomposition.

## Why

The first group has 2 signatures across 2 units.

The second group has 4 signatures across 2 units.

Without knowing which schema fields differ, a semantic unit-only test would be
underspecified and could attribute a broader metric-definition problem solely
to `metric_unit`.
