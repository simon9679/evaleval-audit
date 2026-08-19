# T16 — WildBench Common-Scale Eligibility

## Purpose

T14 established an operational causal result: the claim-governing
WildBench/OpenEval production-positive group loses every positive subgroup when
exact source metric identity is preserved.

T15 then established that the four source ids are independently traceable
source-defined metric channels with four distinct non-name structured
signatures.

T16 asks the next narrower question:

> Does the frozen source representation provide a common numeric scale, or an
> explicit transformation into one, that justifies direct raw-range arithmetic
> across the four source channels?

This is a structured scale-eligibility test.

It is not yet a general semantic-equivalence judgment.

## Fixed population

Group:

`d38d8f8e547287b6b0fc78f43f310762`

Source ids:

- `openeval.wildbench.claude-score`
- `openeval.wildbench.gpt-score`
- `openeval.wildbench.llama-score`
- `openeval.wildbench.wildbench-score-rescaled`

Expected rows:

`8`

## Operational eligibility predicate

A source-represented common raw scale is present if either:

1. all four source ids have one identical declared scale signature
   `(metric_unit, min_score, max_score)`; or
2. every source id that differs in scale carries explicit structured
   transformation metadata in `metric_parameters` defining its conversion.

This predicate is intentionally narrow.

It tests whether direct raw arithmetic is justified by the frozen structured
representation, not whether an undocumented transformation might exist
elsewhere.

## Output

- `raw/source_scale_trace.jsonl`
- `raw/integrity_errors.jsonl`
- `results/summary.json`
- `results/RESULT_ANALYSIS.md`
