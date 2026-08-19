# SOURCE_ATTRIBUTION

## Frozen EEE source records

T10 source pointers are used to re-open the exact eight source rows.

Claim-governing fields are taken from each source `metric_config`:

- `metric_unit`
- `min_score`
- `max_score`
- `metric_parameters`
- `additional_details`
- `metric_kind`
- `score_type`
- `lower_is_better`

## T15 dependency

T15 fixed the exact four independently traceable source ids and established
four distinct non-name structured signatures.

## Frozen OpenEval adapter

Repository:

`evaleval/every_eval_ever`

Commit:

`9bce4136e789ec006c62582f5f9d107d20f8b398`

The frozen adapter preserves source metric names/models and emits mean aggregate
results into EEE metric records.

T16 does not assume that absence of a hard-coded adapter transform proves
absence of all upstream transformations. Its primary claim is limited to the
structured EEE source representation.

## Official WildBench context

Official WildBench v2 documentation distinguishes:

- individual WB Score;
- pairwise WB Reward;
- separate reward channels using three reference models.

The official WB Score documentation also defines an explicit rescaling formula
for its own score path.

This context motivates the requirement that a cross-channel transformation
should be explicit before raw arithmetic is treated as commensurate.

T16 does not map the current OpenEval source channel names to the historical
official WildBench channels by name alone.
