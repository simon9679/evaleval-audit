# SOURCE_ATTRIBUTION — T09 Headline Comparability Aggregate Impact

Status: frozen before execution.

## Immediate empirical trigger

T09 is a direct descendant of T08.

T08 found:

- 7 production-applicable mixed-unit variant paths;
- 5 production-positive paths;
- 2 production-positive paths become negative under the preregistered
  exact-label within-unit counterfactual;
- zero reconstruction, consistency, monotonicity, or integrity errors.

T09 asks whether those two consequential paths reach a product-facing frozen
aggregate.

## Frozen product implementation

Frozen backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

Relevant source:

`src/eval_card_backend/canonicalise/sidecars.py`

The source documents `headline.json` as a frontend-consumed corpus-signal
sidecar that drives the home-page corpus signal strip.

The overall comparability block counts from `fact_results`:

- total distinct `comparability_group_id`;
- distinct groups with `has_variant_divergence = TRUE`;
- distinct groups with `has_cross_party_divergence = TRUE`;
- distinct groups where the variant check is applicable;
- distinct groups where the cross-party check is applicable.

The relevant production quantity is therefore:

`variant_divergent_count =
 COUNT(DISTINCT comparability_group_id)
 FILTER (WHERE has_variant_divergence)`

For the overall headline block there is no tag filter.

## Falsification Protocol contribution

The exact T09 test is not stated in the Protocol.

The Protocol contributes:

- Rule 7: test the product-facing outcome rather than stopping at an internal
  arithmetic mechanism;
- Rule 8: freeze the product consequence and counterfactual analysis before
  execution;
- cheapest-to-more-expensive ordering: verify public aggregate consequence
  before paying for semantic/reference adjudication.

## Validation Handbook contribution

The strongest anchors are:

- U8, verdict granularity: a headline aggregate effect is distinct from a
  semantic correctness verdict;
- U9, dependency DAG: T09 is downstream of T08;
- U14, comparison only if the measurement resolves the claimed effect;
- B12, comparability eligibility is claim-governing;
- U17, the underlying statistical operation must match the design.

## Additional-test catalogue contribution

The closest supporting item is:

- Test 1, Claim–Estimand Boundary.

T09 specifically measures whether an already-observed internal decision
difference reaches the product aggregate that communicates comparability.

## Source classification

- Immediate trigger: T08 empirical result.
- Direct product source: frozen `sidecars.py`.
- Direct procedural source: Protocol Rules 7/8 and cost ordering.
- Direct design source: Handbook U8/U9/U14/B12/U17.
