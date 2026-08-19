# SOURCE_ATTRIBUTION — T05 Metric Unit Provenance Decomposition

Status: frozen before execution.

## Immediate empirical trigger

T05 is not copied verbatim from the Falsification Protocol, Validation
Handbook, or additional-test catalogue.

Its immediate trigger is the completed T04 result:

- 1,425 Stage F warning-level root groups;
- 1,234 actual mixed-unit comparability groups;
- 668 threshold-sensitive groups;
- zero classification-sensitive paths.

T04 therefore closed the claim branch:

`mixed unit -> threshold choice -> changed final comparability boolean`

but left a different question unresolved:

`where did the mixed metric identity / unit state come from?`

## Frozen implementation facts motivating the test

In the frozen backend, Stage C derives a raw metric identity and then resolves
a canonical metric id.

The metric raw value comes from either:

- a structured metric id resolution pre-step; or
- extraction from evaluation description, metric name, or evaluation name.

Stage C then resolves a canonical metric id and records
`metric_resolution_strategy`.

It may also apply curated benchmark-specific metric folds.

Stage D defines:

`metric_key = COALESCE(metric_id, metric_raw)`

and carries both the raw and resolved identities into the Stage F facts.

Stage D derives metric metadata through a layered chain and emits
`metric_unit_provenance`. The documented chain is:

`registry > EEE per-record > heuristic > NULL`

These frozen provenance fields make a cheap structural attribution test
possible before opening the raw source JSON files.

Frozen backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

Relevant frozen source:

- `src/eval_card_backend/canonicalise/stages.py`
- `src/eval_card_backend/metric_meta_hotfix.py`

## Falsification Protocol contribution

The exact T05 test is not specified by the Protocol.

The Protocol contributes:

- Rule 2, adapted from memory-specific noise layers to the actual pipeline:
  separate candidate sources of variation rather than treating mixed metadata
  as one undifferentiated phenomenon;
- Rule 6, provenance: locate where the signal or transformation originates;
- Rule 7, avoid calling a mechanism observation a product result;
- Rule 8, freeze competing predictions and analysis rules before running;
- cheapest-to-more-expensive ordering: use existing Stage F provenance fields
  before opening and semantically tracing source records.

## Validation Handbook contribution

The strongest design constraints are:

- U3, reference authority: resolved agreement is not automatically semantic
  correctness;
- U8, verdict granularity: structural convergence is not proof of invalid
  comparability;
- U9, dependency DAG: T05 is a new attribution branch created by T04;
- U11, boundary-aware attribution: distinguish upstream metadata,
  resolution/canonicalization, and audit harness behavior;
- U12, object documentation is a hypothesis, not ground truth;
- B12, comparability eligibility: metric identity is claim-governing for a
  comparability group.

## Additional-test catalogue contribution

The closest direct catalogue item is:

- Test 4, Component / Harness Attribution.

Supporting item:

- Test 1, Claim–Estimand Boundary.

The catalogue did not define the exact T05 implementation. The immediate
trigger and field-level design came from T04 plus the frozen EvalEval pipeline.

## Source classification

- Immediate trigger: empirical T04 result.
- Direct procedural source: Protocol Rules 2, 6, 7, 8 and cost ordering.
- Direct design source: Handbook U3/U8/U9/U11/U12/B12.
- Closest additional-test source: Test 4, Component / Harness Attribution.
