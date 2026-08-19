# Pre-test candidate map

Purpose: record which methodological tests are currently eligible before choosing the first confirmatory EvalEval test.

This is not a checklist. Eligibility depends on a concrete claim and an admissible instrument.

| Candidate | Current status | Reason |
|---|---|---|
| Claim-estimand boundary | ELIGIBLE, EARLY | The public signal names are broader than their implementation details; scope must be mapped before interpretation. |
| Controlled signal calibration | ELIGIBLE, FIRST-CANDIDATE | The four signals are measurement instruments. Positive, negative, graded, and nuisance controls can establish discrimination and invariance before corpus-level interpretation. |
| Full-pipeline variance decomposition | ELIGIBLE, LATER | Relevant after deterministic structure and configurable stages are mapped; factors must come from the actual EvalEval pipeline. |
| Component/harness attribution | ELIGIBLE, LATER | Needed to separate EEE source data, resolver behavior, canonicalization, hotfix layers, signal logic, and audit harness effects. |
| Broken-task/environment gate | ACTIVE GOVERNANCE | Audit-harness, provider, filesystem, transport, or environment failures must not be attributed to EvalEval without evidence. |
| Local discriminability/saturation | ELIGIBLE, AFTER CONTROLLED CALIBRATION | Stronger real-corpus test of whether signals resolve nearby cases in the operating range. |
| Aggregation/weight robustness | CONDITIONAL | Run only where an actual aggregate, weight, threshold, or ranking claim depends on a free choice. |
| Measurement invariance/DIF | DEFERRED ADVANCED | Potential benchmark-family/source effects are relevant, but this requires a justified psychometric design and sufficient data. |
| Deployment transfer | NOT CURRENTLY CLAIM-GOVERNING | Evaluation Cards is primarily an evaluation-reporting pipeline; no broad deployment-performance claim is selected for the first audit branch. |
| Security, privacy, sandbagging, safeguard robustness | N/A FOR CURRENT CLAIM SET | No selected EvalEval claim requires these profiles. |

First-test selection remains provisional until baselines are verified. The final test package must contain its own `TEST_RATIONALE.md` and `PREREGISTRATION.md` frozen before execution.
