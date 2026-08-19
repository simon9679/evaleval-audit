from pathlib import Path
import hashlib
HERE=Path(__file__).resolve().parent
EXPECTED={'README.md': 'a199f2f728c162316f5186b64d14c3123ae9841006db17b464ed4fbd48e60832', 'SOURCE_ATTRIBUTION.md': '9bf9e6f6d3670862d4b1b00f238e9e980e497fc2116ee72b5540d09652ab5c64', 'TEST_RATIONALE.md': 'ea60adfc43b24327ae77f538388fc51ad1ac3cb9c706c4548817f1fd2c7d6c24', 'PREREGISTRATION.md': 'b520b5b67f571e02190318c18960a36d9363b52b608ab47a7822c4d01c08f1ce', 'preflight.py': 'ffee30178e31ff79efb9aa38d6e2791e2e8c8e5259fb7211eccefc80d0767359', 'analyze.py': 'affed5661eb17ccec222c821775e8358036209d6164a57594fbade64ccb67f2b'}
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
