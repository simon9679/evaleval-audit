# TEST_RATIONALE — T13 Structured Metric-ID Rejection Attribution

Status: frozen before execution.

## Primary claim C-T13

> All six T12 source metric ids are rejected by the frozen structured resolver
> because they disclose zero distinct non-catch-all registry metric ids, not
> because they disclose two or more conflicting specific metric ids.

Primary observable counts:

- `rejected_zero_specific_ids`
- `rejected_conflicting_specific_ids`

## Why this test was selected

T12 proves the structured path was not used, but the reason is not yet known.

The resolver specification gives three materially different null outcomes:

1. no registry metric disclosure;
2. catch-all-only disclosure;
3. conflicting specific disclosures.

Only the third is an ambiguity conflict.

The first two are vocabulary/deferral outcomes.

Distinguishing them localizes the transformation boundary without any semantic
judgement.

## Why this test is run now

T13 operates on only six unique source metric ids.

It can replay the frozen resolver directly from the frozen source repository
and frozen registry data.

This is cheaper and more objective than asking a human whether the ids should
be aliases.

## Classification rule

For each unique `(source_metric_id, source_config)` pair:

1. split the namespaced source id exactly as the frozen resolver does;
2. resolve every segment after the first namespace using the frozen resolver in
   exact-only mode, which includes exact and normalized tiers but stops before
   fuzzy matching;
3. collect all metric canonical-id hits;
4. remove ids marked `catch_all` in frozen `canonical_metrics`;
5. compare the resulting distinct specific-hit set with the direct
   `resolve_structured_metric_id` result.

Classification:

- `accepted_single_specific`:
  one distinct non-catch-all hit and structured resolver returns that id;
- `rejected_no_hits`:
  zero segment hits and structured resolver returns null;
- `rejected_catch_all_only`:
  one or more hits exist but zero non-catch-all hits and structured resolver
  returns null;
- `rejected_conflicting_specific`:
  two or more distinct non-catch-all hits and structured resolver returns null;
- `inconsistent`:
  direct resolver result disagrees with the frozen classification rule.

## Competing predictions

### P1 — ambiguity/conflict contributes

`rejected_conflicting_specific_ids >= 1`

At least one source id is rejected because multiple specific registry metrics
are disclosed.

### P2 — pure vocabulary/deferral rejection

`rejected_conflicting_specific_ids = 0`
and
`rejected_zero_specific_ids = 6`

All six source ids disclose zero specific non-catch-all metric ids and are
therefore rejected without a specific-metric conflict.

`rejected_zero_specific_ids` is the sum of:

- `rejected_no_hits`
- `rejected_catch_all_only`

## Primary verdict

C-T13 is formulated as the P2 claim.

- `CONFIRMED` — P2 observed, all six direct structured results are null, and
  all integrity/replay checks pass.
- `REFUTED` — P1 observed, all direct structured results still reproduce the
  frozen null behavior, and integrity checks pass.
- `INCONCLUSIVE` — direct structured replay disagrees with the observed T12
  structured-path absence or with the manually reconstructed segment rule.
- `ERROR` — frozen resolver source, registry data, dependency, or prerequisite
  evidence cannot be loaded.

## What T13 can establish

T13 can establish the deterministic registry-level reason the structured
metric-id pre-step returns null for the six consequential source ids.

## What T13 cannot establish

T13 cannot establish:

- whether the registry should contain aliases for the missing source ids;
- whether the source metric ids are semantically equivalent;
- whether a specific canonical id would be correct;
- whether the fallback `score` mapping is semantically valid;
- original-publisher intent.

Those become the next reference/semantic questions only after component
attribution.
