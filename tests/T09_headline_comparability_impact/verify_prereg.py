from pathlib import Path
import hashlib
HERE=Path(__file__).resolve().parent
EXPECTED={'README.md': '8e39cd8c73fdd8ed6b90ffac7a10cef8385615c76c98a1701dfdb369c74a988d', 'SOURCE_ATTRIBUTION.md': '3087eaea931cf8aef273446fc35202f97e8dc3efac9abcb1d6945344248678d9', 'TEST_RATIONALE.md': '3aa841312779b9c02d16af0b04b76e4c10e20b274dbcd8db21e7fc8dcd403a3e', 'PREREGISTRATION.md': 'd770edfa9835d187bd5d24149788779fa84fb63d0a144e67e879ec1f2a4d9133', 'preflight.py': '6eec599a09593a271dc5133390438957ef4a7f6e69b97f29bddb6c439c43f7e5', 'analyze.py': 'ef3ea1088e2570f1b0925690cacac022b6459fe18a2d63cbad50a52b4d20435e'}
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
