# Method Reference Errata

This file records publication-layer method-reference issues discovered after
the audit artifacts had been frozen.

It does not modify any preregistration, analyzer, raw result, canonical result,
or post-run analysis.

## E1 — unresolved `U17` references

Several frozen audit artifacts cite a Validation Handbook rule labelled `U17`,
usually described as requiring a statistical operation to match the relevant
scale or design.

The current Validation Handbook version available for publication review
defines universal rules `U1` through `U16`. It does not contain a rule labelled
`U17`.

Accordingly, all frozen references to `U17` in this repository must currently
be treated as an unresolved or version-mismatched method citation.

They must not be used as evidence that the current Handbook contains such a
numbered rule.

### Effect on completed test results

This erratum does not change any canonical T01–T17 verdict.

The affected tests froze their concrete claims, populations, operations,
thresholds, competing predictions, analyzers, and verdict functions
independently of the Handbook rule number.

For example, T16 explicitly freezes the tested operation and common-scale
eligibility predicate in its own test artifacts. The erroneous `U17`
attribution is methodological provenance, not an executable input to the
decision rule.

### Preservation policy

The frozen test files containing `U17` are intentionally not rewritten.

Changing them after execution would destroy the chronology and hashes of the
registered audit artifacts.

Instead, this publication-layer erratum supersedes the affected method
citation until the Validation Handbook itself receives a separate source and
version audit.

### Public wording

Do not state that the current Validation Handbook contains `U17`.

Where the substantive scale/design principle is needed, cite the concrete
test rationale and frozen source/algorithm evidence directly unless and until
a verified Handbook rule or external primary source is mapped to it.
