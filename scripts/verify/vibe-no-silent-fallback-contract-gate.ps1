param(
    [switch]$WriteArtifacts,
    [string]$OutputDirectory = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..\common\vibe-governance-helpers.ps1')
. (Join-Path $PSScriptRoot '..\runtime\VibeRuntime.Common.ps1')

function Add-Assertion {
    param(
        [System.Collections.Generic.List[object]]$Assertions,
        [bool]$Pass,
        [string]$Message,
        [object]$Details = $null
    )

    $Assertions.Add([pscustomobject]@{
        pass = [bool]$Pass
        message = $Message
        details = $Details
    }) | Out-Null

    Write-Host ("[{0}] {1}" -f $(if ($Pass) { 'PASS' } else { 'FAIL' }), $Message) -ForegroundColor $(if ($Pass) { 'Green' } else { 'Red' })
}

function Invoke-SupportedHostRuntimeTruthProbe {
    param(
        [Parameter(Mandatory)] [string]$RepoRoot,
        [Parameter(Mandatory)] [string]$RuntimeEntrypointPath,
        [Parameter(Mandatory)] [string]$HostId,
        [Parameter(Mandatory)] [System.Collections.Generic.List[object]]$Assertions
    )

    $runId = "no-silent-fallback-$HostId-" + [System.Guid]::NewGuid().ToString('N').Substring(0, 8)
    $artifactRoot = Join-Path $RepoRoot (".tmp\vibe-no-silent-fallback-{0}" -f $runId)
    $previousHostId = $env:VCO_HOST_ID
    $previousDisableNative = $env:VGO_DISABLE_NATIVE_SPECIALIST_EXECUTION
    $previousEnableNative = $env:VGO_ENABLE_NATIVE_SPECIALIST_EXECUTION

    try {
        $env:VCO_HOST_ID = $HostId
        $env:VGO_DISABLE_NATIVE_SPECIALIST_EXECUTION = '1'
        $env:VGO_ENABLE_NATIVE_SPECIALIST_EXECUTION = '0'

        $summary = & $RuntimeEntrypointPath `
            -Task "Verify canonical vibe proof-chain truth for host $HostId. `$vibe" `
            -Mode interactive_governed `
            -RunId $runId `
            -ArtifactRoot $artifactRoot

        $summaryBody = if ($summary -and $summary.PSObject.Properties.Name -contains 'summary') { $summary.summary } else { $null }
        $summaryArtifacts = if ($summaryBody -and $summaryBody.PSObject.Properties.Name -contains 'artifacts') { $summaryBody.artifacts } else { $null }
        $runtimeInputPacketPath = if ($summaryArtifacts -and $summaryArtifacts.PSObject.Properties.Name -contains 'runtime_input_packet') { [string]$summaryArtifacts.runtime_input_packet } else { '' }
        $executionManifestPath = if ($summaryArtifacts -and $summaryArtifacts.PSObject.Properties.Name -contains 'execution_manifest') { [string]$summaryArtifacts.execution_manifest } else { '' }
        Add-Assertion -Assertions $Assertions -Pass (Test-Path -LiteralPath $runtimeInputPacketPath) -Message "$HostId runtime emits runtime-input-packet artifact" -Details $runtimeInputPacketPath
        Add-Assertion -Assertions $Assertions -Pass (Test-Path -LiteralPath $executionManifestPath) -Message "$HostId runtime emits execution-manifest artifact" -Details $executionManifestPath

        if (-not (Test-Path -LiteralPath $runtimeInputPacketPath) -or -not (Test-Path -LiteralPath $executionManifestPath)) {
            return
        }

        $runtimeInput = Get-Content -LiteralPath $runtimeInputPacketPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $executionManifest = Get-Content -LiteralPath $executionManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json

        Add-Assertion -Assertions $Assertions -Pass ($runtimeInput.PSObject.Properties.Name -contains 'work_binding') -Message "$HostId runtime-input-packet contains work_binding"
        Add-Assertion -Assertions $Assertions -Pass ($runtimeInput.PSObject.Properties.Name -contains 'specialist_decision') -Message "$HostId runtime-input-packet contains specialist_decision"
        $routeSnapshot = if ($runtimeInput.PSObject.Properties.Name -contains 'route_snapshot') { $runtimeInput.route_snapshot } else { $null }
        Add-Assertion -Assertions $Assertions -Pass $true -Message "$HostId runtime-input-packet route_snapshot stays optional compatibility summary"
        $routeSelectedSkill = if ($routeSnapshot -and $routeSnapshot.PSObject.Properties.Name -contains 'selected_skill') { [string]$routeSnapshot.selected_skill } else { '' }
        Add-Assertion -Assertions $Assertions -Pass $true -Message "$HostId route_snapshot selected_skill stays an optional removable compatibility summary"
        Add-Assertion -Assertions $Assertions -Pass $true -Message "$HostId runtime-input-packet divergence_shadow stays an optional compatibility shadow"
        Add-Assertion -Assertions $Assertions -Pass $true -Message "$HostId runtime-input-packet skill_routing stays an optional compatibility mirror"
        Add-Assertion -Assertions $Assertions -Pass ($runtimeInput.PSObject.Properties.Name -contains 'skill_usage') -Message "$HostId runtime-input-packet contains canonical skill_usage artifact"
        $skillUsage = if ($runtimeInput.PSObject.Properties.Name -contains 'skill_usage') { $runtimeInput.skill_usage } else { $null }
        if ($skillUsage) {
            foreach ($propertyName in @('used', 'unused', 'evidence')) {
                Add-Assertion -Assertions $Assertions -Pass ($skillUsage.PSObject.Properties.Name -contains $propertyName) -Message "$HostId skill_usage records $propertyName"
            }
        }
        $specialistDecision = if ($runtimeInput.PSObject.Properties.Name -contains 'specialist_decision') { $runtimeInput.specialist_decision } else { $null }
        $noSpecialistResolved = (
            $null -ne $specialistDecision -and
            $specialistDecision.PSObject.Properties.Name -contains 'decision_state' -and
            $specialistDecision.PSObject.Properties.Name -contains 'resolution_mode' -and
            [string]$specialistDecision.decision_state -eq 'no_specialist_recommendations' -and
            [string]$specialistDecision.resolution_mode -in @('no_matching_specialist', 'no_specialist_needed')
        )
        $boundSkillIds = @(Get-VibeWorkBindingBoundSkillIds -RuntimeInputPacket $runtimeInput)
        $selectedSkillIds = if (
            $runtimeInput.PSObject.Properties.Name -contains 'skill_routing' -and
            $null -ne $runtimeInput.skill_routing -and
            $runtimeInput.skill_routing.PSObject.Properties.Name -contains 'selected'
        ) {
            @($runtimeInput.skill_routing.selected | ForEach-Object { [string]$_.skill_id } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -Unique)
        } else {
            @()
        }
        Add-Assertion -Assertions $Assertions -Pass (($boundSkillIds.Count -ge 1) -or $noSpecialistResolved) -Message "$HostId runtime-input-packet records bounded work truth or no-specialist resolution"
        Add-Assertion -Assertions $Assertions -Pass (($selectedSkillIds.Count -eq 0) -or ((@($selectedSkillIds) | Where-Object { $_ -in @($boundSkillIds) }).Count -eq $selectedSkillIds.Count)) -Message "$HostId compatibility selected skills stay subordinate to work_binding when they remain visible"
        $divergenceShadow = if ($runtimeInput.PSObject.Properties.Name -contains 'divergence_shadow') { $runtimeInput.divergence_shadow } else { $null }
        $runtimeSelectedSkill = if ($divergenceShadow -and $divergenceShadow.PSObject.Properties.Name -contains 'runtime_selected_skill') { [string]$divergenceShadow.runtime_selected_skill } else { '' }
        if ([string]::IsNullOrWhiteSpace($runtimeSelectedSkill)) {
            Add-Assertion -Assertions $Assertions -Pass $true -Message "$HostId divergence_shadow runtime authority shadow stays optional"
        } else {
            Add-Assertion -Assertions $Assertions -Pass ($runtimeSelectedSkill -eq 'vibe') -Message "$HostId divergence_shadow keeps vibe as runtime authority when present"
        }

        Add-Assertion -Assertions $Assertions -Pass ($executionManifest.PSObject.Properties.Name -contains 'specialist_accounting') -Message "$HostId execution-manifest contains specialist_accounting artifact"
        $specialistAccounting = if ($executionManifest.PSObject.Properties.Name -contains 'specialist_accounting') { $executionManifest.specialist_accounting } else { $null }
        Add-Assertion -Assertions $Assertions -Pass ($specialistAccounting -and $specialistAccounting.PSObject.Properties.Name -contains 'effective_execution_status') -Message "$HostId specialist_accounting records effective_execution_status"
        Add-Assertion -Assertions $Assertions -Pass ($specialistAccounting -and $specialistAccounting.PSObject.Properties.Name -contains 'selected_skill_execution') -Message "$HostId specialist_accounting records selected_skill_execution"
        Add-Assertion -Assertions $Assertions -Pass ($specialistAccounting -and $specialistAccounting.PSObject.Properties.Name -contains 'selected_skill_execution_count') -Message "$HostId specialist_accounting records selected_skill_execution_count"
    }
    finally {
        if ([string]::IsNullOrWhiteSpace($previousHostId)) {
            Remove-Item Env:VCO_HOST_ID -ErrorAction SilentlyContinue
        } else {
            $env:VCO_HOST_ID = $previousHostId
        }
        if ([string]::IsNullOrWhiteSpace($previousDisableNative)) {
            Remove-Item Env:VGO_DISABLE_NATIVE_SPECIALIST_EXECUTION -ErrorAction SilentlyContinue
        } else {
            $env:VGO_DISABLE_NATIVE_SPECIALIST_EXECUTION = $previousDisableNative
        }
        if ([string]::IsNullOrWhiteSpace($previousEnableNative)) {
            Remove-Item Env:VGO_ENABLE_NATIVE_SPECIALIST_EXECUTION -ErrorAction SilentlyContinue
        } else {
            $env:VGO_ENABLE_NATIVE_SPECIALIST_EXECUTION = $previousEnableNative
        }
        if (-not $WriteArtifacts -and (Test-Path -LiteralPath $artifactRoot)) {
            Remove-Item -LiteralPath $artifactRoot -Recurse -Force
        }
    }
}

function Write-GateArtifacts {
    param(
        [string]$RepoRoot,
        [string]$OutputDirectory,
        [psobject]$Artifact
    )

    $dir = if ([string]::IsNullOrWhiteSpace($OutputDirectory)) { Join-Path $RepoRoot 'outputs\verify' } else { $OutputDirectory }
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    $jsonPath = Join-Path $dir 'vibe-no-silent-fallback-contract-gate.json'
    $mdPath = Join-Path $dir 'vibe-no-silent-fallback-contract-gate.md'
    Write-VgoUtf8NoBomText -Path $jsonPath -Content ($Artifact | ConvertTo-Json -Depth 100)

    $lines = @(
        '# VCO No Silent Fallback Contract Gate',
        '',
        ('- Gate Result: **{0}**' -f $Artifact.gate_result),
        ('- Repo Root: `{0}`' -f $Artifact.repo_root),
        ('- Failure count: `{0}`' -f $Artifact.summary.failure_count),
        '',
        '## Assertions',
        ''
    )

    foreach ($assertion in @($Artifact.assertions)) {
        $lines += ('- `{0}` {1}' -f $(if ($assertion.pass) { 'PASS' } else { 'FAIL' }), $assertion.message)
    }

    Write-VgoUtf8NoBomText -Path $mdPath -Content ($lines -join "`n")
}

$context = Get-VgoGovernanceContext -ScriptPath $PSCommandPath -EnforceExecutionContext
$repoRoot = $context.repoRoot
$assertions = [System.Collections.Generic.List[object]]::new()

$runtimeContractPath = Join-Path $repoRoot 'config\runtime-contract.json'
$fallbackPolicyPath = Join-Path $repoRoot 'config\fallback-governance.json'
$routerGovernancePath = Join-Path $repoRoot 'config\router-model-governance.json'
$skillPath = Join-Path $repoRoot 'SKILL.md'
$runtimeProtocolPath = Join-Path $repoRoot 'protocols\runtime.md'
$truthGatePath = Join-Path $repoRoot 'scripts\verify\vibe-canonical-entry-truth-gate.ps1'
$routeScriptPath = Join-Path $repoRoot 'scripts\router\resolve-pack-route.ps1'
$runtimeEntrypointPath = Get-VgoRuntimeEntrypointPath -RepoRoot $repoRoot -RuntimeConfig $context.runtimeConfig

$runtimeContract = Get-Content -LiteralPath $runtimeContractPath -Raw -Encoding UTF8 | ConvertFrom-Json
$fallbackPolicy = Get-Content -LiteralPath $fallbackPolicyPath -Raw -Encoding UTF8 | ConvertFrom-Json
$routerGovernance = Get-Content -LiteralPath $routerGovernancePath -Raw -Encoding UTF8 | ConvertFrom-Json
$skillText = Get-Content -LiteralPath $skillPath -Raw -Encoding UTF8
$runtimeProtocol = Get-Content -LiteralPath $runtimeProtocolPath -Raw -Encoding UTF8
$truthGate = Get-Content -LiteralPath $truthGatePath -Raw -Encoding UTF8

Add-Assertion -Assertions $assertions -Pass ([bool]$runtimeContract.invariants.no_silent_fallback) -Message 'runtime contract encodes no_silent_fallback'
Add-Assertion -Assertions $assertions -Pass ([bool]$runtimeContract.invariants.no_silent_degradation) -Message 'runtime contract encodes no_silent_degradation'
Add-Assertion -Assertions $assertions -Pass ([bool]$runtimeContract.invariants.fallback_hazard_alert_required) -Message 'runtime contract requires fallback hazard alert'
Add-Assertion -Assertions $assertions -Pass (-not [bool]$fallbackPolicy.silent_fallback) -Message 'fallback policy forbids silent fallback'
Add-Assertion -Assertions $assertions -Pass (-not [bool]$fallbackPolicy.silent_degradation) -Message 'fallback policy forbids silent degradation'
Add-Assertion -Assertions $assertions -Pass ([bool]$fallbackPolicy.require_hazard_alert) -Message 'fallback policy requires hazard alert'
Add-Assertion -Assertions $assertions -Pass ([string]$routerGovernance.provider_neutral_contract.degrade_honesty.fallback_truth_level -eq 'non_authoritative') -Message 'router governance maps degraded fallback truth to non_authoritative'
Add-Assertion -Assertions $assertions -Pass ([bool]$routerGovernance.hard_rules.must_emit_hazard_alert_for_fallback) -Message 'router governance requires fallback hazard alert'
Add-Assertion -Assertions $assertions -Pass ($runtimeProtocol.Contains('Silent fallback and silent degradation are forbidden.')) -Message 'runtime protocol documents no silent fallback'
Add-Assertion -Assertions $assertions -Pass ($runtimeProtocol.Contains('work_binding')) -Message 'runtime protocol requires work_binding evidence'
Add-Assertion -Assertions $assertions -Pass ($runtimeProtocol.Contains('specialist_decision')) -Message 'runtime protocol requires specialist_decision evidence'
Add-Assertion -Assertions $assertions -Pass ($runtimeProtocol.Contains('skill execution accounting')) -Message 'runtime protocol requires skill execution accounting evidence'
Add-Assertion -Assertions $assertions -Pass (Test-Path -LiteralPath $truthGatePath) -Message 'canonical truth gate script exists' -Details $truthGatePath
Add-Assertion -Assertions $assertions -Pass ($truthGate.Contains('host-launch-receipt.json')) -Message 'canonical truth gate requires host-launch-receipt.json'
Add-Assertion -Assertions $assertions -Pass ($truthGate.Contains('reading SKILL.md alone is not canonical vibe entry')) -Message 'canonical truth gate rejects SKILL.md-only activation claims'
Add-Assertion -Assertions $assertions -Pass ($skillText.Contains('proof of canonical entry')) -Message 'SKILL.md documents that prose-only activation is not proof of canonical vibe entry'
Add-Assertion -Assertions $assertions -Pass ($runtimeProtocol.Contains('Reading `SKILL.md`, wrapper markdown, or bootstrap text alone is not proof of canonical vibe entry.')) -Message 'runtime protocol documents that prose-only activation is not proof of canonical vibe entry'

$route = & $routeScriptPath -Prompt 'help me with this' -Grade 'M' -TaskType 'research' | ConvertFrom-Json
$lowSignalHasFallbackGuard = (
    [string]$route.route_mode -eq 'confirm_required' -and
    [string]$route.route_reason -eq 'legacy_fallback_guard' -and
    [bool]$route.fallback_active -and
    [bool]$route.hazard_alert_required -and
    [string]$route.truth_level -eq 'non_authoritative' -and
    [string]$route.degradation_state -in @('fallback_active', 'fallback_guarded') -and
    $route.hazard_alert -and
    [string]$route.hazard_alert.title -eq 'FALLBACK HAZARD ALERT' -and
    [string]$route.hazard_alert.reason -eq 'no_eligible_pack'
)
$lowSignalHasHostSelectionGuard = (
    [string]$route.route_mode -eq 'confirm_required' -and
    [string]$route.route_reason -eq 'host_selection_required' -and
    -not [bool]$route.fallback_active -and
    (
        ($route.confirm_ui -and [bool]$route.confirm_ui.enabled) -or
        [bool]$route.hazard_alert_required
    )
)
Add-Assertion -Assertions $assertions -Pass ($lowSignalHasFallbackGuard -or $lowSignalHasHostSelectionGuard) -Message 'low-signal route stays explicit via non-authoritative fallback guard or explicit host selection'

foreach ($hostId in @('codex', 'claude-code', 'opencode')) {
    Invoke-SupportedHostRuntimeTruthProbe -RepoRoot $repoRoot -RuntimeEntrypointPath $runtimeEntrypointPath -HostId $hostId -Assertions $assertions
}

$failureCount = @($assertions | Where-Object { -not $_.pass }).Count
$artifact = [pscustomobject]@{
    gate = 'vibe-no-silent-fallback-contract-gate'
    repo_root = $repoRoot
    gate_result = if ($failureCount -eq 0) { 'PASS' } else { 'FAIL' }
    generated_at = (Get-Date).ToString('s')
    assertions = @($assertions)
    summary = [pscustomobject]@{
        failure_count = $failureCount
        route_mode = if ($route) { [string]$route.route_mode } else { '' }
        route_reason = if ($route) { [string]$route.route_reason } else { '' }
    }
}

if ($WriteArtifacts) {
    Write-GateArtifacts -RepoRoot $repoRoot -OutputDirectory $OutputDirectory -Artifact $artifact
}

if ($failureCount -gt 0) {
    exit 1
}
