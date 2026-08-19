# PREREGISTRATION — T05 Metric Unit Provenance Decomposition

Status: registered before T05 execution.

## Frozen prerequisites

Backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

T03 Stage F Parquet SHA-256:

`e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196`

Required completed T04 result:

- verdict = `REFUTED`;
- actual_mixed_unit_groups = 1234;
- classification_sensitive_paths = 0;
- production_reconstruction_errors = 0;
- group_consistency_errors = 0.

## Population

All actual Stage F comparability groups in the frozen T03 Parquet with more
than one distinct non-null `metric_unit`.

No sampling is permitted.

Expected population size from T04:

`1234`

The expected count is a prerequisite integrity value, not a T05 outcome.

## Primary claim C-T05

At least one actual mixed-unit group is a full resolved
canonical-convergence group.

## Full resolved canonical-convergence definition

A group qualifies iff all four conditions hold:

1. `count(distinct non-null metric_raw) >= 2`;
2. `count(rows with metric_id IS NULL) = 0`;
3. `count(distinct non-null metric_id) = 1`;
4. the one canonical `metric_id` equals the group's stable `metric_key`.

No semantic judgement of metric labels is used in this definition.

## Competing predictions

### P1

`full_resolved_canonical_convergence_groups = 0`

### P2

`full_resolved_canonical_convergence_groups >= 1`

## Primary verdict

- `CONFIRMED` — P2 is observed and all integrity controls pass.
- `REFUTED` — P1 is observed and all integrity controls pass.
- `INCONCLUSIVE` — the frozen artifact is readable but required provenance
  fields or group invariants do not support a valid structural attribution.
- `ERROR` — prerequisite evidence, dependency, commit, or input artifact
  cannot be verified/read.

The verdict applies only to C-T05.

## Required raw outputs

- `raw/mixed_group_attribution.jsonl` — one record for every actual mixed-unit
  group;
- `raw/full_canonical_convergence_groups.jsonl` — every primary-claim group;
- `raw/full_canonical_convergence_rows.jsonl` — every row belonging to those
  groups, including source pointers;
- `raw/integrity_errors.jsonl`.

## Required summary counts

At minimum:

- fact_rows_scanned;
- comparability_groups_scanned;
- actual_mixed_unit_groups;
- single_raw_metric_groups;
- multi_raw_metric_groups;
- groups_with_unresolved_metric_rows;
- single_metric_id_groups;
- multi_metric_id_groups;
- multi_resolution_strategy_groups;
- multi_unit_provenance_groups;
- full_resolved_canonical_convergence_groups;
- partial_or_mixed_resolution_convergence_groups;
- integrity_error_records;
- resolution-strategy-pattern breakdown;
- metric-unit-provenance-pattern breakdown;
- source-config breakdown;
- unit-pattern breakdown.

All counts must be reported even when zero.

## Branch decision

If `CONFIRMED`:

- do not call the convergence erroneous;
- the next semantic/source trace should target the full-convergence groups
  first, because they are the cheapest subset capable of testing whether the
  converged raw labels represent the same estimand.

If `REFUTED`:

- do not spend a source trace on canonical-convergence as the explanation;
- use the descriptive provenance decomposition to choose the next attribution
  layer, such as upstream per-record metadata or heuristic metadata inference.

If `INCONCLUSIVE` or `ERROR`:

- repair or replace the measurement step;
- do not attribute the failure to EvalEval without boundary evidence.
