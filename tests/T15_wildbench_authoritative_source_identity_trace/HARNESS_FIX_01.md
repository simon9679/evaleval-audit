# HARNESS_FIX_01 — Runtime output-directory creation

Status: pre-substantive harness repair.

## Trigger

The original T15 preflight failed before emitting any T15 preflight payload:

`FileNotFoundError: ... T15_wildbench_authoritative_source_identity_trace\raw\preflight.json`

The command was executed twice and failed identically.

No T15 claim-governing source rows, counts, or verdict were produced.

## Root cause

The original T15 package contained no files under `raw/` or `results/` at
packaging time.

The package builder added file entries only. Therefore those empty directories
were absent from the ZIP archive and were not created by extraction.

The original `preflight.py` then attempted:

`(HERE / "raw" / "preflight.json").write_text(...)`

without first creating `raw/`.

The original `analyze.py` would have the same packaging-dependent failure for
`results/` even after `raw/` existed.

## Repair

Fix 1 does not modify any frozen T15 preregistration, rationale, source
attribution, preflight logic, or analyzer logic.

It adds two wrapper scripts:

- `preflight_fix1.py`
- `analyze_fix1.py`

Each wrapper creates the runtime output directories with:

`mkdir(parents=True, exist_ok=True)`

and then executes the original frozen script with `runpy.run_path`.

Thus the only change is filesystem setup.

## Claim invariance

Unchanged:

- C-T15;
- fixed population;
- expected row counts;
- P1 / P2;
- derivation rule;
- structured signature;
- verdict rule;
- branch stop / continue rule;
- original `preflight.py`;
- original `analyze.py`;
- original `verify_prereg.py`.

## Attribution

This is an audit-package harness error.

It is not an EvalEval finding and must not be counted as an EvalEval defect.
