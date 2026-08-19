from pathlib import Path
import hashlib
HERE=Path(__file__).resolve().parent
EXPECTED={'README.md': '38a8bc93022b0c02e73520a1698d9c2ca98f9ea67542b73e23ad1844909720df', 'SOURCE_ATTRIBUTION.md': '1695e0532f672361a403114ecf71cb3705ec49d40a20875a8341ff1cd635736a', 'TEST_RATIONALE.md': '0194f4acab3ba93db5a97c7293d46dc14d60f30a6e737110b52cc8605d2b1963', 'PREREGISTRATION.md': '5bffecd45f7d6fab0cfd835f9c1be086e05d7de047950520eb84fdeefc60d69e', 'preflight.py': 'f43d5fc40dc8f3908cfa6fd38540af1f1f64d079cdc62e8dae2c4cca15fb8d09', 'analyze.py': '1b113b4cf105a10636e057af38b98bec1edc667ce7b2500081add198f59f9571'}
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
