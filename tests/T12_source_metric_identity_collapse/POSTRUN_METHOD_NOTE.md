# POSTRUN_METHOD_NOTE — T12

Status: post-run meta-audit note.

## Method behavior observed

T12 reconciled a downstream single metric identity with upstream source metric
heterogeneity by tracing the transformation row by row.

This is stronger than inferring a resolver collapse from group-level counts.

## Protocol contribution

Rule 6 was central: the identity used by the product was traced to its source
and transformation path.

Rule 7 kept the test on the exact grouping operation responsible for the
product-consequential result.

Rule 8 fixed the collapse predicate before the row-level trace.

## Handbook contribution

B12 is central because `metric_key` is part of the claim-governing
comparability eligibility predicate.

U11 requires this transformation-boundary attribution before assigning a
defect to source or resolver.

U8 limits the finding to identity collapse rather than semantic invalidity.

## Candidate methodological lesson

When a canonicalized measurement group looks internally homogeneous, inspect
whether the canonical identity was inherited from the structured source or
reconstructed from a lossy fallback field.

Canonical homogeneity can be produced by transformation rather than by source
homogeneity.
