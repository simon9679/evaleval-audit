# PREREGISTRATION — T03 Frozen-Corpus Comparability Boundary Impact

Status: registered before execution.

## Frozen upstream evidence

Required prior gates:

- freeze verification: `bad=0`, `missing=0`;
- baseline verification: `bad=0`;
- T01 verdict: `REFUTED`, fail_count = 1;
- T02 verdict: `REFUTED`, fail_count = 8;
- T02 boundary_fail_count = 8;
- T02 below_fail_count = 0;
- T02 above_fail_count = 0.

Backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

Frozen source revisions are inherited from the audit freeze lock and are not refreshed by T03.

## Claim

C-T03:

At least one production-applicable comparability group in the full frozen corpus has a different boolean classification under:

A. the frozen production binary-float comparison; versus
B. exact-decimal recomputation of the same stored scores and declared threshold rule.

The primary targeted subset is exact-boundary groups where exact-decimal divergence equals the exact-decimal threshold.

## Production paths

Both are tested:

1. variant divergence;
2. cross-party divergence.

## Group population

The population is every Stage F row with a non-null `comparability_group_id` produced from all configs selected by the frozen production pipeline from the full local EEE snapshot, subject to the frozen pipeline's own ignored-config and row-drop policies.

No post-hoc sampling is allowed.

## Decimal threshold oracle

Threshold factor is fixed to production default 1.0.

For each group, the Stage F metric-config aggregation is reconstructed:

- `metric_unit` = maximum non-null group metric_unit;
- `min_score` = maximum non-null group min_score;
- `max_score` = maximum non-null group max_score.

Exact threshold:

- metric_unit = `proportion` -> Decimal("0.05");
- metric_unit = `percent` -> Decimal("5.0");
- else valid max_score > min_score -> Decimal("0.05") * (max_score - min_score);
- else -> Decimal("0.05").

The group threshold basis is recorded.

## Variant oracle

Only production-applicable groups are evaluated.

Exact variant divergence:

`max(Decimal(str(score))) - min(Decimal(str(score)))`

Expected exact-decimal flag:

`exact_divergence > exact_threshold`

## Cross-party oracle

Only production-applicable groups are evaluated.

Organisation normalization uses the frozen production `normalize_org_name`.

For each named normalized organisation:

- collect all group scores;
- sort exact decimal scores;
- odd count median = middle value;
- even count median = exact arithmetic mean of the two middle values.

Exact cross-party divergence:

`max(org_medians) - min(org_medians)`

Expected exact-decimal flag:

`exact_divergence > exact_threshold`

## Mismatch categories

For each path:

- production true / decimal false;
- production false / decimal true.

Each mismatch is further classified as:

- exact-boundary: exact divergence == exact threshold;
- non-boundary: exact divergence != exact threshold.

## Primary verdict

- `CONFIRMED` — at least one exact-boundary classification mismatch exists in the frozen corpus.
- `REFUTED` — zero exact-boundary mismatches and zero analysis-integrity errors.
- `INCONCLUSIVE` — the full Stage F corpus is produced but claim-governing analysis cannot be completed or group consistency is violated in a way that prevents classification.
- `ERROR` — frozen source reuse, production execution, dependency, source-integrity, or evidence-capture failure prevents a valid Stage F corpus.

The verdict is only for C-T03. It is not a global EvalEval verdict.

## Secondary outputs

Regardless of the primary verdict, T03 must report:

- total fact rows;
- total comparability groups;
- variant-applicable groups;
- cross-party-applicable groups;
- production divergent counts;
- exact-decimal divergent counts;
- total mismatches;
- exact-boundary mismatches;
- non-boundary mismatches;
- mismatch direction;
- counts by threshold basis;
- pipeline source/config counts if available from captured logs;
- evidence-file SHA-256.

## Follow-up rule

If T03 finds at least one mismatch, the next test must trace every affected group needed for the public claim back to frozen source records before any final product-level finding is stated.

If T03 finds zero mismatch, the boundary defect remains confirmed by T01/T02 but is classified as not observed to affect this frozen corpus snapshot.
