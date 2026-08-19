# T03 Result Analysis — Frozen-Corpus Comparability Boundary Impact

Status: post-run analysis. This file describes the completed test and does not alter the frozen preregistration, pipeline code, analyzer, or verdict rules.

## Execution integrity

The first preflight attempt stopped before test execution because the audit Python environment lacked `duckdb`. That attempt was preserved separately as environment evidence and is not an EvalEval result.

The frozen backend lock resolved `duckdb==1.5.2`; after installing that exact locked version, preflight reported zero problems and `network_refresh_required=false`.

The preregistration verifier then reported `VERIFY_PREREG bad=0` before the production pipeline run.

The production Stage A-through-F run completed from frozen local sources without network refresh.

Pipeline evidence:

- validated EEE records: 24,787
- Stage B evaluation-result rows: 210,474
- Stage E output fact rows: 209,382
- Stage F comparability groups: 93,495
- Stage F groups with more than one distinct `metric_unit`: 1,425
- captured Stage F Parquet bytes: 20,789,981
- captured Stage F Parquet SHA-256: `e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196`

The 1,425 mixed-`metric_unit` warning is a separate descriptive candidate branch. It is **not** a T03 boundary-mismatch finding and is not used to change the T03 verdict.

## Confirmatory result

Verdict: **REFUTED** for the preregistered claim that at least one full-corpus Stage F comparability classification changes under exact-decimal recomputation.

Analyzer counts:

- fact rows scanned: 209,382
- comparability groups scanned: 93,495
- variant-applicable groups: 862
- cross-party-applicable groups: 886
- variant production-true groups: 343
- variant exact-decimal-true groups: 343
- cross-party production-true groups: 57
- cross-party exact-decimal-true groups: 57
- variant classification mismatches: 0
- cross-party classification mismatches: 0
- exact-boundary mismatches: 0
- non-boundary mismatches: 0
- production-true / decimal-false: 0
- production-false / decimal-true: 0
- group consistency errors: 0

By threshold basis:

- fallback_default: 17 groups, 0 variant mismatches, 0 cross-party mismatches, 0 exact-boundary mismatches
- percent: 8,101 groups, 0 variant mismatches, 0 cross-party mismatches, 0 exact-boundary mismatches
- proportion: 77,795 groups, 0 variant mismatches, 0 cross-party mismatches, 0 exact-boundary mismatches
- range_5pct: 7,582 groups, 0 variant mismatches, 0 cross-party mismatches, 0 exact-boundary mismatches

## Interpretation

T03 does not invalidate T01 or T02. Those controlled tests established that exact-boundary binary floating-point sensitivity exists and generalizes across the tested controlled boundary fixtures.

T03 establishes that, in this frozen corpus snapshot, the identified mechanism produced **zero observed Stage F classification differences** under the preregistered exact-decimal recomputation.

The correct combined interpretation is therefore:

> The frozen production comparability implementation has systematic binary floating-point sensitivity at exact mathematical thresholds in controlled tests, but no affected Stage F comparability classification was observed in the full frozen corpus snapshot scanned by T03.

## What T03 does not establish

T03 does not establish:

- that future or historical EvalEval snapshots cannot contain affected exact-boundary groups;
- that the comparability construct is generally valid;
- that every public-site representation is correct;
- that mixed-`metric_unit` groups are valid or invalid;
- that unrelated signal branches are correct.

## Methodological consequence

T03 materially narrowed the interpretation of T01/T02. Without the product-consequence step, the controlled systematic boundary defect could have been overreported as a corpus-level EvalEval failure.

The T01 -> T02 -> T03 chain is therefore positive evidence that the method behaved as a dependency-based falsification decision procedure rather than a defect checklist.
