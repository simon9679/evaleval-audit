# Reproduction and Bundle Scope

This repository is a compact publication/review bundle, not a byte-for-byte copy of the full local freeze.

## What is included

- all 17 completed test packages;
- canonical summaries and post-run analyses;
- compact raw evidence used by the published findings;
- the T03 Stage F Parquet used by many downstream tests;
- freeze metadata and the full `SHA256SUMS.txt` list;
- claim and test indices;
- preregistration-integrity verifiers.

## What is not included

The full frozen `freeze/repos/...` and `freeze/hf/...` trees are omitted because the original freeze is approximately 18 GB.

The original freeze verifier recorded:

```text
VERIFY_FREEZE
ok=68126
bad=0
missing=0
```

The hash list remains in `freeze/SHA256SUMS.txt` so an independently materialized freeze can be checked against the same object.

## Environment observed during the audit

The freeze manifest records:

- Python 3.12.10
- PowerShell 5.1.26100.9168
- Git 2.53.0.windows.2
- Windows NT 10.0.26200.0

Downstream preflight records show DuckDB 1.5.2; typed-representation T14 preflights also record PyArrow 24.0.0.

## What can be verified from this compact repository alone

Run:

```bash
python tools/verify_public_bundle.py
```

This checks the publication bundle's canonical index, summary hashes/verdicts, required per-test files, preregistration-integrity verifiers, T14 canonicalization, freeze-metadata hashes, and JSON readability.

This is an integrity check, not a scientific re-execution of every analyzer.

## What requires the full freeze

A full from-source rerun of tests that resolve source files or reconstruct the EvalEval pipeline requires the omitted frozen repositories/datasets at the exact revisions recorded in `freeze/FREEZE_MANIFEST.json` and `freeze/SHA256SUMS.txt`.

## Absolute local paths in raw captures

Some raw preflight/summary captures contain strings such as `C:\Users\Limon\Downloads\evaleval-audit\...`.

These strings record the original execution environment. They are preserved unchanged because modifying them would change raw evidence and break existing artifact hashes/manifests. They are not API keys or credentials.
