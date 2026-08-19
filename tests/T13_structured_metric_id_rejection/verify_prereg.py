from pathlib import Path
import hashlib
HERE=Path(__file__).resolve().parent
EXPECTED={'README.md': 'acdd7d8d626157d99bf266e92c835e25b6a5f93d9619364487b6fe283afda405', 'SOURCE_ATTRIBUTION.md': 'e335a9732836c1ad7a3bfc7fd8abf6e75555c5e83c3cbb35883e932b69b94018', 'TEST_RATIONALE.md': '2ec1af6e730b86aceb3b94a46bedbcac2c58c00613caa5c3e88fed9556f5f69c', 'PREREGISTRATION.md': 'c81f8772a3540101c9cc783db2b9d2a20cec9551f5f9d5d6c54584f86acfc5a7', 'preflight.py': '3fea402243ef48352b7fff517b255e90d00ef44bd3d78a0a6e0dfc8424f46049', 'analyze.py': '0c288f4658bd107c85d0d177fdc77f085dd270b336101dad21d82914a453576a'}
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
