# T09 — Headline Comparability Aggregate Impact

Status before execution: preregistered package.

T09 tests whether the two T08 positive-to-negative paths contribute to the
frozen product-facing `headline.json` comparability aggregate and whether the
headline `variant_divergent_count` changes when only those two frozen booleans
are replaced by their T08 exact-label counterfactual values.

The test reproduces the frozen backend's overall comparability-block SQL
directly from the Stage F Parquet.

It does not perform semantic unit adjudication and does not modify any source
record.

Run order:

1. `python .\tests\T09_headline_comparability_impact\preflight.py`
2. `python .\tests\T09_headline_comparability_impact\verify_prereg.py`
3. `python .\tests\T09_headline_comparability_impact\analyze.py`
