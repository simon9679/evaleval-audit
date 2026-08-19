# Completed Test History and Source Attribution

Status: retrospective method record written after T01 and T02, before T03 execution.

This file does not alter the preregistrations, fixtures, verdicts, or raw evidence of T01 or T02. It records why those tests were selected and which methodological source contributed each part of the design.

## Source set

### S1 — Falsification Protocol

Source: `FALSIFICATION_PROTOCOL.md`

Role in this audit:

- minimal cheap-to-expensive decision procedure;
- validate prerequisites before expensive descendants;
- test product-level consequences after mechanism-level observations;
- preregister hypotheses, thresholds, competing predictions, and analysis rules;
- preserve attribution and do not convert setup or audit-harness failures into target findings.

Relevant source rules:

1. reproducibility before quality/superiority;
2. separate major noise sources;
3. positive effects must survive re-run/re-ingest where applicable;
4. calibrate LLM judges independently where applicable;
5. cheap dataset/task validity canary before expensive comparison;
6. establish provenance of intelligence;
7. test product outcome, not only mechanism execution;
8. fix hypotheses, thresholds, competing predictions, and analysis rules before the run.

The original memory-specific order is adapted to the EvalEval object class rather than copied literally.

### S2 — Validation Handbook

Source: `VALIDATION_HANDBOOK.md`

Role in this audit:

- claims are the unit of audit, not projects;
- a test has no verdict-bearing reading until it demonstrates capacity to distinguish relevant states;
- every free parameter must be derived, swept, or dropped;
- no instrument is universal;
- prior findings transfer only as priorities;
- verdict granularity cannot exceed measurement granularity;
- dependencies form a DAG;
- ERROR and INCONCLUSIVE are distinct;
- clean finite runs have finite detection power;
- statistical operations must match measurement scale and design;
- every check is preregistered with claim, instrument, controls, thresholds, outcome meanings, limitations, dependencies, and error conditions.

Most directly relevant catalogue entry:

`P8 — Computed-signal discrimination and degeneracy`

P8 requires:

1. state signal semantics and scale;
2. construct anchored positive/negative poles from the governing definition rather than from the implementation alone;
3. use graded controlled mutation where the construct supports an ordering;
4. estimate detection capability;
5. later measure behavior on the full pinned corpus;
6. separate discrimination from signal provenance.

The Handbook also explicitly identifies dataset registries/cards and evaluation-card infrastructures as suitable targets for full-corpus D/P-series checks because they make measurement claims about completeness, provenance, reproducibility, and comparability.

### S3 — Additional Tests Catalogue supplied during this audit

Source: `AI_SYSTEM_VALIDATION_ADDITIONAL_TESTS_2026-08-19(1).txt`

Role in this audit:

This source is an applicability catalogue, not a mandatory checklist. It explicitly states that a test should be used only when a corresponding claim exists and applicability is justified.

Relevant entries:

- Test 1: Claim–Estimand Boundary
- Test 3: Full-Pipeline Variance Decomposition
- Test 4: Component / Harness Attribution
- Test 5: Environment Solvability / Broken-Task Gate
- Test 17: Local Discriminability / Saturation
- Test 18: Aggregation / Weight Robustness
- Test 19: Measurement Invariance / DIF

The catalogue also proposes an Eval/Benchmark profile where instrument validity and local resolution are tested before broad comparison claims.

This source influenced prioritisation and future branches. It did not directly specify every test that was ultimately run.

### S4 — Frozen EvalEval object

Backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

Public claims and known-issue baselines were frozen before confirmatory testing.

The target itself supplied the concrete measurands and production rules:

- reproducibility;
- completeness;
- provenance;
- comparability.

The audit did not invent those four signal families.

---

# Pre-test gates completed before T01

These are setup and validity gates, not confirmatory EvalEval findings.

## G0 — Frozen object

Result:

- 68,126 frozen files verified;
- bad = 0;
- missing = 0.

Why:

The Protocol requires reproducible evidence before downstream interpretation. The Handbook requires revision-anchored claims, pinned artifacts, and explicit context.

## G1 — Known-issues and public-claims baseline

Result:

- 9 baseline objects verified;
- bad = 0.

Why:

Author-documented limitations must not be re-labelled as independent discoveries. Mutable public claims must be frozen before results are observed.

Primary source:

- Protocol Rule 8;
- Handbook U6, U10, U12;
- audit neutrality requirement.

---

# T01 — Controlled Signal Calibration

## Test identity

Directory:

`tests/T01_signal_calibration`

Verdict:

`REFUTED`

Raw result:

- total cases: 24
- pass: 23
- fail: 1
- inconclusive: 0

By signal:

- reproducibility: 6 / 6 pass
- completeness: 5 / 5 pass
- provenance: 5 / 5 pass
- comparability: 7 / 8 pass

Failed case:

`V2`

Observed behavior:

- score pair: 0.50 and 0.55
- nominal threshold: 0.05
- production classification: divergent
- preregistered expected classification: non-divergent at exact threshold under strict `>` semantics.

