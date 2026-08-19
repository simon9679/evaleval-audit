$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$AuditRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Freeze = Join-Path $AuditRoot "freeze"
$Repos = Join-Path $Freeze "repos"
$HF = Join-Path $Freeze "hf"
$Meta = Join-Path $Freeze "metadata"
$Logs = Join-Path $AuditRoot "logs"

New-Item -ItemType Directory -Force -Path $Repos,$HF,$Meta,$Logs | Out-Null

$Transcript = Join-Path $Logs "00_freeze_transcript.txt"
Start-Transcript -Path $Transcript -Append | Out-Null

function Run-Git {
    param([Parameter(Mandatory=$true)][string[]]$GitArgs)
    & git @GitArgs
    if ($LASTEXITCODE -ne 0) { throw "git failed: git $($GitArgs -join ' ')" }
}

function Prepare-FrozenRepo {
    param(
        [Parameter(Mandatory=$true)][string]$Url,
        [Parameter(Mandatory=$true)][string]$Dest
    )

    if (Test-Path (Join-Path $Dest ".git")) {
        $sha = (& git -C $Dest rev-parse HEAD).Trim()
        if ($LASTEXITCODE -ne 0 -or -not $sha) {
            throw "Cannot read existing frozen HEAD: $Dest"
        }
        Write-Host "REUSE FROZEN REPO: $Dest @ $sha"
        return $sha
    }

    Run-Git -GitArgs @("clone","--no-tags",$Url,$Dest)
    $sha = (& git -C $Dest rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0 -or -not $sha) {
        throw "Cannot read cloned HEAD: $Dest"
    }
    Run-Git -GitArgs @("-C",$Dest,"checkout","--detach",$sha)
    Write-Host "FROZEN REPO: $Dest @ $sha"
    return $sha
}

