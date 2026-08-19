# POSTRUN_METHOD_NOTE — T04

Status: post-run meta-audit note.

## Method behavior observed

T04 provides a concrete example of the decision procedure preventing an
overclaim.

The production pipeline emitted a warning count of 1,425.

Before T04, that count could not validly be interpreted as 1,425 defective
comparability groups because:

- the warning grouping omitted `slice_key`;
- the actual comparability grouping included `slice_key`;
- no product-consequence test had yet been run.

T04 reduced the uncertainty in stages:

1. 1,425 warning-level root groups were reconstructed.
2. 191 were cross-slice-only at the actual comparability boundary.
3. 1,234 actual mixed-unit groups remained.
4. 668 were threshold-sensitive.
5. only seven had an applicable variant path.
6. none changed the final boolean classification.

The method therefore changed the likely narrative from a broad mechanism
warning to a narrower descriptive finding with zero observed decision impact.

## Protocol contribution

Rule 7 required the audit to ask whether the mechanism changed a final
decision.

Rule 8 required the two competing predictions to be frozen before execution.

The general cheapest-to-more-expensive ordering justified using the existing
Stage F artifact before source-level tracing.

## Handbook contribution

The Handbook constrained:

- the group boundary used for the verdict;
- the scope of the claim;
- the attribution of any failure;
- the unit sweep to observed values rather than invented alternatives;
- the interpretation of threshold sensitivity separately from decision
  sensitivity.

## Candidate methodological lesson

A production warning is not itself a verdict-bearing instrument.

When the warning grouping differs from the claim-governing grouping, an audit
should reconstruct both explicitly before assigning significance.

This lesson should be considered for inclusion in the final method postmortem,
but it does not retroactively modify the current Protocol or Handbook.
