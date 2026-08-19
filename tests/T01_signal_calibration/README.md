# T01 — Controlled Signal Calibration

This bundle is the first confirmatory test in the independent EvalEval audit.

Run order:

1. `python tests\T01_signal_calibration\preflight.py`
2. `python tests\T01_signal_calibration\verify_prereg.py`
3. `python tests\T01_signal_calibration\run_test.py`

Do not edit `TEST_RATIONALE.md`, `PREREGISTRATION.md`, `run_test.py`, or the package manifest between steps 2 and 3.

Outputs:

- `raw/cases.jsonl`
- `raw/source_hashes.json`
- `results/summary.json`

The test requires no network access.
