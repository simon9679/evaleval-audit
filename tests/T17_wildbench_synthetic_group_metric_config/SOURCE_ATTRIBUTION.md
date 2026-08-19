# SOURCE_ATTRIBUTION

## Frozen backend

Repository:

`evaleval/eval_cards_backend_pipeline`

Commit:

`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

Relevant production behavior:

Stage F constructs group metric configuration fields using non-null field-wise
`MAX` over `metric_kind`, `metric_unit`, `min_score`, and `max_score`.

The threshold resolver uses:

- `proportion` -> 0.05;
- `percent` -> 5.0;
- otherwise valid `(min_score, max_score)` -> 5% of the range;
- otherwise -> 0.05 fallback.

T17 imports the frozen threshold resolver directly from the local frozen
backend.

## Stage-F artifact

The exact Stage-F Parquet is the T03 frozen artifact with SHA-256:

`e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196`

## T16 dependency

T16 provides the exact four source scale signatures and the CONFIRMED
common-scale result.

## T14 dependency

T14 Fix 4 previously established exact full production replay for the two
affected groups. T17 does not reuse the T14 verdict as a substitute for its own
threshold replay.
