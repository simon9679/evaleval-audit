# RESEARCH_NOTE_2026-08-19 — T14 Fix 4

Status: written before Fix 4 execution.

This note records the external/library research performed after the repeated
T14 replay failure and before designing Fix 4.

## Question researched

Why does the frozen production representation contain:

`"additional_details": {...}`

while Fix 3 produces:

`"additional_details": [[key, value], ...]`

even though both start from the same frozen EEE record and frozen Arrow schema?

## Apache Arrow finding

Apache Arrow documents that `MapArray.to_pylist()` with the default
`maps_as_pydicts=None` converts Arrow maps to Python association lists:

`[(key1, value1), (key2, value2), ...]`

rather than Python dictionaries.

Primary documentation:

https://arrow.apache.org/docs/python/generated/pyarrow.MapArray.html

The frozen EvalEval Arrow translator explicitly maps
`additionalProperties: {"type": "string"}` objects to:

`MAP<string, string>`

and its cast-padding helper emits key/value pairs for those maps.

Frozen backend source:

`src/eval_card_backend/schemas/eee_arrow.py`
commit:
`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

## DuckDB finding

DuckDB documents that:

`to_json(any)`

converts both `STRUCT` and `MAP` values to JSON objects.

Primary documentation:

https://duckdb.org/docs/current/data/json/creating_json

DuckDB also documents that LIST indexing is 1-based.

Primary documentation:

https://duckdb.org/docs/lts/sql/dialect/indexing

## Frozen production path

The frozen EvalEval Stage D path serializes the typed generation-args struct as:

`CAST(to_json(j.generation_config.generation_args) AS VARCHAR) AS generation_args_json`

Stage F then places that JSON string into each UDF row as:

`generation_args := generation_args_json`

The divergence code parses the string with `json.loads` before comparing setup
fields.

Frozen backend sources:

- `src/eval_card_backend/canonicalise/stages.py`
- `src/eval_card_backend/signals/setup.py`
- `src/eval_card_backend/signals/comparability.py`

commit:
`9c16ab3f93a4ba02a5b44590858bbdf824ed09d3`

## Conclusion for Fix 4

Fix 3 introduced a non-production conversion step:

`Arrow Table -> PyArrow to_pylist() -> Python object`

That conversion is documented to turn MAP values into association lists.

Fix 4 removes that step.

For each frozen source record it will reconstruct:

`raw EEE JSON`
`-> frozen Pydantic validation`
`-> frozen Arrow schema padding/cast`
`-> DuckDB Arrow relation`
`-> DuckDB to_json(generation_args)`
`-> frozen divergence Python function`

No map/list repair is performed manually.

## Guardrail

Both complete production groups must replay exactly before the source-id
counterfactual is allowed to execute.

The original T14 claim, competing predictions, population, intervention, and
verdict rule remain unchanged.
