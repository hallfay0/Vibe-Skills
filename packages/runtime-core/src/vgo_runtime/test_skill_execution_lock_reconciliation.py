from __future__ import annotations

import json
import pytest
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]


def _powershell_executable() -> str:
    for name in ("pwsh", "powershell"):
        resolved = shutil.which(name)
        if resolved:
            return resolved
    pytest.skip("PowerShell executable was not found on PATH.")


def _powershell_single_quoted_path(path: Path) -> str:
    return str(path).replace("'", "''")


def test_powershell_single_quoted_path_escapes_apostrophes():
    assert _powershell_single_quoted_path(Path(r"C:\Users\O'Brien\repo\file.ps1")) == r"C:\Users\O''Brien\repo\file.ps1"


def _run_projection(script_body: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp_dir:
        script_path = Path(tmp_dir) / "run-lock-projection.ps1"
        skill_routing_common = REPO_ROOT / "scripts" / "runtime" / "VibeSkillRouting.Common.ps1"
        runtime_common = REPO_ROOT / "scripts" / "runtime" / "VibeRuntime.Common.ps1"
        skill_routing_common_ps = _powershell_single_quoted_path(skill_routing_common)
        runtime_common_ps = _powershell_single_quoted_path(runtime_common)
        script_path.write_text(
            textwrap.dedent(
                f"""
                $ErrorActionPreference = 'Stop'
                Set-StrictMode -Version Latest
                . '{skill_routing_common_ps}'
                . '{runtime_common_ps}'
                {script_body}
                """
            ),
            encoding="utf-8",
        )
        completed = subprocess.run(
            [_powershell_executable(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_path)],
            cwd=str(REPO_ROOT),
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=30,
        )
        assert completed.returncode == 0, completed.stderr + completed.stdout
        return json.loads(completed.stdout)


def _run_confirm_ui(script_body: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp_dir:
        script_path = Path(tmp_dir) / "run-confirm-ui.ps1"
        confirm_ui = REPO_ROOT / "scripts" / "router" / "modules" / "46-confirm-ui.ps1"
        confirm_ui_ps = _powershell_single_quoted_path(confirm_ui)
        script_path.write_text(
            textwrap.dedent(
                f"""
                $ErrorActionPreference = 'Stop'
                Set-StrictMode -Version Latest
                . '{confirm_ui_ps}'
                {script_body}
                """
            ),
            encoding="utf-8",
        )
        completed = subprocess.run(
            [_powershell_executable(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_path)],
            cwd=str(REPO_ROOT),
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=30,
        )
        assert completed.returncode == 0, completed.stderr + completed.stdout
        return json.loads(completed.stdout)


def test_bounded_stop_projection_forbids_same_turn_manual_continuation():
    result = _run_projection(
        r"""
        $control = New-VibeBoundedReturnControlProjection `
            -RepoRoot (Get-Location).Path `
            -RunId 'run-123' `
            -EntryIntentId 'vibe' `
            -StageLineage ([pscustomobject]@{ last_stage_name = 'requirement_doc' })
        $control | ConvertTo-Json -Depth 20
        """
    )

    assert result["assistant_must_stop"] is True
    assert result["same_turn_continuation_forbidden"] is True
    assert result["manual_execution_forbidden"] is True
    assert result["completion_allowed"] is False
    assert result["original_prompt_is_not_approval"] is True
    assert result["next_allowed_assistant_action"] == "wait_for_new_user_approval_or_revision"
    assert "manual_workaround" in result["forbidden_actions"]
    assert "consume_reentry_token_in_same_turn" in result["forbidden_actions"]
    assert "Do not continue in the same assistant turn" in result["rendered_text"]
    assert "manual execution outside governed re-entry is forbidden" in result["rendered_text"]


def test_confirm_ui_asks_user_before_using_routed_skills():
    result = _run_confirm_ui(
        r"""
        $confirmSkillOptions = [pscustomobject]@{
            selected_pack = 'clinical-ml'
            selected_skill = 'scikit-learn'
            options = @(
                [pscustomobject]@{
                    option_id = 1
                    skill = 'scikit-learn'
                    description = 'Train and validate the prediction model.'
                    score = 0.91
                }
            )
        }
        $routeResult = [pscustomobject]@{
            route_mode = 'confirm_required'
            hazard_alert_required = $false
        }
        $text = Build-ConfirmUiText `
            -ConfirmSkillOptions $confirmSkillOptions `
            -UnattendedDecision $null `
            -Result $routeResult
        [pscustomobject]@{ text = $text } | ConvertTo-Json -Depth 20
        """
    )

    assert "我将会在接下来的工作中使用这些 skills，你觉得 OK 吗？" in result["text"]
    assert "这只是准备使用，不是实际使用证据" in result["text"]


def test_intent_contract_exposes_l_xl_workflow_confirmation_without_new_entrypoints():
    result = _run_projection(
        r"""
        $contract = New-VibeIntentContractObject `
            -Task 'deliver a small clinical machine learning study' `
            -Mode 'interactive_governed'
        $contract | ConvertTo-Json -Depth 20
        """
    )

    assert result["workflow_level_confirmation"]["enabled"] is True
    assert result["workflow_level_confirmation"]["user_visible"] is True
    assert result["workflow_level_confirmation"]["recommended_level"] in ["L", "XL"]
    assert result["workflow_level_confirmation"]["levels"]["L"]
    assert result["workflow_level_confirmation"]["levels"]["XL"]
    assert "Do not create separate M/L/XL entry commands." in result["non_goals"]
    assert "Do not treat M/L/XL as user-facing entry branches." not in result["non_goals"]


def test_host_skill_execution_contract_requires_user_confirmation_for_l_xl():
    result = _run_projection(
        r"""
        $policy = Get-Content -LiteralPath (Join-Path (Get-Location).Path 'config\runtime-input-packet-policy.json') -Raw | ConvertFrom-Json
        $contract = Get-VibeHostSkillExecutionContract -Policy $policy
        $contract | ConvertTo-Json -Depth 20
        """
    )

    assert result["requires_user_confirmation_for"] == ["L", "XL"]
    assert result["approval_owner"] == "user"
    assert result["default_selection_mode"] == "inherit_runtime_default"
    assert "我将会在接下来的工作中使用这些 skills，你觉得 OK 吗？" in result["user_prompt"]


def test_previous_active_lock_unions_current_selected_skill():
    result = _run_projection(
        r"""
        $previous = [pscustomobject]@{
            skill_execution_lock = [pscustomobject]@{
                schema_version = 'v1'
                state = 'active'
                locked_skill_ids = @('latex-submission-pipeline', 'scientific-writing', 'scholarly-publishing')
                locked_dispatch = @(
                    [pscustomobject]@{ skill_id = 'latex-submission-pipeline'; task_slice = 'paper build' },
                    [pscustomobject]@{ skill_id = 'scientific-writing'; task_slice = 'scientific writing' },
                    [pscustomobject]@{ skill_id = 'scholarly-publishing'; task_slice = 'publishing package' }
                )
                resolution_required = $true
            }
        }
        $current = [pscustomobject]@{
            selected = @(
                [pscustomobject]@{ skill_id = 'latex-submission-pipeline'; task_slice = 'paper build current' },
                [pscustomobject]@{ skill_id = 'literature-review'; task_slice = 'literature verification' },
                [pscustomobject]@{ skill_id = 'scientific-writing'; task_slice = 'scientific writing current' },
                [pscustomobject]@{ skill_id = 'scholarly-publishing'; task_slice = 'publishing package current' }
            )
            candidates = @(
                [pscustomobject]@{ skill_id = 'candidate-only'; task_slice = 'candidate only' }
            )
            rejected = @(
                [pscustomobject]@{ skill_id = 'rejected-only'; task_slice = 'rejected only' }
            )
        }
        $lock = New-VibeSkillExecutionLockProjection `
            -PreviousRuntimeInputPacket $previous `
            -CurrentSkillRouting $current `
            -SourceRunId 'previous-run' `
            -Source 'approved_plan_reentry'
        $lock | ConvertTo-Json -Depth 20
        """
    )

    assert result["state"] == "active"
    assert result["locked_skill_ids"] == [
        "latex-submission-pipeline",
        "literature-review",
        "scientific-writing",
        "scholarly-publishing",
    ]
    assert "candidate-only" not in result["locked_skill_ids"]
    assert "rejected-only" not in result["locked_skill_ids"]


def test_host_approved_skills_do_not_replace_previous_or_current_obligations():
    result = _run_projection(
        r"""
        $previous = [pscustomobject]@{
            skill_execution_lock = [pscustomobject]@{
                schema_version = 'v1'
                state = 'active'
                locked_skill_ids = @('latex-submission-pipeline')
                locked_dispatch = @(
                    [pscustomobject]@{ skill_id = 'latex-submission-pipeline'; task_slice = 'previous paper build' }
                )
                resolution_required = $true
            }
        }
        $current = [pscustomobject]@{
            selected = @(
                [pscustomobject]@{ skill_id = 'literature-review'; task_slice = 'current literature review' }
            )
            candidates = @()
            rejected = @()
        }
        $hostDecision = [pscustomobject]@{
            approved_skill_ids = @('scientific-writing')
        }
        $lock = New-VibeSkillExecutionLockProjection `
            -PreviousRuntimeInputPacket $previous `
            -CurrentSkillRouting $current `
            -HostSpecialistDispatchDecision $hostDecision `
            -SourceRunId 'previous-run' `
            -Source 'approved_plan_reentry'
        $lock | ConvertTo-Json -Depth 20
        """
    )

    assert result["locked_skill_ids"] == [
        "literature-review",
        "scientific-writing",
        "latex-submission-pipeline",
    ]


def test_host_deferred_and_rejected_skills_are_excluded_from_execution_lock():
    result = _run_projection(
        r"""
        $previous = [pscustomobject]@{
            skill_execution_lock = [pscustomobject]@{
                schema_version = 'v1'
                state = 'active'
                locked_skill_ids = @('prior-reporting', 'rejected-prior')
                locked_dispatch = @(
                    [pscustomobject]@{ skill_id = 'prior-reporting'; task_slice = 'prior report' },
                    [pscustomobject]@{ skill_id = 'rejected-prior'; task_slice = 'rejected prior' }
                )
                resolution_required = $true
            }
        }
        $current = [pscustomobject]@{
            selected = @(
                [pscustomobject]@{ skill_id = 'keep-current'; task_slice = 'current selected' },
                [pscustomobject]@{ skill_id = 'deferred-current'; task_slice = 'deferred selected' }
            )
            candidates = @()
            rejected = @()
        }
        $hostDecision = [pscustomobject]@{
            approved_skill_ids = @('keep-approved', 'rejected-approved')
            deferred_skill_ids = @('deferred-current')
            rejected_skill_ids = @('rejected-prior', 'rejected-approved')
        }
        $lock = New-VibeSkillExecutionLockProjection `
            -PreviousRuntimeInputPacket $previous `
            -CurrentSkillRouting $current `
            -HostSpecialistDispatchDecision $hostDecision `
            -SourceRunId 'previous-run' `
            -Source 'approved_plan_reentry'
        $lock | ConvertTo-Json -Depth 20
        """
    )

    assert result["locked_skill_ids"] == [
        "keep-current",
        "keep-approved",
        "prior-reporting",
    ]


def test_explicit_zero_host_approval_does_not_rehydrate_previous_lock_without_current_selection():
    result = _run_projection(
        r"""
        $previous = [pscustomobject]@{
            skill_execution_lock = [pscustomobject]@{
                schema_version = 'v1'
                state = 'active'
                locked_skill_ids = @('literature-review')
                locked_dispatch = @(
                    [pscustomobject]@{ skill_id = 'literature-review'; task_slice = 'previous literature review' }
                )
                resolution_required = $true
            }
        }
        $current = [pscustomobject]@{
            selected = @()
            candidates = @()
            rejected = @()
        }
        $hostDecision = [pscustomobject]@{
            approved_skill_ids = @()
        }
        $lock = New-VibeSkillExecutionLockProjection `
            -PreviousRuntimeInputPacket $previous `
            -CurrentSkillRouting $current `
            -HostSpecialistDispatchDecision $hostDecision `
            -SourceRunId 'previous-run' `
            -Source 'approved_plan_reentry'
        $lock | ConvertTo-Json -Depth 20
        """
    )

    assert result["state"] == "inactive"
    assert result["locked_skill_ids"] == []
    assert result["locked_dispatch"] == []


def test_single_selected_skill_stays_single_locked_skill():
    result = _run_projection(
        r"""
        $current = [pscustomobject]@{
            selected = @(
                [pscustomobject]@{ skill_id = 'latex-submission-pipeline'; task_slice = 'single selected skill' }
            )
            candidates = @(
                [pscustomobject]@{ skill_id = 'candidate-only'; task_slice = 'candidate only' }
            )
            rejected = @()
        }
        $lock = New-VibeSkillExecutionLockProjection -CurrentSkillRouting $current
        $lock | ConvertTo-Json -Depth 20
        """
    )

    assert result["locked_skill_ids"] == ["latex-submission-pipeline"]


def test_previous_locked_skill_ids_without_dispatch_are_preserved():
    result = _run_projection(
        r"""
        $previous = [pscustomobject]@{
            skill_execution_lock = [pscustomobject]@{
                schema_version = 'v1'
                state = 'active'
                locked_skill_ids = @('literature-review')
                resolution_required = $true
            }
        }
        $current = [pscustomobject]@{
            selected = @()
            candidates = @()
            rejected = @()
        }
        $lock = New-VibeSkillExecutionLockProjection `
            -PreviousRuntimeInputPacket $previous `
            -CurrentSkillRouting $current `
            -SourceRunId 'previous-run' `
            -Source 'approved_plan_reentry'
        $lock | ConvertTo-Json -Depth 20
        """
    )

    assert result["locked_skill_ids"] == ["literature-review"]
    dispatch = result["locked_dispatch"][0]
    assert dispatch["skill_id"] == "literature-review"
    assert dispatch["lock_source"] == "previous_skill_execution_lock"
    assert dispatch["reconciliation_state"] == "inherited_not_currently_surfaced"


def test_locked_skill_ids_derive_from_locked_dispatch_when_id_list_missing():
    result = _run_projection(
        r"""
        $lock = [pscustomobject]@{
            schema_version = 'v1'
            state = 'active'
            locked_dispatch = @(
                [pscustomobject]@{ skill_id = 'scientific-writing' }
            )
            resolution_required = $true
        }
        [pscustomobject]@{
            active = Test-VibeSkillExecutionLockActive -SkillExecutionLock $lock
            locked_skill_ids = @(Get-VibeSkillExecutionLockSkillIds -SkillExecutionLock $lock)
        } | ConvertTo-Json -Depth 20
        """
    )

    assert result["active"] is True
    assert result["locked_skill_ids"] == ["scientific-writing"]
