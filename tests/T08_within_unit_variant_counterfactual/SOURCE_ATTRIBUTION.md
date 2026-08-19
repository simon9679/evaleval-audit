# SOURCE_ATTRIBUTION — T08 Within-Unit Variant Divergence Counterfactual

Status: frozen before execution.

## Immediate empirical trigger

T08 is a direct descendant of T07.

T07 found:

- 7 production-applicable variant-divergence paths inside the mixed-unit
  population;
- 7 / 7 have multiple declared non-null units among the numeric score rows;
- 4 / 7 have disjoint unit-label sets at the global minimum and maximum score;
- 5 / 7 are production-positive;
- 2 / 7 are production-negative;
- zero divergence-reconstruction or integrity errors.

T08 asks whether the five positive production booleans depend on allowing
cross-label extrema in the same raw range calculation.

## Frozen production implementation

Frozen backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

Relevant source:

`src/eval_card_backend/signals/comparability.py`

Production variant divergence uses numeric score rows and computes:

`divergence = max(scores) - min(scores)`

The production boolean is:

`divergence > threshold`

T08 keeps the frozen production threshold unchanged and changes only the row
eligibility boundary for the range operation.

## Falsification Protocol contribution

The exact T08 counterfactual is not specified by the Protocol.

The Protocol contributes:

- Rule 7: test consequence at the produced decision, not merely a metadata or
  mechanism observation;
- Rule 8: freeze the counterfactual rule, prediction, and verdict before the
  run;
- cheapest-to-more-expensive ordering: use deterministic existing rows before
  manual semantic adjudication or external tracing.

## Validation Handbook contribution

The strongest direct anchors are:

- B12, comparability eligibility: a comparison system must have a defensible
  predicate for which rows enter one comparison;
- U17, statistical operation must match the scale/design;
- U4, free-parameter discipline: exact declared label partitioning is fixed and
  introduces no learned or hand-selected conversion;
- U8, verdict granularity: the result applies only to this exact-label
  eligibility counterfactual;
- U14, comparison only if the measurement resolves the effect;
- U9, dependency DAG: T08 follows T07 operation-input evidence.

## Additional-test catalogue contribution

The closest supporting items are:

- Test 1, Claim–Estimand Boundary;
- Test 17, Local Discriminability / Saturation, only in the broad sense that
  the measurement should resolve the operational distinction under test.

The exact T08 counterfactual is derived from T07 plus the frozen production
operation, not copied from the catalogue.

## Source classification

- Immediate trigger: T07 empirical result.
- Direct procedural source: Protocol Rules 7 and 8 plus cost ordering.
- Direct design source: Handbook B12/U17/U4/U8/U14/U9.
- Supporting additional tests: primarily Test 1.
