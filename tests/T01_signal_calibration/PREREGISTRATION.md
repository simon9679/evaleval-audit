# PREREGISTRATION — T01 Controlled Signal Calibration

Status: registered before any T01 execution.

## Frozen object

Backend repository commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

Required prior audit gates:

- freeze verification: `bad=0`, `missing=0`;
- baseline verification: `bad=0`.

## Primary hypothesis

H1:

The tested signal primitives will satisfy all mandatory controlled discrimination and nuisance-invariance cases.

Competing prediction H0:

At least one mandatory case will contradict the frozen operational rule or expected invariance.

## Case families and preregistered expectations

### R — reproducibility

R1 non-agentic, temperature and max_tokens populated:
- required fields = [`temperature`, `max_tokens`];
- missing = [];
- gap = false.

R2 non-agentic, temperature missing:
- missing = [`temperature`];
- gap = true.

R3 non-agentic, max_tokens missing:
- missing = [`max_tokens`];
- gap = true.

R4 agentic, all four active fields populated:
- required fields = [`temperature`, `max_tokens`, `eval_plan`, `eval_limits`];
- missing = [];
- gap = false.

R5 agentic, eval_plan missing:
- missing contains only `eval_plan`;
- gap = true.

R6 nuisance top_p and prompt_template changes:
- active required-field set and missing-field result unchanged.

### C — completeness

The frozen registry is the reference authority for the operationalised field set.

C1 fully populated declared record:
- score = 1.0.

C2 empty record:
- score = 0.0 unless the frozen registry itself contains a field whose declared scoring semantics make an empty record non-zero; if so, the case is ERROR because the preregistered fixture model is incompatible with the frozen registry.

C3 remove one full declared field:
- score decreases by exactly `1 / N`, where `N` is the number of declared top-level completeness fields.

C4 remove one subitem from one partial field with `k` subitems:
- score decreases by exactly `1 / (N * k)`.

C5 add an undeclared nuisance field:
- score unchanged.

If the frozen registry contains no full field or no partial field suitable for the mutation, the corresponding case is INCONCLUSIVE, not silently replaced post-run.

### P — provenance

P1 one first-party organisation:
- distinct_reporting_orgs = 1;
- is_multi_source = false;
- first_party_only = true.

P2 one third-party organisation:
- distinct_reporting_orgs = 1;
- is_multi_source = false;
- first_party_only = false.

P3 two distinct organisations:
- distinct_reporting_orgs = 2;
- is_multi_source = true;
- first_party_only = false for every row.

P4 organisation case / ASCII-whitespace nuisance:
- `Example Org` and `  example   org  ` collapse to one normalised organisation.

P5 source type `other`:
- Stage E provenance source type collapses to `unspecified`.

Provenance limitation:
T01 uses a source-anchored independent implementation of the frozen Stage E/F.1 formula. It does not count as an end-to-end execution of Stage F.1.

### V — comparability variant divergence

Frozen threshold basis for `metric_unit=proportion`:
- threshold = 0.05 at threshold factor 1.0.

V1 setup differs, score divergence = 0.04:
- applicable;
- has_variant_divergence = false.

V2 setup differs, score divergence = 0.05:
- applicable;
- has_variant_divergence = false because the production rule is strict `>`.

V3 setup differs, score divergence = 0.050001:
- applicable;
- has_variant_divergence = true.

V4 score differs but only an undeclared generation-argument key differs:
- no declared setup difference;
- result = N/A (`None`).

V5 prompt-template cosmetic whitespace only:
- no declared setup difference after normalisation.

### X — comparability cross-party divergence

X1 one named organisation:
- result = N/A (`None`).

X2 two named organisations with medians separated by 0.06:
- applicable;
- organization_count = 2;
- has_cross_party_divergence = true.

X3 organisation names differing only by case / whitespace:
- collapse to one organisation;
- result = N/A (`None`).

## Decision rule

Mandatory cases are all R, P, V, X cases plus applicable C cases.

Outcome:

- `CONFIRMED` — every mandatory executable case passes and no case is ERROR.
- `REFUTED` — at least one mandatory executable case produces a value contrary to its preregistered expectation.
- `INCONCLUSIVE` — no mandatory executable case fails, but one or more claim-governing cases cannot be instantiated from the frozen registry.
- `ERROR` — environment, import, source-integrity, or harness execution failure prevents valid measurement.

No global EvalEval PASS/FAIL is permitted from this test.

## Numeric comparison rule

Floating-point comparisons use absolute tolerance `1e-12` only where exact rational operations are represented in binary floating point.

No post-run threshold tuning is permitted.

## Raw evidence rule

All individual cases must be written before the summary is computed.

The summary must contain counts but must not replace raw case evidence.
