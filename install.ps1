param(
  [ValidateSet("minimal", "full")]
  [string]$Profile = "minimal",
  [string]$HostId = "codex",
  [string]$TargetRoot = '',
  [switch]$InstallExternal,
  [switch]$StrictOffline,
  [switch]$RequireClosedReady,
  [switch]$AllowExternalSkillFallback,
  [switch]$SkipRuntimeFreshnessGate,
  [Alias('?')]
  [switch]$Help
)
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$helperPath = Join-Path $RepoRoot 'scripts\common\vibe-governance-helpers.ps1'
$cliMain = Join-Path $RepoRoot 'apps\vgo-cli\src\vgo_cli\main.py'

function Show-WrapperUsage {
  Write-Output 'Usage: install.ps1 [-Profile minimal|full] [-HostId <id>] [-TargetRoot <path>] [-InstallExternal] [-StrictOffline] [-RequireClosedReady] [-AllowExternalSkillFallback] [-SkipRuntimeFreshnessGate] [-Help|-?]'
  Write-Output 'Installs the governed VCO runtime for the requested host without falling back to legacy installer scripts.'
}

if ($Help) {
  Show-WrapperUsage
  exit 0
}

if (Test-Path -LiteralPath $helperPath) {
  . $helperPath
  $HostId = Resolve-VgoHostId -HostId $HostId
}

# Invoke-InstalledRuntimeFreshnessGate semantics are delegated to vgo_cli.main.
# Codex host payload materialization, including config/plugins-manifest.codex.json,
# remains delegated to vgo_cli.main / installer-core.

function Get-PreferredPythonInvocation {
  if (Get-Command Get-VgoPythonCommand -ErrorAction SilentlyContinue) {
    try {
      return Get-VgoPythonCommand
    } catch {
    }
  }

  foreach ($candidate in @(
    [pscustomobject]@{ name = 'python3'; prefix_arguments = @() },
    [pscustomobject]@{ name = 'python'; prefix_arguments = @() },
    [pscustomobject]@{ name = 'py'; prefix_arguments = @('-3') }
  )) {
    $command = Get-Command ([string]$candidate.name) -ErrorAction SilentlyContinue
    if ($command) {
      return [pscustomobject]@{ host_path = $command.Source; prefix_arguments = @($candidate.prefix_arguments) }
    }
  }

  $pyFallbacks = @()
  if (-not [string]::IsNullOrWhiteSpace($env:SystemRoot)) {
    $pyFallbacks += (Join-Path $env:SystemRoot 'py.exe')
  }
  $pyFallbacks += 'C:\Windows\py.exe'
  foreach ($candidate in ($pyFallbacks | Select-Object -Unique)) {
    if (-not [string]::IsNullOrWhiteSpace($candidate) -and (Test-Path -LiteralPath $candidate)) {
      return [pscustomobject]@{
        host_path = [System.IO.Path]::GetFullPath($candidate)
        prefix_arguments = @('-3')
      }
    }
  }
  throw 'Python 3.10+ is required to launch vgo-cli.'
}

$pythonInvocation = $null
if (Test-Path -LiteralPath $cliMain) {
  $pythonInvocation = Get-PreferredPythonInvocation
}

if ($null -ne $pythonInvocation) {
  $pythonPathEntries = @((Join-Path $RepoRoot 'apps\vgo-cli\src'))
  if (-not [string]::IsNullOrWhiteSpace($env:PYTHONPATH)) {
    $pythonPathEntries += $env:PYTHONPATH
  }
  $env:PYTHONPATH = ($pythonPathEntries -join [System.IO.Path]::PathSeparator)

  $argsList = @($pythonInvocation.prefix_arguments)
  $argsList += @(
    '-m', 'vgo_cli.main',
    'install',
    '--repo-root', $RepoRoot,
    '--frontend', 'powershell',
    '--profile', $Profile,
    '--host', $HostId
  )
  if (-not [string]::IsNullOrWhiteSpace($TargetRoot)) { $argsList += @('--target-root', $TargetRoot) }
  if ($InstallExternal) { $argsList += '--install-external' }
  if ($StrictOffline) { $argsList += '--strict-offline' }
  if ($RequireClosedReady) { $argsList += '--require-closed-ready' }
  if ($AllowExternalSkillFallback) { $argsList += '--allow-external-skill-fallback' }
  if ($SkipRuntimeFreshnessGate) { $argsList += '--skip-runtime-freshness-gate' }

  & $pythonInvocation.host_path @argsList
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  exit 0
}

throw "Missing required vgo-cli entrypoint at $cliMain. The PowerShell install wrapper no longer falls back to legacy installer scripts."
