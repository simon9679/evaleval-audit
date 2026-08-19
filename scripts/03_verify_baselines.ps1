$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$KnownManifest = Join-Path $Root "known_issues\KNOWN_ISSUES_MANIFEST.json"
$ClaimsManifest = Join-Path $Root "claims_freeze\CLAIMS_MANIFEST.json"

if (-not (Test-Path $KnownManifest)) { throw "Missing known-issues manifest." }
if (-not (Test-Path $ClaimsManifest)) { throw "Missing claims manifest." }

$known = Get-Content $KnownManifest -Raw | ConvertFrom-Json
$claims = Get-Content $ClaimsManifest -Raw | ConvertFrom-Json

$bad = 0
$ok = 0

foreach ($item in $known) {
    $path = Join-Path $Root ($item.frozen_copy -replace '/', '\')
    if (-not (Test-Path $path)) {
        Write-Host "MISSING $($item.frozen_copy)"
        $bad++
        continue
    }
    $actual = (Get-FileHash $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $item.sha256) {
        Write-Host "BAD_HASH $($item.frozen_copy)"
        $bad++
    } else {
        $ok++
    }
}

foreach ($item in $claims.targets) {
    if ($item.error) {
        Write-Host "CLAIM_FETCH_ERROR $($item.name): $($item.error)"
        $bad++
        continue
    }
    $path = Join-Path $Root ($item.raw_file -replace '/', '\')
    if (-not (Test-Path $path)) {
        Write-Host "MISSING $($item.raw_file)"
        $bad++
        continue
    }
    $actual = (Get-FileHash $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $item.sha256) {
        Write-Host "BAD_HASH $($item.raw_file)"
        $bad++
    } else {
        $ok++
    }
}

@(
    "VERIFY_BASELINES",
    "ok=$ok",
    "bad=$bad"
) | Set-Content (Join-Path $Root "VERIFY_BASELINES.txt") -Encoding UTF8

Write-Host "VERIFY_BASELINES"
Write-Host "ok=$ok"
Write-Host "bad=$bad"

if ($bad -ne 0) { exit 1 }
