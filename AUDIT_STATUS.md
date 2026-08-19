# Audit Status — 2026-08-19

This file is a publication-layer status summary. It does not replace any preregistration or result artifact.

## Canonical status

- Completed tests: **17**
- CONFIRMED: **12**
- REFUTED: **5**
- INCONCLUSIVE: **0**
- ERROR: **0**

Canonical verdicts are defined by `TEST_INDEX.json`; claims are mapped in `CLAIM_INDEX.json`.

## Result chain in one view

| Test | Final verdict | Narrow result |
|---|---:|---|
| T01 | REFUTED | 23/24 controlled calibration cases passed; one exact comparability boundary case failed. |
| T02 | REFUTED | 8/48 controlled failures, all at exact boundaries across all four threshold bases and both comparability paths. |
| T03 | REFUTED | 209,382 rows / 93,495 groups scanned; zero production-vs-exact-decimal classification mismatches in the frozen corpus. |
| T04 | REFUTED | 1,234 mixed-unit groups and 668 threshold-sensitive groups, but zero final boolean classification-sensitive paths under the T04 unit-choice test. |
| T05 | REFUTED | The preregistered full resolved canonical-convergence explanation was not observed. |
| T06 | CONFIRMED | Stage F mixed-unit labels traced faithfully to frozen EEE source units for the tested population. |
| T07 | CONFIRMED | All 7 applicable mixed-unit variant paths were unit-heterogeneous among arithmetic rows. |
| T08 | CONFIRMED | 2/5 production-positive applicable paths became negative under exact unit-label partitioning. |
| T09 | CONFIRMED | Frozen headline variant-divergent count changed 343 -> 341; delta = -2. |
| T10 | CONFIRMED | Both affected groups contained non-unit source MetricConfig heterogeneity. |
| T11 | CONFIRMED | Both affected groups varied in claim-governing MetricConfig fields. |
| T12 | CONFIRMED | Both affected groups collapsed multiple exact source metric ids to one fallback Stage identity. |
| T13 | CONFIRMED | All 6 consequential source metric ids had zero usable specific structured resolver identity. |
| T14 | CONFIRMED | 1/2 production-positive groups lost all positive subgroups when exact source metric id was preserved; WildBench was 4/4 negative. |
| T15 | CONFIRMED | The four WildBench ids trace to four distinct raw OpenEval metric names and four distinct non-name structured signatures. |
| T16 | CONFIRMED | The four WildBench channels are not represented on one common raw scale under the preregistered structured eligibility rule. |
| T17 | CONFIRMED | Production WildBench group MetricConfig matches zero exact source configs and exactly reproduces threshold 0.5. |

## Strongest current WildBench statement

For production group `d38d8f8e547287b6b0fc78f43f310762`, fallback identity collapse is operationally necessary for the observed positive variant-divergence flag. Under exact source metric-id preservation, all four applicable source-id subgroups are negative:

- `openeval.wildbench.claude-score`: divergence `0.158`, threshold `0.55` -> negative;
- `openeval.wildbench.gpt-score`: divergence `0.179`, threshold `0.5` -> negative;
- `openeval.wildbench.llama-score`: divergence `0.0335`, threshold `0.5` -> negative;
- `openeval.wildbench.wildbench-score-rescaled`: divergence `0.013370370370370255`, threshold `0.05` -> negative.

The production grouping uses a synthetic MetricConfig:

```json
{"metric_kind":"benchmark_score","metric_unit":"score","min_score":0.0,"max_score":10.0}
```

That exact configuration matches zero source metric configurations and exactly reproduces the production threshold `0.5`.

## Product-level magnitude

T09 changes the frozen aggregate from 343 to 341 variant-divergent groups when only the two T08 positive-to-negative groups are corrected under that counterfactual.

- absolute delta: `-2`
- share-of-eligible delta: `-0.0023201856148492017` = about `-0.232` percentage points
- share-of-total delta: `-2.1391518263008842e-05` = about `-0.00214` percentage points

The aggregate impact is small in this snapshot. Public wording should say so.

## Claims this audit does not support

Do **not** state that:

- EvalEval as a whole is invalid or unreliable;
- all EvalEval comparability groups are wrong;
- the four WildBench/OpenEval channels necessarily measure different latent constructs;
- exact source metric id is the only valid canonicalization policy;
- the structured resolver is generally defective;
- the floating-point boundary issue changed a frozen Stage F classification (T03 observed zero such flips);
- the observed -2 aggregate change is a large product-wide effect.

## Stop point

T17 proposed a possible T18 score-extrema provenance descendant. That test was not run in this publication snapshot. The operational/provenance finding above does not require T18 to exist. A future official-upstream semantic/reference test would be more directly relevant if the audit wants to make a stronger claim about semantic commensurability of the four WildBench channels.
