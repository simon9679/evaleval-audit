# Method Sources

## Falsification Protocol

Canonical public source:

https://github.com/simon9679/tbg-postmortem/blob/main/FALSIFICATION_PROTOCOL.md

Audit-time verified Protocol SHA-256 recorded during the project:

`c97f8a4d2b67d502ca54290be55764bd5c1d8ac7`

The Protocol was used as a decision procedure: cheap validity checks first,
dependency/stop semantics, provenance/noise separation where applicable, and
preregistration before claim-bearing runs. It was not treated as a literal
one-size-fits-all test list.

## Validation Handbook

A literature-grounded working Validation Handbook was used to construct and
constrain several tests. It is not bundled in this publication snapshot.

Reason: its bibliography, venue classifications, and
source-to-normative-statement mappings are themselves auditable claims and
require a separate source audit before public release. The audit therefore
does not ask readers to treat the unpublished Handbook as independent
evidence.

A post-freeze method-reference issue involving `U17` is documented in
[`METHOD_ERRATA.md`](METHOD_ERRATA.md). The frozen test artifacts are preserved
unchanged.

Test-level method provenance remains visible in each `TEST_RATIONALE.md` and
`SOURCE_ATTRIBUTION.md`.
