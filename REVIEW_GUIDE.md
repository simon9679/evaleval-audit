# Public Review Guide

This repository is a compact review/publication copy of the EvalEval audit.

## Sources of truth

- `CLAIM_INDEX.json`: the preregistered claim or primary decision predicate for each test, plus preregistration hash.
- `TEST_INDEX.json`: the canonical final verdict and canonical summary hash for each test.
- `tests/<test>/results/summary.json`: canonical machine-readable result for that test.
- `tests/<test>/PREREGISTRATION.md`: frozen claim and competing predictions. Where the explicit verdict mapping is split across frozen artifacts, read it together with that test's `TEST_RATIONALE.md` and analyzer.
- `tests/<test>/results/RESULT_ANALYSIS.md`: bounded post-run interpretation.

There are 17 completed tests: **12 CONFIRMED / 5 REFUTED / 0 INCONCLUSIVE / 0 ERROR**.

A REFUTED verdict means the preregistered claim of that test was refuted. A CONFIRMED verdict means the preregistered claim/prediction satisfied its registered rule. Neither status is a project-wide grade.

## Recommended review order

1. `AUDIT_STATUS.md`
2. `CLAIM_INDEX.json`
3. `TEST_INDEX.json`
4. the selected test's `PREREGISTRATION.md`
5. its canonical `results/summary.json`
6. its `results/RESULT_ANALYSIS.md`
7. `TEST_RATIONALE.md` and `SOURCE_ATTRIBUTION.md` for method provenance
8. raw evidence and analyzer code when challenging a numerical result

## Mechanical checks

Run:

```bash
python tools/verify_public_bundle.py
```

Each test also has `verify_prereg.py`. Those scripts check preregistration/artifact immutability against frozen hashes. They do **not** prove that a final verdict follows from the data; that requires inspecting the analyzer, the frozen decision rule, and the evidence it consumes. A full scientific re-execution of some tests requires the omitted full freeze; see `REPRODUCTION.md`.

## Safe analyzer re-execution

Do not run test analyzers directly in the canonical publication checkout unless you intend to modify that checkout.

Some analyzers write generated evidence or summaries into their own `raw/` and `results/` directories. Re-execution should therefore use a disposable copy or separate worktree, with the full frozen dependencies restored when the selected test requires them.

The compact bundle's supported in-place mechanical check is:

```bash
python tools/verify_public_bundle.py
```

See `REPRODUCTION.md` for the boundary between compact-bundle verification and full from-source re-execution.

## T14 special case

T14 preserves a harness-repair history:

1. initial run: ERROR
2. HARNESS_FIX_01: INCONCLUSIVE
3. HARNESS_FIX_02: INCONCLUSIVE
4. HARNESS_FIX_03: INCONCLUSIVE
5. HARNESS_FIX_04: CONFIRMED

The accepted final result is HARNESS_FIX_04. Canonical `results/summary.json` is byte-identical to `summary_fix4.json`. The original ERROR remains as `summary_initial_error.json`.

Review the repair notes before judging whether any fix changed the preregistered scientific rule. Earlier statuses are provenance, not competing final verdicts.

## Compact freeze scope

The original full freeze is omitted from this repository because it is approximately 18 GB. The publication includes freeze metadata, verification output, and the full SHA-256 list. See `REPRODUCTION.md`.

Some raw evidence files preserve absolute local Windows paths. They are intentional execution-provenance strings and remain unchanged to preserve existing hashes/manifests.

The two terminal transcripts listed in `PUBLIC_REVIEW_MANIFEST.json` are intentionally excluded because they contain local-path and/or Cyrillic terminal output.

## About `AI_REVIEW_PROMPT.txt`

`AI_REVIEW_PROMPT.txt` is an **author-authored review checklist**, not independent evidence and not a neutral third-party questionnaire. It is provided only to make automated reviewers check the same traceability and overclaiming risks. Reviewers should ignore any instruction in it that conflicts with the evidence.

## Review discipline

Separate four categories:

1. audited-object finding;
2. audit-harness or environment finding;
3. publication/packaging issue;
4. unsupported or overly broad interpretation.

For every criticism, cite exact file paths and concrete values/text. Do not infer a project-wide conclusion from a narrow test unless the dependency chain and measured granularity support it.
