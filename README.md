# EvalEval Technical Audit

This repository contains a frozen, claim-scoped technical audit of EvalEval's Evaluation Cards pipeline and related public artifacts.

The audit does **not** assign EvalEval a project-wide PASS or FAIL grade. Every verdict belongs to a preregistered test claim at a stated measurement granularity.

## Current status

- Frozen object date: **2026-08-19**
- Completed confirmatory tests: **17**
- Final canonical verdicts: **12 CONFIRMED / 5 REFUTED / 0 INCONCLUSIVE / 0 ERROR**
- Canonical machine-readable test map: [`TEST_INDEX.json`](TEST_INDEX.json)
- Claim-to-verdict traceability: [`CLAIM_INDEX.json`](CLAIM_INDEX.json)
- Current scope and strongest supported findings: [`AUDIT_STATUS.md`](AUDIT_STATUS.md)
- Review instructions: [`REVIEW_GUIDE.md`](REVIEW_GUIDE.md)

`CONFIRMED` and `REFUTED` are claim-level outcomes. They are not project-level endorsements or grades.

## Strongest supported finding

The strongest completed branch concerns EvalEval's comparability grouping for one WildBench/OpenEval production group.

The completed chain shows that:

1. the production group collapses four exact source metric identities into one fallback production identity;
2. preserving exact source metric identity makes all four applicable WildBench source-id subgroups negative for variant divergence;
3. the frozen structured source representation exposes multiple units and scale signatures and no explicit structured common-scale transform under the preregistered eligibility rule; and
4. Stage F constructs a field-wise group MetricConfig that matches **zero** exact source metric configurations while exactly reproducing the production threshold of **0.5**.

The supported conclusion is operational and provenance-scoped. The audit does **not** claim that all four channels necessarily measure different latent constructs, that exact source-id preservation is the only valid repair, or that EvalEval comparability is generally invalid.

## Observed product-level magnitude

The affected mixed-unit branch changes the frozen headline variant-divergence count from **343 to 341** under the preregistered two-group counterfactual (`T09`). The absolute aggregate effect in this snapshot is therefore small: **-2 groups**, or about **-0.232 percentage points among variant-eligible groups**.

That small aggregate magnitude does not erase the correctness/provenance finding for the specific claim-governing WildBench group, but it constrains how broadly the result should be described.

## Other important result

`T01` and `T02` confirm controlled exact-boundary binary floating-point sensitivity in comparability arithmetic. `T03` then scans the full frozen Stage F population and finds **zero** real-corpus classification flips from that particular boundary mechanism. The controlled defect therefore must not be presented as a frozen-corpus impact finding.

## Frozen object

The audit pinned the following repositories:

- `evaleval/eval_cards_backend_pipeline` — `9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`
- `evaleval/eval-card-registry` — `6fb026d7483467f063da465c15a76733b3d25f4c`
- `evaleval/every_eval_ever` — `9bce4136e789ec006c62582f5f9d107d20f8b398`

The original full freeze verified **68,126 files** with `bad=0` and `missing=0`. See [`freeze/VERIFY_FREEZE.txt`](freeze/VERIFY_FREEZE.txt) and [`freeze/SHA256SUMS.txt`](freeze/SHA256SUMS.txt).

The compact public repository does **not** include the full multi-gigabyte frozen corpus. It includes the compact evidence artifacts needed to inspect the completed claims plus freeze hashes/metadata. See [`REPRODUCTION.md`](REPRODUCTION.md).

## How to review

Start here:

1. [`AUDIT_STATUS.md`](AUDIT_STATUS.md)
2. [`CLAIM_INDEX.json`](CLAIM_INDEX.json)
3. [`TEST_INDEX.json`](TEST_INDEX.json)
4. the relevant test's `PREREGISTRATION.md`
5. its canonical `results/summary.json`
6. its `results/RESULT_ANALYSIS.md`

For a mechanical integrity check of this compact publication bundle, run:

```bash
python tools/verify_public_bundle.py
```

Each test also contains `verify_prereg.py`. Those scripts verify the immutability/hash integrity of preregistered test artifacts; they do **not** independently recompute the scientific verdict.

## T14 harness-repair history

T14 preserves the full technical repair sequence:

`ERROR -> INCONCLUSIVE -> INCONCLUSIVE -> INCONCLUSIVE -> CONFIRMED`

The accepted result is `HARNESS_FIX_04`; canonical `results/summary.json` is byte-identical to `summary_fix4.json`. Earlier attempts remain as provenance and are not competing final verdicts.

## Method provenance

Test selection and construction used two methodological sources:

- the [Falsification Protocol](https://github.com/simon9679/tbg-postmortem/blob/main/FALSIFICATION_PROTOCOL.md), used as a dependency/decision procedure rather than as a literal test checklist;
- a literature-grounded Validation Handbook used during test construction.

The Handbook itself is **not included in this publication snapshot** because its bibliography and venue/source classifications still require an independent source audit before public release. Test-level method provenance is recorded in each `TEST_RATIONALE.md` and `SOURCE_ATTRIBUTION.md`.

## Historical files

Some root and method artifacts intentionally preserve earlier audit stages. In particular, [`PREREGISTRATION.md`](PREREGISTRATION.md) is the original freeze-only initial preregistration, and `method/COMPLETED_TESTS_RATIONALE.md` is a historical snapshot that stops before later tests. They are evidence of chronology, not current status documents.

The original freeze-stage README is preserved at [`history/README_FREEZE_STAGE.md`](history/README_FREEZE_STAGE.md).

## Publication notes

Some raw JSON captures preserve absolute local Windows paths from the execution environment. They are retained unchanged because they are provenance-bearing raw artifacts and are covered by existing hashes/manifests. They are not credentials. The two local terminal transcripts that contained local-path/Cyrillic output were excluded from the compact public bundle and are listed in `PUBLIC_REVIEW_MANIFEST.json`.

No scientific preregistration, raw result, canonical result, or post-run test analysis was rewritten for this publication wrapper.
