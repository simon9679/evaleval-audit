# RESULT_ANALYSIS — T12 Source Metric Identity Collapse Trace

Status: post-run analysis written after the completed preregistered T12 execution.

This document interprets the completed T12 result. It does not modify the
preregistration, test rationale, source attribution, analyzer, or raw evidence.

## 1. Primary preregistered question

C-T12 asked whether at least one of the two product-consequential groups
contains multiple distinct non-null frozen source `metric_config.metric_id`
values that are represented in Stage F by one `metric_raw`, one canonical
`metric_id`, and one `metric_key`, with no row using the
`metric_id_structured` strategy.

## 2. Competing predictions frozen before execution

### P1 — no fallback source-id collapse

`affected_groups_with_fallback_source_id_collapse = 0`

### P2 — fallback source-id collapse exists

`affected_groups_with_fallback_source_id_collapse >= 1`

## 3. Primary verdict

`CONFIRMED`

Observed:

- `affected_groups_with_fallback_source_id_collapse = 2`
- `affected_group_ids = 2`

Therefore P2 was observed in both consequential groups.

## 4. Complete reported counts

- `source_rows_scanned = 12`
- `stage_rows_joined = 12`
- `distinct_source_metric_ids_total = 6`
- `affected_groups_with_multiple_source_metric_ids = 2`
- `affected_groups_with_single_stage_metric_raw = 2`
- `affected_groups_with_single_stage_metric_id = 2`
- `affected_groups_with_single_stage_metric_key = 2`
- `affected_groups_with_structured_strategy_rows = 0`
- `affected_groups_with_fallback_source_id_collapse = 2`
- `source_ids_mapping_to_one_metric_key_groups = 2`
- `row_identity_errors = 0`
- `integrity_error_records = 0`

All twelve source rows joined one-to-one to the frozen Stage F rows.

## 5. Group-level transformation

### Group `0dc7e803e7438c7faf39dfc4b461faef`

Source metric ids:

- `cocoabench.overall.accuracy_percent`
- `cocoabench.overall.avg_time_seconds`

Downstream identity:

- `metric_raw = score`
- `metric_id = score`
- `metric_key = score`
- resolution strategy = `exact`
- structured strategy rows = 0

The full preregistered fallback-collapse predicate is true.

### Group `d38d8f8e547287b6b0fc78f43f310762`

Source metric ids:

- `openeval.wildbench.claude-score`
- `openeval.wildbench.gpt-score`
- `openeval.wildbench.llama-score`
- `openeval.wildbench.wildbench-score-rescaled`

Downstream identity:

- `metric_raw = score`
- `metric_id = score`
- `metric_key = score`
- resolution strategy = `exact`
- structured strategy rows = 0

The full preregistered fallback-collapse predicate is true.

## 6. What T12 establishes

T12 establishes, for the frozen consequential population:

1. six distinct source-declared metric ids occur across the two groups;
2. both groups contain multiple source metric ids;
3. both groups have exactly one downstream `metric_raw`;
4. both groups have exactly one downstream canonical `metric_id`;
5. both groups have exactly one production `metric_key`;
6. no affected row uses `metric_id_structured`;
7. every affected group satisfies the full preregistered fallback source-id
   collapse predicate;
8. all source ids in each group map to the same production metric key;
9. no row-identity or integrity failure occurred.

The strongest justified statement is:

> In both product-consequential groups, multiple source-declared metric ids are
> collapsed through the fallback metric path into the single production
> identity `score`, which is then used as the comparability `metric_key`.

## 7. Relation to T11

T11 showed that the source metric definitions differ in claim-governing fields:

- source `metric_id` varies in both groups;
- `max_score` varies in both;
- the CocoaBench group also varies in `metric_kind` and `lower_is_better`;
- the WildBench group also varies in `min_score`.

T12 now identifies how those heterogeneous source definitions become one
production metric identity.

The transformation boundary is no longer unknown.

## 8. Relation to T05

T05 reported one Stage F raw/canonical metric identity and exact resolution per
mixed group.

T12 explains how that downstream homogeneity can coexist with heterogeneous
source metric ids:

- the structured source ids were not used as the downstream raw identity;
- the affected rows instead reached `metric_raw = score`;
- ordinary exact resolution then mapped that fallback raw value to canonical
  `score`.

Thus T05 and T11 are not contradictory. They observe different sides of the
identity transformation.

## 9. What T12 does not establish

T12 does not establish:

- why the structured metric-id pre-step returned no usable id for each source
  metric id;
- whether rejection was caused by no registry vocabulary hit, catch-all-only
  hits, or conflicting specific hits;
- whether the six source ids are semantically equivalent or non-equivalent;
- whether `score` is an acceptable canonical alias;
- which source id should be canonical;
- original-publisher intent.

The next cheapest test is direct attribution of the structured resolver
rejection mechanism.

## 10. Branch decision

Proceed to a direct frozen structured metric-id resolver replay for the six
source metric ids.

The next test should:

1. instantiate the frozen resolver vocabulary;
2. resolve each source metric id with its frozen source config;
3. replay the exact segment-level membership rule;
4. classify each rejection as:
   - no metric hit;
   - catch-all-only hit;
   - conflicting specific hits;
   - accepted single specific hit;
5. verify direct replay agrees with the observed absence of
   `metric_id_structured`.

Only after that component-attribution step should semantic equivalence be
adjudicated.

## 11. Methodological interpretation

T12 is a provenance-of-transformation result.

It does not rely on interpreting metric names.

The audit now has a concrete causal chain in the frozen pipeline:

`source metric ids`
`-> structured path not used`
`-> fallback metric extraction`
`-> raw score`
`-> exact canonical score`
`-> one metric_key`
`-> one comparability group`
`-> mixed-metric arithmetic`
`-> two boolean flips`
`-> headline count 343 -> 341`

The remaining uncertainty is the reason for structured-path deferral and then
semantic admissibility of the source-id collapse.

## 12. Final T12 statement

Across twelve rows in two product-consequential comparability groups, six
distinct source-declared metric ids collapse to the single Stage F
`metric_raw`, canonical `metric_id`, and `metric_key` value `score`.

No affected row uses the `metric_id_structured` strategy.

Both groups satisfy the full preregistered fallback source-id collapse
predicate.

Row identity errors and integrity errors are zero.

Therefore C-T12 is CONFIRMED.
