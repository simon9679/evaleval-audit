# Known-issues baseline

Purpose: separate EvalEval-authored or EvalEval-documented limitations from independent audit findings.

This directory is frozen before the first confirmatory audit test. A documented issue may motivate test design or define a baseline, but it must not be reported as an independently discovered defect.

The preparation script copies exact files from the already frozen backend repository at commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

Baseline source set:

1. `benchmark_known_issues.json`
2. `metric_meta_hotfix.py`
3. `resolution_hotfixes.py`
4. `hierarchy_hotfixes.py`

`KNOWN_ISSUES_MANIFEST.json` records source paths, commit, SHA-256 hashes, byte counts, and local frozen-copy paths.

This baseline is not a claim that the four files exhaust every limitation known to the EvalEval authors. It is the pre-test set explicitly inspected by this audit before confirmatory testing. Additional author-documented issues discovered later must be labeled as later-discovered baseline material, not audit discoveries.
