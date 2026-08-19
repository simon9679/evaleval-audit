# T06 — Frozen EEE Source Unit Trace

Status before execution: preregistered package.

T06 independently verifies the T05 provenance attribution against the frozen
EEE aggregate JSON records.

It does not rerun the production pipeline and it does not use the network.

Primary question:

> For every Stage F row belonging to an actual mixed-unit comparability group,
> does the referenced frozen EEE source record contain the same `metric_unit`
> value at the referenced `evaluation_results[result_idx].metric_config`,
> after only the documented `percentage -> percent` normalization?

Run order:

1. `python .\tests\T06_eee_source_unit_trace\preflight.py`
2. `python .\tests\T06_eee_source_unit_trace\verify_prereg.py`
3. `python .\tests\T06_eee_source_unit_trace\analyze.py`
