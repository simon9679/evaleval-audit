# POSTRUN_DECISION — T14

Status: final post-run branch decision.

## Verdict

`CONFIRMED`

## Accepted execution

Fix 4 is the first admissible T14 counterfactual execution because it passes:

- 12/12 source reconstruction;
- 2/2 exact production replay;
- 0 production replay errors;
- 0 source metric config consistency errors;
- 0 row identity errors;
- 0 integrity errors.

## Primary result

One of the two affected production-positive groups loses every positive
source-id subgroup under exact source metric-id preservation.

That group is the WildBench/OpenEval group.

All four WildBench source-id subgroups are applicable and negative.

CocoaBench retains one positive exact-source-id subgroup.

## Next branch

Proceed to authoritative semantic/reference adjudication of the exact source
metric identities.

Priority is the WildBench/OpenEval group because T14 establishes causal
operational dependence there.

Do not yet prescribe a canonical alias or claim semantic invalidity.
