# POSTRUN_METHOD_NOTE — T17

Status: final post-run meta-audit note.

T17 separates three distinct layers:

1. source metric definitions;
2. group-level aggregation of metric metadata;
3. downstream threshold computation.

This separation matters because a group configuration can be internally valid
as a Python object while lacking provenance as an exact source metric
definition.

A threshold replay demonstrates that the synthetic representation is
claim-governing rather than merely cosmetic.
