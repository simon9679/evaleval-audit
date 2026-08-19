# HARNESS_FIX_03 — Frozen typed Stage-A generation-args reconstruction

Status: post-INCONCLUSIVE harness repair.

## Trigger

T14 Fix 2 completed with:

- verdict = INCONCLUSIVE
- affected production groups = 2
- affected rows = 12
- generation args source rows complete = 12
- generation args source errors = 0
- production groups replayed exact = 1
- production replay errors = 1
- integrity error records = 1
- no counterfactual subgroup execution

The single remaining mismatch is confined to the representation of
`agentic_eval_config` in `differing_setup_fields`.

All of the following already match for the remaining CocoaBench group:

- production boolean;
- divergence magnitude;
- threshold;
- threshold basis.

The frozen representation contains the nullable schema field
`available_tools: null`; the direct raw-JSON reconstruction omits that key.

## Root cause

The production pipeline does not feed raw EEE JSON directly to Stage F.

Stage A first:

1. validates each record with the vendored Pydantic `EvaluationLog`;
2. pads the record to the vendored Arrow schema;
3. casts it to the typed Arrow schema.

Stage D then serializes the typed
`generation_config.generation_args` struct to JSON.

Fix 2 reconstructed generation args directly from raw source JSON and
therefore missed schema-added nullable fields.

## Repair

Fix 3 reconstructs the exact typed Stage-A representation for each of the
twelve frozen source records:

1. read the frozen EEE JSON by the T10 source pointer;
2. validate with frozen `EvaluationLog.model_validate`;
3. derive the frozen Arrow schema with `derive_pyarrow_schema`;
4. apply frozen `pad_record_for_cast`;
5. cast a one-row table to that Arrow schema;
6. convert the typed row back to Python;
7. extract `evaluation_results[result_idx].generation_config.generation_args`.

No field is manually inserted.

## Unchanged T14 contract

Fix 3 does not change:

- the original T14 claim;
- affected population;
- source metric ids;
- exact-source-id counterfactual;
- scores;
- production metric-config reconstruction;
- frozen production divergence function;
- competing predictions;
- verdict rule.

## Replay gate

Both complete affected production groups must reproduce frozen Stage F exactly
for:

- `has_variant_divergence`;
- divergence magnitude;
- threshold;
- threshold basis;
- differing setup fields.

Only then may the source-id counterfactual execute.

## Attribution

The original T14 ERROR, Fix 1 INCONCLUSIVE, and Fix 2 INCONCLUSIVE are harness
failures.

They are not EvalEval findings.
