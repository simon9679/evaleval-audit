# PREREGISTRATION — T06 Frozen EEE Source Unit Trace

Status: registered before T06 execution.

## Frozen prerequisites

Backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

T03 Stage F Parquet SHA-256:

`e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196`

Required T05 result:

- verdict = `REFUTED`;
- actual_mixed_unit_groups = 1234;
- single_raw_metric_groups = 1234;
- multi_raw_metric_groups = 0;
- groups_with_unresolved_metric_rows = 0;
- resolution strategy pattern = `{"exact": 1234}`;
- metric-unit provenance pattern = `{"eee_record": 1234}`;
- full resolved canonical-convergence groups = 0;
- integrity errors = 0.

## Population

All Stage F rows in all actual mixed-unit comparability groups.

Expected group count:

`1234`

No sample or manual case selection is allowed.

## Row trace rule

For each population row:

- `source_record_path` must be non-null;
- the referenced file must exist inside the frozen EEE root;
- file content must parse as JSON object;
- `evaluation_results` must be a list;
- `result_idx` must be a valid zero-based index;
- the source row is `evaluation_results[result_idx]`;
- source unit is
  `source_row.metric_config.metric_unit`, or null if absent;
- source unit is normalized only by:
  - string value `percentage` in any letter case -> `percent`;
  - every other value is left unchanged;
- normalized source unit must equal the Stage F `metric_unit`.

The case-insensitive handling of the literal synonym matches the frozen
implementation's `.lower()` lookup. No other case normalization is allowed.

## Group trace rule

For every actual mixed-unit group:

`set(normalized source non-null units) == set(Stage F non-null units)`

## Competing predictions

### P1

- `row_unit_mismatches = 0`
- `group_unit_set_mismatches = 0`
- `pointer_or_index_errors = 0`

### P2

At least one valid source trace produces:

- `row_unit_mismatches >= 1`
  or
- `group_unit_set_mismatches >= 1`

## Verdict

- `CONFIRMED` — P1 holds for the complete population and all integrity checks
  pass.
- `REFUTED` — at least one validly traced row/group has a source-vs-Stage-F
  unit mismatch and all global prerequisite integrity checks pass.
- `INCONCLUSIVE` — the frozen inputs are readable but missing/invalid source
  pointers, index errors, source-root ambiguity, or population reconstruction
  prevents complete interpretation.
- `ERROR` — prerequisite evidence, backend commit, Stage F artifact, or EEE
  source root cannot be verified/read at all.

This verdict applies only to the source-faithfulness claim C-T06.

## Required raw outputs

- `raw/source_root.json`
- `raw/row_trace.jsonl`
- `raw/row_mismatches.jsonl`
- `raw/group_trace.jsonl`
- `raw/group_mismatches.jsonl`
- `raw/integrity_errors.jsonl`

## Required summary counts

At minimum:

- fact_rows_scanned;
- comparability_groups_scanned;
- mixed_unit_groups;
- mixed_unit_rows;
- source_files_referenced;
- source_files_opened;
- row_traces_complete;
- row_unit_matches;
- row_unit_mismatches;
- group_unit_set_matches;
- group_unit_set_mismatches;
- pointer_or_index_errors;
- evaluation_id_mismatches;
- integrity_error_records;
- source-unit pattern breakdown.

All counts must be printed even when zero.

## Branch decision

If `CONFIRMED`:

- the mixed-unit labels are verified as already present in the frozen EEE
  datastore records referenced by Stage F;
- do not call the original publisher wrong;
- the next semantic question, if still claim-governing, is whether EEE records
  are legitimately representing different quantities under one comparison
  identity or whether a normalization/eligibility rule is missing.

If `REFUTED`:

- inspect only the mismatching source traces to localize the transformation
  between source JSON and Stage F;
- do not attribute the mismatch upstream.

If `INCONCLUSIVE` or `ERROR`:

- repair the source-trace measurement;
- do not convert file/pointer failures into EvalEval defects without boundary
  evidence.
