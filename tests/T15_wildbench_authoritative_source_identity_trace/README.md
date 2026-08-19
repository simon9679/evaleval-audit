# T15 — WildBench Authoritative Source-Identity Trace

## Purpose

T14 established an operational causal result for one production-positive
WildBench/OpenEval comparability group: preserving exact source metric identity
caused that group to lose every positive source-id subgroup.

T15 is the next cheaper provenance gate before semantic adjudication.

The question is narrow:

> Are the four exact source metric ids in the T14 claim-governing group
> traceable through the frozen OpenEval-to-EEE adapter to four distinct raw
> OpenEval metric names, with source metadata differences beyond the names?

This test does not decide whether the four metrics are semantically
non-equivalent.

## Fixed population

Group:

`d38d8f8e547287b6b0fc78f43f310762`

Expected source metric ids:

- `openeval.wildbench.claude-score`
- `openeval.wildbench.gpt-score`
- `openeval.wildbench.llama-score`
- `openeval.wildbench.wildbench-score-rescaled`

Expected arithmetic rows:

`8`

Expected rows per source id:

`2`

## Frozen authorities

- Frozen EEE datastore already used by T06, T10 and T14.
- Frozen `evaleval/every_eval_ever` commit
  `9bce4136e789ec006c62582f5f9d107d20f8b398`.
- Official `allenai/WildBench` commit
  `d6b8dcaf377d173d031980f97c16e1a82618c03d`.

The WildBench authority establishes that the benchmark has separate
individual-score and pairwise-reward procedures, including three pairwise
reference-model channels. T15 does not map the OpenEval source metric names to
those procedures from names alone.

## Output

The analyzer writes:

- `raw/source_identity_trace.jsonl`
- `raw/integrity_errors.jsonl`
- `results/summary.json`
- `results/RESULT_ANALYSIS.md`
