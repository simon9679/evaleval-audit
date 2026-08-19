# POSTRUN_DECISION — T17

Status: final post-run branch decision.

## Verdict

`CONFIRMED`

## Accepted observations

- production signature source match count = 0
- threshold replay exact = true
- frozen threshold = 0.5
- replay threshold = 0.5
- integrity errors = 0

## Claim-governing provenance

The production group configuration uses:

- `metric_unit = score` from the rescaled 0-to-1 source channel;
- `max_score = 10.0` from the point-valued source channels.

No exact source definition has the resulting
`score / 0.0 / 10.0` scale signature.

## Continue

Proceed to score-extrema provenance.

The next test should identify the exact source ids and source scale signatures
of the global minimum and maximum used by production
`max(score) - min(score)`.
