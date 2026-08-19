# TEST_RATIONALE

## 1. Claim being tested

The production group-level metric configuration for the claim-governing
WildBench group is a synthetic field-wise combination that matches no exact
source metric configuration.

The same reconstructed production configuration must reproduce the frozen
production threshold magnitude and basis.

## 2. Where the test comes from

Immediate empirical trigger:

T16 CONFIRMED three distinct source scale signatures and no represented common
scale.

Methodological guidance:

- Falsification Protocol Rule 6 — provenance;
- Rule 7 — inspect the actual product computation;
- Rule 8 — fixed competing predictions;
- Validation Handbook U3 — source authority;
- U4 — do not silently introduce a free transformation;
- U8 — verdict granularity;
- U9 — dependency DAG;
- U11 — boundary-aware error attribution;
- U17 — operation must match scale/design;
- B12 — derive eligibility and grouping from frozen algorithm.

## 3. Why chosen now

This is cheaper and more directly causal than broad semantic interpretation.

Before asking what the four channels mean in theory, the audit should determine
whether production already synthesizes a metric configuration that exists in
no source row.

## 4. Exact procedure

1. load the eight affected Stage-F rows;
2. load the four exact source scale/config signatures from T16;
3. reconstruct the production group configuration using the frozen field-wise
   non-null `MAX` rule;
4. count exact source signatures equal to the production signature;
5. identify which source ids support each selected field value;
6. run the frozen `compute_threshold` function on the reconstructed group
   configuration;
7. require exact equality with the frozen Stage-F threshold magnitude and basis.

No source value is changed.

No semantic mapping is introduced.

## 5. Competing outcomes

P1 — benign:

The reconstructed production group configuration exactly matches at least one
source configuration.

P2 — consequential:

The reconstructed production group configuration matches zero exact source
configurations, while threshold replay is exact.

## 6. What it can prove

A P2 result proves that production uses a group metric configuration that is
not an exact source metric definition for this claim-governing group.

## 7. What it cannot prove

It does not prove that:

- field-wise MAX is always invalid;
- a synthetic group configuration can never be legitimate;
- every source channel is semantically non-equivalent;
- one particular repair is mandatory.
