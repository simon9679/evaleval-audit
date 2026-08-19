from pathlib import Path
import hashlib
HERE=Path(__file__).resolve().parent
EXPECTED={'HARNESS_FIX_03.md': '3d936b6b66c037ca105b12fcfbed12855e1a420a48fdd901fecbfd1ee7e69009', 'preflight_fix3.py': '27fc3bec5e80db328028860f3d584878988c94ebfbaa208712e3077a69b78130', 'analyze_fix3.py': 'caa20434d09924dd88eb2634ef1114d82e827eaac920a1ad78928e95bfb4c7ad'}
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
print(f"VERIFY_FIX3 bad={bad}")
raise SystemExit(1 if bad else 0)
