# Method Directory Status

This directory contains both historical method snapshots and current
test-level provenance records.

## Historical snapshots

The following files are preserved unchanged for chronology and must not be
used to determine the current audit status:

- `COMPLETED_TESTS_RATIONALE.md` — written when only T01 and T02 were
  complete and T03 was still planned;
- `TEST_SOURCE_ATTRIBUTION.json` — retrospective method record after T01/T02
  and before T03 execution. It therefore lists only T01/T02 as completed and
  T03 as not yet completed.

The historical files are intentionally not rewritten because they document
the audit chronology.

## Current sources of truth

Use these for the completed T01-T17 audit:

- `../TEST_INDEX.json` — canonical final verdicts;
- `../CLAIM_INDEX.json` — claim-to-verdict mapping;
- `../AUDIT_STATUS.md` — current publication status;
- `../METHOD_ERRATA.md` — post-freeze method-reference corrections;
- each test's own `TEST_RATIONALE.md`, `PREREGISTRATION.md`,
  `SOURCE_ATTRIBUTION.md`, and `results/RESULT_ANALYSIS.md`.

There are currently 17 completed tests. Historical method snapshots do not
override those current publication-layer indexes.
