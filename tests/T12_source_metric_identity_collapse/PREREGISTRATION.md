# PREREGISTRATION — T12 Source Metric Identity Collapse Trace

Status: registered before T12 execution.

## Frozen prerequisites

Required T11 result:

- verdict = `CONFIRMED`;
- affected_group_ids = 2;
- source_rows_scanned = 12;
- affected_groups_with_claim_governing_field_variation = 2;
- integrity_error_records = 0;
- `metric_id` varies in 2 groups;
- `max_score` varies in 2 groups.

Required T10 source-row input:

`tests/T10_source_metric_config_heterogeneity/raw/source_metric_configs.jsonl`

Required frozen Stage F input:

`tests/T03_corpus_boundary_impact/raw/fact_results_stage_f.parquet`

SHA-256:

`e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196`

Backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

## Population

Exactly the 12 T10 source rows in exactly the two T11 affected groups.

No sampling.

## Row identity join

Primary row identity uses `fact_id`.

For every source row, exactly one Stage F row with the same `fact_id` must
exist in the same `comparability_group_id`.

Any duplicate/missing join is an integrity failure.

## Required Stage F fields

- `fact_id`
- `comparability_group_id`
- `metric_raw`
- `metric_id`
- `metric_resolution_strategy`
- `metric_key`

Optional, reported when present:

- `metric_id_effective`
- `metric_key_effective`

## Primary collapse predicate

For each affected group:

- `source_metric_id_count >= 2`
- `stage_metric_raw_count = 1`
- `stage_metric_id_count = 1`
- `stage_metric_key_count = 1`
- `metric_id_structured_row_count = 0`

Then:

`fallback_source_id_collapse = true`

## Primary claim C-T12

At least one affected group satisfies the full fallback source-id collapse
predicate.

## Competing predictions

### P1

`affected_groups_with_fallback_source_id_collapse = 0`

### P2

`affected_groups_with_fallback_source_id_collapse >= 1`

## Primary verdict

- `CONFIRMED` — P2 observed and all integrity controls pass.
- `REFUTED` — P1 observed and all integrity controls pass.
- `INCONCLUSIVE` — Stage F/source evidence is readable but row identity,
  group identity, or transformation fields are inconsistent.
- `ERROR` — required input, backend commit, Stage F SHA, or dependency cannot
  be verified/read.

## Integrity controls

The test must verify:

- exactly 12 source rows;
- exactly 2 group ids;
- every source row has non-null source metric id;
- exactly one Stage F match per source `fact_id`;
- Stage F group id equals source-record group id;
- the source metric id in T10 is unchanged;
- no duplicate `fact_id`;
- required Stage F columns exist.

## Required outputs

- `raw/row_identity_trace.jsonl`
- `raw/group_collapse_summary.jsonl`
- `raw/collapse_groups.jsonl`
- `raw/integrity_errors.jsonl`

## Required summary counts

At minimum:

- affected_group_ids;
- source_rows_scanned;
- stage_rows_joined;
- distinct_source_metric_ids_total;
- affected_groups_with_multiple_source_metric_ids;
- affected_groups_with_single_stage_metric_raw;
- affected_groups_with_single_stage_metric_id;
- affected_groups_with_single_stage_metric_key;
- affected_groups_with_structured_strategy_rows;
- affected_groups_with_fallback_source_id_collapse;
- source_ids_mapping_to_one_metric_key_groups;
- row_identity_errors;
- integrity_error_records;
- per-group identity sets.

All counts must be printed.

## Branch decision

If `CONFIRMED`:

- the audit may state that multiple source-declared metric ids are collapsed
  into one fallback production metric identity in at least one
  product-consequential group;
- next, use only the confirmed collapse groups for a narrow semantic/reference
  equivalence test.

If `REFUTED`:

- source metric-id heterogeneity is not explained by this fallback collapse
  predicate;
- inspect the alternative identity mechanism before semantic judgement.

If `INCONCLUSIVE` or `ERROR`:

- repair the transformation trace;
- do not attribute the measurement failure to EvalEval.
