# T01 Result Analysis — Controlled Signal Calibration

Status: post-run analysis. This file describes the completed test and does not alter the frozen preregistration or verdict rules.

## Result

Verdict: **REFUTED** for the narrow preregistered controlled-calibration claim.

Raw result counts:

- total cases: 24
- PASS: 23
- FAIL: 1
- INCONCLUSIVE: 0
- reproducibility: 6 / 6 PASS
- completeness: 5 / 5 PASS
- provenance: 5 / 5 PASS
- comparability: 7 / 8 PASS, 1 / 8 FAIL

## Failed case

The only failed preregistered case was comparability case V2 at the nominal exact threshold.

Inputs included scores `0.5` and `0.55`, with a declared threshold of `0.05` and a strict production rule `divergence > threshold`.

Production binary floating-point subtraction produced:

`0.55 - 0.5 = 0.050000000000000044`

Therefore the production comparison evaluated the pair as divergent even though the intended exact decimal difference is exactly `0.05` and should be non-divergent under a strict `>` rule.

A post-hoc diagnostic reproduced the representation sensitivity around the same boundary. That diagnostic is supporting attribution evidence, not an additional confirmatory test.

## Interpretation

T01 refutes only the claim that all tested controlled cases respect the declared discrimination/invariance behavior. It identifies one comparability boundary failure while the tested reproducibility, completeness, provenance, and the other comparability controls passed.

The result does **not** establish that EvalEval comparability is generally invalid, that public aggregate counts are wrong, or that any real corpus group is affected.

## Attribution

The failure is attributable to binary floating-point boundary behavior in the frozen production comparability arithmetic for the tested fixture. No evidence from T01 attributes the failure to source-data corruption, the audit harness, or the environment.

## Decision consequence

Because the failure occurred at a claim-governing threshold, the next test had to determine whether the effect was isolated to one decimal pair or systematic across mathematically equivalent threshold cases. This directly motivated T02.
