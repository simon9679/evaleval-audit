# TEST_RATIONALE — T01 Controlled Signal Calibration

Status: frozen before execution.

## Claim being tested

Narrow claim:

> The frozen EvalEval signal implementations discriminate controlled changes that are explicitly relevant to their operational definitions, and remain invariant to selected changes that are explicitly outside those operational definitions.

This is an instrument-calibration claim. It is not a claim that the four public signal names are fully valid measurements of the broader real-world constructs.

Signal families covered:

1. reproducibility;
2. completeness;
3. provenance;
4. comparability.

## Why this claim was selected

Evaluation Cards exposes these four signals as interpretive measurements. Any later corpus-level statement based on them depends on the signals having basic discrimination and invariance properties.

A full-corpus analysis before this calibration would risk measuring the behaviour of an unvalidated instrument.

## Why this test is first

Protocol ordering:

- instrument/data validity precedes interpretation of comparative or product-level results;
- reproducibility of the audit object has already been established by the clean frozen snapshot verification;
- known author-documented issues and public claims have already been frozen as baselines.

Validation Handbook constraints:

- a positive result must have a defined capacity to fail;
- controlled mutations must target a declared construct;
- nuisance mutations must test invariance;
- free parameters must be derived, swept, or removed;
- verdict granularity must not exceed measurement granularity;
- a clean run is only a finite-power statement.

Additional evaluation-profile guidance:

- local discriminability should be tested before using an evaluation instrument to separate nearby real systems;
- this T01 is the controlled precursor to that later real-corpus test.

## Why this instrument is appropriate

The test executes the frozen Python signal primitives directly for reproducibility, completeness, and comparability.

Provenance is implemented as SQL inside canonicalisation rather than as a standalone Python signal module. T01 therefore calibrates the Stage E/F.1 provenance formula on controlled fixtures using a source-anchored independent implementation. A later full-pipeline test must verify the same behaviour through the actual canonicalisation stage.

This split is deliberate and recorded before the run.

## Controls and mutations

### Reproducibility

Relevant mutations:

- remove `temperature`;
- remove `max_tokens`;
- for agentic evaluations, remove `eval_plan`;
- for agentic evaluations, remove `eval_limits`.

Nuisance mutations for the active production rule:

- vary `top_p`;
- vary `prompt_template`.

Expected property:

- missing active required fields must increase the missing-field set;
- nuisance changes must not change the active required-field set.

### Completeness

Relevant mutations:

- remove one registry-declared full field;
- remove one subitem from a registry-declared partial field;
- compare fully populated versus empty records.

Nuisance mutation:

- add an undeclared extra field.

Expected property:

- declared-field removal must reduce score by the registry-defined amount;
- undeclared fields must not change the score.

### Provenance

Relevant mutations:

- one reporting organisation versus two distinct organisations;
- first-party versus third-party source type.

Nuisance mutation:

- casing and ASCII-whitespace changes in organisation names.

Expected property:

- normalised aliases of the same organisation must remain one reporting organisation;
- two distinct organisations must produce multi-source coverage;
- first-party-only must require first-party source type and exactly one reporting organisation.

### Comparability

Relevant mutations:

- score divergence below, at, and just above the frozen threshold;
- setup variation on a declared comparison field;
- one versus two reporting organisations.

Nuisance mutations:

- changes to undeclared generation-argument keys;
- cosmetic whitespace differences in normalised prompt templates.

Expected property:

- the threshold boundary must behave exactly as declared (`divergence > threshold`);
- nuisance changes must not create a setup difference;
- one reporting organisation must make cross-party divergence not applicable.

## Alternative candidate tests considered

1. Full-corpus signal distribution analysis.
   Deferred because it would interpret the instrument before controlled calibration.

2. Full-pipeline reproducibility.
   Deferred to the next dependency branch because the audit object itself is already frozen and verified; T01 first checks signal discrimination.

3. Local discriminability / saturation on real corpus groups.
   Deferred until after T01 because it is a stronger operating-range test that assumes the primitive signal behaviour is understood.

4. Aggregation / weight robustness.
   Deferred until a claim-governing aggregation, threshold, or weighting choice is identified.

5. Security, privacy, sandbagging, and safeguard tests.
   Not applicable to the selected claim.

## How the test is constructed

The harness imports signal code only from the already frozen backend repository at:

`freeze/repos/eval_cards_backend_pipeline`

Required backend commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

No network access is required.

The harness writes every case, expected value, actual value, and pass/fail comparison to `raw/cases.jsonl`, then derives `results/summary.json` from those raw case records.

## What the test can confirm or refute

It can confirm or refute the narrow controlled-fixture discrimination and invariance claim for the tested primitives and boundaries.

## What the test does not permit

A passing T01 does not establish:

- real-world construct validity;
- corpus-level accuracy;
- absence of long-tail failures;
- public-claim scope validity;
- full-pipeline provenance correctness;
- cross-platform reproducibility;
- ranking validity;
- product superiority.

Those require later tests.
