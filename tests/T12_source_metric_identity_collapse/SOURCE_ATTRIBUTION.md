# SOURCE_ATTRIBUTION — T12 Source Metric Identity Collapse Trace

Status: frozen before execution.

## Immediate empirical trigger

T12 is a direct descendant of the combination of T05 and T11.

T05 reported, for the actual mixed-unit population:

- one Stage F `metric_raw` per group;
- one Stage F canonical `metric_id` per group;
- no multi-resolution-strategy groups;
- resolution strategy pattern `exact`.

T11 later established, for both product-consequential groups:

- source `metric_id` varies;
- source `max_score` varies;
- one group also varies in `metric_kind` and `lower_is_better`;
- the other also varies in `min_score`.

This creates a concrete source-to-canonical identity question.

## Frozen production transformation

Frozen backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

Stage C first computes a structured metric-id candidate from
`metric_config.metric_id`.

If that structured candidate is non-null:

- `metric_raw` records the trimmed source `metric_config.metric_id`;
- canonical `metric_id` uses the structured candidate;
- `metric_resolution_strategy` is `metric_id_structured`.

If the structured candidate is null:

- Stage C extracts a metric from evaluation description, metric name, or
  evaluation name;
- `metric_raw` becomes that extracted metric;
- canonical `metric_id` is resolved from that fallback raw metric;
- `metric_resolution_strategy` is the normal resolver strategy.

Stage D defines production:

`metric_key = COALESCE(metric_id, metric_raw)`

Stage F comparability groups on:

`(model_aggregation_key, benchmark_key, slice_key, metric_key)`

Therefore a source-id collapse can be tested directly from the frozen row
fields without re-running the resolver.

## Falsification Protocol contribution

The exact T12 test is not specified by the Protocol.

The Protocol contributes:

- Rule 2: separate source identity from downstream canonical identity;
- Rule 6: provenance of the identity transformation;
- Rule 7: trace the transformation that governs the consequential production
  grouping;
- Rule 8: freeze the collapse predicate before inspection;
- cheapest-to-more-expensive ordering: deterministic transformation trace
  before semantic alias adjudication.

## Validation Handbook contribution

Strongest anchors:

- U3: source identifiers are structured evidence, not automatic semantic truth;
- U4: no alias map or equivalence judgement is invented;
- U8: identity collapse is a narrower claim than semantic invalidity;
- U9: T12 follows T11;
- U11: explicit transformation-boundary attribution;
- U12: source metadata remain hypotheses;
- B12: the metric identity used for comparability grouping is claim-governing.

## Additional-test catalogue contribution

Closest supporting items:

- Test 1, Claim–Estimand Boundary;
- Test 4, Component / Harness Attribution.
