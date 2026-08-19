# SOURCE_ATTRIBUTION — T14 Source Metric Identity Preservation Counterfactual

Status: frozen before execution.

## Immediate empirical trigger

T14 is a direct descendant of T12 and T13.

T12 established that both consequential production groups contain multiple
source metric ids that collapse to:

- `metric_raw = score`
- canonical `metric_id = score`
- `metric_key = score`

with no `metric_id_structured` rows.

T13 established why the structured path defers:

- 4 source ids have no structured metric hits;
- 2 have catch-all-only hits;
- 0 have conflicting specific metric hits.

T14 asks whether the fallback identity collapse is operationally necessary for
the two production-positive variant flags.

## Frozen production function

Frozen backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

Relevant implementation:

`src/eval_card_backend/signals/comparability.py`

The production variant-divergence function:

1. requires at least two rows;
2. requires at least one differing generation setup field;
3. requires at least two real scores;
4. computes raw `max(score) - min(score)`;
5. computes the metric threshold from metric config;
6. returns `divergence > threshold`.

T14 calls this frozen production function unchanged.

## Counterfactual grouping identity

Production affected grouping uses:

`metric_key = score`

T14 replaces only that identity boundary within the twelve affected rows:

`counterfactual_metric_key = exact source metric_config.metric_id`

Other group coordinates remain frozen:

- model aggregation key;
- benchmark key;
- slice key.

No source metric ids are normalized, merged, or aliased.

## Metric config for each source-id subgroup

For each exact source metric id, T14 uses its frozen source metric config
fields:

- metric_kind
- metric_unit
- min_score
- max_score

These are the fields consumed by the frozen variant-divergence threshold logic.

All rows sharing one source metric id must agree on these fields.

Disagreement is an integrity failure, not an EvalEval finding.

## Falsification Protocol contribution

The exact T14 counterfactual is not specified by the Protocol.

The Protocol contributes:

- Rule 7: test whether the identified identity transformation changes the
  produced decision;
- Rule 8: freeze the identity-preservation rule before the run;
- cheapest-to-more-expensive ordering: deterministic causal counterfactual
  before external semantic adjudication.

## Validation Handbook contribution

Strongest anchors:

- B12: metric identity is a claim-governing comparability eligibility
  predicate;
- U4: exact source ids introduce no learned alias or free parameter;
- U8: operational dependence is narrower than semantic correctness;
- U9: T14 follows T12/T13;
- U14: the measurement must resolve whether identity preservation changes the
  consequential decision;
- U17: the same production operation is recomputed within the alternative
  eligibility boundary.

## Additional-test catalogue contribution

Closest supporting items:

- Test 1, Claim–Estimand Boundary;
- Test 4, Component / Harness Attribution.
