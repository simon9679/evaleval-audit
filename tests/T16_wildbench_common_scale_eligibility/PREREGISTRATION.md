# PREREGISTRATION — T16

## Primary claim C-T16

The four T15 claim-governing WildBench/OpenEval source channels are not
source-represented as one common raw numeric scale for direct range arithmetic.

## Fixed population

Group:

`d38d8f8e547287b6b0fc78f43f310762`

Expected rows:

`8`

Expected source ids:

- `openeval.wildbench.claude-score`
- `openeval.wildbench.gpt-score`
- `openeval.wildbench.llama-score`
- `openeval.wildbench.wildbench-score-rescaled`

Expected rows per source id:

`2`

## Scale signature

Per exact source id:

`(metric_unit, min_score, max_score)`

Null is retained as null.

No bounds are inferred.

## Explicit transformation metadata

Primary structured transformation metadata:

`metric_parameters`

Supporting structured transformation-key scan:

all keys under `metric_config.additional_details` whose key name contains one
of:

- `normal`
- `rescal`
- `transform`
- `convert`
- `scale`

The raw metric name itself is excluded from this key scan.

A text label such as `wildbench_score_rescaled` does not count as an explicit
conversion formula.

## Common-scale eligibility predicate

`common_scale_eligible = true` if either:

A. `distinct_scale_signatures == 1`

or

B. every source id with a scale signature different from the modal scale has
non-empty `metric_parameters`.

Otherwise:

`common_scale_eligible = false`

This predicate is intentionally restricted to represented structured metadata.

## Competing predictions

### P1 — benign explanation

Expected:

`common_scale_eligible = true`

### P2 — consequential explanation

Expected:

- `distinct_scale_signatures >= 2`
- `common_scale_eligible = false`

## Verdict

`CONFIRMED` if:

- affected rows = 8;
- unique source ids = 4;
- every source id has 2 rows;
- source configs are internally consistent per source id;
- distinct scale signatures >= 2;
- common scale eligible = false;
- integrity errors = 0.

`REFUTED` if all integrity checks pass and:

`common_scale_eligible = true`

`INCONCLUSIVE` if:

- a claim-governing scale field cannot be read consistently;
- T15 accepted dependency cannot be verified;
- source pointers fail;
- structured transform fields are malformed.

`ERROR` if the test cannot execute.

## Branch stop / continue rule

If REFUTED:

`STOP RULE FOR THIS CLAIM BRANCH`

Do not claim lack of source-represented commensurability.

If INCONCLUSIVE:

repair only the missing source/integrity acquisition path.

If CONFIRMED:

proceed to procedure/semantic adjudication only if a stronger statement than
"not source-represented on one raw scale" is required.
