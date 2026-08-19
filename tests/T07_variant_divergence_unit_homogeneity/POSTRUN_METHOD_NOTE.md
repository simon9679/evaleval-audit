# POSTRUN_METHOD_NOTE — T07

Status: post-run meta-audit note.

## Method behavior observed

T07 converted a metadata-level observation into an operation-level
eligibility result.

The audit did not assume that mixed units anywhere in a group mattered.

Instead it first established that only seven mixed groups were
production-applicable and then checked the exact numeric rows used by the
production `max(score) - min(score)` operation.

All seven were unit-label heterogeneous.

This is stronger than the T04 metadata warning but still narrower than a
semantic invalidity finding.

## Protocol contribution

Rule 7 was decisive: test the actual measurement operation, not merely the
metadata mechanism.

Rule 8 prevented post-hoc redefinition of what counted as "heterogeneous
arithmetic."

The cost ordering limited the analysis to seven applicable paths rather than
launching a broad semantic audit of all 1,234 mixed groups.

## Handbook contribution

B12 supplied the comparability-eligibility framing.

U17 supplied the operation-versus-scale requirement.

U4 prevented introduction of a conversion or preferred-unit parameter.

U8 prevented the operation-level finding from being inflated into a semantic
or public-product verdict.

## Candidate methodological lesson

For comparison systems, metadata heterogeneity should be traced to the exact
rows that feed the comparison statistic before it is treated as
claim-governing.

A useful validation pattern is:

`group heterogeneity -> operation input -> operation consequence -> semantic reference`

rather than jumping directly from metadata inconsistency to a defect claim.
