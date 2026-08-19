# T04 — Comparability Unit Consistency and Threshold-Choice Sensitivity

Status before execution: preregistered package.

This test reuses the frozen Stage F evidence produced by T03. It does not rerun
the EvalEval production pipeline and it does not inspect new network data.

Primary question:

> Does the presence of more than one observed `metric_unit` inside an actual
> Stage F comparability group make the final comparability boolean sensitive
> to which observed unit is used for the threshold rule?

The test also distinguishes the production Stage F warning population
`(model_aggregation_key, benchmark_key, metric_key)` from the actual
comparability grouping
`(model_aggregation_key, benchmark_key, slice_key, metric_key)`.

Run order:

1. `python .\tests\T04_comparability_unit_consistency\preflight.py`
2. `python .\tests\T04_comparability_unit_consistency\verify_prereg.py`
3. `python .\tests\T04_comparability_unit_consistency\analyze.py`

`analyze.py` writes all raw group records, all classification-sensitive records,
a machine-readable summary, and a deterministic result-analysis document.
