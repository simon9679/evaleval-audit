# HARNESS_FIX_04 — DuckDB serialization replay

Status: post-INCONCLUSIVE harness repair.

## Trigger

T14 Fix 3 ended INCONCLUSIVE with one production replay mismatch.

For the remaining CocoaBench group, these quantities matched frozen Stage F:

- `has_variant_divergence`
- divergence magnitude
- threshold
- threshold basis

The only mismatch was within the serialized
`agentic_eval_config.additional_details` representation.

Frozen:

`additional_details` is a JSON object.

Fix 3:

`additional_details` is a list of key/value pairs.

## Root cause

The frozen Arrow schema represents `additional_details` as
`MAP<string, string>`.

Fix 3 used PyArrow `to_pylist()` to leave the Arrow representation.
Apache Arrow documents that the default Python conversion of MapArray values
is an association list, not a dictionary.

Production does not use that conversion.

Production registers the typed Arrow table in DuckDB and Stage D applies
`to_json` directly to the typed generation-args value.

DuckDB documents that `to_json` converts MAP and STRUCT values to JSON
objects.

## Repair

Fix 4 reconstructs generation arguments through the exact representation path
that matters to Stage F:

1. read the frozen EEE JSON;
2. frozen Pydantic validation;
3. frozen Arrow schema derivation;
4. frozen schema padding;
5. Arrow table construction with the production table schema;
6. register that Arrow table in DuckDB;
7. select the 1-based evaluation-result element corresponding to the frozen
   0-based `result_idx`;
8. execute
   `CAST(to_json(generation_config.generation_args) AS VARCHAR)`;
9. pass that JSON string directly to the frozen production divergence
   function.

No nested value is manually rewritten.

## Unchanged T14 contract

Fix 4 does not change:

- C-T14;
- the two affected production groups;
- the twelve affected rows;
- the six exact source metric ids;
- the exact-source-id grouping intervention;
- scores;
- source metric configs;
- production metric-config MAX reconstruction;
- the frozen production divergence function;
- P1 / P2;
- the verdict rule.

## Replay gate

Counterfactual source-id subgroup computation is forbidden unless both complete
affected groups reproduce frozen Stage F exactly for:

- boolean;
- divergence magnitude;
- threshold;
- threshold basis;
- differing setup fields.

## Attribution

All earlier T14 failures remain harness failures, not EvalEval findings.
