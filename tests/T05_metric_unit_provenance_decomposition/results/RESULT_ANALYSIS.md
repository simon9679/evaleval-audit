# RESULT_ANALYSIS — T05 Metric Unit Provenance Decomposition

Status: post-run analysis written after the completed preregistered T05 execution.

This document interprets the frozen T05 result. It does not modify the
preregistration, test rationale, source attribution, code, or raw evidence.

## 1. Primary preregistered question

C-T05 asked whether at least one actual mixed-unit Stage F comparability group
was a **full resolved canonical-convergence group**:

- at least two distinct non-null `metric_raw` labels;
- every row resolved to non-null `metric_id`;
- exactly one canonical `metric_id`;
- that canonical id equals the production `metric_key`.

The purpose was to test whether canonical metric resolution structurally
collapsed multiple raw metric labels into one identity inside the mixed-unit
population.

## 2. Competing predictions frozen before the run

### P1 — no full canonical-convergence involvement

`full_resolved_canonical_convergence_groups = 0`

### P2 — canonical-convergence involvement exists

`full_resolved_canonical_convergence_groups >= 1`

## 3. Primary verdict

`REFUTED`

Observed:

- `full_resolved_canonical_convergence_groups = 0`
- `partial_or_mixed_resolution_convergence_groups = 0`

Therefore P1 was observed and P2 was not observed.

The canonical-convergence explanation tested by C-T05 is not supported in the
frozen mixed-unit population.

This verdict is structural and narrow. It does not mean the mixed-unit state is
valid, and it does not identify the final root cause.

## 4. Complete reported counts

### Frozen population

- `fact_rows_scanned = 209382`
- `comparability_groups_scanned = 93495`
- `actual_mixed_unit_groups = 1234`

The 1,234 mixed-unit groups exactly reproduce the T04 population.

### Raw metric identity

- `single_raw_metric_groups = 1234`
- `multi_raw_metric_groups = 0`

Every mixed-unit group contains exactly one distinct non-null `metric_raw`
label.

This is the most important result for the primary T05 claim.

The mixed-unit state is therefore not caused, within these frozen groups, by
multiple different raw metric labels being collapsed into one group.

### Canonical metric identity

- `single_metric_id_groups = 1234`
- `multi_metric_id_groups = 0`
- `groups_with_unresolved_metric_rows = 0`

Every mixed-unit group has exactly one canonical metric id, and no group
contains unresolved metric rows.

The raw and canonical identity paths are therefore structurally stable at the
group level.

### Resolution strategy

- `multi_resolution_strategy_groups = 0`
- `resolution_strategy_patterns = {"exact": 1234}`

Every mixed-unit group uses only the `exact` metric-resolution strategy.

No mixed-unit group combines different resolution strategies.

This substantially weakens a resolver-ambiguity explanation for the observed
unit heterogeneity.

### Unit metadata provenance

- `multi_unit_provenance_groups = 0`
- `metric_unit_provenance_patterns = {"eee_record": 1234}`

Every mixed-unit group receives all of its observed `metric_unit` values from
the `eee_record` provenance layer.

No mixed-unit group in this population mixes registry, heuristic, or null
provenance with EEE-record provenance.

This is a strong attribution result, but it is not yet a final upstream-cause
finding. T05 proves what provenance label the frozen EvalEval pipeline emitted.
It does not independently verify the corresponding source JSON fields.

### Integrity

- `integrity_error_records = 0`

The result is interpretable under the preregistered rules.

## 5. What T05 establishes

For all 1,234 actual mixed-unit Stage F comparability groups in the frozen
snapshot:

1. each group has exactly one raw metric label;
2. each group has exactly one canonical metric id;
3. no metric row is unresolved;
4. every group uses only the `exact` metric-resolution strategy;
5. every unit value is labeled by the pipeline as originating from
   `eee_record`;
6. no group satisfies the preregistered full or partial
   canonical-convergence condition.

Therefore the tested explanation:

`multiple raw metric labels -> canonical convergence -> mixed unit state`

is not supported.

## 6. What the result strongly suggests, but does not yet prove

