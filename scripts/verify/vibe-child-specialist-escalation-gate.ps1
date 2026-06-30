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
        [ref]$Results,
        [bool]$Condition,
        [string]$Message,
        [string]$Details = ''
    )

    $record = [pscustomobject]@{
        passed = [bool]$Condition
        message = $Message
        details = $Details
    }
    $Results.Value += $record

    if ($Condition) {
        Write-Host "[PASS] $Message"
    } else {
        Write-Host "[FAIL] $Message" -ForegroundColor Red
        if ($Details) {
            Write-Host "       $Details" -ForegroundColor DarkRed
        }
    }
}

function New-ChildDelegationEnvelopeForGate {
    param(
        [Parameter(Mandatory)] [object]$RootSummary,
        [Parameter(Mandatory)] [string]$ChildRunId,
        [AllowNull()] [string[]]$ApprovedSpecialists = @()
    )

    $sessionRoot = [string]$RootSummary.summary.session_root
    $childSessionRoot = Join-Path ([System.IO.Path]::GetDirectoryName($sessionRoot)) $ChildRunId
    New-Item -ItemType Directory -Path $childSessionRoot -Force | Out-Null
    $envelopePath = Get-VibeGovernanceArtifactPath -SessionRoot $childSessionRoot -ArtifactName 'delegation_envelope'
    Write-VibeDelegationEnvelope `
        -Path $envelopePath `
        -RootRunId ([string]$RootSummary.summary.run_id) `
        -ParentRunId ([string]$RootSummary.summary.run_id) `
        -ParentUnitId 'child-specialist-escalation-unit' `
        -ChildRunId $ChildRunId `
        -RequirementDocPath ([string]$RootSummary.summary.artifacts.requirement_doc) `
        -ExecutionPlanPath ([string]$RootSummary.summary.artifacts.execution_plan) `
        -WriteScope 'gate:child-specialist-escalation' `
        -ApprovedSpecialists @($ApprovedSpecialists) `
        -ReviewMode 'native_contract' | Out-Null
    return $envelopePath
}

$context = Get-VgoGovernanceContext -ScriptPath $PSCommandPath -EnforceExecutionContext
$repoRoot = $context.repoRoot
$runtimeEntryPath = Get-VgoRuntimeEntrypointPath -RepoRoot $repoRoot -RuntimeConfig $context.runtimeConfig
$results = @()

$policyText = Get-Content -LiteralPath (Join-Path $repoRoot 'config\runtime-input-packet-policy.json') -Raw -Encoding UTF8
foreach ($token in @('child_specialist_suggestion_contract', 'local_specialist_suggestions', 'escalation_required', 'auto_promote_when_safe_same_round', 'auto_absorb_gate')) {
    Add-Assertion -Results ([ref]$results) -Condition ($policyText.Contains($token)) -Message ("runtime input policy contains child specialist suggestion token: {0}" -f $token)
}

$teamText = Get-Content -LiteralPath (Join-Path $repoRoot 'protocols\team.md') -Raw -Encoding UTF8
$stableDocText = Get-Content -LiteralPath (Join-Path $repoRoot 'docs\root-child-vibe-hierarchy-governance.md') -Raw -Encoding UTF8
Add-Assertion -Results ([ref]$results) -Condition ($teamText.Contains('safe bounded candidates should aggressively promote into selected skill execution')) -Message 'team protocol documents work-first skill promotion'
Add-Assertion -Results ([ref]$results) -Condition ($stableDocText.Contains('same-round auto-approve safe suggestions')) -Message 'stable hierarchy doc documents root-governed same-round absorb path'

$runId = "child-specialist-escalation-" + [System.Guid]::NewGuid().ToString('N').Substring(0, 8)
$artifactRoot = Join-Path $repoRoot (".tmp\child-specialist-escalation-{0}" -f $runId)

