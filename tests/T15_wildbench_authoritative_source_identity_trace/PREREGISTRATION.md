# PREREGISTRATION — T15

## Primary claim C-T15

For the four exact source metric ids in the T14 claim-governing
WildBench/OpenEval group:

1. all four are exactly derivable from four distinct preserved raw OpenEval
   metric names under the frozen adapter's naming rule; and
2. at least two distinct structured source signatures remain after excluding
   both `metric_id` and `raw_metric_name`.

## Fixed population

Group:

`d38d8f8e547287b6b0fc78f43f310762`

Expected rows:

`8`

Expected source metric ids:

- `openeval.wildbench.claude-score`
- `openeval.wildbench.gpt-score`
- `openeval.wildbench.llama-score`
- `openeval.wildbench.wildbench-score-rescaled`

Expected rows per source id:

`2`

## Exact derivation rule

For each frozen EEE row:

1. read `metric_config.additional_details.raw_metric_name`;
2. normalize underscores/spaces to hyphens under the frozen adapter slug rule;
3. derive `openeval.wildbench.<metric-slug>`;
4. require exact equality with the frozen `metric_config.metric_id`.

No manual aliases are allowed.

## Non-name structured source signature

The signature excludes both metric id and raw metric name.

Fields:

- `metric_models_json`;
- `metric_kind`;
- `metric_unit`;
- `lower_is_better`;
- `score_type`;
- `min_score`;
- `max_score`;
- `metric_parameters`.

Missing values remain null. No imputation is allowed.

## Competing predictions

### P1 — benign explanation

At least one of these is true:

- fewer than four distinct raw metric names are recovered;
- fewer than four exact adapter-derived ids are recovered;
- all four source ids share one non-name structured source signature.

Expected observable result:

`source_identity_trace_complete = false`

### P2 — consequential explanation

All four source ids trace exactly to four distinct preserved raw metric names,
and at least two non-name structured source signatures exist.

Expected observable result:

`source_identity_trace_complete = true`

## Verdict rule

`CONFIRMED` if:

- affected rows = 8;
- unique source ids = 4;
- rows per source id = 2;
- distinct raw metric names = 4;
- exact adapter-derived ids = 4;
- distinct non-name structured source signatures >= 2;
- integrity errors = 0.

`REFUTED` if all integrity checks pass but
`source_identity_trace_complete = false`.

`INCONCLUSIVE` if a claim-governing source field, source pointer, frozen
adapter, or accepted T14 dependency cannot be validated.

`ERROR` if the required files cannot be loaded or the test cannot execute.

## Branch stop / continue rule

If REFUTED:

`STOP RULE FOR THIS CLAIM BRANCH`

Do not infer semantic heterogeneity from source ids.

If INCONCLUSIVE:

obtain the missing authoritative source representation before semantic
adjudication.

If CONFIRMED:

continue to semantic/reference adjudication without assuming that different raw
metric names necessarily mean different estimands.
