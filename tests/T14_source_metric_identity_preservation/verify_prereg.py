from pathlib import Path
import hashlib
HERE=Path(__file__).resolve().parent
EXPECTED={'README.md': 'ae869124e07ddd2611233629621b0d11ebe2aa5d99005696d1c1d02d1ce56748', 'SOURCE_ATTRIBUTION.md': '03f6004d857a77cb795fa4dcc1b6e2b2e0c596a5f56f75535389d426fc128afb', 'TEST_RATIONALE.md': '3bc62bb0ea64835bba8e244b00dfde2d9a9a29afc066456d2c41b178daeaf48b', 'PREREGISTRATION.md': 'c780a0342fcd93bf49888ca1a776e97585a3fce121e2fe897ace6af92963b2fe', 'preflight.py': '53771bec4f01e3f8523b213ddb43fa1f3d6de806db4fd5e4931de3391ce405fa', 'analyze.py': 'f1ab53c546bb47dbc6cbc325b0608c54b0dbe4a9dba5c474e2b0b2cac6972f5e'}
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
