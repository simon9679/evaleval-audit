# PREREGISTRATION — T08 Within-Unit Variant Divergence Counterfactual

Status: registered before T08 execution.

## Frozen prerequisites

Backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

T03 Stage F Parquet SHA-256:

`e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196`

Required T07 result:

- verdict = `CONFIRMED`;
- mixed_unit_groups = 1234;
- applicable_mixed_variant_paths = 7;
- unit_homogeneous_applicable_variant_paths = 0;
- unit_heterogeneous_applicable_variant_paths = 7;
- production_true_paths = 5;
- production_false_paths = 2;
- divergence_reconstruction_errors = 0;
- group_consistency_errors = 0;
- integrity_error_records = 0.

## Population

All seven production-applicable mixed-unit variant paths from the frozen Stage
F population.

No sampling is permitted.

## Exact-label partition rule

Use all numeric score rows used by production.

Partition them by the exact stored non-null `metric_unit` string.

No normalization, conversion, case folding, synonym map, or manually chosen
equivalence class is allowed.

For each partition:

`within_unit_range = max(score) - min(score)`

A singleton partition has range `0`.

For the path:

`max_within_unit_range = max(within_unit_range across partitions)`

## Fixed threshold rule

Use the frozen production `variant_divergence_threshold` for that path.

Do not recompute a new threshold from the partition unit.

This isolates the effect of arithmetic row eligibility from the already-tested
threshold-choice branch.

Counterfactual flag:

`max_within_unit_range > variant_divergence_threshold`

Production uses strict `>` and T08 uses the same strict operator.

## Primary claim C-T08

At least one production-positive path becomes negative under the exact-label
partition counterfactual.

## Competing predictions

### P1

`positive_to_negative_paths = 0`

### P2

`positive_to_negative_paths >= 1`

## Primary verdict

- `CONFIRMED` — P2 is observed and all integrity controls pass.
- `REFUTED` — P1 is observed and all integrity controls pass.
- `INCONCLUSIVE` — the frozen artifact is readable but group, threshold, or
  divergence reconstruction does not support a valid counterfactual.
- `ERROR` — prerequisite evidence, backend commit, dependency, or input
  artifact cannot be verified/read.

The verdict applies only to C-T08.

## Required transition counts

- `positive_to_positive_paths`
- `positive_to_negative_paths`
- `negative_to_negative_paths`
- `negative_to_positive_paths`

Expected production totals before counterfactual:

- positive = 5
- negative = 2

`negative_to_positive_paths` must be 0 by the range-subset invariant.

## Required magnitude counts

- `production_divergence_gt_max_within_unit_paths`
- `production_divergence_eq_max_within_unit_paths`
- `production_divergence_lt_max_within_unit_paths`

The last count must be 0 within absolute tolerance `1e-12`.

## Required raw outputs

- `raw/path_counterfactuals.jsonl`
- `raw/positive_to_negative_paths.jsonl`
- `raw/integrity_errors.jsonl`

Each path record must contain all exact-unit partition ranges and source
pointers for score rows.

## Required summary counts

At minimum:

- fact_rows_scanned;
- comparability_groups_scanned;
- mixed_unit_groups;
- applicable_mixed_variant_paths;
- production_true_paths;
- production_false_paths;
- positive_to_positive_paths;
- positive_to_negative_paths;
- negative_to_negative_paths;
- negative_to_positive_paths;
- production_divergence_gt_max_within_unit_paths;
- production_divergence_eq_max_within_unit_paths;
- production_divergence_lt_max_within_unit_paths;
- counterfactual_true_paths;
- counterfactual_false_paths;
- divergence_reconstruction_errors;
- group_consistency_errors;
- invariant_errors;
- integrity_error_records;
- unit-pattern transition breakdown.

All counts must be printed even when zero.

## Branch decision

If `CONFIRMED`:

- the audit may state that at least one production-positive flag depends on
  allowing cross-exact-unit arithmetic under the frozen grouping;
- do not call the flag semantically wrong without a reference rule;
- the next test should determine whether the affected flag is exposed in the
  public product or governs a published comparability claim before paying for
  semantic adjudication.

If `REFUTED`:

- the exact-label arithmetic counterfactual does not change any production
  positive boolean;
- stop this descendant branch and move to the next independent audit branch.

If `INCONCLUSIVE` or `ERROR`:

- repair or replace the measurement;
- do not attribute harness failure to EvalEval without boundary evidence.
