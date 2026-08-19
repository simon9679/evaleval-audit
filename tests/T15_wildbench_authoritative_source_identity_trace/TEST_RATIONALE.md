# TEST_RATIONALE

## Immediate trigger

The immediate trigger is T14 Fix 4.

T14 showed that the WildBench/OpenEval production-positive group
`d38d8f8e547287b6b0fc78f43f310762` becomes entirely non-positive when exact
source metric identity is preserved.

That makes the provenance of the four source identities claim-governing.

## Methodological source

This test is guided by:

- Falsification Protocol Rule 6 — provenance;
- Falsification Protocol Rule 7 — test the product/outcome;
- Falsification Protocol Rule 8 — fixed competing predictions;
- Validation Handbook U3 — authority of reference;
- U8 — verdict granularity no broader than measurement;
- U9 — dependency DAG;
- U11 — ERROR and INCONCLUSIVE attribution;
- U12 — hypotheses before the run;
- B12 — derive claim-governing identity from frozen schema/algorithm.

## Why now

A semantic equivalence verdict would be premature if the four source ids were
not independently traceable to source-defined metric channels.

T15 therefore tests source identity before semantic meaning.

## Cost

No LLM calls.

No network is required during execution.
