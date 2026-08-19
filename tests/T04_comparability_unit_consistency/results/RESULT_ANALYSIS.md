# RESULT_ANALYSIS — T04 Comparability Unit Consistency and Threshold-Choice Sensitivity

Status: post-run analysis written after the completed preregistered T04 execution.

This document interprets the frozen T04 result. It does not modify the
preregistration, test rationale, source attribution, code, or raw evidence.

## 1. Primary preregistered question

C-T04 asked:

> Does at least one production-applicable Stage F comparability path in the
> frozen corpus change its boolean divergence classification when its threshold
> is recomputed across distinct non-null `metric_unit` values that are actually
> present inside that same production comparability group?

The test was intentionally narrow. It did not ask which unit is semantically
correct, whether mixed units are globally acceptable, whether the upstream
source is wrong, or whether the public website is affected.

## 2. Competing predictions frozen before the run

### P1 — benign / non-consequential heterogeneity

`classification_sensitive_paths = 0`

Mixed units may exist. Threshold magnitudes may even differ. But no
production-applicable final comparability boolean changes when the unit choice
is swept across units already present inside the same group.

### P2 — consequential threshold ambiguity

`classification_sensitive_paths >= 1`

At least one production-applicable final comparability boolean changes solely
because a different unit already present inside the same group is used by the
threshold rule.

No subjective probability was assigned to either prediction. The purpose of
the preregistration was to let the observed data choose between them.

## 3. Primary verdict

`REFUTED`

The preregistered claim C-T04 was not observed in the frozen snapshot.

Observed:

- `classification_sensitive_groups = 0`
- `classification_sensitive_paths = 0`
- `variant_classification_sensitive_paths = 0`
- `cross_party_classification_sensitive_paths = 0`

Therefore P1 was observed and P2 was not observed.

This verdict applies only to C-T04. It is not a global verdict on EvalEval
comparability.

## 4. Complete reported counts

### Frozen population

- `fact_rows_scanned = 209382`
- `comparability_groups_scanned = 93495`

The test reused the complete hashed Stage F artifact produced by T03. It did
not sample groups and did not rerun the production source pipeline.

### Production warning reconstruction

- `warning_root_groups = 1425`
- `actual_mixed_unit_groups = 1234`
- `warning_roots_with_actual_mixed_group = 1234`
- `warning_roots_cross_slice_only = 191`

The production warning grouped by:

`(model_aggregation_key, benchmark_key, metric_key)`

while the actual comparability computation grouped by:

`(model_aggregation_key, benchmark_key, slice_key, metric_key)`

The difference matters.

Of the 1,425 warning-level root groups, 191 did not contain mixed units inside
any actual comparability group after the `slice_key` boundary was restored.
Those 191 warning cases were cross-slice-only heterogeneity at the level
relevant to T04.

The remaining 1,234 were genuine actual Stage F comparability groups containing
more than one distinct non-null `metric_unit`.

Therefore the original production warning was directionally meaningful, but
its raw count could not be interpreted as 1,425 already-proven ambiguous
comparability groups.

### Threshold sensitivity

- `threshold_sensitive_groups = 668`

In 668 actual mixed-unit groups, changing only the observed unit supplied to
the frozen production threshold resolver changed the threshold magnitude
and/or threshold basis.

This is a real mechanism-level sensitivity.

It does not by itself establish a wrong final comparability decision.

### Production-applicable paths

- `variant_eligible_paths = 7`
- `cross_party_eligible_paths = 0`

Only seven mixed-unit groups had an applicable variant-divergence path under
the frozen Stage F result.

No mixed-unit group had an applicable cross-party path.

This is the key reason the large mixed-unit population did not translate into
a large population of decision-sensitive cases.

### Final classification sensitivity

- `classification_sensitive_groups = 0`
- `classification_sensitive_paths = 0`
- `variant_classification_sensitive_paths = 0`
- `cross_party_classification_sensitive_paths = 0`

Across the seven applicable variant paths, the final strict production
comparison remained on the same side of the threshold under every unit value
actually observed inside the relevant group.

Therefore T04 found no frozen boolean-classification consequence from unit
choice.

## 5. Integrity and reconstruction checks

- `production_reconstruction_errors = 0`
- `group_consistency_errors = 0`
- `integrity_error_records = 0`

The result is therefore interpretable under the preregistered rules.

The REFUTED verdict is not caused by a failed harness, missing field, corrupted
artifact, or an inability to reconstruct the frozen production threshold
choice.

## 6. Observed unit-pattern breakdown

The actual mixed-unit groups had the following observed patterns:

- `percent | points = 7`
- `percent | seconds = 8`
- `percent | words = 315`
- `points | proportion = 183`
- `points | proportion | score = 78`
- `points | score = 88`
- `points | usd = 4`
- `proportion | score = 77`
- `seconds | tokens_per_second | usd_per_1m_tokens = 474`

These counts are descriptive evidence.

