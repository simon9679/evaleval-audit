# PREREGISTRATION — T04 Comparability Unit Consistency and Threshold-Choice Sensitivity

Status: registered before T04 execution.

## Frozen prerequisite evidence

Backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

T03 evidence required:

- verdict = `REFUTED`;
- fact_rows_scanned = 209382;
- comparability_groups = 93495;
- variant_mismatches = 0;
- cross_party_mismatches = 0;
- fact Parquet SHA-256 =
  `e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196`;
- production Stage F warning count observed in the T03 run = 1425.

The warning count is known prior evidence and is not a T04 outcome.

## Claim

C-T04:

At least one production-applicable Stage F comparability path in the frozen
corpus changes its boolean divergence classification when the threshold is
recomputed across distinct non-null `metric_unit` values actually present in
that same actual comparability group.

## Group definitions

### Warning-level root group

The production warning is reconstructed over:

`(model_aggregation_key, benchmark_key, metric_key)`

with more than one distinct non-null `metric_unit`.

### Actual comparability group

The production Stage F comparability metric config is grouped over:

`(model_aggregation_key, benchmark_key, slice_key, metric_key)`

and represented by `comparability_group_id`.

A group enters the T04 sensitivity population only when that actual group has
more than one distinct non-null `metric_unit`.

No sampling is allowed.

## Fixed production inputs

For each actual mixed-unit group:

- group rows: unchanged;
- production divergence magnitude: unchanged;
- min_score aggregation: maximum non-null group value;
- max_score aggregation: maximum non-null group value;
- threshold factor: production default 1.0;
- decision operator: strict `>`.

The only swept field is `metric_unit`.

## Admissible unit sweep

The sweep contains exactly the distinct non-null `metric_unit` strings observed
inside the actual frozen comparability group.

No synthetic unit is introduced.

For each observed unit `u`, call the frozen production threshold resolver with:

`{"metric_unit": u, "min_score": group_max_min_score, "max_score": group_max_max_score}`

The resulting production threshold and basis are recorded.

## Path evaluation

Variant and cross-party paths are evaluated independently.

A path is eligible only when its production boolean and production divergence
magnitude are non-null and internally constant across rows of the group.

For each eligible path and each observed unit:

`counterfactual_flag[u] = production_divergence_magnitude > threshold[u]`

A path is classification-sensitive when the set of counterfactual flags across
observed units contains both `True` and `False`.

A group is threshold-sensitive when the threshold magnitude or basis differs
across observed unit choices, whether or not the boolean flips.

## Competing predictions

### P1 — benign / non-consequential heterogeneity

`classification_sensitive_paths = 0`

The branch does not demonstrate a frozen product-classification consequence.

### P2 — consequential threshold ambiguity

`classification_sensitive_paths >= 1`

At least one frozen production-applicable boolean depends on which observed
unit is chosen.

## Primary verdict

- `CONFIRMED` — `classification_sensitive_paths >= 1` and all integrity
  controls pass.
- `REFUTED` — `classification_sensitive_paths = 0` and all integrity controls
  pass.
- `INCONCLUSIVE` — Stage F evidence is readable, but warning reconstruction,
  group consistency, or production-threshold reconstruction prevents a valid
  sensitivity interpretation.
- `ERROR` — prerequisite evidence, dependency, frozen commit, or Stage F
  artifact cannot be obtained or verified.

This verdict applies only to C-T04.

## Required raw outputs

T04 must write:

- every reconstructed warning-level root group;
- every actual mixed-unit comparability group and all observed unit choices;
- every classification-sensitive path with source pointers where available;
- all integrity errors;
- SHA-256 for each generated raw artifact.

## Required summary numbers

At minimum:

- fact_rows_scanned;
- comparability_groups_scanned;
- warning_root_groups;
- actual_mixed_unit_groups;
- warning_roots_with_actual_mixed_group;
- warning_roots_cross_slice_only;
- variant_eligible_paths;
- cross_party_eligible_paths;
- threshold_sensitive_groups;
- classification_sensitive_groups;
- classification_sensitive_paths;
- variant_classification_sensitive_paths;
- cross_party_classification_sensitive_paths;
- production_reconstruction_errors;
- group_consistency_errors;
- unit-pattern breakdown.

All counts are reported even when zero.

## Stop / continue rule

If `REFUTED`:

- stop this unit-choice consequence branch;
- do not perform expensive source tracing solely because the Stage F warning
  existed;
- preserve the warning and any threshold-only sensitivity as descriptive
  evidence;
- continue the audit on the next independent claim branch.

If `CONFIRMED`:

- the next descendant test must trace every classification-sensitive group
  needed for the claim back to frozen source records;
- no final claim about semantic correctness, root cause, or public-site impact
  is allowed before that trace.

If `INCONCLUSIVE` or `ERROR`:

- repair or replace only the measurement step;
- do not attribute the failure to EvalEval without boundary evidence.
