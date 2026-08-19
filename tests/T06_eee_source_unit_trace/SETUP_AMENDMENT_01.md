# SETUP_AMENDMENT_01 — EEE Root Discovery

Status: setup-only amendment created after the first T06 preflight attempt and
before `verify_prereg.py` or `analyze.py` execution.

## Trigger

The original T06 preflight attempted to discover the frozen EEE root by
searching for `.eee_file_listing.json`.

Observed first-attempt result:

- `eee_root_candidates = 0`
- `eee_root_matching_24787 = 0`
- `eee_root = None`

This is an audit-harness path-discovery failure. It is not a T06 test result
and is not attributed to EvalEval.

## Why the preregistration is not changed

The T06 claim, population, competing predictions, normalization rule, row trace
rule, group trace rule, and verdict rules do not depend on the presence of a
`.eee_file_listing.json` marker.

Therefore:

- `PREREGISTRATION.md` is unchanged;
- `TEST_RATIONALE.md` is unchanged;
- `SOURCE_ATTRIBUTION.md` is unchanged;
- `analyze.py` is unchanged;
- the original `preflight.py` is preserved;
- the original `verify_prereg.py` remains the authority for confirming those
  frozen files.

## Replacement discovery procedure

`preflight_fix1.py` uses the frozen Stage F artifact only to read
`source_record_path` values.

It does not read `metric_unit`, mixed-unit outcomes, source JSON contents, or
T06 result variables.

Procedure:

1. read deterministic non-null `source_record_path` values from the frozen
   Stage F Parquet;
2. locate the exact first relative path under the audit freeze tree by matching
   its leaf file and full relative-path suffix;
3. derive the candidate EEE root by stripping the relative path;
4. verify a deterministic set of up to 32 additional source paths exists under
   the same root;
5. write the selected root to the same `raw/source_root.json` consumed by the
   already-frozen `analyze.py`.

This changes only source-root discovery and does not expose T06 outcome data.

## Evidence preservation

The failed first preflight should be preserved as:

`raw/preflight_attempt_01_marker_not_found.json`

The successful amended preflight is written to:

`raw/preflight.json`

The original failed console transcript should remain in the conversation/audit
history.
