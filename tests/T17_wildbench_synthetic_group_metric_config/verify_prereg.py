from pathlib import Path
import hashlib
HERE=Path(__file__).resolve().parent
EXPECTED={'README.md': 'd5c94e84b79cad0422dad919a164a8fd39d94860d8f233d8c3025b3f09572b3b', 'TEST_RATIONALE.md': 'a6d18a8652e44b2ee1f2fa14abdaef1e8d9bd1e6c5f96749a19b705c428604f4', 'SOURCE_ATTRIBUTION.md': 'dc7cb24a4bec531e6efd60e0492f4a9bf652329190fb95a981d9f8f4d455c048', 'PREREGISTRATION.md': '9f8353933e0c0aceafd51aabfff1e11faa1f6eb5ae3d049fa0f33643f9fe2541', 'preflight.py': 'ae102588bb4e2590cec9a5d41ea81d5a02c02374265aad63c4212c080d3ed8a6', 'analyze.py': 'd43a4dbd3dae81c44138e2a3d87ccb9e5f4894d6cefdabc4cbe35f660aeaef5d'}
bad=0
for rel,exp in EXPECTED.items():
    p=HERE/rel
    if not p.exists():
        print(f"MISSING {rel}")
        bad+=1
        continue
    got=hashlib.sha256(p.read_bytes()).hexdigest()
    if got==exp:
        print(f"OK {rel}")
    else:
        print(f"BAD {rel} got={got} expected={exp}")
        bad+=1
print(f"VERIFY_PREREG bad={bad}")
raise SystemExit(1 if bad else 0)
