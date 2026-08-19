# Freeze fix 5

This patch replaces the failed Windows path workarounds with a byte-faithful extended-path strategy.

Changes:
- `scripts/00_freeze.ps1` automatically prefixes Hugging Face `local_dir` values with the Windows `\\?\` namespace.
- Existing downloaded files remain in the same physical directories and are reused.
- Frozen-content SHA-256 generation now uses Python extended-path traversal so trailing-dot directory names remain addressable.
- Hugging Face `.cache` transport metadata is excluded from scientific object hashes.
- `scripts/01_verify_freeze.ps1` now verifies hashes through the same extended-path mechanism.
- `METHOD_LOG.md` corrects the earlier path-length diagnosis and records the actual trailing-dot materialization issue and the successful single-file control.

No EvalEval scientific finding is claimed by this patch.