$rootSummary = & $runtimeEntryPath `
    -Task 'Root bounded work seed for child skill escalation gate.' `
    -Mode interactive_governed `
    -GovernanceScope root `
    -RunId ("{0}-root" -f $runId) `
    -ArtifactRoot $artifactRoot

Add-Assertion -Results ([ref]$results) -Condition ($null -ne $rootSummary) -Message 'root specialist escalation probe returned summary payload'
$hasRootSummary = ($null -ne $rootSummary) -and ($rootSummary.PSObject.Properties.Name -contains 'summary')
Add-Assertion -Results ([ref]$results) -Condition $hasRootSummary -Message 'root specialist escalation probe has summary object'

$approvedForChild = @()
if ($hasRootSummary) {
    $rootRuntimeInputPacket = Get-Content -LiteralPath $rootSummary.summary.artifacts.runtime_input_packet -Raw -Encoding UTF8 | ConvertFrom-Json
    Add-Assertion -Results ([ref]$results) -Condition ($rootRuntimeInputPacket.governance_scope -eq 'root') -Message 'root specialist escalation probe is in root scope'
    Add-Assertion -Results ([ref]$results) -Condition ($rootRuntimeInputPacket.authority_flags.explicit_runtime_skill -eq 'vibe') -Message 'root specialist escalation probe keeps vibe authority'
    $rootBoundSkillIds = @(Get-VibeWorkBindingBoundSkillIds -RuntimeInputPacket $rootRuntimeInputPacket)
    Add-Assertion -Results ([ref]$results) -Condition ($rootRuntimeInputPacket.PSObject.Properties.Name -contains 'work_binding') -Message 'root runtime packet includes work_binding'
    Add-Assertion -Results ([ref]$results) -Condition (@($rootBoundSkillIds).Count -ge 1) -Message 'root runtime packet uses work_binding as bounded skill truth'

    $rootSelectedSkillExecution = Get-VibeRuntimeSelectedSkillExecutionProjection -RuntimeInputPacket $rootRuntimeInputPacket
    $rootSelectedSkillIds = if ($null -ne $rootSelectedSkillExecution -and $rootSelectedSkillExecution.PSObject.Properties.Name -contains 'selected_skill_ids') {
        @($rootSelectedSkillExecution.selected_skill_ids | ForEach-Object { [string]$_ } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -Unique)
    } else {
        @()
    }
    Add-Assertion -Results ([ref]$results) -Condition ((@($rootSelectedSkillIds).Count -eq 0) -or ((@($rootSelectedSkillIds) | Where-Object { $_ -in @($rootBoundSkillIds) }).Count -eq @($rootSelectedSkillIds).Count)) -Message 'root runtime packet keeps compatibility selected skill mirror subordinate to work_binding'
    if (@($rootBoundSkillIds).Count -gt 0) {
        $approvedForChild = @([string]$rootBoundSkillIds[0])
    }
}

$childSummary = $null
if ($hasRootSummary) {
    $childRunId = ("{0}-child" -f $runId)
    $childDelegationEnvelopePath = New-ChildDelegationEnvelopeForGate -RootSummary $rootSummary -ChildRunId $childRunId -ApprovedSpecialists @($approvedForChild)
    $childSummary = & $runtimeEntryPath `
        -Task 'Child specialist escalation advisory smoke.' `
        -Mode interactive_governed `
        -GovernanceScope child `
        -RunId $childRunId `
        -RootRunId ([string]$rootSummary.summary.run_id) `
        -ParentRunId ([string]$rootSummary.summary.run_id) `
        -ParentUnitId 'child-specialist-escalation-unit' `
        -InheritedRequirementDocPath ([string]$rootSummary.summary.artifacts.requirement_doc) `
        -InheritedExecutionPlanPath ([string]$rootSummary.summary.artifacts.execution_plan) `
        -DelegationEnvelopePath $childDelegationEnvelopePath `
        -ApprovedSpecialistSkillIds $approvedForChild `
        -ArtifactRoot $artifactRoot
}

Add-Assertion -Results ([ref]$results) -Condition ($null -ne $childSummary) -Message 'child specialist escalation probe returned summary payload'
$hasChildSummary = ($null -ne $childSummary) -and ($childSummary.PSObject.Properties.Name -contains 'summary')
Add-Assertion -Results ([ref]$results) -Condition $hasChildSummary -Message 'child specialist escalation probe has summary object'

$approvedDispatch = @()
$localSuggestions = @()
$childClaims = @()
if ($hasChildSummary) {
    $runtimeInputPacket = Get-Content -LiteralPath $childSummary.summary.artifacts.runtime_input_packet -Raw -Encoding UTF8 | ConvertFrom-Json
    $executionManifest = Get-Content -LiteralPath $childSummary.summary.artifacts.execution_manifest -Raw -Encoding UTF8 | ConvertFrom-Json
    $delegationValidation = Get-Content -LiteralPath $childSummary.summary.artifacts.delegation_validation_receipt -Raw -Encoding UTF8 | ConvertFrom-Json

    $selectedSkillExecution = Get-VibeRuntimeSelectedSkillExecutionProjection -RuntimeInputPacket $runtimeInputPacket
    $boundSkillIds = @(Get-VibeWorkBindingBoundSkillIds -RuntimeInputPacket $runtimeInputPacket)
    $selectedSkillIds = if ($null -ne $selectedSkillExecution -and $selectedSkillExecution.PSObject.Properties.Name -contains 'selected_skill_ids') {
        @($selectedSkillExecution.selected_skill_ids | ForEach-Object { [string]$_ } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -Unique)
    } else {
        @()
    }

    $approvedDispatch = if ($null -ne $selectedSkillExecution -and $selectedSkillExecution.PSObject.Properties.Name -contains 'selected_skill_execution') {
        @($selectedSkillExecution.selected_skill_execution)
    } else {
        @()
    }

    $localSuggestions = if ($runtimeInputPacket.PSObject.Properties.Name -contains 'local_specialist_suggestions') {
        @($runtimeInputPacket.local_specialist_suggestions)
    } else {
        @()
    }

    Add-Assertion -Results ([ref]$results) -Condition ($runtimeInputPacket.governance_scope -eq 'child') -Message 'specialist escalation smoke runs in child scope'
    Add-Assertion -Results ([ref]$results) -Condition ($runtimeInputPacket.authority_flags.explicit_runtime_skill -eq 'vibe') -Message 'specialist escalation smoke keeps vibe runtime authority'
    Add-Assertion -Results ([ref]$results) -Condition ($runtimeInputPacket.PSObject.Properties.Name -contains 'work_binding') -Message 'child runtime packet includes work_binding'
    Add-Assertion -Results ([ref]$results) -Condition (@($boundSkillIds).Count -ge 1) -Message 'child runtime packet keeps root-approved bounded work in work_binding'
    Add-Assertion -Results ([ref]$results) -Condition ((@($selectedSkillIds).Count -eq 0) -or ((@($selectedSkillIds) | Where-Object { $_ -in @($boundSkillIds) }).Count -eq @($selectedSkillIds).Count)) -Message 'child runtime packet keeps compatibility selected skills subordinate to work_binding'
    Add-Assertion -Results ([ref]$results) -Condition ([bool]$delegationValidation.write_scope_valid) -Message 'child specialist escalation smoke validates delegation write scope'
    Add-Assertion -Results ([ref]$results) -Condition ([bool]$delegationValidation.prompt_tail_valid) -Message 'child specialist escalation smoke preserves $vibe prompt-tail discipline'
    Add-Assertion -Results ([ref]$results) -Condition (-not [bool]$runtimeInputPacket.authority_flags.allow_completion_claim) -Message 'child runtime input packet disallows final completion claim'
    $specialistDecision = if ($runtimeInputPacket.PSObject.Properties.Name -contains 'specialist_decision') { $runtimeInputPacket.specialist_decision } else { $null }
    Add-Assertion -Results ([ref]$results) -Condition ($null -ne $specialistDecision) -Message 'child runtime packet records specialist_decision'
    if ($null -ne $specialistDecision) {
        $decisionState = [string](Get-VibePropertySafe -InputObject $specialistDecision -PropertyName 'decision_state' -DefaultValue '')
        Add-Assertion -Results ([ref]$results) -Condition ($decisionState -in @('approved_dispatch', 'local_suggestion_only', 'no_specialist_recommendations')) -Message 'child specialist decision stays within current work-first decision states'
    }

    $approvedSkillIds = @($approvedDispatch | ForEach-Object { [string]$_.skill_id } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -Unique)
    foreach ($entry in $localSuggestions) {
        $skillId = if ($entry.PSObject.Properties.Name -contains 'skill_id') { [string]$entry.skill_id } else { 'unknown-skill' }
        Add-Assertion -Results ([ref]$results) -Condition (-not ($approvedSkillIds -contains $skillId)) -Message ("local specialist suggestion is not approved selected skill execution: {0}" -f $skillId)
        Add-Assertion -Results ([ref]$results) -Condition (-not ($boundSkillIds -contains $skillId)) -Message ("residual local specialist suggestion does not mutate current work_binding: {0}" -f $skillId)
    }

    Add-Assertion -Results ([ref]$results) -Condition ($executionManifest.governance_scope -eq 'child') -Message 'execution manifest is marked child scope'
    Add-Assertion -Results ([ref]$results) -Condition (-not [bool]$executionManifest.authority.completion_claim_allowed) -Message 'child execution manifest cannot issue final completion claim'
    Add-Assertion -Results ([ref]$results) -Condition ($executionManifest.route_runtime_alignment.runtime_selected_skill -eq 'vibe') -Message 'execution manifest keeps explicit vibe authority'
    Add-Assertion -Results ([ref]$results) -Condition ([bool]$executionManifest.dispatch_integrity.proof_passed) -Message 'child execution manifest preserves skill execution integrity proof'
    Add-Assertion -Results ([ref]$results) -Condition ([bool]$executionManifest.dispatch_integrity.local_suggestions_contained) -Message 'child execution manifest keeps residual local suggestions contained'
    Add-Assertion -Results ([ref]$results) -Condition ([bool]$executionManifest.dispatch_integrity.executed_specialists_subset_of_approved_dispatch) -Message 'child execution manifest executes only root-approved selected skills'
    $specialistAccounting = if ($executionManifest.PSObject.Properties.Name -contains 'specialist_accounting') { $executionManifest.specialist_accounting } else { $null }
    if (@($localSuggestions).Count -gt 0) {
        Add-Assertion -Results ([ref]$results) -Condition ($null -ne $specialistAccounting -and $specialistAccounting.PSObject.Properties.Name -contains 'auto_absorb_gate') -Message 'child execution manifest records same-round auto-absorb status when residual local suggestions remain visible'
    }
    if (@($localSuggestions).Count -gt 0 -and $null -ne $specialistAccounting -and $specialistAccounting.PSObject.Properties.Name -contains 'auto_absorb_gate') {
        $autoAbsorbGate = $specialistAccounting.auto_absorb_gate
        Add-Assertion -Results ([ref]$results) -Condition ([string]$autoAbsorbGate.status -in @('auto_approved_same_round', 'partially_auto_approved_same_round')) -Message 'child execution manifest keeps same-round auto-absorb subordinate to bounded work'
        if ($autoAbsorbGate.receipt_path) {
            Add-Assertion -Results ([ref]$results) -Condition (Test-Path -LiteralPath ([string]$autoAbsorbGate.receipt_path)) -Message 'same-round auto-absorb gate emits receipt'
        }
    }

    $childClaims = if ($executionManifest.PSObject.Properties.Name -contains 'child_completion_claims') { @($executionManifest.child_completion_claims) } else { @() }
}

$failureCount = @($results | Where-Object { -not $_.passed }).Count
$gatePassed = ($failureCount -eq 0)
$report = [pscustomobject]@{
    generated_at = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    repo_root = $repoRoot
    gate_passed = $gatePassed
    assertion_count = @($results).Count
    failure_count = $failureCount
    runtime_summary_path = if ($null -ne $childSummary -and ($childSummary.PSObject.Properties.Name -contains 'summary_path')) { $childSummary.summary_path } else { $null }
    approved_dispatch_count = @($approvedDispatch).Count
    local_suggestion_count = @($localSuggestions).Count
    child_claim_count = @($childClaims).Count
    results = @($results)
}

if ($WriteArtifacts) {
    $targetDir = if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
        Join-Path $repoRoot 'outputs\verify\vibe-child-specialist-escalation'
    } elseif ([System.IO.Path]::IsPathRooted($OutputDirectory)) {
        [System.IO.Path]::GetFullPath($OutputDirectory)
    } else {
        [System.IO.Path]::GetFullPath((Join-Path $repoRoot $OutputDirectory))
    }

    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    Write-VibeJsonArtifact -Path (Join-Path $targetDir 'vibe-child-specialist-escalation-gate.json') -Value $report
} elseif (Test-Path -LiteralPath $artifactRoot) {
    Remove-Item -LiteralPath $artifactRoot -Recurse -Force
}

if (-not $gatePassed) {
    throw "vibe-child-specialist-escalation-gate failed with $failureCount failing assertion(s)."
}

$report
