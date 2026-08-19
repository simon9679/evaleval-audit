# Public-claims freeze

Purpose: freeze mutable public wording before confirmatory EvalEval tests.

The raw HTML responses are evidence objects. `CLAIMS_MANIFEST.json` records fetch time, requested URL, final URL, HTTP metadata where available, byte count, and SHA-256.

The public pages are not treated as immutable source code. Claims tied to dated snapshots must be evaluated against the corresponding dated data snapshot when possible. Live-site values must not be silently compared with a different historical corpus.

Primary claim families to preserve:

- Evaluation Cards computes four interpretive signals: reproducibility, completeness, provenance, and comparability.
- Reproducibility is presented as whether an evaluation can be independently re-run from recorded setup information.
- Completeness concerns whether benchmark documentation is sufficient to interpret a score.
- Provenance concerns who reported a score and whether it has corroboration or reproduction across reporting parties.
- Comparability concerns whether scores grouped together correspond to the same measurement target and sufficiently comparable setups.
- Evaluation Cards composes run data, benchmark metadata, and model metadata into a canonical evaluation record.
- Corpus-level percentages and counts are time-dependent descriptive claims and must retain their stated snapshot date.

No confirmatory verdict is assigned in this directory.
