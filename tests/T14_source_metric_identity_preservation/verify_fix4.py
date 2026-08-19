from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
EXPECTED = {'RESEARCH_NOTE_2026-08-19.md': '70953b94645b49eeb5b991dba6a4ef9a3183e355c94c5e671c2327a80a0993f2', 'HARNESS_FIX_04.md': '4b6bb0e4f9cba6533c92456e6b48c4bc7a13a084cd7dc986e284e9a58d96861d', 'preflight_fix4.py': 'c60320f272b2961821f2496a2463a340318cf030af501d1fead9d508cab62f22', 'analyze_fix4.py': '40366285bfab4b7e46c76c3bcb7c93a0429e174ae5efd7369eb07752b184d5f4'}

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

print(f"VERIFY_FIX4 bad={bad}")
raise SystemExit(1 if bad else 0)
