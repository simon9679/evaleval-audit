# SOURCE_ATTRIBUTION — T04 Comparability Unit Consistency and Threshold-Choice Sensitivity

Status: frozen before execution.

## Immediate empirical trigger

T04 was not copied verbatim from the Falsification Protocol, the Validation
Handbook, or the additional-test catalogue.

Its immediate trigger is T03. During the full frozen production Stage F run,
EvalEval emitted an operator-visible warning that 1,425 root-collapsed groups
had more than one distinct non-null `metric_unit`.

Frozen source inspection then established an important design fact before T04
execution:

- Stage F constructs the actual comparability `metric_config` over
  `(model_aggregation_key, benchmark_key, slice_key, metric_key)`;
- the warning counter is computed over
  `(model_aggregation_key, benchmark_key, metric_key)`, without `slice_key`;
- the metric config selects non-null `metric_unit`, `min_score`, and `max_score`
  using deterministic `MAX(...)` aggregation.

Therefore the observed count 1,425 cannot be treated as 1,425 already-proven
ambiguous comparability groups. T04 must first separate cross-slice unit
heterogeneity from within-comparability-group heterogeneity.

Frozen backend:
`evaleval/eval_cards_backend_pipeline`
commit:
`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

Relevant frozen code:
- `src/eval_card_backend/canonicalise/stages.py`
- `src/eval_card_backend/canonicalise/thresholds.py`

## Falsification Protocol contribution

The Protocol does not define this exact test.

It contributes:

- the cheapest-to-most-expensive decision procedure: resolve the cheaper
  ambiguity before paying for a source-level or product-level follow-up;
- Rule 7, test the product rather than stopping at a mechanism warning;
- Rule 8, preregister hypotheses, thresholds, competing predictions, and
  analysis rules before the run.

The T04 stop rule is a direct application of that decision procedure.

## Validation Handbook contribution

Primary methodological anchors:

- B12, Comparability eligibility for evaluation infrastructure:
  required comparison semantics must align before results are treated as
  comparable;
- U4, every free parameter has a source:
  T04 does not invent alternative unit values; it sweeps only units actually
  present in the frozen group;
- U8, verdict granularity cannot exceed measurement granularity:
  a unit-choice-sensitive group does not imply that all EvalEval comparability
  results are invalid;
- U9, dependencies form a DAG:
  only this branch is continued or stopped;
- U11, attribution follows the declared system boundary:
  evidence-capture or reconstruction failure is not an EvalEval defect;
- U17, statistical operations must match the scale:
  `proportion`, `percent`, range-based, and fallback thresholds are not treated
  as interchangeable without testing their consequences;
- P8 Step 3 supports measuring the real frozen corpus after controlled
  instrument calibration.

B12 is the strongest direct Handbook source for T04.

## Additional-test catalogue contribution

No catalogue entry defines T04 directly.

Supporting analogues:

- Test 1, Claim–Estimand Boundary: prevents interpreting the Stage F warning
  count itself as a product-level defect;
- Test 18, Aggregation / Weight Robustness: supports preregistered sensitivity
  analysis when a final decision can depend on an operational aggregation
  choice.

Test 18 is an analogy, not the source of T04. T04 varies observed unit choices,
not leaderboard weights.

## Source classification

- Immediate test trigger: empirical result from T03.
- Direct procedural source: Falsification Protocol Rules 7 and 8 plus its
  cheapest-to-most-expensive ordering.
- Direct test-design source: Validation Handbook B12, with U4/U8/U9/U11/U17.
- Supporting catalogue analogues: additional tests 1 and 18.
