# TEST_RATIONALE — T09 Headline Comparability Aggregate Impact

Status: frozen before execution.

## Primary claim C-T09

> Replacing only the two T08 positive-to-negative group booleans with their
> preregistered T08 counterfactual values decreases the frozen overall
> `headline.json` comparability `variant_divergent_count`.

Observable primary quantity:

`headline_variant_divergent_count_delta`

defined as:

`counterfactual_count - production_count`

C-T09 predicts a negative value.

## Why this test was selected

T08 established an internal production boolean consequence in exactly two
groups.

Before semantic adjudication, the audit must determine whether those two
booleans are merely internal fields or contribute to a user/product-facing
aggregate.

The frozen backend explicitly states that `headline.json` drives the home-page
corpus signal strip and computes its comparability counts from the same
Stage F group flags.

Therefore this is the cheapest product-consequence gate.

## Why this test is run now

The two affected group ids are already frozen in:

`T08/raw/positive_to_negative_paths.jsonl`

The Stage F source artifact is already hashed.

The production headline SQL can be reproduced without:

- a new pipeline run;
- a web request;
- semantic unit judgement;
- manual case selection.

## Fixed production reconstruction

T09 reproduces the overall `_comparability_block` group counts using the
frozen Stage F Parquet.

Production fields:

- `total_triples`;
- `variant_divergent_count`;
- `cross_party_divergent_count`;
- `groups_with_variant_check`;
- `groups_with_cross_party_check`.

No tag filter is applied.

## Fixed counterfactual

Use the exact two unique `comparability_group_id` values in the T08
positive-to-negative raw evidence.

For those two groups only:

`has_variant_divergence := FALSE`

All other rows and fields remain unchanged.

Do not recompute:

- thresholds;
- divergence magnitudes;
- eligibility;
- cross-party flags;
- group ids;
- units;
- any other signal.

Then rerun the same aggregate count.

## Competing predictions

### P1 — no product aggregate consequence

`headline_variant_divergent_count_delta = 0`

### P2 — product aggregate consequence exists

`headline_variant_divergent_count_delta < 0`

The primary preregistered claim expects only direction, not a hard-coded
magnitude.

## Secondary expected structural checks

The two T08 paths are expected to be:

- two unique group ids;
- production `has_variant_divergence = TRUE`;
- present in the Stage F population;
- counted once each under the distinct-group headline query.

The observed absolute delta will be reported rather than assumed.

## Derived descriptive rates

T09 also reports, for production and counterfactual:

- `variant_divergent_count / total_triples`;
- `variant_divergent_count / groups_with_variant_check`.

These are audit diagnostics derived from the sidecar counts.

T09 does not claim that either derived rate is exactly how a particular
frontend label is rendered unless separately verified.

## What T09 can establish

T09 can establish whether the two T08 consequential group booleans affect the
frozen backend's product-facing headline comparability aggregate.

## What T09 cannot establish

T09 cannot establish:

- semantic invalidity of the affected groups;
- correctness of exact-label partitioning as a normative rule;
- original-publisher fault;
- live-site state at another snapshot;
- user harm;
- materiality of the aggregate delta without a separately defined materiality
  threshold.

T09 measures exposure and exact numerical aggregate consequence only.
