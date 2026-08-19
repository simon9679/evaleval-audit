# RESULT_ANALYSIS — T14 Source Metric Identity Preservation Counterfactual

Status: final post-run analysis after the accepted Fix 4 execution.

The original T14 preregistration is unchanged. The original analyzer ERROR and
Fixes 1–3 INCONCLUSIVE runs are retained as harness-history evidence. Fix 4 is
the first execution that passed the full production replay gate and therefore
the first execution whose counterfactual result is admissible.

## 1. Final verdict

`CONFIRMED`

Primary preregistered quantity:

`production_positive_groups_losing_all_positive_source_id_subgroups`

Observed:

`1`

Preregistered competing predictions:

- P1: value = 0
- P2: value >= 1

Therefore P2 was observed.

## 2. Replay and integrity gate

The final execution passed every prerequisite needed to interpret the
counterfactual:

- `affected_production_groups = 2`
- `affected_rows = 12`
- `duckdb_generation_args_rows_complete = 12`
- `duckdb_generation_args_errors = 0`
- `production_groups_replayed_exact = 2`
- `production_replay_errors = 0`
- `source_metric_config_consistency_errors = 0`
- `row_identity_errors = 0`
- `integrity_error_records = 0`

This matters because all earlier T14 attempts stopped before the source-id
counterfactual was allowed to run.

## 3. Counterfactual population

The twelve affected arithmetic rows contain six exact source metric ids.

The counterfactual preserved those six source ids as separate grouping
identities while leaving the production variant-divergence function unchanged.

Observed subgroup counts:

- `unique_source_metric_ids = 6`
- `source_id_subgroups_total = 6`
- `source_id_subgroups_applicable = 6`
- `source_id_subgroups_positive = 1`
- `source_id_subgroups_negative = 5`
- `source_id_subgroups_inapplicable = 0`

Thus 1/6 source-id subgroups is positive and 5/6 are negative.

## 4. Group-level result

### Group `0dc7e803e7438c7faf39dfc4b461faef` — CocoaBench

Source metric ids:

1. `cocoabench.overall.accuracy_percent`
2. `cocoabench.overall.avg_time_seconds`

Counterfactual outcome:

- positive source-id subgroups: 1
- negative source-id subgroups: 1
- inapplicable source-id subgroups: 0
- `retains_positive_source_id_subgroup = true`

The production-positive group therefore remains positive under exact source-id
preservation because the accuracy subgroup is independently positive.

#### Accuracy subgroup

- rows = 2
- metric kind = `accuracy`
- unit = `percent`
- min = 0.0
- max = 100.0
- divergence = 8.5
- threshold = 5.0
- threshold basis = `percent`
- result = POSITIVE

Ratio:

`8.5 / 5.0 = 1.70`

The within-source-id divergence is 170% of its threshold.

#### Average-time subgroup

- rows = 2
- metric kind = `latency`
- unit = `seconds`
- min = 0.0
- max = 3322.1
- divergence = 94.69999999999993
- threshold = 166.10500000000002
- threshold basis = `range_5pct`
- result = NEGATIVE

Ratio:

`94.69999999999993 / 166.10500000000002 ≈ 0.5701`

The within-source-id divergence is about 57.0% of its threshold.

### Group `d38d8f8e547287b6b0fc78f43f310762` — WildBench / OpenEval

Source metric ids:

1. `openeval.wildbench.claude-score`
2. `openeval.wildbench.gpt-score`
3. `openeval.wildbench.llama-score`
4. `openeval.wildbench.wildbench-score-rescaled`

Counterfactual outcome:

- positive source-id subgroups: 0
- negative source-id subgroups: 4
- inapplicable source-id subgroups: 0
- `retains_positive_source_id_subgroup = false`

This is the claim-governing T14 result.

The original production group is positive, but none of its four exact source
metric identities is positive when evaluated separately with the unchanged
production divergence function.

#### Claude-score subgroup

- rows = 2
- unit = `points`
- min = -1.0
- max = 10.0
- divergence = 0.15800000000000125
- threshold = 0.55
- threshold basis = `range_5pct`
- result = NEGATIVE

`0.15800000000000125 / 0.55 ≈ 0.2873`

#### GPT-score subgroup

- rows = 2
- unit = `points`
- min = 0.0
- max = 10.0
- divergence = 0.17900000000000027
- threshold = 0.5
- threshold basis = `range_5pct`
- result = NEGATIVE

`0.17900000000000027 / 0.5 ≈ 0.3580`

#### Llama-score subgroup

