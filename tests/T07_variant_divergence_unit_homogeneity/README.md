# T07 — Variant Divergence Unit-Homogeneity Eligibility

Status before execution: preregistered package.

T07 tests whether a production-applicable variant-divergence calculation uses
numeric score rows carrying more than one declared non-null `metric_unit`
inside the same actual Stage F comparability group.

This is not a semantic equivalence test. T07 does not decide whether two unit
labels are convertible, synonymous, correct, or incorrect.

It tests the narrower production eligibility fact that the frozen
`max(scores) - min(scores)` operation receives score-bearing rows with one
declared unit label or multiple declared unit labels.

Run order:

1. `python .\tests\T07_variant_divergence_unit_homogeneity\preflight.py`
2. `python .\tests\T07_variant_divergence_unit_homogeneity\verify_prereg.py`
3. `python .\tests\T07_variant_divergence_unit_homogeneity\analyze.py`
