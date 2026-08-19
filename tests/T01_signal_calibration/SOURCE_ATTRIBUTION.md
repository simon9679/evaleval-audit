# T01 Source Attribution — Controlled Signal Calibration

Status: post-run documentation. This file was added after T01 completed. It does not modify the frozen preregistration, test rationale, fixtures, code, or verdict criteria.

## Immediate test-selection trigger

T01 was selected as the first confirmatory signal test because downstream corpus claims depend on the four EvalEval signals having basic controlled discrimination and invariance properties. The audit had already frozen the target, verified the freeze, and frozen known issues and public claims. The next cheapest claim-governing uncertainty was therefore instrument validity rather than corpus interpretation.

## Falsification Protocol contribution

The Falsification Protocol did **not** specify this exact T01 test. It contributed the decision logic:

- perform cheap validity checks before expensive comparative or product-level interpretation;
- use canary/control-style tests before trusting an instrument;
- test product-relevant behavior rather than infer correctness from mechanism alone;
- preregister hypotheses, thresholds, competing outcomes, and analysis rules before execution.

The concrete controlled mutations were adapted to an AI evaluation pipeline rather than copied from a memory-system test.

## Validation Handbook contribution

The Validation Handbook was the **primary methodological source** for T01 construction, especially the scale-aware discrimination / controlled-mutation logic in P8 and the following universal constraints:

- U1: test a bounded claim, not an entire project;
- U2: no positive verdict without demonstrated capacity to fail;
- U3: define the reference authority / oracle explicitly;
- U4: derive, sweep, or remove free parameters;
- U5: do not assume one universal instrument;
- U8: verdict granularity must not exceed measurement granularity;
- U9: respect the dependency DAG;
- U11: separate target failure from harness/environment error;
- U15: a clean run is only a finite-power statement;
- U17: use operations appropriate to the measurement scale and decision boundary.

These rules determined the use of controlled positive/negative poles, nuisance mutations, exact boundary cases, and narrow signal-level conclusions.

## Additional test catalog contribution

The user's `AI_SYSTEM_VALIDATION_ADDITIONAL_TESTS_2026-08-19` catalog did **not** define T01 verbatim. The closest direct support was:

- Test #17, Local Discriminability / Saturation: validate that a signal can discriminate relevant nearby changes before relying on it in the operating range;
- Test #1, Claim–Estimand Boundary: limit interpretation to what the tested signal actually estimates;
- Test #5, Environment Solvability / Broken-Task Gate: keep setup failures separate from EvalEval findings.

T01 is best understood as a controlled precursor to later real-corpus local-discriminability work.

## Why T01 was chosen over alternatives

- Full-corpus analysis was deferred because it would interpret the instrument before calibration.
- Full-pipeline reproducibility was deferred because the immediate dependency was signal validity after a verified freeze.
- Aggregation robustness was deferred until a claim-governing aggregation or threshold issue emerged.
- Security/privacy/sandbagging tests were not applicable to the selected signal-validity claim.

## Selection summary

Primary origin: **Validation Handbook**.

Decision-order support: **Falsification Protocol**.

Supporting evaluation-specific analogues: **Additional test catalog #17, #1, #5**.

Audit-object specifics: **frozen EvalEval production signal implementations and public signal claims**.
