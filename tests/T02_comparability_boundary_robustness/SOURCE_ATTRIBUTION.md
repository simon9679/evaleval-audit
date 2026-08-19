# T02 Source Attribution — Comparability Boundary Robustness

Status: post-run documentation. This file was added after T02 completed. It does not modify the frozen preregistration, fixtures, code, or verdict criteria.

## Immediate test-selection trigger

T02 was **not selected directly from a checklist**. Its primary trigger was the empirical T01 V2 failure at the exact comparability threshold.

The audit-specific question was: is that failure an isolated score-pair artifact, or does the same decision-boundary instability recur across mathematically equivalent pairs, all production threshold bases, and both comparability paths?

## Falsification Protocol contribution

The Falsification Protocol did not define this exact boundary sweep. It contributed:

- follow the falsified dependency branch before opening unrelated branches;
- resolve the cheapest claim-governing uncertainty first;
- preregister the fixtures, threshold bases, expected boundary behavior, and outcome rules;
- defer product-level severity claims until a later consequence test.

Rule 7 / product-consequence logic was deliberately **not yet completed** by T02; it required the later corpus-impact test.

## Validation Handbook contribution

The Validation Handbook supplied the main construction constraints:

- P8: controlled graded/boundary mutation and detection-limit reasoning;
- U2: the test must have capacity to fail;
- U4: no post-run free-parameter tuning;
- U8: keep the verdict at boundary-instrument granularity;
- U9: follow the dependency branch opened by T01;
- U11: separate a target arithmetic failure from harness or environment failure;
- U15: a clean boundary sweep would still be bounded evidence;
- U17: compare the production threshold operation to an appropriate exact-decimal reference.

## Additional test catalog contribution

The additional catalog did not define T02 verbatim.

Supporting analogues were:

- Test #17, Local Discriminability / Saturation, because the threshold must separate nearby values consistently;
- Test #18, Aggregation / Weight Robustness, only as a general reminder that claim-governing threshold/aggregation choices require robustness checks.

T02 did **not** test arbitrary weights, ranking saturation, or the full catalog Test #18. Those would be overstatements of its source.

## Why T02 was chosen over alternatives

- A full-corpus run was deferred because a controlled sweep was cheaper and could first determine whether the boundary issue generalized.
- Another unrelated signal test was deferred because T01 opened a specific falsified dependency branch.
- A repair using epsilon/tolerance was rejected because the audit measures the frozen implementation rather than patching it.

## Selection summary

Primary trigger: **empirical T01 failure**.

Construction rules: **Validation Handbook P8 and U2/U4/U8/U9/U11/U15/U17**.

Decision-order support: **Falsification Protocol**.

Supporting analogues: **Additional test catalog #17 and, secondarily, #18**.
