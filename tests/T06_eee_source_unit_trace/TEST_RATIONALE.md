# TEST_RATIONALE — T06 Frozen EEE Source Unit Trace

Status: frozen before execution.

## Primary claim C-T06

> Every Stage F row in the 1,234 actual mixed-unit comparability groups is
> source-traceable to the frozen EEE aggregate JSON identified by
> `source_record_path`, the referenced `evaluation_results[result_idx]` exists,
> and the source `metric_config.metric_unit`, after only the documented
> `percentage -> percent` normalization, equals the Stage F `metric_unit`.

This is a row-level source-trace claim.

A second required invariant is that the normalized source-unit set for every
mixed group equals the Stage F unit set for that group.

## Why this test was selected

T05 localized the mixed-unit population away from:

- multiple raw metric labels;
- canonical-convergence;
- unresolved metrics;
- mixed resolution strategies;
- heuristic unit inference.

Every group instead carried only `eee_record` unit provenance.

The next cheapest falsifiable question is therefore whether that provenance
label is true when checked against the referenced frozen source artifact.

## Why this test is run now

Manual semantic inspection would be premature.

Before asking whether a unit is "correct", the audit must establish whether the
unit disagreement already exists in the source records or is introduced later
inside the EvalEval transformation.

T06 can answer that deterministically for the complete mixed-unit population.

## Competing predictions

### P1 — provenance trace is source-faithful

All required source pointers resolve and:

- every row's normalized source unit equals its Stage F unit;
- every group's normalized source-unit set equals its Stage F unit set.

Observable result:

- `row_unit_mismatches = 0`
- `group_unit_set_mismatches = 0`
- `pointer_or_index_errors = 0`

### P2 — provenance trace is not fully source-faithful

At least one otherwise validly addressable row has a normalized source unit
different from Stage F, or at least one group has a different source-unit set.

Observable result:

- `row_unit_mismatches >= 1`
  or
- `group_unit_set_mismatches >= 1`

Pointer/file/index failures are not P2. They are evidence-integrity failures
and are handled as INCONCLUSIVE or ERROR under the preregistered rules.

## Fixed normalization

T06 applies exactly one unit synonym normalization documented by the frozen
metric-meta implementation:

`percentage -> percent`

No trimming, case-folding, inferred conversion, percent/proportion scaling, or
other semantic normalization is introduced.

## Population

All Stage F rows whose `comparability_group_id` belongs to an actual
mixed-unit group:

`count(distinct non-null metric_unit) > 1`

Expected group count from T04/T05:

`1234`

No sampling is permitted.

## Source pointer

For each Stage F row:

1. resolve `EEE_ROOT / source_record_path`;
2. parse the aggregate JSON;
3. verify `evaluation_id` where present against the Stage F value;
4. index `evaluation_results[result_idx]` using the frozen zero-based index;
5. read `metric_config.metric_unit`;
6. normalize only `percentage -> percent`;
7. compare with Stage F `metric_unit`.

## What T06 can establish

T06 can establish whether the mixed-unit state seen in Stage F is already
present in the frozen EEE aggregate records referenced by those exact rows.

If P1 is observed, the audit can attribute the existence of the differing
unit labels to the frozen EEE datastore boundary rather than to the later
metric-meta unit selection layer.

## What T06 cannot establish

T06 cannot establish:

- whether the original leaderboard/site scraped by EEE emitted the value;
- whether EEE extraction transformed the original publisher value;
- whether a source unit is semantically correct;
- whether EvalEval should normalize different unit labels;
- whether the public product exposes a consequential error;
- whether the mixed-unit state changes a comparability boolean.

The final item was separately tested by T04.
