# RESULT_ANALYSIS — T17 WildBench Synthetic Group MetricConfig Provenance

Status: final post-run analysis.

## 1. Final verdict

`CONFIRMED`

The accepted T17 run passed every preregistered claim-governing condition:

- affected rows = 8
- exact source metric ids = 4
- production signature source match count = 0
- threshold replay exact = true
- integrity error records = 0

The frozen production threshold was reproduced exactly:

- frozen threshold = 0.5
- frozen threshold basis = `range_5pct`
- replay threshold = 0.5
- replay threshold basis = `range_5pct`

## 2. Reconstructed production group configuration

The production group configuration is:

- metric kind = `benchmark_score`
- metric unit = `score`
- min score = 0.0
- max score = 10.0

Exact object:

`{"max_score":10.0,"metric_kind":"benchmark_score","metric_unit":"score","min_score":0.0}`

## 3. Exact source configurations

### Claude source channel

`openeval.wildbench.claude-score`

- metric kind = `benchmark_score`
- metric unit = `points`
- min score = -1.0
- max score = 10.0

### GPT source channel

`openeval.wildbench.gpt-score`

- metric kind = `benchmark_score`
- metric unit = `points`
- min score = 0.0
- max score = 10.0

### Llama source channel

`openeval.wildbench.llama-score`

- metric kind = `benchmark_score`
- metric unit = `points`
- min score = 0.0
- max score = 10.0

### Rescaled WildBench source channel

`openeval.wildbench.wildbench-score-rescaled`

- metric kind = `benchmark_score`
- metric unit = `score`
- min score = 0.0
- max score = 1.0

No exact source configuration equals the production group configuration.

Observed:

`production_signature_source_match_count = 0`

## 4. Field-level provenance

The production fields come from different source definitions.

### `metric_unit = score`

Supported only by:

- `openeval.wildbench.wildbench-score-rescaled`

### `max_score = 10.0`

Supported by:

- `openeval.wildbench.claude-score`
- `openeval.wildbench.gpt-score`
- `openeval.wildbench.llama-score`

### `min_score = 0.0`

Supported by:

- `openeval.wildbench.gpt-score`
- `openeval.wildbench.llama-score`
- `openeval.wildbench.wildbench-score-rescaled`

### `metric_kind = benchmark_score`

Supported by all four source channels.

This is the most important T17 provenance fact.

The group configuration combines the unit label from the 0-to-1 rescaled
source channel with the upper bound from the 0-to-10 point-valued source
channels.

That exact combination exists in no source metric definition.

## 5. Threshold consequence

The frozen threshold resolver receives the synthetic group configuration.

Because the unit is neither `proportion` nor `percent`, and the reconstructed
bounds are 0.0 to 10.0, the resolver uses the range-based rule:

`0.05 * (10.0 - 0.0) = 0.5`

The accepted replay exactly matches production:

- magnitude = 0.5
- basis = `range_5pct`

Therefore the synthetic group configuration is not merely display metadata. It
is claim-governing for the production divergence threshold.

## 6. Strongest justified statement

For the claim-governing WildBench/OpenEval group, production constructs a
field-wise synthetic metric configuration that corresponds to no exact source
metric definition.

That synthetic configuration combines `metric_unit = score` from the 0-to-1
rescaled channel with `max_score = 10.0` from the point-valued channels, and it
is the configuration that exactly reproduces the production divergence
threshold of 0.5.

## 7. Relationship to T14–T16

The evidence chain is now:

1. T14:
   preserving exact source metric identity removes every positive subgroup for
   this production-positive WildBench group.

2. T15:
   the four source ids are four independently traceable source-defined metric
   channels with four distinct structured signatures.

3. T16:
   the channels occupy three source scale signatures and the frozen structured
   representation supplies no common-scale transform under the preregistered
   eligibility rule.

4. T17:
   production constructs a new field-wise group metric configuration that
   matches no source definition, and uses it for threshold selection.

## 8. What T17 does not establish

T17 does not establish that:

- every synthetic aggregate configuration is invalid in every system;
- a documented aggregate could never define a legitimate synthetic scale;
- exact source-id preservation is the only valid repair;
- all four source channels necessarily measure different latent constructs.

The result is specific to provenance and the frozen production computation.

## 9. Next empirical descendant

The next cheapest test is score-extrema provenance.

The production variant-divergence function computes:

`max(score) - min(score)`

over all scored rows in the grouped metric identity.

T18 should determine exactly which source metric ids and source scale
signatures supply the global minimum and maximum that create the production
divergence magnitude.

This distinguishes two cases:

- the global range is generated within one source-defined scale; or
- the global range directly spans different source identities/scales.

## 10. Final T17 statement

T17 is CONFIRMED.

The production WildBench group uses a synthetic group MetricConfig that matches
zero exact source metric configurations. Its threshold replay is exact.

The synthetic configuration is assembled across source definitions and is
claim-governing for the 0.5 production divergence threshold.
