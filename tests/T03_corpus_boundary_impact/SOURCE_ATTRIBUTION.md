# T03 Source Attribution — Frozen-Corpus Comparability Boundary Impact

Status: post-run documentation. This file was added after T03 completed. It does not modify the frozen preregistration, pipeline code, analyzer, or verdict criteria.

## Immediate test-selection trigger

T03 was selected because T01 found an exact-boundary failure and T02 showed that the failure generalized across all tested threshold bases and both comparability paths.

The remaining claim-governing question was practical prevalence: does that controlled arithmetic defect change at least one classification in the actual full frozen corpus?

## Falsification Protocol contribution

The Falsification Protocol supplied the main decision transition:

- after a mechanism/instrument failure, test the actual product/outcome consequence before making a product-level claim;
- follow the existing falsified dependency branch before searching for unrelated defects;
- use the cheapest sufficient consequence test rather than expanding scope unnecessarily;
- preserve preregistration and attribution.

This is the clearest Protocol contribution to T03: Rule 7-style consequence testing prevented an automatic leap from “systematic controlled boundary defect” to “real EvalEval corpus is misclassified.”

## Validation Handbook contribution

The Validation Handbook constrained T03 as follows:

- P8 real-corpus step: after controlled calibration, test behavior in the operating distribution;
- U1: define a snapshot-bound claim;
- U4: derive/remove free parameters rather than tune tolerances post hoc;
- U8: verdict granularity cannot exceed Stage F classification granularity;
- U9: follow the dependency DAG from T01 to T02 to T03;
- U11: environment/harness failures are not EvalEval failures;
- U15: zero observed mismatches is a finite-snapshot result, not a universal guarantee;
- U17: use exact-decimal recomputation appropriate to the strict decimal threshold relation.

## Additional test catalog contribution

The additional catalog did not define T03 verbatim.

Relevant support:

- Test #17, Local Discriminability / Saturation: move from controlled boundary behavior into the real operating distribution;
- Test #18, Aggregation / Weight Robustness: threshold-dependent classifications can require robustness checks, but T03 did not test arbitrary weighting schemes.

## Why T03 was chosen over alternatives

- Another synthetic sweep was rejected because T02 had already generalized the controlled effect.
- Raw EEE JSON-only analysis was rejected because production comparability depends on identity resolution, taxonomy, hotfixes, slice handling, and Stage F grouping.
- Full Stage J / website materialization was deferred because Stage F already contains the claim-governing comparability booleans for this question.
- Any repair/tolerance modification was rejected because the audit measures the frozen implementation.

## Selection summary

Primary trigger: **T01 + T02 empirical results**.

Primary decision-rule support: **Falsification Protocol product/outcome consequence logic**.

Construction/scope rules: **Validation Handbook P8 and U1/U4/U8/U9/U11/U15/U17**.

Supporting analogues: **Additional test catalog #17 and secondarily #18**.
