# POSTRUN_DECISION — T08

Status: post-run branch decision.

## Completed result

T08 verdict:

`CONFIRMED`

Key observations:

- applicable mixed variant paths: 7
- production-positive paths: 5
- production-negative paths: 2
- positive-to-positive: 3
- positive-to-negative: 2
- negative-to-negative: 2
- negative-to-positive: 0
- production range > max within-unit range: 4
- production range = max within-unit range: 3
- production range < max within-unit range: 0
- reconstruction errors: 0
- invariant errors: 0
- integrity errors: 0

## Branch that is confirmed

Confirmed:

`cross-exact-unit arithmetic can be necessary for a production-positive
variant-divergence flag`

This occurs in two frozen paths.

## What is not yet confirmed

Not confirmed:

- semantic incompatibility of the unit labels;
- semantic incorrectness of either positive flag;
- public-user exposure;
- published-claim impact.

## Next branch

Next:

`two T08 positive-to-negative paths -> frozen public/product exposure`

Use the exact two records in:

`raw/positive_to_negative_paths.jsonl`

as the complete next-test population.

## Cost rule

Do not perform broad semantic adjudication across all 1,234 mixed-unit groups.

First determine whether either of the two consequential paths reaches a public
or claim-governing surface.

If neither does, stop this descendant branch for public-impact purposes.

If one or both do, semantic/reference adjudication becomes justified for only
the exposed consequential subset.
