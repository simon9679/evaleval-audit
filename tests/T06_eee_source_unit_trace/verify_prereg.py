from pathlib import Path
import hashlib
HERE = Path(__file__).resolve().parent
EXPECTED = {'README.md': 'e94d8dfac8999e52e5885554d0481fa53804ed5edc07f108eb62c96863dd6a01', 'SOURCE_ATTRIBUTION.md': '7ced60371420fbb406d248a88ac3efab6fed3eb0f11b54a00b531871a9410973', 'TEST_RATIONALE.md': 'ecd85c255e6fc525f7d0e8101d7f1917ac1708b64cd2b1c2c49501c278f6fef5', 'PREREGISTRATION.md': 'e996b1756e0fd3cde6b5f087a0797e83bff82248ac7ffe83426d694e1e5e78cf', 'preflight.py': '487f59d94e3016e1532c91d43180a4c14fb8b2f4024607b28faf980e0af56634', 'analyze.py': '9a6b1bafe3f4533dec93da562b02f9b5374929105c8bdad8623577c075cef0e3'}
bad = 0
for rel, expected in EXPECTED.items():
    path = HERE / rel
    if not path.exists():
        print(f"MISSING {rel}")
        bad += 1
        continue
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    if got == expected:
        print(f"OK {rel}")
    else:
        print(f"BAD {rel} got={got} expected={expected}")
        bad += 1
print(f"VERIFY_PREREG bad={bad}")
raise SystemExit(1 if bad else 0)