The evidence strongly points away from metric-name resolution and away from
heuristic unit inference.

The next candidate explanation is:

`same raw metric identity + per-record EEE unit metadata variation`

However, T05 must not convert the pipeline's `eee_record` provenance label into
independent source truth.

A source-record trace is required to verify that:

- the frozen EEE JSON records actually contain the differing unit metadata;
- the row pointers and result indices map correctly;
- the source field values match the Stage F values;
- the disagreement is already present before EvalEval's metric-meta resolver.

Only after that trace can the audit attribute the mixed-unit state to the
upstream frozen records rather than to an internal provenance-labeling defect.

## 7. What T05 does not establish

T05 does not establish:

- that the EEE source files themselves contain the reported unit values;
- whether the upstream source that EEE scraped originally emitted those values;
- whether the differing units are semantically wrong;
- whether one unit is a synonym, display convention, or different estimand;
- whether EvalEval should normalize those values;
- whether the public website is affected;
- whether mixed units change a comparability boolean.

The last item was already tested separately by T04 and had zero observed
classification-sensitive paths.

## 8. Branch decision

The following explanation branch stops:

`different raw metric labels -> canonical resolution collapse -> mixed units`

Reason:

- `multi_raw_metric_groups = 0`
- `full_resolved_canonical_convergence_groups = 0`
- `partial_or_mixed_resolution_convergence_groups = 0`

An expensive semantic trace of canonical-convergence cases is therefore not
justified, because no such cases exist under the preregistered definition.

A new descendant attribution branch is justified:

`EEE-record provenance label -> frozen source-record verification`

That branch should be tested directly against the frozen source records.

## 9. Why the result matters methodologically

T05 prevents another plausible but unsupported story.

After T04, one could have guessed that canonicalization merged different raw
metrics such as time, throughput, cost, score, or percent under a single metric
key.

The full-population T05 result rejects that structural explanation.

All 1,234 groups instead show one raw metric identity, one canonical identity,
one exact resolution strategy, and EEE-record unit provenance.

The method therefore narrowed the attribution layer before any manual source
inspection.

This is exactly the role of a cheap provenance decomposition in a
falsification-oriented decision procedure.

## 10. Relation to the method sources

### Falsification Protocol

The exact T05 test is not stated in the Protocol.

The Protocol contributed:

- Rule 2: separate candidate sources rather than reporting one undifferentiated
  variability phenomenon;
- Rule 6: trace provenance of the observed signal;
- Rule 7: do not mistake a mechanism for a final product result;
- Rule 8: freeze competing predictions before the run;
- cheapest-to-more-expensive ordering.

### Validation Handbook

The main constraints were:

- U3: provenance labels are not independent reference authority;
- U8: structural attribution cannot support a semantic-error verdict;
- U9: the T05 branch is distinct from the T04 boolean-impact branch;
- U11: attribution must respect system boundaries;
- U12: implementation metadata are hypotheses to verify, not ground truth;
- B12: metric identity is claim-governing for comparability.

### Additional-test catalogue

The closest direct catalogue item was:

- Test 4, Component / Harness Attribution.

Supporting:

- Test 1, Claim–Estimand Boundary.

## 11. Evidence files

Primary T05 evidence:

- `raw/preflight.json`
- `raw/mixed_group_attribution.jsonl`
- `raw/full_canonical_convergence_groups.jsonl`
- `raw/full_canonical_convergence_rows.jsonl`
- `raw/integrity_errors.jsonl`
- `results/summary.json`

Frozen input:

- T03 `raw/fact_results_stage_f.parquet`
- SHA-256:
  `e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196`

Backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

## 12. Final T05 statement

Across all 1,234 actual mixed-unit Stage F comparability groups, the frozen
pipeline reports one raw metric label, one canonical metric id, no unresolved
metric rows, only exact metric resolution, and only `eee_record` unit
provenance.

No group satisfies the preregistered canonical-convergence condition.

Therefore C-T05 is REFUTED: the tested canonical-convergence explanation does
not account for the mixed-unit population.

The next justified attribution step is direct verification of the frozen EEE
source records referenced by those Stage F rows.
