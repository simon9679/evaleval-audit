# SOURCE_ATTRIBUTION — T13 Structured Metric-ID Rejection Attribution

Status: frozen before execution.

## Immediate empirical trigger

T13 is a direct descendant of T12.

T12 established:

- six distinct source `metric_config.metric_id` values;
- two product-consequential groups;
- zero rows using `metric_id_structured`;
- both groups collapse through fallback `metric_raw = score`;
- both groups use canonical `metric_id = score`;
- both groups use `metric_key = score`.

T13 asks why the structured pre-step did not preserve a specific metric
identity.

## Frozen resolver algorithm

Frozen eval-card-registry resolver commit:

`6fb026d7483467f063da465c15a76733b3d25f4c`

The structured metric-id resolver:

1. requires a namespaced id containing `.` or `/`;
2. splits the id into segments;
3. ignores the first adapter namespace segment;
4. resolves each remaining segment against the metric vocabulary using exact
   then normalized matching only;
5. removes canonical ids marked as `catch_all`;
6. returns a canonical metric id only when exactly one distinct non-catch-all
   metric remains;
7. otherwise returns null.

Therefore a null structured result can arise from:

- no metric hits;
- only catch-all hits;
- two or more conflicting specific metric hits.

This distinction is the T13 target.

## Frozen backend use

Frozen backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

The backend passes the registry's catch-all metric ids into the structured-id
resolver.

If structured resolution returns null, Stage C falls through to the existing
description/name extraction path.

T12 already observed the resulting fallback identity `score`.

## Falsification Protocol contribution

The exact T13 test is not stated in the Protocol.

The Protocol contributes:

- Rule 2: distinguish competing rejection mechanisms;
- Rule 6: provenance of the identity decision;
- Rule 7: test the component that directly controls the consequential grouping;
- Rule 8: freeze rejection classes and competing predictions before replay;
- cheapest-to-more-expensive ordering: deterministic resolver attribution
  before semantic adjudication.

## Validation Handbook contribution

Strongest anchors:

- U3: registry vocabulary is an instrument, not semantic ground truth;
- U4: no alias map or semantic normalization is invented;
- U8: resolver rejection mechanism is narrower than semantic correctness;
- U9: T13 follows T12;
- U11: component-boundary attribution;
- U12: registry entries are operational definitions, not final truth;
- B12: identity resolution governs comparability eligibility.

## Additional-test catalogue contribution

Closest supporting test:

- Test 4, Component / Harness Attribution.

Test 1, Claim–Estimand Boundary, remains a downstream semantic concern.
