$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Verify = Join-Path $Root "freeze\VERIFY_FREEZE.txt"
$Backend = Join-Path $Root "freeze\repos\eval_cards_backend_pipeline"
$KnownOut = Join-Path $Root "known_issues"
$ClaimsOut = Join-Path $Root "claims_freeze"

if (-not (Test-Path $Verify)) { throw "Missing freeze\VERIFY_FREEZE.txt." }
$verifyText = Get-Content $Verify -Raw
if ($verifyText -notmatch '(?m)^bad=0\s*$' -or $verifyText -notmatch '(?m)^missing=0\s*$') {
    throw "Freeze verification is not clean."
}

$backendHead = (& git -C $Backend rev-parse HEAD).Trim()
$expectedBackendHead = "9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
if ($backendHead -ne $expectedBackendHead) {
    throw "Frozen backend HEAD mismatch: $backendHead"
}

New-Item -ItemType Directory -Force -Path (Join-Path $KnownOut "source") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ClaimsOut "raw") | Out-Null

$knownFiles = @(
    "src/eval_card_backend/registry/benchmark_known_issues.json",
    "src/eval_card_backend/metric_meta_hotfix.py",
    "src/eval_card_backend/canonicalise/resolution_hotfixes.py",
    "src/eval_card_backend/canonicalise/hierarchy_hotfixes.py"
)

$knownManifest = @()
foreach ($rel in $knownFiles) {
    $src = Join-Path $Backend ($rel -replace '/', '\')
    if (-not (Test-Path $src)) { throw "Missing known-issues source: $rel" }
    $dstName = ($rel -replace '/', '__')
    $dst = Join-Path (Join-Path $KnownOut "source") $dstName
    Copy-Item $src $dst -Force
    $knownManifest += [PSCustomObject]@{
        source_repository = "evaleval/eval_cards_backend_pipeline"
        source_commit = $backendHead
        source_path = $rel
        frozen_copy = "known_issues/source/$dstName"
        sha256 = (Get-FileHash $dst -Algorithm SHA256).Hash.ToLowerInvariant()
        bytes = (Get-Item $dst).Length
    }
}
$knownManifest | ConvertTo-Json -Depth 5 | Set-Content `
    (Join-Path $KnownOut "KNOWN_ISSUES_MANIFEST.json") -Encoding UTF8

$env:EVALEVAL_AUDIT_ROOT = $Root

@'
import hashlib
import json
import os
import pathlib
import urllib.request
from datetime import datetime, timezone

root = pathlib.Path(os.environ["EVALEVAL_AUDIT_ROOT"])
out = root / "claims_freeze"
raw = out / "raw"
raw.mkdir(parents=True, exist_ok=True)

targets = [
    ("evaluation_cards_launch", "https://evalevalai.com/infrastructure/2026/06/09/evaluation-cards-launch/"),
    ("evaluation_cards_project", "https://evalevalai.com/projects/eval-cards/"),
    ("evaluation_cards_live", "https://evalcards.evalevalai.com/"),
    ("evaluation_cards_help_general_public", "https://evalcards.evalevalai.com/help/general-public"),
    ("every_eval_ever_project", "https://evalevalai.com/projects/every-eval-ever/"),
]

manifest = {
    "schema_version": 1,
    "purpose": "Public-claims freeze before confirmatory EvalEval tests.",
    "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
    "targets": [],
}
errors = 0

for name, url in targets:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "evaleval-independent-audit/0.1 public-claims-freeze"},
    )
    item = {"name": name, "requested_url": url}
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read()
            final_url = resp.geturl()
            status = getattr(resp, "status", None)
            headers = resp.headers
        path = raw / f"{name}.html"
        path.write_bytes(body)
        item.update({
            "status": status,
            "final_url": final_url,
            "content_type": headers.get("Content-Type"),
            "etag": headers.get("ETag"),
            "last_modified": headers.get("Last-Modified"),
            "sha256": hashlib.sha256(body).hexdigest(),
            "bytes": len(body),
            "raw_file": f"claims_freeze/raw/{path.name}",
            "error": None,
        })
        print(f"CLAIM_FREEZE_OK {name} bytes={len(body)}")
    except Exception as exc:
        errors += 1
        item.update({
            "status": None,
            "final_url": None,
            "content_type": None,
            "etag": None,
            "last_modified": None,
            "sha256": None,
            "bytes": None,
            "raw_file": None,
            "error": f"{type(exc).__name__}: {exc}",
        })
        print(f"CLAIM_FREEZE_ERROR {name}: {type(exc).__name__}: {exc}")
    manifest["targets"].append(item)

(out / "CLAIMS_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2, ensure_ascii=True) + "\n",
    encoding="utf-8",
)

if errors:
    raise SystemExit(f"Public claims freeze incomplete: {errors} target(s) failed.")
'@ | python -

if ($LASTEXITCODE -ne 0) { throw "Public claims freeze failed." }

@(
    "BASELINES_COMPLETE",
    "backend_commit=$backendHead",
    "known_issue_sources=$($knownFiles.Count)",
    "claims_manifest=claims_freeze/CLAIMS_MANIFEST.json",
    "prepared_at_utc=$([DateTime]::UtcNow.ToString('o'))"
) | Set-Content (Join-Path $Root "BASELINES_SUMMARY.txt") -Encoding UTF8

Write-Host ""
Write-Host "BASELINES COMPLETE"
Write-Host "backend_commit=$backendHead"
Write-Host "known_issue_sources=$($knownFiles.Count)"
Write-Host "Run scripts\03_verify_baselines.ps1 next."
