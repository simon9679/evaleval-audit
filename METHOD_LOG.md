# Method log

## M-001 - Windows materialization failure on a trailing-dot path component

Date: 2026-08-18
Stage: object freeze, before confirmatory testing
Classification: audit-method/setup portability issue; not a confirmatory EvalEval finding

Observed behavior:
- `huggingface_hub.snapshot_download(..., local_dir=..., max_workers=1)` repeatedly reached the EEE datastore and failed while creating a Hugging Face metadata lock file.
- Shortening the audit root with `R:` and then mapping the dataset root to `S:` did not fix the failure.
- The failing repository path contains the directory component `gpt-3.5-turbo-0125_claude-3-sonnet-2024022...`, which ends in dots.
- Windows long-path support was already enabled (`LongPathsEnabled=1`).
- Python 3.12.10 successfully created and removed a 398-character test path, ruling out path length as the immediate cause.
- Python successfully preserved a directory named `name...` when the Windows extended-path namespace (`\\?\`) was used.
- `huggingface_hub.hf_hub_download` then successfully downloaded the exact previously failing EEE file when `local_dir` used the `\\?\` prefix.
- Existing downloaded EEE content (approximately 6.52 GB at the time of diagnosis) was preserved throughout.

Method implication:
- A byte-faithful local freeze can encounter platform-specific filename semantics even when ordinary long-path support is enabled.
- Transport/cache behavior must be separated from the scientific object being frozen.
- A freeze procedure should not silently rename repository paths merely to make a platform accept them; doing so would alter the frozen object.

Mitigation adopted:
- Keep the canonical physical audit directory unchanged.
- On Windows, pass Hugging Face dataset destinations through the `\\?\` extended-path namespace so trailing-dot components are preserved exactly.
- Use the same extended-path namespace for recursive SHA-256 hashing and verification.
- Exclude `.cache/huggingface` transport metadata from the scientific freeze hash set. Dataset files themselves remain included.
- Keep all immutable repository and dataset revisions unchanged.

Scientific interpretation:
- No correctness, quality, or reliability conclusion about EvalEval is permitted from this setup failure.
- The event is retained as evidence for the parallel audit of the falsification/validation workflow itself, specifically cross-platform freeze cost and portability.
