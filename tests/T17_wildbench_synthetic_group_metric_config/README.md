# T17 — WildBench Synthetic Group MetricConfig Provenance

## Purpose

T16 established that the four claim-governing WildBench/OpenEval source
channels have three distinct source scale signatures and no represented common
scale under the fixed eligibility rule.

T17 tests the immediate production consequence of that heterogeneity.

The question is:

> Does Stage F construct a group-level metric configuration by field-wise
> aggregation that matches no exact source metric configuration, and is that
> reconstructed configuration consistent with the production divergence
> threshold?

## Fixed population

Comparability group:

`d38d8f8e547287b6b0fc78f43f310762`

Expected source ids:

- `openeval.wildbench.claude-score`
- `openeval.wildbench.gpt-score`
- `openeval.wildbench.llama-score`
- `openeval.wildbench.wildbench-score-rescaled`

Expected arithmetic rows:

`8`

## Production aggregation rule

Frozen Stage F constructs group metric metadata field-by-field using non-null
`MAX` for:

- `metric_kind`
- `metric_unit`
- `min_score`
- `max_score`

T14 already validated this reconstruction as part of exact full production
replay.

T17 independently reconstructs that group-level signature from the affected
Stage-F rows and compares it to every exact source signature.

## Output

- `raw/source_and_group_config_trace.json`
- `raw/integrity_errors.jsonl`
- `results/summary.json`
- `results/RESULT_ANALYSIS.md`
