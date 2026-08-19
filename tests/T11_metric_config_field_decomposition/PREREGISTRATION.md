# PREREGISTRATION — T11 MetricConfig Field-Level Decomposition

Status: registered before T11 execution.

## Frozen prerequisites

Required T10 result:

- verdict = `CONFIRMED`;
- affected_group_ids = 2;
- affected_groups_present = 2;
- affected_arithmetic_rows = 12;
- source_rows_complete = 12;
- source_unit_matches = 12;
- source_unit_mismatches = 0;
- affected_groups_with_single_nonunit_signature = 0;
- affected_groups_with_nonunit_metric_config_heterogeneity = 2;
- pointer_or_index_errors = 0;
- evaluation_id_mismatches = 0;
- arithmetic_row_identity_errors = 0;
- integrity_error_records = 0.

Required input:

`tests/T10_source_metric_config_heterogeneity/raw/source_metric_configs.jsonl`

T10 primary signature fields must equal exactly:

- `metric_id`
- `metric_name`
- `metric_kind`
- `metric_parameters`
- `lower_is_better`
- `score_type`
- `min_score`
- `max_score`

## Population

All 12 complete source rows from the two T10 affected groups.

No sampling is allowed.

## Primary field set

All measured fields:

1. `metric_id`
2. `metric_name`
3. `metric_kind`
4. `metric_parameters`
5. `lower_is_better`
6. `score_type`
7. `min_score`
8. `max_score`

Claim-governing subset for C-T11:

- `metric_id`
- `metric_kind`
- `metric_parameters`
- `lower_is_better`
- `score_type`
- `min_score`
- `max_score`

`metric_name` is measured but excluded from the primary claim because it is a
display field in the frozen schema.

## Exact canonical value rule

- null remains null;
- dict/list values use canonical JSON with sorted dictionary keys;
- scalar types are preserved;
- no conversion or semantic normalization.

## Primary claim C-T11

At least one affected group varies in one or more claim-governing fields.

## Competing predictions

### P1

`affected_groups_with_claim_governing_field_variation = 0`

### P2

`affected_groups_with_claim_governing_field_variation >= 1`

## Primary verdict

- `CONFIRMED` — P2 observed and integrity controls pass.
- `REFUTED` — P1 observed and integrity controls pass.
- `INCONCLUSIVE` — T10 evidence is readable but source-row/signature
  invariants prevent decomposition.
- `ERROR` — prerequisite evidence cannot be verified/read.

## Required outputs

- `raw/field_decomposition.jsonl`
- `raw/claim_governing_variation_groups.jsonl`
- `raw/integrity_errors.jsonl`

## Required summary counts

At minimum:

- affected_group_ids;
- source_rows_scanned;
- affected_groups_with_claim_governing_field_variation;
- affected_groups_with_display_name_only_variation;
- affected_groups_with_no_nonunit_field_variation;
- per-field varying group counts for all 8 fields;
- per-group varying field lists;
- per-group claim-governing varying field lists;
- per-field unit-disjoint-value group counts;
- integrity_error_records.

All values must be printed.

## Branch decision

If `CONFIRMED`:

- source MetricConfig differences extend beyond display naming;
- use the exact varying fields to design the final narrow semantic/reference
  adjudication.

If `REFUTED`:

- T10 heterogeneity is display-name-only under the frozen schema;
- semantic adjudication should focus on unit labels and display naming.

If `INCONCLUSIVE` or `ERROR`:

- repair measurement before semantic attribution.
