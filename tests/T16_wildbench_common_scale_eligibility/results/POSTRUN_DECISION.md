# POSTRUN_DECISION — T16

Status: final post-run branch decision.

## Verdict

`CONFIRMED`

## Raw result

- 8 affected rows
- 4 source metric ids
- 2 declared units
- 3 bound signatures
- 3 exact scale signatures
- 0 source ids with non-empty metric parameters
- 0 source ids with structured transform-key metadata
- common scale eligible = false
- 0 integrity errors

## Branch consequence

The frozen source representation does not itself justify one raw numeric scale
for all four claim-governing source channels.

## Continue

Before broader semantic adjudication, test the immediate production consequence
of this heterogeneity:

does field-wise Stage-F aggregation create a synthetic group metric
configuration that matches no source metric definition?

This is cheaper and more directly tied to the production arithmetic.
