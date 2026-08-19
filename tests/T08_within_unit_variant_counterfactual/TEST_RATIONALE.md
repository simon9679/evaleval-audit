# TEST_RATIONALE — T08 Within-Unit Variant Divergence Counterfactual

Status: frozen before execution.

## Primary claim C-T08

> At least one production-positive mixed-unit variant-divergence path becomes
> negative when its raw divergence is constrained to the largest range
> obtainable inside any one exact declared non-null `metric_unit` partition,
> while keeping the frozen production threshold unchanged.

Observable primary quantity:

`positive_to_negative_paths`

## Why this test was selected

T07 proved that every applicable mixed-unit variant path performs its raw
range calculation over numeric rows carrying multiple declared unit labels.

That still does not prove that cross-label mixing affects the final production
boolean.

A single exact-unit partition could independently contain a score range large
enough to cross the same production threshold.

T08 measures that consequence directly.

## Why this test is run now

This is the cheapest product-consequence descendant of T07.

It requires no semantic judgement, no source web access, no new pipeline run,
and no unit conversion.

If the production-positive booleans survive the most permissive exact-unit
partition rule, the arithmetic heterogeneity has no observed boolean
consequence under this counterfactual.

If at least one positive flag disappears, the production positive decision
depends on allowing score ranges across exact declared unit labels.

## Fixed counterfactual

For each applicable mixed-unit variant path:

1. use the same numeric score rows as production;
2. partition rows by exact non-null `metric_unit`;
3. for each partition:
   - if it has one numeric row, within-unit range = `0`;
   - otherwise range = `max(score) - min(score)`;
4. define:
   `max_within_unit_range = max(all exact-unit partition ranges)`;
5. keep the frozen production `variant_divergence_threshold` unchanged;
6. define counterfactual boolean:
   `max_within_unit_range > production_threshold`.

This is deliberately the most permissive exact-label partition counterfactual:
if any declared unit alone can reproduce a large range, its range is used.

## Competing predictions

### P1 — positive decisions survive exact-label eligibility

`positive_to_negative_paths = 0`

Every production-positive mixed-unit variant path remains positive using the
largest exact-unit range under the same frozen threshold.

### P2 — at least one positive decision depends on cross-label mixing

`positive_to_negative_paths >= 1`

At least one production-positive path becomes negative when the range operation
is restricted to exact-unit partitions.

## Secondary descriptive measurements

For all seven applicable paths, report:

- production divergence;
- maximum within-unit range;
- cross-label excess:
  `production_divergence - max_within_unit_range`;
- production threshold;
- production boolean;
- counterfactual boolean;
- per-unit row counts and ranges;
- whether production divergence equals the maximum within-unit range;
- whether production divergence exceeds every within-unit range;
- exact unit pattern.

Also report:

- positive-to-positive paths;
- positive-to-negative paths;
- negative-to-negative paths;
- negative-to-positive paths.

A negative-to-positive result should be impossible because a within-unit range
cannot exceed the global range. If observed, it is an integrity failure.

## Integrity controls

The test must verify:

- backend commit unchanged;
- T03 Stage F Parquet SHA unchanged;
- T07 verdict is CONFIRMED;
- T07 reports exactly 7 applicable paths, all 7 unit-heterogeneous;
- T07 reports 5 production-positive and 2 production-negative paths;
- recomputed group population and production booleans agree with T07;
- production divergence reconstructs as global raw `max - min`;
- `max_within_unit_range <= production_divergence + 1e-12`;
- no negative-to-positive counterfactual transition occurs.

Integrity failure is not an EvalEval defect.

## What T08 can establish

T08 can establish whether a frozen production-positive variant-divergence
boolean depends on allowing numeric score extrema from different exact declared
unit-label partitions to contribute to one range operation.

## What T08 cannot establish

T08 cannot establish:

- that different labels are semantically incompatible;
- that exact label equality is the only valid comparability rule;
- that labels such as `score`, `points`, and `proportion` cannot be valid
  aliases in a particular source;
- which source label is correct;
- whether the original publisher caused the state;
- whether the public website presents the flag in a misleading way.

Those require separate reference or product-surface evidence.
