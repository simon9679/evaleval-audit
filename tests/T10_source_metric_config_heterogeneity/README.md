# T10 — Source MetricConfig Heterogeneity in Consequential Groups

Status before execution: preregistered package.

T10 examines only the two T08/T09 product-consequential groups.

It asks whether their exact unit partitions differ in structured source
`MetricConfig` fields beyond `metric_unit`.

The test reads the frozen EEE records through the already-verified
`source_record_path + result_idx` pointers.

No web access, semantic unit ontology, unit conversion, or manual case
selection is used.

Run order:

1. `python .\tests\T10_source_metric_config_heterogeneity\preflight.py`
2. `python .\tests\T10_source_metric_config_heterogeneity\verify_prereg.py`
3. `python .\tests\T10_source_metric_config_heterogeneity\analyze.py`