## Why T01 was selected

The audit target exposes four computed interpretive signals. Before using those signals to make statements about the full real corpus, the audit needed evidence that the instruments could:

1. react to claim-relevant controlled changes;
2. avoid reacting to selected nuisance changes;
3. expose a meaningful decision boundary;
4. fail under a preregistered negative condition.

Running full-corpus interpretation before this step would have treated uncalibrated signals as measurements.

## Source attribution

### Primary origin: Validation Handbook

T01 is most directly an instantiation of:

`P8 — Computed-signal discrimination and degeneracy`

Specific imported design elements:

- controlled positive and negative conditions;
- nuisance-invariance checks;
- graded or boundary mutations;
- use of the frozen governing definition rather than post-hoc expectations;
- separate signal-level verdicts;
- explicit limitation that controlled calibration does not establish real-world construct validity;
- full-corpus behavior deferred to a later test.

Universal Handbook rules also shaped T01:

- U1: audit claims, not projects;
- U2: no positive verdict without demonstrated capacity to fail;
- U3: use source/specification anchors for conformance-shaped claims;
- U4: derive/sweep/drop free parameters;
- U5: no universal instrument;
- U8: verdict granularity does not exceed measurement granularity;
- U9: dependencies form a DAG;
- U11: audit ERROR is not target failure;
- U15: a clean finite run is a bounded statement;
- U17: measurement operations must match scale/design.

### Supporting origin: Falsification Protocol

The Protocol did not contain a literal "four-signal calibration test."

It contributed the decision logic:

- cheap validity checks before expensive interpretation;
- Rule 5 style canary logic: an instrument must be able to distinguish relevant states;
- Rule 7: later follow the signal-level result to a product/corpus consequence rather than stopping at mechanism execution;
- Rule 8: preregister predictions, thresholds, and analysis before observing the outcome.

### Supporting origin: Additional Tests Catalogue

The additional TXT did not define T01 verbatim.

Its strongest contribution was:

`Test 17 — Local Discriminability / Saturation`

This reinforced the requirement that an evaluation instrument must distinguish systems or states in the region that matters, rather than merely separate extreme poles.

For T01 this principle was used in a controlled precursor form. Real-corpus local discriminability remained deferred.

The TXT also contributed:

`Test 1 — Claim–Estimand Boundary`

This constrained interpretation: a successful controlled calibration could not be generalized into a claim that EvalEval fully measures real-world reproducibility, completeness, provenance, or comparability.

`Test 5 — Environment Solvability / Broken-Task Gate`

This governed error attribution during setup and prevented Hugging Face, Windows-path, or audit-harness failures from being counted as EvalEval failures.

## Why other tests were not selected before T01

- Full-pipeline variance decomposition was deferred because signal validity was unresolved.
- Component/harness attribution was deferred because no observed effect yet required attribution.
- Local discriminability on the real corpus was deferred because primitive controlled calibration had not yet been established.
- Aggregation/weight robustness was conditional on an actual claim-governing aggregate/weight choice.
- Measurement invariance/DIF was advanced and required a separate psychometric justification.
- Security/privacy/sandbagging profiles were not claim-governing for the selected EvalEval claims.

## What T01 was allowed to conclude

T01 could only test controlled discrimination and nuisance invariance of the selected frozen signal primitives.

It could not establish:

- corpus-level accuracy;
- construct validity in the broad real-world sense;
- absence of long-tail failures;
- public product correctness;
- project-level PASS/FAIL.

---

# T01 Post-hoc Attribution Diagnostic

This was not a confirmatory test.

Purpose:

Determine whether the V2 failure was caused by the audit harness, preregistration mistake, or the frozen production arithmetic.

Observed three-point diagnostic:

- 0.50 to 0.55 -> divergence `0.050000000000000044`, threshold `0.05`, flag `true`
- 0.50 to 0.5499999999999999 -> divergence `0.04999999999999993`, flag `false`
- 0.50 to 0.5500000000000002 -> divergence `0.050000000000000155`, flag `true`

Interpretation:

The failure was attributed to binary floating-point sensitivity at the strict threshold boundary in the frozen comparability calculation.

Method source:

- Handbook U11: boundary-aware error attribution;
- Handbook U8: do not generalize one case beyond what was measured;
- Protocol Rule 7: do not stop at a mechanism observation; follow its outcome relevance.

This diagnostic did not change the frozen T01 verdict.

---

# T02 — Comparability Boundary Robustness

## Test identity

Directory:

`tests/T02_comparability_boundary_robustness`

Verdict:

`REFUTED`

Raw result:

- total cases: 48
- pass: 40
- fail: 8
- boundary failures: 8
- below-threshold failures: 0
- above-threshold failures: 0

By threshold basis:

- proportion: 12 total, 10 pass, 2 fail
- percent: 12 total, 10 pass, 2 fail
- range_5pct: 12 total, 10 pass, 2 fail
- fallback_default: 12 total, 10 pass, 2 fail

