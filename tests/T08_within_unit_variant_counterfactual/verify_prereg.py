from pathlib import Path
import hashlib
HERE=Path(__file__).resolve().parent
EXPECTED={'README.md': '49a294e9acb50c9a9880654b25c530615ba2d0b6c07b3d319653ca79a5892682', 'SOURCE_ATTRIBUTION.md': 'eff103e0b4007060e9e3c0b082659ddf88c28eb8407bb1675c26a44707507e74', 'TEST_RATIONALE.md': '1089ec515fb0fd163503d68bd1f62e7260d9ade934732be4b3d04859075af4d8', 'PREREGISTRATION.md': '6580c8cb690b16f283e2dd587b721a801a9ecd3ac8bf547589f4783377047866', 'preflight.py': '9aa67fca6f1737558c386ffacc90a428b0c088e25ca02c090a34cba1885d018f', 'analyze.py': 'a01f5e9744f7fc0feca091a607ee9ac841b0a751e545b46b6a0a082c144c3df0'}
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
