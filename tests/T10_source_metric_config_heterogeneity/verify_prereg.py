from pathlib import Path
import hashlib
HERE=Path(__file__).resolve().parent
EXPECTED={'README.md': '4ffd60527f57881d7132cefd6a5ced65682908ae7ea254042ded1f173675742b', 'SOURCE_ATTRIBUTION.md': '7e6fb8d5c5418da96ec6520513003668637e895d6a02c6a9dc03153929cfad12', 'TEST_RATIONALE.md': '96fa1a6ba77183929be982407f986c8fd846eb772121f91bd05a9b40df7902bc', 'PREREGISTRATION.md': 'e49488568671cd3d3ef1abc4dc28348de4b00d9911800e82275a69a4cba0f1c0', 'preflight.py': '9abef69ab6a84729937fe27069d5bd0e7772688de89366dd12097f415450dae0', 'analyze.py': 'd8602b7072fa18a71f2a2ca260701de8752ecc8099eedfc0f8aa3df970c14352'}
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
