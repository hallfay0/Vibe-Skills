param(
    [string]$SkillsRoot = "",
    [string]$PackManifestPath = ""
)

$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "lib\VibeOfflineSkillsAudit.ps1")
. (Join-Path $PSScriptRoot "lib\VibeOfflineSkillsAudit.Suites.ps1")

$summary = Invoke-VibeOfflineRequiredSkillsAudit -ScriptRoot $PSScriptRoot -SkillsRoot $SkillsRoot -PackManifestPath $PackManifestPath
if (-not $summary.gate_passed) {
    exit 1
}

Write-Host "Vibe offline required-skills audit passed." -ForegroundColor Green
exit 0
