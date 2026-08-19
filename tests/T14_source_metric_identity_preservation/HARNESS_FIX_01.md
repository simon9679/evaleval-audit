# HARNESS_FIX_01 — T14 source reconstruction

Status: post-error harness repair.

## Trigger

The original preregistered T14 analyzer stopped before producing test
measurements with:

`T14 ERROR`
`Stage F missing required columns: ['generation_args', 'source_organization_name']`

This is a harness/input-schema error, not an EvalEval result.

The original preregistration was verified before this error and is not changed.

## Root cause

The frozen backend constructs the Stage F comparability UDF payload from:

- `generation_args := generation_args_json`
- `source_organization_name := org_raw`

but the final `fact_results` output deliberately excludes
`generation_args_json`.

Therefore the T03 Stage F Parquet cannot by itself reconstruct the exact
variant UDF row payload.

`source_organization_name` was also a harness naming mistake: the persisted
row field is `org_raw`.

## Repair

Fix 1 changes data acquisition only.

It does not change:

- the T14 claim;
- the affected population;
- the counterfactual identity;
- source metric-id grouping;
- scores;
- thresholds;
- production variant-divergence function;
- competing predictions;
- verdict rule.

The repaired analyzer obtains:

- score / evaluation identity / evaluator relationship / `org_raw` /
  production metric metadata from frozen Stage F;
- generation arguments from the already-frozen EEE source record addressed by
  T10's `source_record_path + result_idx`.

## Replay gate

Because direct JSON source reconstruction can differ from the typed Arrow
representation in missing-vs-null shape, the repaired analyzer must first
reproduce each full production affected group.

For both groups, it requires equality with frozen Stage F for:

- `has_variant_divergence`;
- divergence magnitude;
- threshold;
- threshold basis;
- differing setup fields.

If either full-group replay differs, T14 remains INCONCLUSIVE and no
counterfactual interpretation is allowed.

## Method status

This is a harness repair after ERROR.

It is not a new test and does not retroactively rewrite the frozen
preregistration.
