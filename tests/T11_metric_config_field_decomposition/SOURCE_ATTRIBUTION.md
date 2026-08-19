# SOURCE_ATTRIBUTION — T11 MetricConfig Field-Level Decomposition

Status: frozen before execution.

## Immediate empirical trigger

T11 is a direct descendant of T10.

T10 found:

- both product-consequential groups contain non-unit MetricConfig
  heterogeneity;
- group `0dc7e803e7438c7faf39dfc4b461faef` has 2 units and 2 non-unit signatures;
- group `d38d8f8e547287b6b0fc78f43f310762` has 2 units and 4 non-unit signatures;
- no non-unit signature is shared across multiple units;
- zero source-trace or integrity errors.

T11 asks which exact structured fields create those signatures.

## Frozen schema fields

The field set is exactly the T10 primary signature:

- `metric_id`
- `metric_name`
- `metric_kind`
- `metric_parameters`
- `lower_is_better`
- `score_type`
- `min_score`
- `max_score`

No new field is added to the primary verdict after seeing T10.

`metric_unit` is analyzed as the partition label, not as a non-unit difference
field.

## Falsification Protocol contribution

The exact T11 test is not specified by the Protocol.

The Protocol contributes:

- Rule 2: decompose a combined source-definition difference into components;
- Rule 6: preserve source provenance;
- Rule 7: stay restricted to the product-consequential subset;
- Rule 8: freeze field-level predictions and rules before inspection;
- cost ordering: deterministic field decomposition before semantic reference
  adjudication.

## Validation Handbook contribution

The strongest anchors are:

- U3: structured fields are an instrument, not final semantic authority;
- U4: no field weighting or hand-selected importance threshold;
- U8: field-level variation supports only field-level conclusions;
- U9: T11 follows T10 in the evidence DAG;
- U11: source-boundary attribution remains explicit;
- U12: metadata are hypotheses until independently interpreted;
- B12: metric identity and definition are claim-governing for comparability.

## Additional-test catalogue contribution

Closest supporting items:

- Test 1, Claim–Estimand Boundary;
- Test 4, Component / Harness Attribution.
