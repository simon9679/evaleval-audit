# T08 — Within-Unit Variant Divergence Counterfactual

Status before execution: preregistered package.

T08 tests whether any production-positive mixed-unit variant-divergence flag
depends on combining score extrema across different exact declared
`metric_unit` labels.

The counterfactual changes exactly one eligibility rule:

- production: one raw `max(score) - min(score)` across all numeric rows in the
  comparability group;
- T08 counterfactual: compute a raw range separately inside each exact non-null
  `metric_unit` partition and take the largest within-unit range.

The frozen production threshold is held fixed.

No unit conversion, semantic equivalence map, preferred unit, or manual label
classification is introduced.

Run order:

1. `python .\tests\T08_within_unit_variant_counterfactual\preflight.py`
2. `python .\tests\T08_within_unit_variant_counterfactual\verify_prereg.py`
3. `python .\tests\T08_within_unit_variant_counterfactual\analyze.py`
