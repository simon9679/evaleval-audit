# RESULT_ANALYSIS — T06 Frozen EEE Source Unit Trace

Status: post-run analysis written after the completed preregistered T06 execution.

This document interprets the completed T06 result. It does not modify the
preregistration, test rationale, source attribution, analyzer, or raw evidence.

## 1. Primary preregistered question

C-T06 asked whether every Stage F row belonging to an actual mixed-unit
comparability group can be traced back to the referenced frozen EEE aggregate
JSON record and whether the source value:

`evaluation_results[result_idx].metric_config.metric_unit`

matches the Stage F `metric_unit`, after only the frozen implementation's
documented normalization:

`percentage -> percent`

The test also required equality of the complete non-null unit set at the group
level.

## 2. Competing predictions frozen before execution

### P1 — source-faithful provenance

All valid traces agree:

- `row_unit_mismatches = 0`
- `group_unit_set_mismatches = 0`
- `pointer_or_index_errors = 0`

### P2 — provenance not fully source-faithful

At least one otherwise valid source trace disagrees:

- `row_unit_mismatches >= 1`
  or
- `group_unit_set_mismatches >= 1`

Pointer/file/index failures were explicitly not counted as P2; they would make
the result INCONCLUSIVE rather than create an EvalEval defect finding.

## 3. Primary verdict

`CONFIRMED`

P1 was observed across the complete mixed-unit population.

The Stage F unit values are directly reproducible from the frozen EEE aggregate
JSON records referenced by the Stage F row pointers.

## 4. Complete reported counts

### Frozen population

- `fact_rows_scanned = 209382`
- `comparability_groups_scanned = 93495`
- `mixed_unit_groups = 1234`
- `mixed_unit_rows = 28196`

The test covered the full T04/T05 mixed-unit group population, not a sample.

### Source-file coverage

- `source_files_referenced = 4278`
- `source_files_opened = 4278`

Every referenced frozen source file needed for the population was opened.

### Row-level trace

- `row_traces_complete = 28196`
- `row_unit_matches = 28196`
- `row_unit_mismatches = 0`

Every Stage F row in the mixed-unit population had a complete source trace and
the normalized frozen-source unit exactly matched the Stage F unit.

Observed row agreement:

`28196 / 28196 = 100%`

### Group-level trace

- `group_unit_set_matches = 1234`
- `group_unit_set_mismatches = 0`

For every actual mixed-unit comparability group, the complete set of non-null
normalized source units exactly matched the Stage F unit set.

Observed group agreement:

`1234 / 1234 = 100%`

### Pointer and identity integrity

- `pointer_or_index_errors = 0`
- `evaluation_id_mismatches = 0`
- `integrity_error_records = 0`

The result is therefore not explained by missing files, incorrect row indices,
evaluation-id disagreement, or an incomplete trace.

## 5. Source-unit distribution

Across the 28,196 traced rows, the normalized frozen EEE source units were:

- `usd_per_1m_tokens = 10629`
- `seconds = 7096`
- `tokens_per_second = 3543`
- `percent = 2866`
- `words = 1368`
- `points = 1299`
- `proportion = 1054`
- `score = 326`
- `usd = 15`

Total:

`10629 + 7096 + 3543 + 2866 + 1368 + 1299 + 1054 + 326 + 15 = 28196`

The distribution therefore accounts for every traced row.

These are descriptive source-level counts. T06 does not assign semantic
correctness or incorrectness to any unit.

## 6. What T06 establishes

T06 establishes, for the complete frozen mixed-unit population:

1. all 28,196 Stage F rows are traceable to frozen EEE aggregate JSON records;
2. all 4,278 referenced files exist and are readable;
3. every `result_idx` points to a valid source result row;
4. all source evaluation ids checked are consistent with the Stage F row;
5. every normalized source `metric_config.metric_unit` matches Stage F;
6. every group's complete source unit set matches the Stage F group unit set;
7. therefore the mixed-unit labels are already present at the frozen EEE
   datastore boundary and are not introduced by the later Stage D metric-unit
   provenance selection layer.

This is the strongest attribution justified by T06.

## 7. What T06 does not establish

T06 does not establish:

- that the original publisher or leaderboard emitted the same unit value;
- that EEE extraction preserved the original publisher field without
  transformation;
- that a source unit is semantically correct;
- that two different unit labels inside one comparability identity measure the
  same or different estimands;
- that EvalEval should normalize, reject, or split those records;
- that the public EvalEval product displays a consequential error;
- that mixed units change a final comparability boolean.

The last item was tested separately by T04 and had zero observed
classification-sensitive paths.

## 8. Attribution boundary after T06

The evidence now supports the following chain:

`frozen EEE source JSON`
`-> source_record_path + result_idx`
`-> Stage F row`
`-> same metric_unit`

with 100% row and group agreement in the T06 population.

Therefore the mixed-unit state is present before the downstream metric-meta
selection layer.

The remaining unresolved boundary is earlier:

`original publisher / leaderboard`
`-> EEE extraction / datastore`
`-> frozen EEE JSON`

T06 does not cross that boundary.

## 9. Relationship to T04 and T05

### T04

T04 established:

- 1,234 actual mixed-unit groups;
- 668 threshold-sensitive groups;
- 0 classification-sensitive paths.

