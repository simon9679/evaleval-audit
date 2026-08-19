# Verification Tools

Use `verify_public_bundle.py` for the current compact publication bundle.

`verify_completed_tests.py` is a preserved historical verifier created when only T01-T03 had been documented. It also expects the local-only T03 transcript that is intentionally excluded from the compact public bundle. It is retained as historical provenance and is not the current bundle verifier.

Per-test `verify_prereg.py` scripts verify immutability/hash integrity of preregistered files. They do not independently recompute the scientific verdict.
