from pathlib import Path
import hashlib
HERE=Path(__file__).resolve().parent
EXPECTED={'README.md': '3aaef105ffd67b12f274fe0f5ed4ede7ebab01df932bf4405c8d326f499194cf', 'SOURCE_ATTRIBUTION.md': '509c3b94668e57964ad5efabadf847dca8cec6f62bb0fa83545bae0cc063b7e0', 'TEST_RATIONALE.md': 'f3000dba818059022a9f610862840ea7b9a17632a7cf43adfcb56873b1ec3766', 'PREREGISTRATION.md': 'eeaeaf4346cee7115843f95ce98e951f08e369cd6748040f2796e5f9dfb29219', 'preflight.py': '3a0bbc0558b26472e3cc92137e390135ebed0c8f4bba9659b4285ee65b5e5c68', 'analyze.py': 'f7439fe5b2f9a43611357c0a8de928c1aa8c4294642544c65f9790bea1a82284'}
bad=0
for rel,exp in EXPECTED.items():
    p=HERE/rel
    if not p.exists():
        print(f"MISSING {rel}"); bad+=1; continue
    got=hashlib.sha256(p.read_bytes()).hexdigest()
    if got==exp: print(f"OK {rel}")
    else: print(f"BAD {rel} got={got} expected={exp}"); bad+=1
print(f"VERIFY_PREREG bad={bad}")
raise SystemExit(1 if bad else 0)
