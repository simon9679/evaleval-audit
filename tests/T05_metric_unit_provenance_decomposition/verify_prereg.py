from pathlib import Path
import hashlib
HERE=Path(__file__).resolve().parent
EXPECTED={'README.md': '81e999285281e4b75c43a4bcf2cd337a5b3fbfac528b47f959a0c7d844151fc8', 'SOURCE_ATTRIBUTION.md': 'ddef34786178ed324fde27ad5a97ed623ea53945471c5acee8f0fe2bc147db0a', 'TEST_RATIONALE.md': '205d8dcbd571a929d57db7c4f1e6870508fda04023fbefd25568a14ea355f5ea', 'PREREGISTRATION.md': 'dd953944daf2450f1ee3f967088ccb587395461bbd354ad5fdadfbb0f1de66d7', 'preflight.py': '5fc2a4926e8638df7b8f8553114211e05819e319cc33b01a8a49442c2cf3def8', 'analyze.py': '122fb9ad13f4d59c90006014a0c526af6034aa579f96a67b7518b4e249664e8a'}
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
