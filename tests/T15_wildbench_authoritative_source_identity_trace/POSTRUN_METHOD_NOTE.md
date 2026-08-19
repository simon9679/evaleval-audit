# POSTRUN_METHOD_NOTE — T15

Status: final post-run meta-audit note.

## Harness issue

The original T15 package omitted empty `raw/` and `results/` directories from
the ZIP archive.

The original preflight therefore failed before any substantive T15 result was
produced.

Harness Fix 1 created only the runtime output directories and then executed the
unchanged frozen preflight/analyzer.

This is an audit-package defect, not an EvalEval defect.

## Methodological value

T15 illustrates a useful provenance sequence:

1. establish a downstream operational consequence;
2. trace exact source identity;
3. exclude the trivial alias explanation;
4. only then adjudicate semantic or scale eligibility.

This avoids treating different names as sufficient evidence of different
metrics while also avoiding the opposite error of treating one downstream
canonical id as proof of source homogeneity.
