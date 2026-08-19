# TEST_RATIONALE — T03 Frozen-Corpus Comparability Boundary Impact

Status: frozen before execution.

## Claim being tested

Narrow claim:

> The exact-threshold floating-point sensitivity confirmed by T01 and T02 changes at least one comparability classification in the full frozen EvalEval corpus used by this audit.

The claim is snapshot-bound. It is not a claim that every EvalEval snapshot or every comparability result is affected.

## Why this claim was selected

T01 found one preregistered exact-boundary failure in comparability.

T02 then generalized that failure:

- 48 total controlled cases;
- 40 pass;
- 8 fail;
- all 8 failures were exact-boundary cases;
- zero below-threshold failures;
- zero above-threshold failures;
- all four threshold bases were affected;
- both variant and cross-party paths were affected.

The remaining claim-governing uncertainty is practical prevalence: whether the defect appears in real frozen corpus groups rather than only synthetic controls.

## Why this test is run now

This is the cheapest next test that can change the interpretation of the T01/T02 finding.

If no real frozen group changes classification, the defect remains a real but laboratory-bound boundary defect for this snapshot.

If at least one real group changes classification, the defect becomes corpus-relevant and requires source-level trace verification before a public product-level claim.

No unrelated defect search is performed in T03.

## Protocol and Handbook basis

Protocol:

- validate the instrument before interpreting corpus-level effects;
- follow a falsified dependency branch before opening unrelated branches;
- test the product-level consequence after mechanism-level failure is established;
- preserve attribution between target, audit harness, and environment.

Validation Handbook:

- claim scope must match the measured estimand and population;
- verdict granularity must not exceed measurement granularity;
- free parameters must be derived, swept, or removed;
- ERROR is distinct from INCONCLUSIVE;
- a clean run is a bounded statement, not universal validation.

Additional evaluation-profile guidance:

- local discriminability and threshold behavior should be checked in the operating distribution;
- aggregation/threshold sensitivity is claim-governing when classification depends on a fixed boundary.

## Production object and execution path

Frozen backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

T03 runs the frozen production stages A through F on the full frozen local inputs:

- EEE datastore;
- entity registry data;
- auto-benchmarkcards;
- frozen registry taxonomy seed.

Stage F is the first stage that has the production group-level comparability outputs required by this test.

The audit harness disables network fallback and source refresh. The production source loaders must reuse the already frozen local files or fail.

The harness uses the production orchestrator and production stage functions. It changes only evidence capture: after Stage F completes, it copies the resulting `fact_results` table to a Parquet evidence file. It does not modify signal computation.

## Reference comparison

Production uses binary floating-point score arithmetic and a strict `>` threshold comparison.

The T03 reference recomputes group divergence from the stored production scores using `Decimal(str(score))` and re-derives the declared threshold basis in exact decimal arithmetic.

This is a deliberately narrow oracle for the boundary defect identified by T02.

For cross-party divergence, the reference reproduces the production organisation normalization and median aggregation, but computes medians and final divergence in exact decimal arithmetic.

## Why the Decimal reference is admissible

The defect under test is specifically whether binary floating-point representation changes a strict threshold decision.

The declared threshold rules are decimal-valued rules (0.05, 5.0, or 5% of a declared range). Exact decimal arithmetic is therefore an independent representation-level reference for the boundary relation.

However, `Decimal(str(score))` operates on the canonical stored score value, not the original JSON lexical token. Any real-corpus mismatch found in T03 must be traced back to the frozen source record before it is reported as a final product finding.

## Controls

T03 records:

- all Stage F comparability groups;
- all production-applicable variant groups;
- all production-applicable cross-party groups;
- production divergent counts;
- exact-decimal divergent counts;
- all classification mismatches;
- exact-boundary mismatches;
- mismatch direction;
- threshold basis;
- group identifiers;
- source-record pointers where available.

No sampling is used.

## Alternatives considered

1. Another synthetic boundary sweep.
   Rejected because T02 already established cross-basis and cross-path generality.

2. Search raw EEE JSON without canonicalisation.
   Rejected because comparability grouping depends on identity resolution, slice handling, metric metadata, hotfixes, and production grouping logic.

3. Run the full Stage J website/view layer.
   Deferred because Stage F already contains the claim-governing comparability classifications. Building later stages would add cost without changing the T03 estimand.

4. Introduce an epsilon or tolerance repair.
   Rejected. T03 measures the frozen implementation; it does not patch it.

## What T03 can establish

T03 can establish whether the identified boundary defect changes at least one Stage F comparability classification in this full frozen corpus snapshot.

## What T03 cannot establish

T03 cannot by itself establish:

- that a changed classification is visible on the public website;
- that the original source JSON lexical score confirms the decimal interpretation;
- severity across other snapshots;
- general comparability construct validity;
- correctness of unrelated EvalEval signals.

Those require later trace or product-surface tests if T03 finds affected groups.
