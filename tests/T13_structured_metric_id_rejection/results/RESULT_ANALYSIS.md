# RESULT_ANALYSIS — T13 Structured Metric-ID Rejection Attribution

Status: post-run analysis written after the completed preregistered T13 execution.

This document interprets the frozen T13 result. It does not modify the
preregistration, rationale, source attribution, analyzer, verifier, or raw
evidence.

## 1. Primary preregistered question

C-T13 asked whether all six T12 source metric ids are rejected by the frozen
structured metric-id resolver because they disclose zero distinct
non-catch-all specific registry metric ids, rather than because they disclose
two or more conflicting specific metric ids.

The preregistered zero-specific count combines:

- `rejected_no_hits`
- `rejected_catch_all_only`

## 2. Competing predictions

### P1 — specific-metric conflict contributes

`rejected_conflicting_specific_ids >= 1`

### P2 — pure vocabulary / deferral rejection

`rejected_conflicting_specific_ids = 0`

and

`rejected_zero_specific_ids = 6`

## 3. Primary verdict

`CONFIRMED`

Observed:

- `rejected_conflicting_specific_ids = 0`
- `rejected_zero_specific_ids = 6`

Therefore P2 was observed exactly.

## 4. Complete counts

- `source_rows_scanned = 12`
- `unique_source_metric_ids = 6`
- `unique_source_metric_id_config_pairs = 6`
- `structured_accept_ids = 0`
- `structured_reject_ids = 6`
- `rejected_no_hits = 4`
- `rejected_catch_all_only = 2`
- `rejected_zero_specific_ids = 6`
- `rejected_conflicting_specific_ids = 0`
- `inconsistent_replay_ids = 0`
- `affected_ids_with_multiple_source_configs = 0`
- `catch_all_metric_ids_count = 3`
- `row_source_config_errors = 0`
- `integrity_error_records = 0`

Every unique source metric id had exactly one source-config replay outcome.

## 5. CocoaBench rejection classes

### `cocoabench.overall.accuracy_percent`

- source config: `cocoabench`
- classification: `rejected_catch_all_only`
- direct structured result: null

### `cocoabench.overall.avg_time_seconds`

- source config: `cocoabench`
- classification: `rejected_catch_all_only`
- direct structured result: null

Both CocoaBench source metric ids produce registry hits only in the frozen
catch-all metric set. No specific non-catch-all metric identity survives the
structured resolver rule.

This is not a multi-specific ambiguity.

## 6. WildBench / OpenEval rejection classes

### `openeval.wildbench.claude-score`

- source config: `openeval`
- classification: `rejected_no_hits`
- direct structured result: null

### `openeval.wildbench.gpt-score`

- source config: `openeval`
- classification: `rejected_no_hits`
- direct structured result: null

### `openeval.wildbench.llama-score`

- source config: `openeval`
- classification: `rejected_no_hits`
- direct structured result: null

### `openeval.wildbench.wildbench-score-rescaled`

- source config: `openeval`
- classification: `rejected_no_hits`
- direct structured result: null

All four WildBench/OpenEval source metric ids produce no metric vocabulary hit
under the frozen exact/normalized structured replay.

Again, no multi-specific ambiguity exists.

## 7. Replay integrity

The following are all zero:

- `structured_accept_ids`
- `rejected_conflicting_specific_ids`
- `inconsistent_replay_ids`
- `affected_ids_with_multiple_source_configs`
- `row_source_config_errors`
- `integrity_error_records`

The direct frozen resolver replay therefore agrees with T12's observed absence
of `metric_id_structured` rows.

## 8. What T13 establishes

T13 establishes all of the following for the six consequential source metric
ids:

1. all six are rejected by the structured metric-id pre-step;
2. four are rejected because no registry metric segment is resolved;
3. two are rejected because only catch-all metric identities are resolved;
4. zero are rejected because of multiple conflicting specific metric
   candidates;
5. zero are accepted as a specific structured metric;
6. no source id appears under multiple source configs;
7. no replay or integrity inconsistency is observed.

The strongest justified statement is:

> The structured metric-id pre-step defers all six consequential source metric
> ids because the frozen registry supplies no usable specific metric identity;
> no rejection is caused by ambiguity among multiple specific metric
> candidates.

## 9. Relationship to T12

T12 established:

`multiple source metric ids`
`-> no metric_id_structured rows`
`-> fallback metric_raw = score`
`-> canonical metric_id = score`
`-> metric_key = score`

T13 now identifies why the first arrow occurs:

- CocoaBench ids: catch-all-only structured resolution;
- WildBench/OpenEval ids: no structured metric hits.

The transformation chain is therefore component-attributed through the
registry/structured-resolver boundary.

## 10. What T13 does not establish

T13 does not establish:

- that the registry is defective merely because it lacks these identities;
- that a new alias should automatically be added;
- that the six source metrics are semantically different;
- that preserving each exact source metric id is the only correct identity
  policy;
- that fallback `score` is semantically invalid in every context;
- original-publisher intent.

These remain separate normative/reference questions.

## 11. Next deterministic descendant

Before external semantic adjudication, one low-cost causal question remains:

> If the six exact source metric ids are preserved as the metric identity for
> only these twelve affected rows, do either of the two production-positive
> variant-divergence groups still contain a positive variant-divergence
> subgroup?

This is not a normative claim that source ids must be preserved.

It is a counterfactual causal test of whether the fallback identity collapse is
necessary for the two consequential positive flags.

## 12. Branch decision

Proceed to a source-metric-identity-preservation counterfactual over only the
two affected production groups.

If neither production-positive group retains any positive source-id subgroup,
the fallback identity collapse is operationally necessary for both flags.

If one or both retain positive source-id subgroups, the identity collapse is
not necessary for those flags and the semantic branch must account for that.

## 13. Methodological interpretation

T13 demonstrates the value of distinguishing resolver ambiguity from resolver
deferral.

A null structured result is not one mechanism.

Here the six nulls split into:

- four no-hit outcomes;
- two catch-all-only outcomes;
- zero conflicting-specific outcomes.

That distinction localizes the failure mode before any proposed registry
change is considered.

## 14. Final T13 statement

All six consequential source metric ids are rejected by the frozen structured
metric-id resolver with zero usable specific metric identities.

Four have no metric hits and two have catch-all-only hits.

No id is rejected because of conflicting specific metric candidates.

All replay and integrity controls pass.

Therefore C-T13 is CONFIRMED.