Some patterns combine units that appear semantically very different, including
time, throughput, currency-normalized cost, proportions, points, scores, and
word counts.

T04 does not establish that those combinations are erroneous. Their semantic
meaning, origin, and admissibility were outside the preregistered claim.

## 7. What T04 establishes

T04 establishes all of the following for the frozen snapshot:

1. The Stage F warning population of 1,425 is not identical to the actual
   comparability mixed-unit population because the warning omits `slice_key`.

2. There are 1,234 actual Stage F comparability groups with more than one
   distinct non-null `metric_unit`.

3. There are 668 actual mixed-unit groups where the production threshold
   changes across unit values already present in the same group.

4. Only seven such groups have an applicable variant-divergence path and none
   have an applicable cross-party path.

5. No applicable final comparability boolean changes across those observed
   unit choices.

6. The measurement completed with zero recorded reconstruction or consistency
   errors.

## 8. What T04 does not establish

T04 does not establish:

- which `metric_unit` is semantically correct for any mixed group;
- whether the same canonical `metric_key` is wrongly collapsing distinct
  estimands;
- whether the heterogeneity originated upstream or inside EvalEval;
- whether resolution, canonicalization, registry metadata, or source metadata
  is responsible;
- whether any mixed-unit group is exposed on the public website;
- whether a non-applicable group could become consequential under another
  future snapshot;
- whether comparability as a whole is valid or invalid.

Any statement stronger than the six established points above would exceed the
measurement granularity of T04.

## 9. Branch decision

The preregistered descendant branch was:

`mixed metric_unit -> threshold choice -> changed comparability boolean`

That branch stops here because:

`classification_sensitive_paths = 0`

The stop applies only to this claim branch.

It means that expensive source tracing is not justified solely to prove that
mixed units changed a frozen comparability boolean, because T04 found no such
change.

It does not mean that the 1,234 mixed-unit groups should be ignored.

## 10. New independent branch opened by the result

T04 exposes a separate unresolved question:

> Why do 1,234 actual comparability groups contain multiple unit labels, and do
> those labels represent the same estimand or distinct quantities that were
> collapsed under one canonical metric identity?

That is a metric-identity / provenance / comparability-eligibility question,
not the already-refuted T04 boolean-sensitivity claim.

A later test may investigate that branch under a new preregistration.

The later test must not retroactively change the meaning or verdict of T04.

## 11. Methodological interpretation

T04 is an example of why the audit uses claim-level branching rather than
turning every production warning into a defect finding.

A weaker procedure could have reported:

> 1,425 comparability groups have inconsistent units.

That statement would have over-interpreted the warning.

The preregistered test separated three different facts:

- 1,425 warning-level root groups;
- 1,234 actual mixed-unit comparability groups;
- zero applicable boolean-classification changes.

This separation prevents a mechanism-level warning from being presented as a
product-level failure without evidence.

It also demonstrates the purpose of the cheapest-to-more-expensive decision
procedure: the audit obtained a product-consequence answer from the already
saved Stage F artifact before paying for source-level tracing.

## 12. Relation to the method sources

### Falsification Protocol

The exact T04 test is not stated in the Protocol.

The Protocol contributed:

- cheapest-to-more-expensive branching;
- Rule 7: test the product consequence rather than stopping at a mechanism;
- Rule 8: write hypotheses, thresholds, competing predictions, and analysis
  rules before the run.

### Validation Handbook

The strongest direct design source was comparability eligibility, with
additional constraints from:

- reference authority;
- free-parameter control;
- verdict granularity;
- dependency DAG;
- boundary-aware attribution;
- scale-aware statistical operations.

The Handbook prevented the production warning from being treated as a result
without a claim-specific measurement.

### Additional-test catalogue

The test was not copied from the catalogue.

The closest supporting ideas were:

- Claim–Estimand Boundary;
- Aggregation / Weight Robustness.

They supported the decision to test the consequence of an operational choice,
but the immediate trigger and exact design came from T03/T04 frozen evidence.

## 13. Evidence files

Primary T04 evidence:

- `raw/preflight.json`
- `raw/warning_root_groups.jsonl`
- `raw/mixed_unit_groups.jsonl`
- `raw/classification_sensitive_paths.jsonl`
- `raw/integrity_errors.jsonl`
- `results/summary.json`

Frozen inputs:

- T03 `raw/fact_results_stage_f.parquet`
- T03 Stage F SHA-256:
  `e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196`
- backend commit:
  `9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

## 14. Final T04 statement

The frozen EvalEval Stage F corpus contains substantial mixed-unit metadata
heterogeneity: 1,234 actual comparability groups contain multiple non-null
unit labels, and 668 of those groups produce different threshold values across
the observed unit choices.

However, under the production-applicable paths present in this snapshot, no
final comparability boolean changes as a consequence of that unit choice.

Therefore the preregistered T04 classification-sensitivity claim is REFUTED,
while metric-identity and unit-provenance remain unresolved as a separate
future audit branch.