By production path:

- variant: 24 total, 20 pass, 4 fail
- cross_party: 24 total, 20 pass, 4 fail

## Why T02 was selected

T02 was not selected from a generic checklist before T01.

It was created because T01 opened a specific falsified dependency branch:

1. one preregistered comparability boundary case failed;
2. a post-hoc diagnostic localized the mechanism to floating-point representation;
3. the next cheapest uncertainty was whether this was one accidental numeric pair or a systematic property across threshold bases and production paths.

A full-corpus run before resolving this would have been more expensive and would have mixed prevalence with mechanism characterization.

Therefore T02 asked a narrower question first:

Does the exact-boundary classification instability generalize across all frozen comparability threshold bases and both comparability paths?

## Source attribution

### Primary origin: observed T01 result

The existence and exact shape of T02 came from empirical evidence generated by this audit.

No source document pre-specified:

"Run a four-threshold, two-path exact-decimal boundary robustness test after V2 fails."

That design is audit-specific.

### Methodological origin: Validation Handbook

The Handbook supplied the rules used to construct the follow-up:

- P8: graded mutation / detection-capability logic around a computed signal;
- U2: test must have capacity to fail;
- U4: no post-hoc threshold tuning;
- U8: narrow verdict at the measured boundary;
- U9: follow the falsified dependency branch rather than opening unrelated branches;
- U11: distinguish implementation behavior from harness/environment error;
- U15: finite boundary sweep does not establish universal absence/presence;
- U17: compare the declared mathematical decision rule with production arithmetic using a scale-appropriate exact representation.

### Methodological origin: Falsification Protocol

The Protocol supplied:

- Rule 8 preregistration before the T02 run;
- cheap-to-expensive sequencing;
- Rule 7 product consequence as a later descendant, not an immediate conclusion from the mechanism;
- no project-level verdict from a component-level failure.

### Relationship to the Additional Tests Catalogue

T02 was not directly copied from a named TXT test.

Closest relevant entries:

- Test 17 Local Discriminability / Saturation: reinforces that behavior near the operating/decision region matters;
- Test 18 Aggregation / Weight Robustness: reinforces sensitivity analysis when a decision depends on a threshold or aggregation choice.

However, T02 did not vary arbitrary weights and did not test leaderboard saturation. Its exact-boundary design was derived from the observed V2 failure.

This distinction is intentional: the audit should not retroactively claim a test was "from the TXT" when it was actually generated by the dependency logic of the audit.

## What T02 established

Within its controlled fixtures:

- the boundary effect was not unique to one score pair;
- it appeared in all four frozen threshold bases;
- it appeared in both variant and cross-party comparability paths;
- all tested below-threshold and above-threshold controls behaved as preregistered.

This supports the narrow statement:

The frozen comparability implementation has systematic binary-floating-point sensitivity at exact declared decision boundaries under the tested controlled cases.

## What T02 did not establish

T02 did not establish:

- real-corpus prevalence;
- published-count impact;
- website-visible impact;
- severity;
- broad construct invalidity;
- that comparability is generally broken.

Those are descendants requiring corpus and product-level evidence.

---

# Why T03 is next, but is not yet a completed test

T03 is not included in the completed-test count.

Planned question:

Does the exact-boundary defect confirmed by T01/T02 change at least one real Stage F comparability classification in the full frozen corpus?

Why it is the next descendant:

- T01 established a controlled failure;
- T02 established that the mechanism is systematic across controlled boundary conditions;
- the next claim-governing question is prevalence/product relevance;
- the full corpus is now necessary because sampling could miss rare exact-boundary groups.

Primary methodological sources for T03:

- Protocol Rule 7: test the product/outcome consequence;
- Handbook P8 Step 3: measure real-corpus behavior after controlled calibration;
- Handbook U8: snapshot-bound corpus claim only;
- Handbook U15: zero observed corpus mismatches would mean "not observed in this frozen corpus," not "the defect has no practical impact anywhere";
- Additional TXT Test 17: local discriminability in the real operating range;
- Additional TXT Test 18: threshold/aggregation robustness where classification depends on a decision boundary.

T03 remains preregistered separately and must not be described as completed until its run finishes.

---

# Method-level observation after T01 and T02

The combined method has so far behaved as a decision procedure rather than a checklist:

1. the Protocol supplied ordering and stop/descendant logic;
2. the Handbook supplied admissible test construction, calibration, bounds, and reporting rules;
3. the Additional Tests Catalogue supplied claim-specific candidate profiles and highlighted missing modern eval-specific stress tests;
4. the actual EvalEval result determined which branch opened next.

The strongest evidence of this is T02:

T02 was not selected because it appeared on a checklist. It was created because T01 produced a specific, preregistered falsification at a decision boundary, and the method required the cheapest next test that could determine whether that failure was isolated or systematic.

This is also evidence for the meta-audit of the Protocol and Handbook. A final method report should later evaluate whether this branching reduced cost, prevented overclaiming, or introduced unnecessary complexity.
