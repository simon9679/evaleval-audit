from pathlib import Path
import hashlib
HERE=Path(__file__).resolve().parent
EXPECTED={'README.md': '6521bea9a2d58937b3497361b0dbe35bb20062d39e4da6f2e2a350fc6e045429', 'TEST_RATIONALE.md': '399f3b0eb8746ec167d02ecf217b65b2c79049e19e540e6153c623e5fe0e008e', 'SOURCE_ATTRIBUTION.md': '0b18ce0315b3ac196ba0ea1b6b41d2cb1dd127f44de84d513f876a0dcea0c514', 'PREREGISTRATION.md': 'e4decc973542b71b31ede0ff20956c5762dad8397d60544f9c9d9cfe5de350db', 'references/REFERENCE_AUTHORITY.json': '481e22e1e2cd66d934f140c583ee9035ff0428fe1528b82868966ee6d1166d25', 'preflight.py': '7875935475dfa3e39dcff06b417a5912f35c1bc8d8a1ffc35fc29921c0719d06', 'analyze.py': 'efb9564726d870f21b90e51e0e892004db8c22b36957931293a9f32664913c18'}
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
