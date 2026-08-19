# RESULT_ANALYSIS — T15 WildBench Authoritative Source-Identity Trace

Status: final post-run analysis.

The original T15 preregistration is unchanged. The initial directory-creation
failure is retained as a harness/package error. Harness Fix 1 only created the
runtime output directories and did not modify the claim, population,
predictions, derivation rule, structured signature, or verdict rule.

## 1. Final verdict

`CONFIRMED`

The preregistered primary condition was:

`source_identity_trace_complete = true`

Observed:

`true`

Integrity errors:

`0`

## 2. Claim-governing counts

- affected rows = 8
- unique source metric ids = 4
- distinct raw metric names = 4
- exact adapter derivation ids = 4
- distinct non-name source signatures = 4
- source identity trace complete = true
- integrity error records = 0

Every preregistered CONFIRMED condition passed.

## 3. Exact source-name trace

The four frozen EEE source metric ids trace to four distinct preserved raw
OpenEval metric names:

- `openeval.wildbench.claude-score`
  <- `claude_score`
- `openeval.wildbench.gpt-score`
  <- `gpt_score`
- `openeval.wildbench.llama-score`
  <- `llama_score`
- `openeval.wildbench.wildbench-score-rescaled`
  <- `wildbench_score_rescaled`

All eight rows satisfy the frozen adapter naming rule.

Therefore the four downstream EEE source ids are not four aliases generated
from one raw OpenEval metric name.

## 4. Non-name structured signatures

The stronger T15 result is not merely four different strings.

After excluding both source metric id and raw metric name, all four identities
still have distinct structured signatures.

### Claude source channel

- evaluator/model metadata:
  `anthropic/claude-3-5-sonnet-20241022`
- metric kind: `benchmark_score`
- unit: `points`
- min: -1.0
- max: 10.0
- lower is better: false
- score type: `continuous`

### GPT source channel

- evaluator/model metadata:
  `openai/gpt-4o-2024-05-13`
- metric kind: `benchmark_score`
- unit: `points`
- min: 0.0
- max: 10.0
- lower is better: false
- score type: `continuous`

### Llama source channel

- evaluator/model metadata:
  `meta/llama-3.1-405b-instruct-turbo`
- metric kind: `benchmark_score`
- unit: `points`
- min: 0.0
- max: 10.0
- lower is better: false
- score type: `continuous`

### WildBench rescaled source channel

- evaluator/model metadata:
  - `anthropic/claude-3-5-sonnet-20241022`
  - `meta/llama-3.1-405b-instruct-turbo`
  - `openai/gpt-4o-2024-05-13`
- metric kind: `benchmark_score`
- unit: `score`
- min: 0.0
- max: 1.0
- lower is better: false
- score type: `continuous`

Thus:

`distinct_nonname_source_signatures = 4`

## 5. Strongest justified statement

The T14 claim-governing WildBench/OpenEval group combines four independently
traceable source-defined metric channels.

Those channels differ not only in raw source name but also in structured source
metadata, including evaluator/model provenance and, for the rescaled channel,
declared numerical scale.

This eliminates the benign explanation that the four source ids are merely
four downstream names for one raw source metric channel.

## 6. Important scale observation

Three source channels are declared as `points` with upper bound 10.0.

The rescaled source channel is declared as `score` with bounds 0.0 to 1.0.

Therefore the four-channel production group is not numerically scale-homogeneous
at the frozen source-definition boundary.

This observation is source-derived and deterministic.

It still does not by itself define the correct canonical repair.

## 7. Relationship to T12–T14

The causal/provenance chain is now:

1. T12:
   six source metric ids in the consequential groups collapse through fallback
   identity to one production metric key.

2. T13:
   the structured resolver rejects the ids because the frozen registry supplies
   no usable specific canonical identity.

3. T14:
   exact source-id preservation causes the WildBench production-positive group
   to lose all positive source-id subgroups.

4. T15:
   the four WildBench source ids are independently traceable to four distinct
   raw OpenEval metric names and four distinct non-name structured signatures.

The remaining question is no longer whether the identities are real.

The remaining question is what arithmetic/canonical relationship between those
four source channels is justified by authoritative source semantics.

## 8. What T15 does not establish

T15 does not establish that:

- every pair of distinct source metrics measures a different latent construct;
- all four source ids must remain permanently separate;
- no normalized or explicitly derived aggregate may combine them;
- exact source id is the correct universal canonical key;
- the source publisher intended any specific EvalEval canonicalization rule.

Different evaluator channels can in principle be intentionally aggregated if a
documented transformation defines that operation.

T15 therefore stops short of a general semantic-non-equivalence verdict.

## 9. Next branch

Proceed to a scale/procedure eligibility adjudication.

The next test should ask:

> Does authoritative frozen source metadata or source documentation specify a
> transformation under which the three 0/10 judge-specific channels and the
> 0/1 rescaled multi-judge channel are eligible for one raw-range arithmetic
> comparability group?

The competing explanations should be:

P1 — documented equivalence/normalization exists, so a common raw arithmetic
identity can be justified.

P2 — no such transformation is represented, and the source channels remain
different in scale and/or evaluation procedure, so raw-range arithmetic under
one metric key is not source-justified.

This test must distinguish:

- semantic construct;
- evaluator/judge channel;
- scale transformation;
- aggregate/derived metric;
- canonical identity.

## 10. Final T15 statement

T15 is CONFIRMED.

All four T14 WildBench/OpenEval source metric ids trace exactly to four distinct
raw OpenEval metric names. All four also retain distinct structured source
signatures after excluding the names themselves.

The four production inputs are therefore independently source-defined metric
channels, not downstream aliases of a single raw OpenEval metric name.
