from __future__ import annotations

import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent

EXPECTED = {'README.md': '279542b8989d3212bf7bdde176a21b0227969e7e54f8fb9ad463fcf8e585474c', 'SOURCE_ATTRIBUTION.md': '9df532e28043c4010bd8cd3277b42128975355e945788a07ffe6d2a744565619', 'TEST_RATIONALE.md': '46d345d05f083f266a97a5089103255dba29e330a098e846f9d8314d402abed2', 'PREREGISTRATION.md': '744da73b6e562929be0fc7b5bf5f5972f18ce5d8e86da6ffa3d26fbe7991a902', 'preflight.py': '5376a4ecc23f01ad8fa86251cb5b53b836d0de37cb539ca0162ba50080655739', 'analyze.py': 'a258aebbc5324598d7b270518a9d880f83976df0cd8a4428ee28ad5bfa3a3862'}

bad = 0
for rel, expected in EXPECTED.items():
    path = HERE / rel
    if not path.exists():
        print(f"MISSING {rel}")
        bad += 1
        continue
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    if got != expected:
        print(f"BAD {rel} got={got} expected={expected}")
        bad += 1
    else:
        print(f"OK {rel}")

print(f"VERIFY_PREREG bad={bad}")
raise SystemExit(1 if bad else 0)
