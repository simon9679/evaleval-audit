# Raw evidence

`preflight.py` writes:
- `preflight.json`

`analyze.py` writes:
- `warning_root_groups.jsonl`
- `mixed_unit_groups.jsonl`
- `classification_sensitive_paths.jsonl`
- `integrity_errors.jsonl`

All JSON output is ASCII-escaped and deterministic in key ordering.
