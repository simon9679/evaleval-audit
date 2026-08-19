# SOURCE_ATTRIBUTION — T07 Variant Divergence Unit-Homogeneity Eligibility

Status: frozen before execution.

## Immediate empirical trigger

T07 is not copied verbatim from the Falsification Protocol, Validation
Handbook, or additional-test catalogue.

It is created by the combined T04-T06 branch:

- T04 found 1,234 actual mixed-unit groups and 7 production-applicable variant
  paths, but zero boolean changes under alternative observed threshold units;
- T05 found one raw metric identity, one canonical metric identity, exact
  resolution, and EEE-record unit provenance throughout the mixed population;
- T06 independently verified 28,196 / 28,196 Stage F unit values against 4,278
  frozen EEE source files.

The remaining question is whether the production divergence arithmetic itself
operates across score-bearing rows with different declared units.

## Frozen production implementation

Frozen backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

Relevant implementation:

`src/eval_card_backend/signals/comparability.py`

For variant divergence, production:

1. takes the rows in one comparability group;
2. checks that setup fields differ;
3. keeps rows with real numeric scores;
4. computes:

`divergence = max(scores) - min(scores)`

5. compares that magnitude against the threshold.

The function does not partition, filter, or convert numeric scores by
`metric_unit` before the `max` and `min` operations.

Stage F's actual comparability group includes:

`(model_aggregation_key, benchmark_key, slice_key, metric_key)`

## Falsification Protocol contribution

The exact T07 test is not stated in the Protocol.

The Protocol contributes:

- Rule 7: test the actual measurement/product operation rather than stopping at
  a metadata mechanism;
- Rule 8: freeze competing predictions and analysis rules before inspecting the
  seven applicable paths;
- cheapest-to-more-expensive ordering: inspect the deterministic arithmetic
  population before any manual semantic adjudication.

Rule 6 provenance was used in T05-T06 and is not the primary source of T07.

## Validation Handbook contribution

The strongest direct anchors are:

- B12, comparability eligibility: the predicate deciding whether rows may enter
  one comparison is claim-governing;
- U17, statistical operation must match the scale/design: T07 checks whether
  the rows entering one raw `max-min` operation have one declared unit label or
  multiple declared unit labels;
- U4, free parameters: T07 invents no conversion map and no preferred unit;
- U8, verdict granularity: multiple labels in one arithmetic input do not by
  themselves establish semantic incompatibility;
- U9, dependency DAG: T07 is a new measurement-eligibility descendant after
  T04-T06;
- U11, boundary-aware attribution: T06 already located the labels at the frozen
  EEE boundary.

B12 and U17 are the principal Handbook sources.

## Additional-test catalogue contribution

The closest supporting item is:

- Test 1, Claim–Estimand Boundary.

T07 asks whether the arithmetic input declared as one comparability estimand
contains multiple declared unit labels.

No additional-test catalogue item defines the exact T07 instrument.

## Source classification

- Immediate trigger: T04-T06 empirical results.
- Direct procedural source: Protocol Rules 7 and 8 plus cost ordering.
- Direct design source: Handbook B12 and U17, supported by U4/U8/U9/U11.
- Supporting additional test: Test 1, Claim–Estimand Boundary.
