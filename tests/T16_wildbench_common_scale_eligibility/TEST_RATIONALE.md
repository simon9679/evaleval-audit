# TEST_RATIONALE

## 1. Claim being tested

The four T15 WildBench/OpenEval source channels are not represented on one
common raw numeric scale, and the frozen source representation does not carry
explicit structured transformation metadata that makes their raw values
directly commensurate.

## 2. Methodological source

Immediate trigger:

- T14 accepted Fix 4 result;
- T15 CONFIRMED source-identity provenance result.

Methodological guidance:

- Falsification Protocol Rule 7 — test the output-relevant operation;
- Falsification Protocol Rule 8 — preregister competing predictions;
- Validation Handbook U3 — use authoritative structured source fields;
- U4 — free transformations must be derived, swept, or dropped;
- U8 — do not claim more than the measurement resolves;
- U9 — respect dependency order;
- U11 — separate harness/source failure from target finding;
- U17 — statistical operation must match the scale/design;
- B12 — derive comparability eligibility from frozen schema/algorithm;
- P8 — inspect scale semantics and anchored ranges.

## 3. Why this test now

T15 has already rejected the trivial alias explanation.

The next cheapest discriminator is therefore not another semantic reading but a
deterministic check of whether the source representation itself supplies the
scale information required for one raw `max(score)-min(score)` operation.

## 4. Exact operation

For the eight fixed source rows:

1. re-open the frozen EEE source records using T10 pointers;
2. reconstruct one source signature per exact source id;
3. count distinct declared units;
4. count distinct `(unit, min, max)` scale signatures;
5. inspect `metric_parameters`;
6. inspect structured `additional_details` key names for explicit
   transformation/normalization fields;
7. apply the preregistered common-scale eligibility predicate.

No score values are changed.

No normalization is invented.

No external semantic alias is introduced.

## 5. Competing outcomes

P1 — benign:

The four channels are already represented on one common scale, or explicit
structured per-channel conversion metadata makes them eligible for one common
raw arithmetic scale.

P2 — consequential:

The source representation contains multiple declared scale signatures and no
complete explicit structured transformation into one common scale.

## 6. What the result can prove

A P2 result can prove that the frozen structured source representation does not
itself justify direct raw-range arithmetic across the four channels.

## 7. What the result cannot prove

It cannot prove that:

- no undocumented transform exists upstream;
- every channel measures a different latent construct;
- exact source-id separation is the only valid repair;
- an explicit future normalization could not make some channels commensurate.

Those require a later semantic/procedure reference test if still necessary.