- rows = 2
- unit = `points`
- min = 0.0
- max = 10.0
- divergence = 0.03349999999999831
- threshold = 0.5
- threshold basis = `range_5pct`
- result = NEGATIVE

`0.03349999999999831 / 0.5 ≈ 0.0670`

#### WildBench-score-rescaled subgroup

- rows = 2
- unit = `score`
- min = 0.0
- max = 1.0
- divergence = 0.013370370370370255
- threshold = 0.05
- threshold basis = `range_5pct`
- result = NEGATIVE

`0.013370370370370255 / 0.05 ≈ 0.2674`

All four WildBench source-id subgroups are comfortably below their own frozen
thresholds; none is a boundary case.

## 5. Strongest justified causal statement

For the WildBench/OpenEval consequential group, the production-positive
variant-divergence flag depends on allowing rows from four distinct exact
source metric ids to share the fallback production identity `score`.

When exact source metric identity is preserved, all four resulting subgroups
are applicable and all four are negative.

This is stronger than the earlier unit-partition result because the
intervention is now source metric identity rather than unit label alone.

## 6. What T14 does not establish

T14 does not establish that:

- every distinct source metric id is semantically non-equivalent;
- exact source metric id is always the correct canonical identity;
- the registry must never alias some of these ids;
- the correct repair is to preserve every source id literally;
- the public product flag is substantively material to users;
- any particular upstream publisher intended these metrics to be separate.

T14 is a causal operational counterfactual, not yet a semantic/reference
adjudication.

## 7. Relationship to T08 and T09

T08 showed that 2/5 production-positive mixed-unit variant paths flip negative
under an exact-unit partition counterfactual.

T09 showed that applying those two T08 flips changes the product-facing
headline variant-divergent count from 343 to 341.

T14 now decomposes the two consequential groups more narrowly:

- CocoaBench retains one independently positive source-id subgroup;
- WildBench loses all positive source-id subgroups.

Therefore source-metric-identity collapse is operationally necessary for one
of the two T08/T09 consequential groups, not both.

A source-id-preservation headline counterfactual would need to be run
separately before assigning an exact corpus-level count change to T14.

## 8. Harness history

T14 contains an unusually important harness history and it must remain visible
in the audit.

### Original analyzer

ERROR because it assumed final Stage F retained internal UDF payload columns
that production intentionally excludes.

### Fix 1

INCONCLUSIVE because it incorrectly required row-level metric metadata to be
constant inside the production comparability group.

### Fix 2

INCONCLUSIVE with one remaining representation mismatch after exact production
metric-config MAX reconstruction.

### Fix 3

INCONCLUSIVE because PyArrow `to_pylist()` converted an Arrow MAP to a Python
association list, which did not match the production DuckDB JSON
representation.

### Fix 4

Before execution, library behavior and frozen code were researched. Fix 4
reconstructed the actual production representation path:

`frozen EEE JSON -> frozen validation -> frozen Arrow schema -> DuckDB -> to_json -> production divergence function`

Fix 4 then achieved exact 2/2 production replay and zero integrity errors.

These failures are audit-harness evidence, not EvalEval defects.

## 9. Methodological lesson

When a counterfactual depends on an internal UDF payload, reconstructing the
logical field values is not sufficient if representation transformations are
claim-governing.

The replay must reproduce the same serialization boundary used by production.

For nested typed data, Arrow, Python, DuckDB, and JSON can preserve the same
logical information while exposing different runtime shapes.

A production replay gate prevented those representation differences from being
misclassified as a target-system finding.

## 10. Branch decision

The next branch should not invent a canonicalization rule from T14.

The next test should adjudicate authoritative metric semantics for the exact
source metric identities, with priority on the WildBench/OpenEval set because
that is the group for which T14 established operational dependence on identity
collapse.

The semantic test must distinguish:

1. source identity difference;
2. scale/rescaling difference;
3. genuinely different estimands or evaluation procedures;
4. insufficient documentation.

Only after that adjudication can the audit say whether the operationally
necessary identity collapse is semantically invalid rather than merely one
possible canonicalization policy.

## 11. Final T14 statement

T14 is CONFIRMED.

Both affected production groups replay exactly under the frozen production
representation, with zero integrity errors.

Under exact source metric-id preservation, CocoaBench retains one positive
subgroup, while the WildBench/OpenEval group loses all positive subgroups: all
four of its exact source metric identities are individually negative.

Thus fallback source-id collapse is operationally necessary for one of the two
consequential production-positive variant-divergence flags.
