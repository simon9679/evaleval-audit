# POSTRUN_DECISION — T09

Status: post-run branch decision.

## Completed result

T09 verdict:

`CONFIRMED`

Key values:

- affected groups: 2
- affected groups present: 2
- affected groups production-positive: 2
- production headline variant-divergent count: 343
- counterfactual headline variant-divergent count: 341
- delta: -2
- production eligible share: 0.39791183294663574
- counterfactual eligible share: 0.39559164733178653
- integrity errors: 0

## Branch that is confirmed

Confirmed:

`T08 operational boolean consequence -> frozen headline aggregate consequence`

## Magnitude

The headline count changes by two groups.

This is:

- approximately 0.5831% of the production positive count;
- approximately 0.2320 percentage points of the variant-eligible population;
- approximately 0.002139 percentage points of the full comparability-group
  population.

No materiality label is assigned because none was preregistered.

## Next branch

Next:

`two affected groups -> source MetricConfig heterogeneity beyond metric_unit`

Only after that source-internal gate should the audit introduce external
semantic unit reference rules if they remain necessary.
