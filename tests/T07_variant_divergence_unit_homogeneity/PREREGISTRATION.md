# PREREGISTRATION — T07 Variant Divergence Unit-Homogeneity Eligibility

Status: registered before T07 execution.

## Frozen prerequisites

Backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

T03 Stage F Parquet SHA-256:

`e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196`

Required T04 result:

- actual_mixed_unit_groups = 1234;
- variant_eligible_paths = 7;
- cross_party_eligible_paths = 0;
- classification_sensitive_paths = 0;
- integrity errors = 0.

Required T06 result:

- verdict = `CONFIRMED`;
- mixed_unit_groups = 1234;
- mixed_unit_rows = 28196;
- row_traces_complete = 28196;
- row_unit_matches = 28196;
- row_unit_mismatches = 0;
- group_unit_set_matches = 1234;
- group_unit_set_mismatches = 0;
- pointer_or_index_errors = 0;
- integrity errors = 0.

## Population

All actual mixed-unit Stage F comparability groups:

`count(distinct non-null metric_unit) > 1`

Primary analysis population:

the subset with non-null production `has_variant_divergence`.

Expected count from T04:

`7`

No sampling is allowed.

## Arithmetic input definition

For an applicable variant group, arithmetic score rows are all rows with
non-null numeric `score`.

The score-unit set is:

`set(metric_unit for arithmetic score rows if metric_unit is not null)`

No unit normalization, conversion, equivalence map, or preferred-unit choice is
introduced by T07.

The Stage F values are used exactly as frozen.

## Primary claim C-T07

At least one applicable mixed-unit variant path has at least two distinct
non-null declared unit labels among the arithmetic score rows.

## Competing predictions

### P1

`unit_heterogeneous_applicable_variant_paths = 0`

### P2

`unit_heterogeneous_applicable_variant_paths >= 1`

## Primary verdict

- `CONFIRMED` — P2 is observed and all integrity controls pass.
- `REFUTED` — P1 is observed and all integrity controls pass.
- `INCONCLUSIVE` — the frozen artifact is readable but group invariants or
  divergence reconstruction prevent a valid eligibility interpretation.
- `ERROR` — prerequisite evidence, backend commit, dependency, or input
  artifact cannot be verified/read.

The verdict applies only to C-T07.

## Divergence reconstruction

For every applicable variant path:

`recomputed_divergence = max(score) - min(score)`

over the arithmetic score rows.

The reconstructed value must match the frozen
`variant_divergence_magnitude` within absolute tolerance `1e-12`.

This tolerance is only a reconstruction integrity check. It is not a
comparability threshold or outcome tolerance.

## Required raw outputs

- `raw/applicable_variant_paths.jsonl`
- `raw/unit_heterogeneous_paths.jsonl`
- `raw/integrity_errors.jsonl`

Each path record must include source pointers for all arithmetic score rows.

## Required summary counts

At minimum:

- fact_rows_scanned;
- comparability_groups_scanned;
- mixed_unit_groups;
- applicable_mixed_variant_paths;
- unit_homogeneous_applicable_variant_paths;
- unit_heterogeneous_applicable_variant_paths;
- applicable_paths_with_null_unit_score_rows;
- extrema_disjoint_unit_paths;
- extrema_overlapping_unit_paths;
- production_true_paths;
- production_false_paths;
- divergence_reconstruction_errors;
- group_consistency_errors;
- integrity_error_records;
- arithmetic score-unit-pattern breakdown.

All counts must be printed even when zero.

## Branch decision

If `CONFIRMED`:

- do not yet call the unit labels semantically incompatible;
- the next descendant test may measure whether the mixed-label arithmetic
  produces a divergence magnitude that cannot be reproduced within any
  single declared-unit partition, using a preregistered no-free-parameter
  rule.

If `REFUTED`:

- the group-level mixed-unit branch does not enter the production variant
  arithmetic;
- stop this arithmetic-eligibility descendant and move to the next independent
  audit branch.

If `INCONCLUSIVE` or `ERROR`:

- repair or replace the measurement step;
- do not attribute the measurement failure to EvalEval without boundary
  evidence.
