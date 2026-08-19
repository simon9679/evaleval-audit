# T03 — Frozen-Corpus Comparability Boundary Impact

T03 follows the exact-boundary comparability defect identified by T01 and generalized by T02.

Run order:

1. `python tests\T03_corpus_boundary_impact\preflight.py`
2. `python tests\T03_corpus_boundary_impact\verify_prereg.py`
3. `python tests\T03_corpus_boundary_impact\run_pipeline.py`
4. `python tests\T03_corpus_boundary_impact\analyze.py`

Recommended PowerShell evidence capture for the expensive Stage A-F run:

`python .\tests\T03_corpus_boundary_impact\run_pipeline.py 2>&1 | Tee-Object .\tests\T03_corpus_boundary_impact\raw\pipeline_transcript.txt`

The pipeline harness:

- uses only frozen local sources;
- forbids network fallback;
- disables refresh;
- runs the frozen production pipeline through Stage F;
- disables normal stage caches to avoid duplicating large intermediate tables;
- captures only the Stage F `fact_results` table required by T03.

T03 does not build the Stage J public view layer.

If `preflight.py` fails, do not run the pipeline. Preserve and report the preflight output.

If `run_pipeline.py` fails, preserve the transcript. The failure is an audit environment/harness outcome unless evidence attributes it to the frozen target.
