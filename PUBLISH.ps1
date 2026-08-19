param(
    [string]$RepoUrl = "https://github.com/simon9679/evaleval-audit.git"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\TEST_INDEX.json")) {
    throw "Run this script from the extracted repository root."
}

python .\tools\verify_public_bundle.py
if ($LASTEXITCODE -ne 0) {
    throw "Publication verification failed."
}

if (-not (Test-Path ".\.git")) {
    git init
}

git add --all

$status = git status --porcelain
if (-not $status) {
    Write-Host "No changes to commit."
} else {
    git commit -m "Initial public EvalEval audit release"
}

git branch -M main

$remotes = @(git remote)

if ($remotes -notcontains "origin") {
    git remote add origin $RepoUrl
}
else {
    $remote = git remote get-url origin

    if ($remote -ne $RepoUrl) {
        throw "Existing origin is $remote, expected $RepoUrl"
    }
}

git push -u origin main
