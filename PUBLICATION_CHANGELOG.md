# Publication Wrapper Changelog

## 2026-08-19 — compact review bundle -> publication-ready wrapper

Source review ZIP SHA-256:

`67a05ea5417e21fcaa8ab2e1b755fdfec4699ae7821ab9d16c83022379659b09`

Publication-layer changes only:

- preserved the original freeze-stage root README as `history/README_FREEZE_STAGE.md`;
- replaced root `README.md` with current T01-T17 status and bounded findings;
- added `CLAIM_INDEX.json` to trace each canonical verdict to its preregistered claim/decision predicate and preregistration hash;
- added `AUDIT_STATUS.md`, `REPRODUCTION.md`, and `METHOD_SOURCES.md`;
- clarified `REVIEW_GUIDE.md` and `AI_REVIEW_PROMPT.txt`;
- added `method/README.md` to mark the old T01-T02 method history as historical;
- added `tools/README.md` and `tools/verify_public_bundle.py` for the current compact bundle.

No file under `tests/T01_*` through `tests/T17_*` was modified. No frozen preregistration, raw result, canonical result, post-run analysis, or test code was changed.
- added `PUBLISH.ps1` as a local verification-and-push helper for the prepared public repository.
