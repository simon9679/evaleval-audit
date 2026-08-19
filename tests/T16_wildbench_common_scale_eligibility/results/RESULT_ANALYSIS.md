# RESULT_ANALYSIS — T16 WildBench Common-Scale Eligibility

Status: final post-run analysis.

## 1. Final verdict

`CONFIRMED`

The preregistered consequential prediction was observed:

- `distinct_scale_signatures >= 2`
- `common_scale_eligible = false`

Observed:

- `affected_rows = 8`
- `unique_source_metric_ids = 4`
- `distinct_declared_units = 2`
- `distinct_bound_signatures = 3`
- `distinct_scale_signatures = 3`
- `nonempty_metric_parameters_ids = 0`
- `structured_transform_key_ids = 0`
- `common_scale_eligible = false`
- `integrity_error_records = 0`

All claim-governing integrity conditions passed.

## 2. Declared units

The eight frozen source rows contain two declared units:

- `points`
- `score`

The unit split is not inferred from metric names; it is read from frozen source
`metric_config.metric_unit`.

## 3. Declared bounds

Three exact bound signatures are present:

1. `[0.0, 1.0]`
2. `[-1.0, 10.0]`
3. `[0.0, 10.0]`

Therefore the source representation is not bound-homogeneous.

## 4. Exact source scale signatures

### Claude source channel

`openeval.wildbench.claude-score`

- unit = `points`
- min = -1.0
- max = 10.0

### GPT source channel

`openeval.wildbench.gpt-score`

- unit = `points`
- min = 0.0
- max = 10.0

### Llama source channel

`openeval.wildbench.llama-score`

- unit = `points`
- min = 0.0
- max = 10.0

### Rescaled WildBench source channel

`openeval.wildbench.wildbench-score-rescaled`

- unit = `score`
- min = 0.0
- max = 1.0

Thus the four source ids occupy three distinct scale signatures.

## 5. Modal scale

The modal exact scale signature is:

`points / 0.0 / 10.0`

It is shared by GPT and Llama.

Two source ids differ from the modal scale:

- `openeval.wildbench.claude-score`
- `openeval.wildbench.wildbench-score-rescaled`

## 6. Explicit transformation metadata

No source id has non-empty `metric_parameters`:

`nonempty_metric_parameters_ids = 0`

No source id has an `additional_details` key whose name matches the
preregistered structured transform-key scan:

`structured_transform_key_ids = 0`

Therefore eligibility case B did not fire.

Eligibility case A also did not fire because the scale signatures are not
identical.

Final eligibility:

`common_scale_eligible = false`

## 7. Strongest justified statement

The frozen structured source representation does not present the four
claim-governing WildBench/OpenEval channels on one common raw numeric scale and
does not provide the explicit structured per-channel transformation metadata
required by the preregistered eligibility rule.

Accordingly, direct raw-range arithmetic across all four channels is not
justified by the frozen structured source representation itself.

## 8. What T16 does not establish

T16 does not establish that:

- no undocumented upstream transformation exists;
- every source channel measures a different latent construct;
- an explicit future normalization could not make some channels commensurate;
- exact source-id separation is the only valid repair;
- the correct canonicalization policy is known.

The verdict is intentionally limited to represented common-scale eligibility.

## 9. Relationship to T14 and T15

T14 showed an operational consequence: preserving source metric identity makes
the claim-governing WildBench group lose all positive source-id subgroups.

T15 showed that the four source ids are independently traceable source-defined
channels with four distinct non-name structured signatures.

T16 now shows that those channels are also not source-represented on one common
raw scale and carry no explicit structured conversion metadata under the fixed
eligibility rule.

## 10. New empirical trigger

T16 exposes a more specific deterministic question before any broader semantic
adjudication.

Production Stage F constructs one group-level metric configuration by selecting
non-null maxima field-by-field across heterogeneous rows.

For this WildBench group, the production configuration observed in T14 is:

- metric kind = `benchmark_score`
- metric unit = `score`
- min score = 0.0
- max score = 10.0

No T16 source channel has that exact scale signature.

The next cheapest descendant test should therefore determine whether production
constructs a synthetic group metric configuration that does not correspond to
any source metric definition, and whether that synthetic configuration is the
configuration used to derive the production divergence threshold.

## 11. Final T16 statement

T16 is CONFIRMED.

The four claim-governing WildBench/OpenEval source channels have two declared
units, three bound signatures, and three exact scale signatures. None has
non-empty structured transformation metadata under the preregistered rule.

The frozen structured source representation therefore does not itself establish
a common raw arithmetic scale for the production grouping.
