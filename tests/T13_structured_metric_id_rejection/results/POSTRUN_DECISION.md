# POSTRUN_DECISION — T13

Status: post-run branch decision.

## Completed result

T13 verdict:

`CONFIRMED`

Key counts:

- unique source metric ids: 6
- structured accepts: 0
- structured rejects: 6
- no-hit rejects: 4
- catch-all-only rejects: 2
- zero-specific rejects: 6
- conflicting-specific rejects: 0
- inconsistent replays: 0
- integrity errors: 0

## Confirmed component attribution

The structured resolver does not reject these source ids because of competing
specific metric candidates.

It rejects them because the frozen registry provides no usable specific metric
identity.

## Next branch

Next deterministic test:

`exact source metric identity preserved -> recomputed variant divergence`

This is a causal counterfactual only.

It does not assert that exact source ids are the normative canonical policy.
