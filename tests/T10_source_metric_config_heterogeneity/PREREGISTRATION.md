# PREREGISTRATION — T10 Source MetricConfig Heterogeneity

Status: registered before T10 execution.

## Frozen prerequisites

Backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

T03 Stage F Parquet SHA-256:

`e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196`

Required T09 result:

- verdict = `CONFIRMED`;
- affected_group_ids = 2;
- affected_groups_present = 2;
- affected_groups_production_true = 2;
- production_variant_divergent_count = 343;
- counterfactual_variant_divergent_count = 341;
- headline_variant_divergent_count_delta = -2;
- integrity_error_records = 0.

Required T08 raw evidence:

`tests/T08_within_unit_variant_counterfactual/raw/positive_to_negative_paths.jsonl`

must contain exactly two unique affected group ids.

Required T06 source root:

`tests/T06_eee_source_unit_trace/raw/source_root.json`

must contain a non-null existing selected frozen EEE root.

## Population

All numeric arithmetic score rows in exactly the two T08
positive-to-negative groups.

No sampling or manual case selection is allowed.

## Source row rule

For each arithmetic row:

1. resolve `source_record_path` under the frozen EEE root;
2. parse the JSON object;
3. select zero-based `evaluation_results[result_idx]`;
4. verify evaluation id where present;
5. read `metric_config`.

Pointer/index/evaluation-id failure is an integrity failure and not a source
heterogeneity finding.

## Primary non-unit signature

The signature is the canonical JSON serialization of exactly these fields:

1. `metric_id`
2. `metric_name`
3. `metric_kind`
4. `metric_parameters`
5. `lower_is_better`
6. `score_type`
7. `min_score`
8. `max_score`

Rules:

- missing field -> null;
- dictionary keys -> sorted canonical JSON;
- list order -> preserved;
- string case -> preserved;
- no trimming;
- no synonym mapping;
- no numerical conversion;
- `metric_unit` excluded.

## Primary claim C-T10

At least one affected group has two or more distinct primary non-unit
MetricConfig signatures.

## Competing predictions

### P1

`affected_groups_with_nonunit_metric_config_heterogeneity = 0`

### P2

`affected_groups_with_nonunit_metric_config_heterogeneity >= 1`

## Primary verdict

- `CONFIRMED` — P2 is observed and all integrity controls pass.
- `REFUTED` — P1 is observed and all integrity controls pass.
- `INCONCLUSIVE` — source files are readable but pointers, group population,
  or source-vs-T08 row identity prevents complete interpretation.
- `ERROR` — prerequisite evidence, backend commit, Stage F artifact, source
  root, or dependency cannot be verified/read.

The verdict applies only to C-T10.

## Integrity controls

The test must verify:

- exactly two affected group ids;
- both affected ids exist in Stage F;
- both remain production-positive;
- Stage F arithmetic row identity matches the rows frozen in T08 evidence;
- every source pointer resolves;
- every result index is valid;
- every source unit reproduces the Stage F unit after only the already-verified
  `percentage -> percent` normalization;
- evaluation id matches where present.

## Required raw outputs

- `raw/source_metric_configs.jsonl`
- `raw/group_signature_summary.jsonl`
- `raw/heterogeneous_groups.jsonl`
- `raw/integrity_errors.jsonl`

## Required summary counts

At minimum:

- fact_rows_scanned;
- affected_group_ids;
- affected_groups_present;
- affected_arithmetic_rows;
- source_rows_complete;
- source_unit_matches;
- source_unit_mismatches;
- affected_groups_with_single_nonunit_signature;
- affected_groups_with_nonunit_metric_config_heterogeneity;
- affected_units_with_multiple_signatures;
- signatures_shared_across_multiple_units;
- pointer_or_index_errors;
- evaluation_id_mismatches;
- arithmetic_row_identity_errors;
- integrity_error_records;
- per-group unit/signature counts.

All counts must be printed even when zero.

## Branch decision

If `CONFIRMED`:

- the audit may state that at least one product-consequential group combines
  source rows with structured metric-definition differences beyond unit;
- the next test should identify which schema fields separate the signatures
  and determine whether those differences establish distinct estimands under a
  defensible reference.

If `REFUTED`:

- the structured source metric definition is otherwise identical under the
  fixed signature;
- the next semantic adjudication should focus narrowly on the declared unit
  disagreement itself.

If `INCONCLUSIVE` or `ERROR`:

- repair the source-trace measurement;
- do not attribute harness failure to EvalEval.
