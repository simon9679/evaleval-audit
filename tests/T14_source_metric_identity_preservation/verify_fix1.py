from pathlib import Path
import hashlib
HERE=Path(__file__).resolve().parent
EXPECTED={'HARNESS_FIX_01.md': '0ded9a35aea9d3ab67424d0b5a45cff7c21d73ba02a391c8a01ec7d4a129a806', 'preflight_fix1.py': 'b9eb196351ce7aba17ac36c6fbd31f8242ddcc278253ad386dbd28fc40fa79f4', 'analyze_fix1.py': '344319a276e2b831767cdbbb41bf0cef6cf7081a003dfd7d46f81d758bf0a2b5'}
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
print(f"VERIFY_FIX1 bad={bad}")
raise SystemExit(1 if bad else 0)
