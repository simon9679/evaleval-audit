# PREREGISTRATION — T17

## Primary claim C-T17

For group:

`d38d8f8e547287b6b0fc78f43f310762`

the frozen Stage-F field-wise aggregation produces a group metric configuration
that:

1. matches zero exact source configurations on the fixed signature fields; and
2. exactly reproduces the frozen production threshold magnitude and basis.

## Fixed signature fields

- `metric_kind`
- `metric_unit`
- `min_score`
- `max_score`

## Fixed population

Expected Stage-F arithmetic rows:

`8`

Expected exact source ids:

`4`

## Production reconstruction rule

For each fixed signature field:

take the maximum non-null Stage-F row value using production-compatible
ordering.

If every value is null, return null.

No field is borrowed by hand from a chosen source id.

## Exact source match

A source id matches the reconstructed production signature only if all four
fixed signature fields are exactly equal.

## Field provenance

For each reconstructed field value, record every exact source id whose source
configuration contains that selected value.

This is descriptive support and is not itself the primary verdict condition.

## Threshold replay

Call the frozen production `compute_threshold` on the reconstructed group
configuration.

Require exact equality with the one constant frozen Stage-F:

- `variant_divergence_threshold`
- `variant_threshold_basis`

for the group.

## Competing predictions

### P1 — benign explanation

`production_signature_source_match_count >= 1`

Expected verdict:

`REFUTED`

### P2 — consequential explanation

`production_signature_source_match_count = 0`

and threshold replay is exact.

Expected verdict:

`CONFIRMED`

## Verdict rule

`CONFIRMED` if:

- affected rows = 8;
- exact source ids = 4;
- reconstructed config fields are complete;
- production signature source match count = 0;
- threshold replay exact = true;
- integrity errors = 0.

`REFUTED` if all integrity checks pass and:

`production_signature_source_match_count >= 1`

`INCONCLUSIVE` if:

- the Stage-F signal is not constant across the group;
- source configurations are internally inconsistent;
- frozen threshold code cannot be verified;
- a reconstruction field cannot be resolved.

`ERROR` if required artifacts cannot be loaded or execution fails.

## Branch stop / continue rule

If REFUTED:

stop the synthetic-config claim branch.

If INCONCLUSIVE:

repair only the integrity/replay acquisition path.

If CONFIRMED:

the production metric configuration may be described as synthetic for this
group. A later test may inspect whether the source-id/scale mixture is directly
responsible for the production range extrema, if further causal detail is
needed.
