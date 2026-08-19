# T01 Post-hoc Attribution — V2 Floating-Point Boundary

Status: post-hoc diagnostic evidence. Not preregistered. Not a new confirmatory test.

T01 case V2 expected no divergence at an exact nominal threshold of 0.05 because the frozen production rule is strict `divergence > threshold`.

Observed T01 result:

- score pair: 0.50, 0.55
- nominal decimal difference: 0.05
- production floating-point divergence: 0.050000000000000044
- threshold: 0.05
- production flag: true

Three-point diagnostic:

- 0.50 -> 0.55 produced 0.050000000000000044 and `true`
- 0.50 -> 0.5499999999999999 produced 0.04999999999999993 and `false`
- 0.50 -> 0.5500000000000002 produced 0.050000000000000155 and `true`

Interpretation:

The T01 failure is attributable to floating-point boundary sensitivity in the frozen comparability calculation. This does not by itself establish corpus-level or product-level impact.

The next confirmatory test characterizes the boundary across all frozen threshold bases and across multiple mathematically equivalent score pairs before any corpus-level claim is made.
