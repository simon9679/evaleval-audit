# T13 — Structured Metric-ID Rejection Attribution

Status before execution: preregistered package.

T13 directly replays the frozen structured metric-id resolver on the six source
metric ids from the two T12 product-consequential groups.

It classifies each structured-id outcome from the resolver's exact/normalized
segment vocabulary:

- accepted single specific metric hit;
- no metric hit;
- catch-all-only hit;
- conflicting specific metric hits.

No semantic alias judgement is used.

Run order:

1. `python .\tests\T13_structured_metric_id_rejection\preflight.py`
2. `python .\tests\T13_structured_metric_id_rejection\verify_prereg.py`
3. `python .\tests\T13_structured_metric_id_rejection\analyze.py`
