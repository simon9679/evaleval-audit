from pathlib import Path
import hashlib

HERE=Path(__file__).resolve().parent
EXPECTED={'README.md': 'c53d3deb340be37a13ba64d43b2b3584a216465d99cc60ac86a2278bfa855d74', 'TEST_RATIONALE.md': 'e6e977cf7d086c5cffda60bcb28030c5c0f93e30b50081d2eab5e1094222209c', 'SOURCE_ATTRIBUTION.md': 'ccf64c33d06233fa390eb66444d191881c4f2e82109bc5b77bbebbbcc1087cb4', 'PREREGISTRATION.md': '0904b225c14aab5c212d245aec1afd76342f2c19a669025406c3b104d98fa69a', 'references/REFERENCE_AUTHORITY.json': 'b45e463c8d2b1f681e0025bda6430f825ba1342a5f9a6ad2f154efd25ab50f1e', 'preflight.py': '7efb6f5518aa155b8a17de64cd8f56d3e85d7f27e4a1f82e4773fa998944f888', 'analyze.py': '2b6eed9f9cbe084008ce6d7c57c0c8e5e1b5dde8c79db5f6f2b0ddd85e84e6c3'}

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
