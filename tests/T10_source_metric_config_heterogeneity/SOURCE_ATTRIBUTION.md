# SOURCE_ATTRIBUTION — T10 Source MetricConfig Heterogeneity

Status: frozen before execution.

## Immediate empirical trigger

T10 is a direct descendant of T09.

T09 confirmed that the two T08 positive-to-negative groups change the frozen
headline `variant_divergent_count` from 343 to 341.

The remaining unresolved question is whether the two affected exact-unit
partitions represent different source-declared metric definitions or whether
`metric_unit` is the only structured metric-definition field that varies.

## Frozen source schema

Frozen backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

Relevant schema:

`src/eval_card_backend/schemas/eee_types.py`

The frozen EEE `MetricConfig` contains structured fields including:

- `metric_id`: stable metric identifier for joining/deduping/querying;
- `metric_name`: display name;
- `metric_kind`: normalized metric family/type used for safe aggregation;
- `metric_unit`: unit of metric values;
- `metric_parameters`: metric-specific parameters;
- `lower_is_better`: score direction;
- `score_type`: type of score;
- `min_score`: minimum possible continuous score;
- `max_score`: maximum possible continuous score.

T10 uses these schema-defined fields rather than inventing a new semantic
ontology.

## Fixed non-unit signature

The primary source metric-definition signature excludes `metric_unit` and uses
exact values for:

- `metric_id`
- `metric_name`
- `metric_kind`
- `metric_parameters`
- `lower_is_better`
- `score_type`
- `min_score`
- `max_score`

Dictionary-valued `metric_parameters` is compared through canonical JSON with
sorted keys.

No free-text `evaluation_description` or `additional_details` field is used in
the primary signature.

Those fields are emitted descriptively but do not govern C-T10.

## Falsification Protocol contribution

The exact T10 test is not specified by the Protocol.

The Protocol contributes:

- Rule 2: separate unit variation from other source metric-definition
  variation;
- Rule 6: trace the affected product consequence back to structured source
  provenance;
- Rule 7: remain tied to the two product-consequential groups;
- Rule 8: freeze the exact source signature before reading the affected source
  configs;
- cheapest-to-more-expensive ordering: inspect structured source metadata
  before external semantic adjudication.

## Validation Handbook contribution

The strongest anchors are:

- U3: structured source fields can be an instrument but are not automatically
  semantic ground truth;
- U4: no free parameter or hand-selected equivalence map;
- U8: source-configuration heterogeneity is not semantic invalidity;
- U9: T10 follows the T08/T09 consequence branch;
- U11: attribution remains at the frozen EEE datastore boundary;
- U12: source documentation/metadata remain hypotheses, not final truth;
- B12: metric identity and metric definition govern comparability eligibility.

## Additional-test catalogue contribution

The closest supporting items are:

- Test 1, Claim–Estimand Boundary;
- Test 4, Component / Harness Attribution.

The exact T10 signature test is derived from the frozen EEE schema and the
T09 product-consequential subset.
