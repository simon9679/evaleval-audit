$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$AuditRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Freeze = Join-Path $AuditRoot "freeze"
$SumFile = Join-Path $Freeze "SHA256SUMS.txt"

if (-not (Test-Path $SumFile)) { throw "Missing $SumFile" }

$env:EVALEVAL_AUDIT_ROOT = $AuditRoot
$verifyPy = @'
import hashlib
import os
import sys
from datetime import datetime, timezone


def extended_windows_path(path):
    if os.name != "nt":
        return os.path.abspath(path)
    path = os.path.abspath(path)
    if path.startswith("\\\\?\\"):
        return path
    if path.startswith("\\\\"):
        return "\\\\?\\UNC\\" + path[2:]
    return "\\\\?\\" + path


audit_root = extended_windows_path(os.environ["EVALEVAL_AUDIT_ROOT"]).rstrip("\\/")
sum_file = audit_root + r"\freeze\SHA256SUMS.txt"
out_file = audit_root + r"\freeze\VERIFY_FREEZE.txt"

ok = 0
bad = 0
missing = 0
results = []

with open(sum_file, "r", encoding="ascii") as f:
    for raw in f:
        line = raw.rstrip("\r\n")
        if not line.strip():
            continue
        if "  " not in line:
            results.append(f"BAD_LINE {line}")
            bad += 1
            continue
        expected, rel = line.split("  ", 1)
        expected = expected.strip().lower()
        rel = rel.strip()
        parts = rel.replace("\\", "/").split("/")
        full = os.path.join(audit_root, *parts)

        if not os.path.isfile(full):
            results.append(f"MISSING {rel}")
            missing += 1
            continue

        h = hashlib.sha256()
        with open(full, "rb") as inp:
            for chunk in iter(lambda: inp.read(1024 * 1024), b""):
                h.update(chunk)
        actual = h.hexdigest()
        if actual == expected:
            ok += 1
        else:
            results.append(
                f"HASH_MISMATCH {rel} expected={expected} actual={actual}"
            )
            bad += 1

lines = [
    "VERIFY_FREEZE",
    f"checked_at_utc={datetime.now(timezone.utc).isoformat()}",
    f"ok={ok}",
    f"bad={bad}",
    f"missing={missing}",
    "",
] + results

text = "\n".join(lines) + "\n"
with open(out_file, "w", encoding="utf-8", newline="\n") as f:
    f.write(text)
print(text, end="")
sys.exit(2 if bad or missing else 0)
'@

try {
    $verifyPy | python -
    $code = $LASTEXITCODE
    if ($code -ne 0) { exit $code }
}
finally {
    Remove-Item Env:EVALEVAL_AUDIT_ROOT -ErrorAction SilentlyContinue
}
