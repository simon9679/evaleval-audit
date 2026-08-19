# PREREGISTRATION — T13 Structured Metric-ID Rejection Attribution

Status: registered before T13 execution.

## Frozen prerequisites

T12 required result:

- verdict = `CONFIRMED`;
- affected_group_ids = 2;
- source_rows_scanned = 12;
- stage_rows_joined = 12;
- distinct_source_metric_ids_total = 6;
- affected_groups_with_multiple_source_metric_ids = 2;
- affected_groups_with_structured_strategy_rows = 0;
- affected_groups_with_fallback_source_id_collapse = 2;
- row_identity_errors = 0;
- integrity_error_records = 0.

Backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

Resolver source commit:

`6fb026d7483467f063da465c15a76733b3d25f4c`

Required input:

`tests/T12_source_metric_identity_collapse/raw/row_identity_trace.jsonl`

## Resolver-source discovery

Do not assume a repository folder name.

Under `freeze/repos`, find exactly one git checkout whose HEAD equals the
frozen resolver-source commit.

That checkout must contain:

`packages/eval-entity-resolver/src/eval_entity_resolver/resolver.py`

## Registry-data discovery

Do not assume a HuggingFace cache folder name.

Under `freeze/hf`, find exactly one directory that contains both:

- aliases parquet data in either `aliases.parquet` or `aliases/*.parquet`;
- canonical metric parquet data in either `canonical_metrics.parquet` or
  `canonical_metrics/*.parquet`.

The directory must be unique.

## Population

The six unique non-null source metric ids in the twelve T12 row traces.

Source config is read from the corresponding frozen Stage F row and is part of
the resolver invocation.

If one source metric id appears under more than one source config, each unique
pair is replayed and reported. The primary six-id prediction requires that the
six ids each have a single source-config outcome; otherwise T13 is
INCONCLUSIVE.

## Catch-all set

Load frozen `canonical_metrics` and include every id whose JSON `metadata`
contains:

`"catch_all": true`

No catch-all id may be invented manually.

## Segment replay

Split source metric id by `[./]`.

Ignore segment zero.

For each later segment call the frozen resolver:

`resolve(segment, "metric", source_config, mode="exact")`

The resolver's exact mode includes its exact and normalized alias tiers but
stops before fuzzy resolution.

Collect canonical ids from non-null hits.

Specific hits are:

`all_hits - catch_all_ids`

## Direct structured replay

Call:

`resolve_structured_metric_id(source_metric_id, source_config, catch_all_ids)`

The direct result must agree with the segment-rule classification.

## Primary claim C-T13

All six source metric ids have zero distinct non-catch-all specific metric hits
and direct structured result null.

## Competing predictions

### P1

`rejected_conflicting_specific_ids >= 1`

### P2

`rejected_conflicting_specific_ids = 0`
and
`rejected_zero_specific_ids = 6`

## Required outputs

- `raw/structured_id_replay.jsonl`
- `raw/rejection_classes.json`
- `raw/integrity_errors.jsonl`
- `raw/discovery.json`

## Required summary counts

At minimum:

- source_rows_scanned;
- unique_source_metric_ids;
- unique_source_metric_id_config_pairs;
- structured_accept_ids;
- structured_reject_ids;
- rejected_no_hits;
- rejected_catch_all_only;
- rejected_zero_specific_ids;
- rejected_conflicting_specific_ids;
- inconsistent_replay_ids;
- affected_ids_with_multiple_source_configs;
- catch_all_metric_ids_count;
- row_source_config_errors;
- integrity_error_records;
- rejection class by source metric id;
- segment hits by source metric id.

All counts must be printed.

## Branch decision

If `CONFIRMED`:

- structured rejection is a registry-vocabulary/deferral outcome for all six
  consequential source ids, not a specific-metric ambiguity conflict;
- the next test should ask whether the source-declared metrics are
  semantically equivalent under authoritative benchmark definitions and
  whether adding/preserving specific identity would prevent the two product
  flips.

If `REFUTED`:

- at least one rejection is due to conflicting specific metric disclosures;
- semantic adjudication must distinguish registry ambiguity from source metric
  identity before proposing any alias fix.

If `INCONCLUSIVE` or `ERROR`:

- repair the replay;
- do not attribute the rejection reason to EvalEval.
