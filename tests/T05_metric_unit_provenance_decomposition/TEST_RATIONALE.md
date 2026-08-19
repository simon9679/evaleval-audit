# TEST_RATIONALE — T05 Metric Unit Provenance Decomposition

Status: frozen before execution.

## Primary claim

C-T05:

> At least one actual mixed-unit Stage F comparability group contains two or
> more distinct non-null `metric_raw` labels that all resolve to one shared
> non-null canonical `metric_id` equal to the group's `metric_key`.

This is called a **full resolved canonical-convergence group** in T05.

C-T05 is structural. Confirmation does not mean the convergence is wrong.
Refutation does not mean the upstream data are correct.

## Why this test was selected

T04 established that mixed-unit heterogeneity is real inside 1,234 actual Stage
F comparability groups, but found zero final boolean changes.

The next unresolved question is therefore not impact but attribution.

Before opening source JSON and manually deciding what a metric "means", the
frozen Stage F artifact already contains:

- `metric_raw`;
- `metric_id`;
- `metric_key`;
- `metric_key_effective`;
- `metric_resolution_strategy`;
- `metric_unit`;
- `metric_unit_provenance`;
- `source_config`;
- source-record pointers.

Those fields can tell us whether canonical identity convergence participates in
the mixed-unit state.

## Why this test is run now

A full source-semantic trace is more expensive and introduces human/reference
judgement.

T05 is deterministic, full-population, and reuses already frozen evidence.

It can narrow a later source trace to the relevant subset or show that the
canonical resolver is not structurally involved in this branch.

This follows the audit's cheapest-to-more-expensive dependency order.

## Competing predictions

### P1 — no full canonical-convergence involvement

`full_resolved_canonical_convergence_groups = 0`

Every actual mixed-unit group fails the strict convergence condition. Mixed
units may still arise from upstream metadata, heuristics, partial resolution,
or another path, but T05 would provide no evidence that multiple raw metric
labels were fully collapsed into one shared canonical metric id inside an
actual mixed-unit group.

### P2 — canonical-convergence involvement exists

`full_resolved_canonical_convergence_groups >= 1`

At least one actual mixed-unit group contains multiple distinct raw metric
labels, while every row in that group has a non-null canonical metric id and
all rows share the same canonical id equal to the production `metric_key`.

This establishes that canonical metric resolution participates structurally in
at least part of the mixed-unit population.

It does not establish that the resolution is semantically incorrect.

## Secondary descriptive decomposition

Regardless of the primary verdict, T05 reports all of the following across the
1,234 mixed-unit groups:

- groups with one vs multiple raw metric labels;
- groups with one vs multiple canonical metric ids;
- groups with unresolved metric rows;
- groups with multiple metric-resolution strategies;
- groups with multiple metric-unit provenance layers;
- provenance-pattern counts;
- source-config counts;
- unit-pattern counts;
- full and partial canonical-convergence counts.

These are descriptive outputs, not separate PASS/FAIL claims.

## Strict full-convergence definition

An actual mixed-unit group is a full resolved canonical-convergence group iff:

1. it has at least two distinct non-null `metric_raw` values;
2. every row has non-null `metric_id`;
3. exactly one distinct `metric_id` occurs;
4. the single `metric_id` equals the group's production `metric_key`.

This deliberately excludes partial or ambiguous cases from the primary claim.

## Integrity controls

The test must verify:

- backend commit unchanged;
- T03 Stage F Parquet SHA unchanged;
- T04 summary is present and reports:
  - verdict `REFUTED`;
  - 1,234 actual mixed-unit groups;
  - zero classification-sensitive paths;
- the Stage F Parquet contains all required provenance columns;
- recomputed actual mixed-unit count equals 1,234;
- each comparability group has one stable production `metric_key`.

Failure of an integrity control is not an EvalEval defect.

## What T05 can establish

T05 can establish whether the frozen canonical metric-resolution layer
structurally converges multiple raw labels inside any actual mixed-unit
comparability group.

It can quantify which provenance layers and source configs are associated with
the mixed-unit population.

## What T05 cannot establish

T05 cannot establish:

- whether converged raw labels are synonyms or different estimands;
- which unit is semantically correct;
- whether upstream EEE metadata are wrong;
- whether EvalEval resolution is wrong;
- whether the public website is affected;
- whether any structural convergence changes a final comparability decision.

Those require later source/reference tracing only if justified by T05.
