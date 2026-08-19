# TEST_RATIONALE — T04 Comparability Unit Consistency and Threshold-Choice Sensitivity

Status: frozen before execution.

## Claim being tested

C-T04:

> At least one production-applicable Stage F comparability path in the frozen
> corpus changes its boolean divergence classification when the threshold is
> recomputed using different non-null `metric_unit` values that are actually
> present inside that same production comparability group.

This is a sensitivity claim. It is deliberately narrower than a claim that a
particular unit is semantically correct or that EvalEval comparability is
globally invalid.

## Why this claim was selected

T03 closed the floating-point-boundary branch at the corpus level: it found
zero production-vs-exact-decimal classification mismatches across 93,495
frozen comparability groups.

The same production run emitted a separate Stage F warning: 1,425
root-collapsed groups had more than one distinct non-null `metric_unit`.

That warning is not itself a defect finding. Frozen source inspection shows
that the warning grouping omits `slice_key`, while the actual comparability
metric-config grouping includes `slice_key`. Therefore T04 must answer two
questions in order:

1. how many actual comparability groups contain more than one non-null unit?;
2. among those groups, does unit choice change any applicable final boolean?

## Why this test is run now

The float-boundary branch has no observed corpus consequence in this snapshot,
so further expensive work on that branch is not currently justified.

The unit warning is the next claim-governing uncertainty already exposed by the
production run. It can be resolved entirely from the saved T03 Stage F Parquet,
without rerunning the 24,787-record source pipeline and without opening raw
source files.

This is therefore the cheapest next measurement capable of deciding whether
the branch should stop or proceed to source-level tracing.

## Measurement design

The frozen T03 Stage F Parquet is the complete input.

For every actual comparability group, T04 collects all distinct non-null
`metric_unit` values. Only groups with more than one such value enter the
sensitivity arm.

For each mixed-unit group:

- keep the production group membership fixed;
- keep the production divergence magnitude fixed;
- keep the production `MAX(min_score)` and `MAX(max_score)` aggregation fixed;
- vary only `metric_unit` across values actually observed in that group;
- call the frozen production `compute_threshold` function for each observed
  unit;
- recompute the strict production decision:
  `divergence_magnitude > threshold`.

This is a controlled one-factor sensitivity test. It does not invent units,
epsilon tolerances, scores, weights, or a new threshold formula.

Both production paths are analyzed separately:

- variant divergence;
- cross-party divergence.

## Competing predictions

### P1 — benign / non-consequential heterogeneity

The Stage F warning is either mainly cross-slice heterogeneity or the observed
within-group unit alternatives do not change any applicable boolean
classification.

Observable prediction:

`classification_sensitive_paths = 0`

Threshold magnitudes may still differ. That would remain a mechanism/metadata
observation, not a demonstrated product-classification consequence.

### P2 — consequential threshold ambiguity

At least one actual mixed-unit comparability group has an applicable variant or
cross-party path whose boolean changes across unit values actually present in
that group.

Observable prediction:

`classification_sensitive_paths >= 1`

## Why no subjective directional forecast is required

Rule 8 requires fixed competing predictions before the run, not a forced bet
on which prediction will win. Both outcomes are publishable. T04 therefore
records the two opposing observable predictions without assigning a
probability.

## Integrity controls

T04 verifies before interpretation:

- T03 fact Parquet SHA-256 matches the completed-test evidence;
- T03 summary reports 209,382 fact rows and 93,495 comparability groups;
- the frozen backend commit is unchanged;
- the Stage F warning population reconstructed from Parquet equals 1,425;
- group-level production signal fields are internally constant where required;
- the frozen production-selected unit and threshold can be reconstructed.

A failure of these controls is not converted into an EvalEval finding.

## Alternatives considered

1. Inspect examples among the 1,425 warning groups first.
   Rejected because it would expose outcome-specific cases before the
   sensitivity test is preregistered.

2. Rerun Stage A through F.
   Rejected because T03 already produced a hashed complete Stage F artifact.

3. Trace all 1,425 groups back to raw JSON immediately.
   Rejected as unnecessarily expensive. Source tracing is justified only if
   T04 shows a classification consequence or another claim-governing need.

4. Decide which metric unit is "correct" from naming conventions.
   Rejected. That would require a source/reference-semantic trace and is a
   later test if needed.

5. Normalize percent to proportion before testing.
   Rejected. That would modify the frozen object instead of measuring it.

## What T04 can establish

T04 can establish:

- how the 1,425 warning-level groups map to actual Stage F comparability groups;
- whether actual within-group unit heterogeneity exists;
- whether the production threshold changes across observed unit choices;
- whether any applicable production comparability boolean changes as a result.

## What T04 cannot establish

T04 cannot by itself establish:

- which source row has the semantically correct unit;
- whether a sensitive group is visible on the public website;
- whether upstream source metadata or EvalEval resolution caused the
  inconsistency;
- severity outside the frozen snapshot;
- global validity or invalidity of EvalEval comparability.

Those require source-trace or product-surface tests only if the preregistered
branch rule says to continue.
