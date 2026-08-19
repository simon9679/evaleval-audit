# T12 — Source Metric Identity Collapse Trace

Status before execution: preregistered package.

T12 traces the two T08-T11 product-consequential groups from frozen source
`metric_config.metric_id` values into Stage F metric identity fields.

The purpose is to determine whether multiple source-declared metric ids become
one production `metric_raw` / canonical `metric_id` / `metric_key`, and whether
that transformation occurs through the structured-id path or the fallback
metric extraction/resolution path.

No semantic alias judgement is introduced.

Run order:

1. `python .\tests\T12_source_metric_identity_collapse\preflight.py`
2. `python .\tests\T12_source_metric_identity_collapse\verify_prereg.py`
3. `python .\tests\T12_source_metric_identity_collapse\analyze.py`
