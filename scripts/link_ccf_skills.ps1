# Recreate the machine-local project skill root for the vendored CCFA skills.
#
# CCFA-Skills/ is tracked in this repository and is the single source of truth.
# The harness scans a project skill root at <repo>/.dsh/skills (rank 100, above
# the user roots), but that layer holds directory junctions and is therefore
# gitignored. A fresh clone needs this script once to expose the 17
# <name>/SKILL.md bundles to the `skill` tool for this workspace.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\link_ccf_skills.ps1
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\link_ccf_skills.ps1 -Remove
#
# Junctions are used instead of copies so no second copy of the content exists;
# the skill loader reads SKILL.md through the link and reports the resolved path.

[CmdletBinding()]
param(
    [switch]$Remove
)

$ErrorActionPreference = 'Stop'

$repo = Split-Path -Parent $PSScriptRoot
$sourceDir = Join-Path $repo 'CCFA-Skills'
$targetDir = Join-Path $repo '.dsh\skills'

if ($Remove) {
    if (Test-Path -LiteralPath $targetDir) {
        Remove-Item -LiteralPath $targetDir -Recurse -Force
        Write-Host "removed $targetDir"
    } else {
        Write-Host "nothing to remove: $targetDir"
    }
    return
}

if (-not (Test-Path -LiteralPath $sourceDir)) {
    throw "missing vendored source directory: $sourceDir"
}

$bundles = @(
    Get-ChildItem -LiteralPath $sourceDir -Directory |
        Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') }
)
if ($bundles.Count -eq 0) {
    throw "no <name>/SKILL.md bundles found under $sourceDir"
}

New-Item -ItemType Directory -Path $targetDir -Force | Out-Null

foreach ($bundle in $bundles) {
    $link = Join-Path $targetDir $bundle.Name
    if (Test-Path -LiteralPath $link) {
        Remove-Item -LiteralPath $link -Recurse -Force
    }
    New-Item -ItemType Junction -Path $link -Target $bundle.FullName | Out-Null
}

Write-Host "linked $($bundles.Count) skill bundles into $targetDir"
