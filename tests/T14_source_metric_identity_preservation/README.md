# T14 — Source Metric Identity Preservation Counterfactual

Status before execution: preregistered package.

T14 tests whether the two product-consequential production-positive
variant-divergence groups remain positive when the exact frozen source
`metric_config.metric_id` is preserved as the metric grouping identity for
only the twelve affected rows.

The production divergence function is reused unchanged inside each resulting
source-id subgroup.

This is an operational counterfactual, not a normative claim that exact source
ids must be canonical.

Run order:

1. `python .\tests\T14_source_metric_identity_preservation\preflight.py`
2. `python .\tests\T14_source_metric_identity_preservation\verify_prereg.py`
3. `python .\tests\T14_source_metric_identity_preservation\analyze.py`