try {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw "Git not found in PATH."
    }
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        throw "Python not found in PATH."
    }

    $backend = Join-Path $Repos "eval_cards_backend_pipeline"
    $registry = Join-Path $Repos "eval-card-registry"
    $eeeRepo = Join-Path $Repos "every_eval_ever"

    # Existing repositories are reused exactly at their current detached HEAD.
    # This prevents a retry after an interrupted download from silently moving
    # the audit object to a newer main branch commit.
    $backendSha = Prepare-FrozenRepo `
        "https://github.com/evaleval/eval_cards_backend_pipeline.git" $backend
    $registrySha = Prepare-FrozenRepo `
        "https://github.com/evaleval/eval-card-registry.git" $registry
    $eeeCodeSha = Prepare-FrozenRepo `
        "https://github.com/evaleval/every_eval_ever.git" $eeeRepo

    $syncPath = Join-Path $backend ".github\workflows\sync.yml"
    if (-not (Test-Path $syncPath)) { throw "Missing production workflow: $syncPath" }
    $sync = Get-Content $syncPath -Raw

    function Extract-YamlEnv([string]$Name) {
        $pattern = '(?m)^\s*' + [regex]::Escape($Name) + ':\s*([^\s#]+)'
        $m = [regex]::Match($sync, $pattern)
        if (-not $m.Success) { return $null }
        return $m.Groups[1].Value.Trim()
    }

    $eeeRevision = Extract-YamlEnv "EEE_REVISION"
    $registryDataRevision = Extract-YamlEnv "ENTITY_REGISTRY_REVISION"
    $cardsRevision = Extract-YamlEnv "BENCHMARK_METADATA_REVISION"
    $resolverRefDeclared = Extract-YamlEnv "RESOLVER_REF"

    if (-not $eeeRevision) { throw "EEE_REVISION not found in production sync.yml" }
    if (-not $registryDataRevision) { throw "ENTITY_REGISTRY_REVISION not found in production sync.yml" }
    if (-not $cardsRevision) { throw "BENCHMARK_METADATA_REVISION not found in production sync.yml" }
    if (-not $resolverRefDeclared) { $resolverRefDeclared = "main" }

    # The registry repository itself was frozen before any HF download.
    # If production declares "main", record the already-frozen registry SHA.
    # For another ref, resolve only from the local frozen repository.
    if ($resolverRefDeclared -eq "main") {
        $resolverResolvedSha = $registrySha
    } else {
        $resolverResolvedSha = (& git -C $registry rev-parse $resolverRefDeclared 2>$null).Trim()
        if (-not $resolverResolvedSha) {
            throw "Cannot resolve RESOLVER_REF=$resolverRefDeclared in frozen registry repository"
        }
    }

    # Write the lock before any network-heavy dataset download.
    # A failed/retried download therefore cannot change the audit object.
    $lock = [ordered]@{
        schema_version = 1
        locked_at_utc = [DateTime]::UtcNow.ToString("o")
        repos = [ordered]@{
            eval_cards_backend_pipeline = $backendSha
            eval_card_registry = $registrySha
            every_eval_ever = $eeeCodeSha
        }
        production_inputs = [ordered]@{
            EEE_REVISION = $eeeRevision
            ENTITY_REGISTRY_REVISION = $registryDataRevision
            BENCHMARK_METADATA_REVISION = $cardsRevision
            RESOLVER_REF_DECLARED = $resolverRefDeclared
            RESOLVER_REF_RESOLVED_SHA = $resolverResolvedSha
        }
    }
    $lock | ConvertTo-Json -Depth 10 |
        Set-Content -Encoding UTF8 (Join-Path $Freeze "FREEZE_LOCK.json")

    & python -c "import huggingface_hub" 2>$null
    if ($LASTEXITCODE -ne 0) {
        & python -m pip install --user "huggingface_hub>=0.24"
        if ($LASTEXITCODE -ne 0) { throw "Failed to install huggingface_hub" }
    }

    $py = @'
from huggingface_hub import snapshot_download
import json
import os
import time


def extended_windows_path(path):
    """Preserve Windows path components that end in dots/spaces."""
    if os.name != "nt":
        return path
    path = os.path.abspath(path)
    if path.startswith("\\\\?\\"):
        return path
    if path.startswith("\\\\"):
        return "\\\\?\\UNC\\" + path[2:]
    return "\\\\?\\" + path


targets = json.loads(os.environ["EVALEVAL_FREEZE_TARGETS"])

for t in targets:
    attempt = 0
    local_dir = extended_windows_path(t["local_dir"])
    if os.name == "nt":
        print(f"WINDOWS EXTENDED LOCAL DIR {local_dir}", flush=True)
    while True:
        attempt += 1
        print(f"FREEZE HF {t['repo_id']} @ {t['revision']} attempt={attempt}", flush=True)
        try:
            path = snapshot_download(
                repo_id=t["repo_id"],
                repo_type="dataset",
                revision=t["revision"],
                local_dir=local_dir,
                max_workers=1,
            )
            print("DONE", path, flush=True)
            break
        except Exception as e:
            msg = str(e)
            if "429" not in msg and "Too Many Requests" not in msg:
                raise
            delay = 330
            print(
                f"RATE_LIMIT_429 retry_after_seconds={delay} "
                f"repo={t['repo_id']} attempt={attempt}",
                flush=True,
            )
            time.sleep(delay)
'@

    $eeeLocalDir = Join-Path $HF "EEE_datastore"
    if ($env:EVALEVAL_EEE_LOCAL_DIR) {
        $eeeLocalDir = $env:EVALEVAL_EEE_LOCAL_DIR
        Write-Host "EEE LOCAL DIR OVERRIDE: $eeeLocalDir"
    }

    $targets = @(
        @{
            repo_id="evaleval/EEE_datastore";
            revision=$eeeRevision;
            local_dir=$eeeLocalDir
        },
        @{
            repo_id="evaleval/entity-registry-data";
            revision=$registryDataRevision;
            local_dir=(Join-Path $HF "entity-registry-data")
        },
        @{
            repo_id="evaleval/auto-benchmarkcards";
            revision=$cardsRevision;
            local_dir=(Join-Path $HF "auto-benchmarkcards")
        }
    )

    $env:EVALEVAL_FREEZE_TARGETS = ($targets | ConvertTo-Json -Compress)
    $py | python -
    if ($LASTEXITCODE -ne 0) { throw "Hugging Face snapshot download failed." }
    Remove-Item Env:EVALEVAL_FREEZE_TARGETS -ErrorAction SilentlyContinue

    $manifest = [ordered]@{
        schema_version = 1
        frozen_at_utc = [DateTime]::UtcNow.ToString("o")
        audit_root = $AuditRoot
        repos = [ordered]@{
            eval_cards_backend_pipeline = @{
                url = "https://github.com/evaleval/eval_cards_backend_pipeline.git"
                commit = $backendSha
            }
            eval_card_registry = @{
                url = "https://github.com/evaleval/eval-card-registry.git"
                commit = $registrySha
            }
            every_eval_ever = @{
                url = "https://github.com/evaleval/every_eval_ever.git"
                commit = $eeeCodeSha
            }
        }
        production_inputs = [ordered]@{
            EEE_REVISION = $eeeRevision
            ENTITY_REGISTRY_REVISION = $registryDataRevision
            BENCHMARK_METADATA_REVISION = $cardsRevision
            RESOLVER_REF_DECLARED = $resolverRefDeclared
            RESOLVER_REF_RESOLVED_SHA = $resolverResolvedSha
        }
        environment = [ordered]@{
            powershell = $PSVersionTable.PSVersion.ToString()
            python = (& python --version 2>&1 | Out-String).Trim()
            git = (& git --version | Out-String).Trim()
            os = [System.Environment]::OSVersion.VersionString
        }
    }

    $manifestPath = Join-Path $Freeze "FREEZE_MANIFEST.json"
    $manifest | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 $manifestPath

    $summary = @"
EVALEVAL AUDIT FREEZE COMPLETE
UTC: $($manifest.frozen_at_utc)

CODE:
eval_cards_backend_pipeline = $backendSha
eval-card-registry          = $registrySha
every_eval_ever             = $eeeCodeSha

PRODUCTION DATA INPUTS:
EEE_REVISION                 = $eeeRevision
ENTITY_REGISTRY_REVISION     = $registryDataRevision
BENCHMARK_METADATA_REVISION  = $cardsRevision
RESOLVER_REF declared        = $resolverRefDeclared
RESOLVER_REF resolved SHA    = $resolverResolvedSha

HF snapshots:
$HF\EEE_datastore
$HF\entity-registry-data
$HF\auto-benchmarkcards
"@
    $summary | Set-Content -Encoding UTF8 (Join-Path $Freeze "FREEZE_SUMMARY.txt")

    Write-Host ""
    Write-Host "HASHING FROZEN CONTENT"

    # Hash with Python using the Windows extended-path namespace. PowerShell's
    # standard filesystem cmdlets can normalize path components ending in dots.
    # Hugging Face's local .cache directory is transport metadata, not part of
    # the frozen scientific object, so it is intentionally excluded.
    $env:EVALEVAL_AUDIT_ROOT = $AuditRoot
    $hashPy = @'
import hashlib
import os


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
freeze_root = audit_root + r"\freeze"
out_path = audit_root + r"\freeze\SHA256SUMS.txt"

rows = []
for dirpath, dirnames, filenames in os.walk(freeze_root):
    # Exclude source-control internals and Hugging Face transport/cache metadata.
    lowered = dirpath.lower().replace("/", "\\")
    filtered = []
    for d in dirnames:
        if d == ".git":
            continue
        if d == ".cache" and "\\hf\\" in (lowered + "\\"):
            continue
        filtered.append(d)
    dirnames[:] = filtered

    for name in filenames:
        if name in {"SHA256SUMS.txt", "VERIFY_FREEZE.txt"}:
            continue
        full = os.path.join(dirpath, name)
        rel = full[len(audit_root) + 1:].replace("\\", "/")
        h = hashlib.sha256()
        with open(full, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        rows.append((rel, h.hexdigest()))

rows.sort(key=lambda x: x[0])
with open(out_path, "w", encoding="ascii", newline="\n") as out:
    for rel, digest in rows:
        out.write(f"{digest}  {rel}\n")
print(f"HASHED_FILES={len(rows)}", flush=True)
'@
    $hashPy | python -
    if ($LASTEXITCODE -ne 0) { throw "Frozen-content hashing failed." }
    Remove-Item Env:EVALEVAL_AUDIT_ROOT -ErrorAction SilentlyContinue

    Write-Host ""
    Write-Host "FREEZE COMPLETE"
    Write-Host "Run scripts\01_verify_freeze.ps1 next."
}
finally {
    Remove-Item Env:EVALEVAL_FREEZE_TARGETS -ErrorAction SilentlyContinue
    Remove-Item Env:EVALEVAL_AUDIT_ROOT -ErrorAction SilentlyContinue
    Stop-Transcript | Out-Null
}
