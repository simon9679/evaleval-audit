from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
EXPECTED = {'HARNESS_FIX_01.md': '54c57c8316451374b6616418d8d798b9122b9cc42ffa83fbd06e5031bda57b68', 'preflight_fix1.py': '73251672b301e85cd2bbca2a3431ee00d4c3d7eb73049b6da33de88ad2b142ad', 'analyze_fix1.py': 'd9818719b01e9fa78b10fb05016ac24c6d7cb908bb5713ec5ab774e599d2ec70'}

bad = 0
for rel, expected in EXPECTED.items():
    path = HERE / rel
    if not path.exists():
        print(f"MISSING {rel}")
        bad += 1
        continue
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    if got == expected:
        print(f"OK {rel}")
    else:
        print(f"BAD {rel} got={got} expected={expected}")
        bad += 1

print(f"VERIFY_FIX1 bad={bad}")
raise SystemExit(1 if bad else 0)
