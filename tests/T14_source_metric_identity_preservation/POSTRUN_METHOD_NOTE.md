# POSTRUN_METHOD_NOTE — T14

Status: final post-run meta-audit note.

## Harness sequence

T14 required four repairs before the counterfactual became admissible.

The sequence exposed three classes of audit-harness failure:

1. assuming an internal production payload survives in a final artifact;
2. replacing a production aggregation rule with an intuitive constancy rule;
3. reconstructing typed nested data through a representation path different
   from production.

## Critical safeguard

The full-group production replay gate blocked every invalid counterfactual.

No T14 source-id subgroup result was accepted until both original production
groups replayed exactly.

## Research-before-repair rule

After the repeated representation failure, the repair process changed:
external/library documentation and frozen implementation were inspected before
writing Fix 4.

That research showed the relevant Arrow MAP / Python / DuckDB JSON behavior and
led to a literal reconstruction of the production serialization path.

## Candidate handbook lesson

For nested typed data, an admissible replay may require representation-path
equivalence, not only semantic-field equivalence.

A useful future handbook clause would be:

> When the target decision consumes serialized or typed nested structures,
> replay validity requires reproducing the claim-governing serialization
> boundary or proving the alternate representation is decision-equivalent.

This is a candidate amendment only. The handbook is not modified during the
audit.
