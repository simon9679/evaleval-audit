from pathlib import Path
import hashlib, json
root=Path(__file__).resolve().parent
m=json.loads((root/"PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
bad=0
for rel,meta in m["files"].items():
    p=root/rel
    if not p.exists():
        print("MISSING",rel); bad+=1; continue
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    if h!=meta["sha256"]:
        print("BAD_HASH",rel); bad+=1
    else:
        print("OK",rel)
print(f"VERIFY_PREREG bad={bad}")
raise SystemExit(1 if bad else 0)
