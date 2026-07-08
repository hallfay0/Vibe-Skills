from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_COMMON = REPO_ROOT / "scripts" / "runtime" / "VibeRuntime.Common.ps1"
SKILL_ROUTING_COMMON = REPO_ROOT / "scripts" / "runtime" / "VibeSkillRouting.Common.ps1"
FREEZE_SCRIPT = REPO_ROOT / "scripts" / "runtime" / "Freeze-RuntimeInputPacket.ps1"


def resolve_powershell() -> str | None:
    candidates = [
        shutil.which("pwsh"),
        shutil.which("pwsh.exe"),
        r"C:\Program Files\PowerShell\7\pwsh.exe",
        shutil.which("powershell"),
        shutil.which("powershell.exe"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(Path(candidate))
    return None


def ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def run_ps_json(script: str) -> dict[str, object]:
    shell = resolve_powershell()
    if shell is None:
        raise unittest.SkipTest("PowerShell executable not available")
    completed = subprocess.run(
        [shell, "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return json.loads(completed.stdout)


def as_list(value: object) -> list[object]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def write_installed_skill(target_root: Path, skill_id: str) -> Path:
    skill_path = target_root / "skills" / skill_id / "SKILL.md"
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    skill_path.write_text(
        "---\n"
        f"name: {skill_id}\n"
        f"description: Installed {skill_id} test skill.\n"
        "---\n",
        encoding="utf-8",
    )
    return skill_path


class SkillExecutionLockContractTests(unittest.TestCase):
    def test_lock_projection_keeps_current_selected_and_host_approved_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            prior_skill = Path(tempdir) / "scientific-reporting" / "SKILL.md"
            current_skill = Path(tempdir) / "latex-submission-pipeline" / "SKILL.md"
            approved_skill = Path(tempdir) / "designing-experiments" / "SKILL.md"
            for skill_path in (prior_skill, current_skill, approved_skill):
                skill_path.parent.mkdir(parents=True)
                skill_path.write_text(f"---\nname: {skill_path.parent.name}\n---\n", encoding="utf-8")
            payload = run_ps_json(
                "& { "
                f". {ps_quote(str(RUNTIME_COMMON))}; "
                f". {ps_quote(str(SKILL_ROUTING_COMMON))}; "
                "$previous = [pscustomobject]@{ "
                "  skill_routing = [pscustomobject]@{ "
                "    selected = @([pscustomobject]@{ "
                "      skill_id = 'scientific-reporting'; task_slice = 'prior plan'; "
                f"      native_skill_entrypoint = {ps_quote(str(prior_skill))}; skill_md_path = {ps_quote(str(prior_skill))} "
                "    }) "
                "  } "
                "}; "
                "$current = [pscustomobject]@{ "
                "  selected = @([pscustomobject]@{ "
                "    skill_id = 'latex-submission-pipeline'; task_slice = 'current pdf'; dispatch_phase = 'post_execution'; "
                f"    native_skill_entrypoint = {ps_quote(str(current_skill))}; skill_md_path = {ps_quote(str(current_skill))} "
                "  }); "
                "  candidates = @([pscustomobject]@{ "
                "    skill_id = 'designing-experiments'; task_slice = 'explicit design'; dispatch_phase = 'pre_execution'; "
                f"    native_skill_entrypoint = {ps_quote(str(approved_skill))}; skill_md_path = {ps_quote(str(approved_skill))} "
                "  }); "
                "  rejected = @() "
                "}; "
                "$decision = [pscustomobject]@{ approved_skill_ids = @('designing-experiments') }; "
                "$lock = New-VibeSkillExecutionLockProjection "
                "-PreviousRuntimeInputPacket $previous "
                "-CurrentSkillRouting $current "
                "-HostSpecialistDispatchDecision $decision "
                "-SourceRunId 'pytest-plan-run' "
                "-Source 'approved_plan_reentry'; "
                "$lock | ConvertTo-Json -Depth 20 "
                "}"
            )

        self.assertEqual(
            ["latex-submission-pipeline", "designing-experiments", "scientific-reporting"],
            as_list(payload["locked_skill_ids"]),
        )
        dispatch_by_id = {item["skill_id"]: item for item in as_list(payload["locked_dispatch"])}
        self.assertEqual("current_surfaced", dispatch_by_id["latex-submission-pipeline"]["reconciliation_state"])
        self.assertEqual("host_approved_added_to_lock", dispatch_by_id["designing-experiments"]["reconciliation_state"])
        self.assertEqual("inherited_not_currently_surfaced", dispatch_by_id["scientific-reporting"]["reconciliation_state"])

    def test_local_authority_drops_bundled_or_missing_locked_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_root = Path(tempdir)
            target_root = temp_root / ".agents"
            current_skill = write_installed_skill(target_root, "exploratory-data-analysis")
            bundled_skill = temp_root / "vibe_full_copy" / "bundled" / "skills" / "aeon" / "SKILL.md"
            bundled_skill.parent.mkdir(parents=True)
            bundled_skill.write_text(
                "---\nname: aeon\ndescription: Bundled stale skill.\n---\n",
                encoding="utf-8",
            )
            payload = run_ps_json(
                "& { "
                f". {ps_quote(str(RUNTIME_COMMON))}; "
                f". {ps_quote(str(SKILL_ROUTING_COMMON))}; "
                "$previous = [pscustomobject]@{ "
                "  skill_execution_lock = [pscustomobject]@{ "
                "    schema_version = 'v1'; state = 'active'; resolution_required = $true; "
                "    locked_skill_ids = @('aeon', 'manuscript-as-code'); "
                "    locked_dispatch = @("
                "      [pscustomobject]@{ "
                "        skill_id = 'aeon'; "
                "        task_slice = 'stale bundled hint'; "
                f"        native_skill_entrypoint = {ps_quote(str(bundled_skill))}; "
                f"        skill_md_path = {ps_quote(str(bundled_skill))} "
                "      }, "
                "      [pscustomobject]@{ "
                "        skill_id = 'manuscript-as-code'; "
                "        task_slice = 'missing local skill'; "
                "        native_skill_entrypoint = $null; "
                "        skill_md_path = $null "
                "      }"
                "    ) "
                "  } "
                "}; "
                "$current = [pscustomobject]@{ "
                "  selected = @([pscustomobject]@{ "
                "    skill_id = 'exploratory-data-analysis'; task_slice = 'analyze data'; "
                f"    native_skill_entrypoint = {ps_quote(str(current_skill))}; skill_md_path = {ps_quote(str(current_skill))} "
                "  }); "
                "  candidates = @(); rejected = @() "
                "}; "
                "$lock = New-VibeSkillExecutionLockProjection "
                "-PreviousRuntimeInputPacket $previous "
                "-CurrentSkillRouting $current "
                f"-RepoRoot {ps_quote(str(REPO_ROOT))} "
                f"-TargetRoot {ps_quote(str(target_root))} "
                "-HostId 'codex' "
                "-SourceRunId 'pytest-plan-run' "
                "-Source 'approved_plan_reentry'; "
                "$lock | ConvertTo-Json -Depth 20 "
                "}"
            )

        self.assertEqual(["exploratory-data-analysis"], as_list(payload["locked_skill_ids"]))
        dispatch_by_id = {item["skill_id"]: item for item in as_list(payload["locked_dispatch"])}
        self.assertNotIn("aeon", dispatch_by_id)
        self.assertNotIn("manuscript-as-code", dispatch_by_id)

    def test_local_authority_ignores_host_approved_skill_missing_from_local_index(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            target_root = Path(tempdir) / ".agents"
            payload = run_ps_json(
                "& { "
                f". {ps_quote(str(RUNTIME_COMMON))}; "
                f". {ps_quote(str(SKILL_ROUTING_COMMON))}; "
                "$current = [pscustomobject]@{ selected = @(); candidates = @(); rejected = @() }; "
                "$decision = [pscustomobject]@{ approved_skill_ids = @('manuscript-as-code') }; "
                "$lock = New-VibeSkillExecutionLockProjection "
                "-CurrentSkillRouting $current "
                "-HostSpecialistDispatchDecision $decision "
                f"-RepoRoot {ps_quote(str(REPO_ROOT))} "
                f"-TargetRoot {ps_quote(str(target_root))} "
                "-HostId 'codex' "
                "-Source 'test'; "
                "$lock | ConvertTo-Json -Depth 20 "
                "}"
            )

        self.assertEqual("inactive", payload["state"])
        self.assertEqual([], as_list(payload["locked_skill_ids"]))
        self.assertEqual([], as_list(payload["locked_dispatch"]))

    def test_freeze_inherits_previous_plan_selection_into_execution_lock(self) -> None:
        shell = resolve_powershell()
        if shell is None:
            self.skipTest("PowerShell executable not available")
        with tempfile.TemporaryDirectory() as tempdir:
            artifact_root = Path(tempdir) / "artifacts"
            target_root = Path(tempdir) / ".agents"
            skill_path = write_installed_skill(target_root, "scientific-reporting")
            prior_session = artifact_root / "outputs" / "runtime" / "vibe-sessions" / "pytest-plan-run"
            prior_session.mkdir(parents=True)
            (prior_session / "runtime-input-packet.json").write_text(
                json.dumps(
                    {
                        "run_id": "pytest-plan-run",
                        "requested_stage_stop": "xl_plan",
                        "skill_routing": {
                            "schema_version": "simplified_skill_routing_v1",
                            "selected": [
                                {
                                    "skill_id": "scientific-reporting",
                                    "task_slice": "write a scientific report",
                                    "native_skill_entrypoint": str(skill_path),
                                    "skill_md_path": str(skill_path),
                                    "dispatch_phase": "post_execution",
                                    "write_scope": "specialist:scientific-reporting",
                                    "verification_expectation": "report evidence",
                                }
                            ],
                            "candidates": [],
                            "rejected": [],
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            host_decision = {
                "decision_kind": "approval_response",
                "decision_action": "approve_plan",
                "approval_decision": "approve",
                "continuation_context": {
                    "structured_bounded_reentry": True,
                    "source_run_id": "pytest-plan-run",
                    "reentry_action": "approve_plan",
                    "prior_task_type": "research",
                    "control_only_prompt": True,
                },
            }
            completed = subprocess.run(
                [
                    shell,
                    "-NoLogo",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(FREEZE_SCRIPT),
                    "-Task",
                    "Continue approved plan and compile the LaTeX paper.",
                    "-Mode",
                    "interactive_governed",
                    "-RunId",
                    "pytest-execute-run",
                    "-ArtifactRoot",
                    str(artifact_root),
                    "-HostDecisionJson",
                    json.dumps(host_decision),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True,
                env={**os.environ, "VIBE_AGENTS_HOME": str(target_root)},
            )
            self.assertIn("packet_path", completed.stdout)
            packet_path = next(
                (artifact_root / "outputs" / "runtime" / "vibe-sessions" / "pytest-execute-run").rglob(
                    "runtime-input-packet.json"
                ),
                None,
            )
            self.assertIsNotNone(packet_path)
            packet = json.loads(packet_path.read_text(encoding="utf-8"))

        lock = packet["skill_execution_lock"]
        self.assertEqual("active", lock["state"])
        self.assertIn("scientific-reporting", as_list(lock["locked_skill_ids"]))
        self.assertTrue(lock["resolution_required"])

    def test_lock_dispatch_stays_authoritative_over_current_router_projection(self) -> None:
        payload = run_ps_json(
            "& { "
            f". {ps_quote(str(RUNTIME_COMMON))}; "
            f". {ps_quote(str(SKILL_ROUTING_COMMON))}; "
            "$runtimePacket = [pscustomobject]@{ "
            "  skill_execution_lock = [pscustomobject]@{ "
            "    schema_version = 'v1'; state = 'active'; resolution_required = $true; "
            "    locked_dispatch = @([pscustomobject]@{ "
            "      skill_id = 'scientific-reporting'; task_slice = 'locked report'; dispatch_phase = 'post_execution'; "
            "      write_scope = 'specialist:scientific-reporting'; verification_expectation = 'report evidence' "
            "    }) "
            "  }; "
            "  skill_routing = [pscustomobject]@{ "
            "    selected = @([pscustomobject]@{ skill_id = 'latex-submission-pipeline'; task_slice = 'current pdf'; dispatch_phase = 'post_execution' }) "
            "  } "
            "}; "
            "$lockDispatch = Convert-VibeSkillExecutionLockToDispatch -SkillExecutionLock $runtimePacket.skill_execution_lock; "
            "$currentDispatch = Convert-VibeSkillRoutingSelectedToDispatch -RuntimeInputPacket $runtimePacket -SkillRouting $runtimePacket.skill_routing; "
            "[pscustomobject]@{ lock_dispatch = $lockDispatch; current_dispatch = $currentDispatch } | ConvertTo-Json -Depth 20 "
            "}"
        )

        self.assertEqual(["scientific-reporting"], [item["skill_id"] for item in as_list(payload["lock_dispatch"])])
        self.assertEqual(["latex-submission-pipeline"], [item["skill_id"] for item in as_list(payload["current_dispatch"])])
