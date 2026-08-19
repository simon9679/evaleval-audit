# POSTRUN_DECISION — T04

Status: post-run decision record.

This file records the branch decision caused by the completed T04 result. It
does not modify the preregistration.

## Completed result

T04 verdict:

`REFUTED`

Primary decision variable:

`classification_sensitive_paths = 0`

Supporting observations:

- warning-level root groups: 1,425
- actual mixed-unit comparability groups: 1,234
- cross-slice-only warning roots: 191
- threshold-sensitive actual groups: 668
- applicable variant paths: 7
- applicable cross-party paths: 0
- classification-sensitive groups: 0
- integrity errors: 0

## Which branch stops

The following claim branch stops:

`mixed metric_unit -> unit-selected threshold -> changed final comparability boolean`

Reason:

T04 found no applicable path whose final boolean changes across unit values
already present in the same frozen group.

No source-level trace is justified solely to prove this already-refuted
boolean-impact claim.

## Which questions do not stop

The following questions remain open and are not descendants of the refuted
boolean-impact claim:

1. Why do 1,234 actual comparability groups contain more than one unit label?
2. Do the unit labels correspond to one estimand expressed inconsistently, or
   to genuinely different estimands?
3. At what stage does the mixed identity arise: upstream source metadata,
   registry metadata, resolution, canonicalization, or another boundary?
4. Is the canonical metric identity semantically valid?
5. Is any unresolved identity issue visible in a public product surface?

Those questions require a separate claim, rationale, competing predictions,
preregistration, and verdict.

## Why the distinction matters

A stop rule in the Falsification Protocol is a branch-economy rule, not an
instruction to stop investigating the entire system.

T04 prevents spending more effort on a specific product-consequence hypothesis
that the frozen data did not support.

At the same time, it preserves a new independent metric-identity/provenance
question created by the observed 1,234 mixed-unit groups.

## Next-test gate

A new test is justified only if it measures the independent metric-identity or
provenance claim directly.

The new test must not treat any of the following as already established:

- that a mixed-unit group is semantically wrong;
- that EvalEval caused the mixed-unit state;
- that upstream data caused the mixed-unit state;
- that the public website is affected;
- that comparability is globally invalid.

Those are possible outcomes to be tested, not premises.
