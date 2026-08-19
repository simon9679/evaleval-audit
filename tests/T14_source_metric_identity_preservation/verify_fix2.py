from pathlib import Path
import hashlib
HERE=Path(__file__).resolve().parent
EXPECTED={'HARNESS_FIX_02.md': '04e0529f2a23883527fff0f831ae7110b3b02a9b2594d63e4e2de43ef434000e', 'preflight_fix2.py': 'b66dd37b974d496259fdde4bd4850bd790dbe4a9de10e1f1ce835b9a85dd44e0', 'analyze_fix2.py': 'ebbf095abbaf1e695b394e2e95bc651442c9e90d326ef8428fe48fce62e0d3e6'}
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
print(f"VERIFY_FIX2 bad={bad}")
raise SystemExit(1 if bad else 0)
