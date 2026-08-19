# T02 Result Analysis — Comparability Boundary Robustness

Status: post-run analysis. This file describes the completed test and does not alter the frozen preregistration, fixtures, or verdict rules.

## Result

Verdict: **REFUTED** for the narrow preregistered boundary-robustness claim.

Raw result counts:

- total cases: 48
- PASS: 40
- FAIL: 8
- boundary FAIL: 8
- below-threshold FAIL: 0
- above-threshold FAIL: 0

By threshold basis:

- proportion: 12 total, 10 PASS, 2 FAIL
- percent: 12 total, 10 PASS, 2 FAIL
- range_5pct: 12 total, 10 PASS, 2 FAIL
- fallback_default: 12 total, 10 PASS, 2 FAIL

By production path:

- variant: 24 total, 20 PASS, 4 FAIL
- cross-party: 24 total, 20 PASS, 4 FAIL

## Interpretation

The exact-threshold sensitivity observed in T01 was not isolated to the original `0.5` / `0.55` fixture.

Failures occurred only at exact mathematical boundaries and occurred across:

- all four threshold bases tested;
- both variant and cross-party comparability paths.

All below-threshold and above-threshold controls passed. This localizes the observed problem to exact-boundary arithmetic rather than showing a broad ordering failure away from the threshold.

## What T02 establishes

T02 establishes a systematic controlled exact-boundary sensitivity in the frozen comparability implementation for the tested decimal fixtures and threshold bases.

## What T02 does not establish

T02 does not establish:

- how often exact affected boundaries occur in the real corpus;
- whether any real Stage F classification changes;
- whether any public aggregate or website value changes;
- the severity of the issue at product level;
- general invalidity of the comparability construct.

## Decision consequence

The next claim-governing uncertainty was real-corpus prevalence. Because T02 generalized the controlled defect, T03 was selected to scan the full frozen Stage F comparability population for actual classification differences between production binary-float arithmetic and exact-decimal recomputation.
