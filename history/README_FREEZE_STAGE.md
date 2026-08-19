# EvalEval Independent Audit

Purpose: an independent, neutral audit of EvalEval using the Falsification Protocol
and the Validation Handbook.

At this stage, no audit tests are executed. The first step is a complete freeze of
the audit object.

## What scripts\00_freeze.ps1 does

1. Clones:
   - evaleval/eval_cards_backend_pipeline
   - evaleval/eval-card-registry
   - evaleval/every_eval_ever
2. Records exact commit SHAs.
3. Reads the production `.github/workflows/sync.yml`.
4. Extracts exact revisions:
   - EEE_REVISION
   - ENTITY_REGISTRY_REVISION
   - BENCHMARK_METADATA_REVISION
5. Resolves the moving `RESOLVER_REF` to an exact eval-card-registry commit SHA.
6. Installs `huggingface_hub` if needed.
7. Downloads complete snapshots of all three Hugging Face datasets at exact revisions.
8. Records Python, Git, PowerShell, and operating-system versions.
9. Computes SHA-256 for every frozen file.
10. Writes:
    - `freeze\FREEZE_MANIFEST.json`
    - `freeze\FREEZE_SUMMARY.txt`
    - `freeze\SHA256SUMS.txt`

## Why the complete snapshots are frozen

The audit will include corpus-level checks. A reduced evidence subset may be valid
for an individual local canary, but it is not a substitute for the full pinned
corpus when testing corpus-level claims.

## After the freeze

Run:

    powershell -ExecutionPolicy Bypass -File .\scripts\01_verify_freeze.ps1

Return these files to the auditor:

    freeze\FREEZE_SUMMARY.txt
    freeze\FREEZE_MANIFEST.json
    freeze\VERIFY_FREEZE.txt
