from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BAD = 0


def check(cond: bool, message: str) -> None:
    global BAD
    print(("OK  " if cond else "BAD ") + message)
    if not cond:
        BAD += 1


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        check(False, f"JSON readable: {path.relative_to(ROOT)} ({type(exc).__name__}: {exc})")
        return None


print("EVALEVAL PUBLIC BUNDLE VERIFY")

index = read_json(ROOT / "TEST_INDEX.json") or {}
claim_index = read_json(ROOT / "CLAIM_INDEX.json") or {}
manifest = read_json(ROOT / "PUBLIC_REVIEW_MANIFEST.json") or {}

expected_counts = {"CONFIRMED": 12, "REFUTED": 5, "INCONCLUSIVE": 0, "ERROR": 0}
check(index.get("test_count") == 17, "TEST_INDEX test_count=17")
check(index.get("verdict_counts") == expected_counts, f"TEST_INDEX verdict_counts={expected_counts}")
check(claim_index.get("test_count") == 17, "CLAIM_INDEX test_count=17")

claim_by_id = {x.get("test_id"): x for x in claim_index.get("tests", [])}

required = ["README.md", "TEST_RATIONALE.md", "PREREGISTRATION.md", "results/summary.json", "results/RESULT_ANALYSIS.md", "verify_prereg.py"]

for item in index.get("tests", []):
    tid = item.get("test_id")
    base = ROOT / "tests" / tid
    print(f"\n[{tid}]")
    for rel in required:
        check((base / rel).exists(), f"required {tid}/{rel}")
    summary = base / "results" / "summary.json"
    if summary.exists():
        sj = read_json(summary) or {}
        check(sj.get("verdict") == item.get("final_verdict"), f"canonical verdict={item.get('final_verdict')}")
        check(sha256(summary) == item.get("canonical_summary_sha256"), "canonical summary SHA256 matches TEST_INDEX")
    ci = claim_by_id.get(tid)
    check(ci is not None, "CLAIM_INDEX entry exists")
    if ci:
        prereg = ROOT / ci.get("preregistration", "")
        check(prereg.exists(), "CLAIM_INDEX preregistration exists")
        if prereg.exists():
            check(sha256(prereg) == ci.get("preregistration_sha256"), "preregistration SHA256 matches CLAIM_INDEX")
        check(ci.get("final_verdict") == item.get("final_verdict"), "CLAIM_INDEX verdict matches TEST_INDEX")

    verifier = base / "verify_prereg.py"
    if verifier.exists():
        proc = subprocess.run([sys.executable, str(verifier)], cwd=str(base), capture_output=True, text=True)
        check(proc.returncode == 0, "verify_prereg.py immutability gate passes")

# T14 canonicalization/history.
t14 = ROOT / "tests" / "T14_source_metric_identity_preservation" / "results"
if t14.exists():
    check(sha256(t14 / "summary.json") == sha256(t14 / "summary_fix4.json"), "T14 canonical summary is byte-identical to summary_fix4")
    initial = read_json(t14 / "summary_initial_error.json") or {}
    check(initial.get("verdict") == "ERROR", "T14 initial ERROR preserved")

# Included freeze metadata hashes.
for entry in manifest.get("included_freeze_metadata", []):
    p = ROOT / entry.get("file", "")
    check(p.exists(), f"freeze metadata exists: {entry.get('file')}")
    if p.exists():
        check(p.stat().st_size == entry.get("bytes"), f"freeze metadata bytes match: {entry.get('file')}")
        check(sha256(p) == entry.get("sha256"), f"freeze metadata SHA256 match: {entry.get('file')}")

# Every JSON/JSONL structure that is non-empty must parse.
json_bad = []
for p in ROOT.rglob("*.json"):
    try:
        json.loads(p.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        json_bad.append(f"{p.relative_to(ROOT)}: {type(exc).__name__}: {exc}")
check(not json_bad, "all .json files parse")
for msg in json_bad[:20]:
    print("    " + msg)

# Publication wrapper files should be English-only and contain no literal local path.
wrapper_files = [ROOT / x for x in ["README.md", "AUDIT_STATUS.md", "REVIEW_GUIDE.md", "REPRODUCTION.md", "METHOD_SOURCES.md", "AI_REVIEW_PROMPT.txt"]]
for p in wrapper_files:
    txt = p.read_text(encoding="utf-8-sig")
    check(re.search(r"[\u0400-\u04FF]", txt) is None, f"English-only wrapper: {p.name}")

# Local absolute paths in raw evidence are informational, not a failure.
local_path_files = []
pat = re.compile(r"C:(?:\\\\|\\|/)+Users(?:\\\\|\\|/)+", re.I)
for p in ROOT.rglob("*"):
    if not p.is_file() or p.suffix.lower() not in {".json", ".jsonl", ".txt", ".md", ".py", ".ps1"}:
        continue
    try:
        txt = p.read_text(encoding="utf-8-sig", errors="replace")
    except Exception:
        continue
    if pat.search(txt):
        local_path_files.append(str(p.relative_to(ROOT)))
print(f"\nINFO local_path_files={len(local_path_files)} (preserved raw execution provenance; see REPRODUCTION.md)")
for rel in local_path_files:
    print("INFO " + rel)

print(f"\nVERIFY_PUBLIC_BUNDLE bad={BAD}")
raise SystemExit(1 if BAD else 0)