Therefore mixed units had no observed final boolean consequence in the frozen
snapshot.

### T05

T05 established:

- one raw metric label in all 1,234 mixed-unit groups;
- one canonical metric id in all 1,234;
- exact metric resolution only;
- `eee_record` unit provenance only;
- no canonical-convergence groups.

That localized the next attribution boundary to the source records.

### T06

T06 independently verified the T05 provenance label:

- 28,196 / 28,196 row unit matches;
- 1,234 / 1,234 group unit-set matches;
- zero trace errors.

The three-test branch therefore resolves as:

`mixed units exist`
`-> they do not change a final boolean in this snapshot`
`-> they are not created by canonical metric convergence`
`-> they are already present in frozen EEE records`

## 10. Branch decision

The source-faithfulness claim C-T06 is confirmed.

The following question is now closed:

`Did the later EvalEval metric-unit layer create the mixed-unit values?`

For this frozen population, the answer is no: the same values already exist in
the referenced frozen EEE source records.

A new question remains open:

> Do the mixed units represent legitimate heterogeneous measurements under one
> benchmark/metric identity, or does the source/eligibility model combine
> distinct estimands that should not be treated as comparable?

That is a semantic comparability / claim-estimand test, not another source
pointer test.

## 11. Why the next step should not automatically be a web/source scrape

T06 verifies only the frozen EEE datastore boundary.

Tracing 4,278 records back to original external publisher pages could be very
expensive, unstable, and unnecessary unless the unresolved semantic question
is claim-governing.

Before paying that cost, the audit should first inspect the frozen source
metadata and grouping semantics to determine whether the unit combinations are
expected by design or indicate distinct estimands under one comparison
identity.

That decision should itself be preregistered.

## 12. Methodological interpretation

T06 demonstrates why a provenance label should be treated as a trace
hypothesis rather than accepted as ground truth.

T05 reported `eee_record` provenance in all 1,234 mixed groups.

T06 independently checked the actual referenced source artifacts and obtained
perfect agreement.

Only after T06 is it justified to state that the mixed-unit values are already
present at the frozen EEE datastore boundary.

This is a positive example of boundary-aware attribution:

- implementation label first;
- independent source trace second;
- semantic judgement deferred until a separate instrument exists.

## 13. Relation to the method sources

### Falsification Protocol

The exact T06 test is not specified by the Protocol.

The Protocol contributed:

- Rule 6: trace provenance to the source boundary;
- Rule 7: test the produced artifact, not only the mechanism label;
- Rule 8: freeze competing predictions and analysis rules before source
  inspection;
- cheapest-to-more-expensive ordering.

### Validation Handbook

The strongest design anchors were:

- U3: a pipeline provenance label is not independent reference authority;
- U8: source-record agreement cannot support a broader semantic verdict;
- U11: attribution follows explicit component boundaries;
- U12: implementation labels are hypotheses until independently verified;
- B12: unit identity is claim-governing for comparability eligibility.

### Additional-test catalogue

The closest direct catalogue item was:

- Test 4, Component / Harness Attribution.

Supporting:

- Test 1, Claim–Estimand Boundary.

## 14. Setup amendment record

The original T06 preflight failed because it attempted to locate the frozen EEE
root through a `.eee_file_listing.json` marker that was not present in the
actual freeze layout.

Observed first attempt:

- `eee_root_candidates = 0`
- `eee_root_matching_24787 = 0`
- `eee_root = None`

This was an audit-harness setup error, not an EvalEval defect.

`SETUP_AMENDMENT_01.md` and `preflight_fix1.py` replaced only root discovery.
The amended preflight located one exact root:

`freeze/hf/EEE_datastore`

using 32 deterministic source-path probes:

- `source_path_probe_count = 32`
- `exact_probe_matches = 1`
- `candidate_roots = 1`
- `problems = 0`

The T06 claim, competing predictions, analyzer, and verdict rules were not
changed by the setup amendment.

## 15. Evidence files

Primary T06 evidence:

- `raw/preflight_attempt_01_marker_not_found.json`
- `raw/preflight.json`
- `raw/source_root.json`
- `raw/row_trace.jsonl`
- `raw/row_mismatches.jsonl`
- `raw/group_trace.jsonl`
- `raw/group_mismatches.jsonl`
- `raw/integrity_errors.jsonl`
- `results/summary.json`

Frozen Stage F input:

- `tests/T03_corpus_boundary_impact/raw/fact_results_stage_f.parquet`
- SHA-256:
  `e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196`

Backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

## 16. Final T06 statement

Across all 28,196 Stage F rows in all 1,234 actual mixed-unit comparability
groups, the frozen EEE aggregate JSON records referenced by
`source_record_path` and `result_idx` reproduce the Stage F `metric_unit`
values exactly after only the documented `percentage -> percent`
normalization.

All 4,278 source files opened successfully; all 28,196 row traces completed;
all 28,196 row units matched; all 1,234 group unit sets matched; and there were
zero pointer, index, evaluation-id, or integrity errors.

Therefore C-T06 is CONFIRMED.

The mixed-unit values are verified as already present at the frozen EEE
datastore boundary. Semantic correctness, original-publisher provenance, and
comparability eligibility remain separate unresolved questions.
