# T05 — Metric Unit Provenance Decomposition

Status before execution: preregistered package.

T05 is an attribution gate created by the T04 result. It does not test whether
mixed units change a comparability boolean; T04 already refuted that claim for
the frozen snapshot.

T05 asks a narrower structural question:

> Are the actual mixed-unit comparability groups produced entirely within one
> raw metric identity, or does Stage C canonical metric resolution converge
> multiple distinct raw metric labels into the same comparability metric key?

The test uses the already-hashed T03 Stage F Parquet. No production pipeline
rerun and no network access are required.

Run order:

1. `python .\tests\T05_metric_unit_provenance_decomposition\preflight.py`
2. `python .\tests\T05_metric_unit_provenance_decomposition\verify_prereg.py`
3. `python .\tests\T05_metric_unit_provenance_decomposition\analyze.py`
