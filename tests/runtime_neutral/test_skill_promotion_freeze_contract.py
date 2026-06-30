from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FREEZE_SCRIPT = REPO_ROOT / "scripts" / "runtime" / "Freeze-RuntimeInputPacket.ps1"
HELPER_SCRIPT = REPO_ROOT / "scripts" / "common" / "vibe-governance-helpers.ps1"
RUNTIME_COMMON = REPO_ROOT / "scripts" / "runtime" / "VibeRuntime.Common.ps1"
ML_PROMPT = (
    "Build a scikit-learn tabular classification baseline, "
    "run feature selection, and compare cross-validation metrics."
)


def resolve_powershell() -> str | None:
    candidates = [
        shutil.which("pwsh"),
        shutil.which("pwsh.exe"),
        r"C:\Program Files\PowerShell\7\pwsh.exe",
        r"C:\Program Files\PowerShell\7-preview\pwsh.exe",
        shutil.which("powershell"),
        shutil.which("powershell.exe"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(Path(candidate))
    return None


def freeze_runtime_packet(task: str, artifact_root: Path, target_root: Path | None = None) -> dict[str, object]:
    shell = resolve_powershell()
    if shell is None:
        raise unittest.SkipTest("PowerShell executable not available in PATH")

    run_id = "pytest-freeze-" + uuid.uuid4().hex[:10]
    env = dict(os.environ)
    if target_root is not None:
        env["VIBE_AGENTS_HOME"] = str(target_root)
    completed = subprocess.run(
        [
            shell,
            "-NoLogo",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            (
                "& { "
                f"$result = & '{FREEZE_SCRIPT}' "
                f"-Task '{task}' "
                "-Mode interactive_governed "
                f"-RunId '{run_id}' "
                f"-ArtifactRoot '{artifact_root}'; "
                "$result | ConvertTo-Json -Depth 20 }"
            ),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        env=env,
    )
    payload = json.loads(completed.stdout)
    if payload is None:
        raise AssertionError(
            "Freeze-RuntimeInputPacket.ps1 returned null. "
            f"stderr was: {completed.stderr.strip()}"
        )
    return payload


def load_json(path: str | Path) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def as_list(value: object) -> list[object]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def selected_rows_from_packet(packet: dict[str, object]) -> list[dict[str, object]]:
    routing = packet.get("skill_routing")
    if isinstance(routing, dict):
        selected = routing.get("selected")
        if isinstance(selected, list) and selected:
            return [item for item in selected if isinstance(item, dict)]
    work_binding = packet.get("work_binding")
    if not isinstance(work_binding, dict):
        return []
    units = work_binding.get("units")
    if not isinstance(units, list):
        return []
    rows: list[dict[str, object]] = []
    for unit in units:
        if not isinstance(unit, dict):
            continue
        skill_id = str(unit.get("bound_skill") or "").strip()
        if not skill_id:
            continue
        row = dict(unit)
        row["skill_id"] = skill_id
        row.setdefault("state", "selected")
        rows.append(row)
    return rows


def run_powershell_json(script_body: str) -> dict[str, object]:
    shell = resolve_powershell()
    if shell is None:
        raise unittest.SkipTest("PowerShell executable not available in PATH")

    completed = subprocess.run(
        [
            shell,
            "-NoLogo",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            f"& {{ . '{RUNTIME_COMMON}'; {script_body} }}",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return json.loads(completed.stdout)


def ps_path(path: Path) -> str:
    return path.resolve().as_posix().replace("'", "''")


def write_installed_skill(target_root: Path, skill_id: str) -> Path:
    skill_path = target_root / "skills" / skill_id / "SKILL.md"
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    skill_path.write_text(
        (
            "---\n"
            f"name: {skill_id}\n"
            f"description: Installed {skill_id} test skill.\n"
            "---\n"
        ),
        encoding="utf-8",
    )
    return skill_path


def extract_split_specialist_dispatch_function() -> str:
    content = FREEZE_SCRIPT.read_text(encoding="utf-8")
    match = re.search(
        r"(function Split-VibeSpecialistDispatch \{.*?^\})\s*^\$runtime =",
        content,
        re.DOTALL | re.MULTILINE,
    )
    if not match:
        raise AssertionError("Unable to locate Split-VibeSpecialistDispatch in Freeze-RuntimeInputPacket.ps1")
    return match.group(1)


class SkillPromotionFreezeContractTests(unittest.TestCase):
    def test_runtime_input_policy_keeps_specialist_recommendations_advisory_without_fallback_table(self) -> None:
        policy = load_json(REPO_ROOT / "config" / "runtime-input-packet-policy.json")

        self.assertTrue(bool(policy["require_specialist_decision_evidence"]))
        self.assertGreater(float(policy["minimum_specialist_recommendation_confidence"]), 0.0)
        self.assertFalse(bool(policy["include_stage_assistant_recommendations"]))
        self.assertNotIn("required_specialist_recommendation_count", policy)
        self.assertNotIn("fallback_specialists_by_task_type", policy)
        self.assertNotIn("specialist_binding_profiles", policy)
        self.assertNotIn("overlay_fields", policy)
        self.assertNotIn("router_script_path", policy)

    def test_eligible_matched_skill_is_approved_and_not_ghosted(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            target_root = Path(tempdir) / ".agents"
            write_installed_skill(target_root, "scikit-learn")
            payload = freeze_runtime_packet(ML_PROMPT, Path(tempdir), target_root)
            packet = load_json(payload["packet_path"])
            field_order = list(packet)
            self.assertLess(field_order.index("work_binding"), field_order.index("canonical_router"))
            self.assertLess(field_order.index("work_binding"), field_order.index("route_snapshot"))
            self.assertLess(field_order.index("specialist_decision"), field_order.index("skill_routing"))
            self.assertLess(field_order.index("specialist_decision"), field_order.index("divergence_shadow"))
            selected = selected_rows_from_packet(packet)
            selected_ids = [item["skill_id"] for item in selected]
            decision = packet["specialist_decision"]

            self.assertIn("scikit-learn", selected_ids)
            self.assertIn("scikit-learn", as_list(decision["matched_skill_ids"]))
            self.assertIn("scikit-learn", as_list(decision["approved_dispatch_skill_ids"]))
            self.assertGreaterEqual(len(as_list(decision["surfaced_skill_ids"])), len(as_list(decision["matched_skill_ids"])))

            scikit_dispatch = next(item for item in selected if item["skill_id"] == "scikit-learn")
            self.assertIsNotNone(
                scikit_dispatch["native_skill_entrypoint"],
                "scikit-learn dispatch should have native_skill_entrypoint populated before path checks",
            )
            self.assertTrue(Path(scikit_dispatch["native_skill_entrypoint"]).is_absolute())
            self.assertTrue(Path(scikit_dispatch["native_skill_entrypoint"]).exists())

    def test_freeze_records_explicit_states_for_all_surfaced_recommendations(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            target_root = Path(tempdir) / ".agents"
            write_installed_skill(target_root, "scikit-learn")
            payload = freeze_runtime_packet(ML_PROMPT, Path(tempdir), target_root)
            packet = load_json(payload["packet_path"])

            routing_rows = (
                as_list(packet["skill_routing"]["candidates"])
                + selected_rows_from_packet(packet)
                + as_list(packet["skill_routing"]["rejected"])
            )
            surfaced = {str(item["skill_id"]) for item in routing_rows if str(item["skill_id"])}
            states = {str(item["state"]) for item in routing_rows if str(item["skill_id"])}

            self.assertTrue(surfaced)
            self.assertTrue(states.issubset({"candidate", "selected", "rejected"}))

    def test_freeze_keeps_consultation_truth_out_of_execution_dispatch_surface(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            target_root = Path(tempdir) / ".agents"
            write_installed_skill(target_root, "scikit-learn")
            payload = freeze_runtime_packet(ML_PROMPT, Path(tempdir), target_root)
            packet = load_json(payload["packet_path"])

            self.assertNotIn("specialist_consultation", packet)
            self.assertNotIn("legacy_skill_routing", packet)
            self.assertGreaterEqual(len(as_list(packet["skill_routing"]["candidates"])), 1)
            self.assertGreaterEqual(len(selected_rows_from_packet(packet)), 1)

    def test_missing_native_entrypoint_cannot_auto_dispatch_even_when_policy_allows_incomplete_contract(self) -> None:
        split_function = extract_split_specialist_dispatch_function()
        payload = run_powershell_json(
            (
                "& { "
                f". '{HELPER_SCRIPT}'; "
                f"{split_function} "
                "$policy = [pscustomobject]@{ "
                "promotion_enabled = $true; "
                "default_mode = 'recall_first'; "
                "allow_auto_dispatch_when_non_destructive = $true; "
                "require_contract_complete = $false; "
                "destructive_prompt_patterns = [pscustomobject]@{}; "
                "degraded_fallback_rules = [pscustomobject]@{ missing_contract = 'explicit_degraded' } "
                "}; "
                "$recommendation = Get-VgoSkillPromotionMetadata "
                "-Prompt 'generic prompt' "
                "-SkillMdPath '' "
                "-Description '' "
                "-RequiredInputs @() "
                "-ExpectedOutputs @() "
                "-VerificationExpectation '' "
                "-PromotionPolicy $policy; "
                "$recommendation | Add-Member -NotePropertyName skill_id -NotePropertyValue 'demo-skill'; "
                "$dispatch = Split-VibeSpecialistDispatch -GovernanceScope 'root' -Recommendations @($recommendation); "
                "$dispatch | ConvertTo-Json -Depth 20 }"
            )
        )

        approved_dispatch = as_list(payload["approved_dispatch"])
        degraded = as_list(payload["degraded"])
        self.assertEqual([], approved_dispatch)
        self.assertEqual(1, len(degraded))
        self.assertEqual("demo-skill", degraded[0]["skill_id"])
        self.assertEqual("missing_native_entrypoint", degraded[0]["degrade_reason"])
        outcome = next(item for item in as_list(payload["promotion_outcomes"]) if item["skill_id"] == "demo-skill")
        self.assertEqual("degraded", outcome["promotion_state"])
        self.assertEqual("missing_native_entrypoint", outcome["degrade_reason"])

    def test_unresolvable_native_entrypoint_cannot_auto_dispatch(self) -> None:
        split_function = extract_split_specialist_dispatch_function()
        with tempfile.TemporaryDirectory() as tempdir:
            missing_skill_path = Path(tempdir) / "missing-skill" / "SKILL.md"
            payload = run_powershell_json(
                (
                    "& { "
                    f". '{HELPER_SCRIPT}'; "
                    f"{split_function} "
                    "$policy = [pscustomobject]@{ "
                    "promotion_enabled = $true; "
                    "default_mode = 'recall_first'; "
                    "allow_auto_dispatch_when_non_destructive = $true; "
                    "require_contract_complete = $true; "
                    "destructive_prompt_patterns = [pscustomobject]@{}; "
                    "degraded_fallback_rules = [pscustomobject]@{ missing_contract = 'explicit_degraded' } "
                    "}; "
                    "$recommendation = Get-VgoSkillPromotionMetadata "
                    "-Prompt 'generic prompt' "
                    f"-SkillMdPath '{ps_path(missing_skill_path)}' "
                    f"-SkillRoot '{ps_path(missing_skill_path.parent)}' "
                    "-Description 'desc' "
                    "-RequiredInputs @('input') "
                    "-ExpectedOutputs @('output') "
                    "-VerificationExpectation 'verify' "
                    "-PromotionPolicy $policy; "
                    "$recommendation | Add-Member -NotePropertyName skill_id -NotePropertyValue 'missing-local-skill'; "
                    f"$recommendation | Add-Member -NotePropertyName native_skill_entrypoint -NotePropertyValue '{ps_path(missing_skill_path)}'; "
                    "$dispatch = Split-VibeSpecialistDispatch -GovernanceScope 'root' -Recommendations @($recommendation); "
                    "$dispatch | ConvertTo-Json -Depth 20 }"
                )
            )

        self.assertEqual([], as_list(payload["approved_dispatch"]))
        degraded = as_list(payload["degraded"])
        self.assertEqual(["missing-local-skill"], [item["skill_id"] for item in degraded])
        self.assertEqual("missing_native_entrypoint", degraded[0]["degrade_reason"])

    def test_missing_native_entrypoint_never_enters_selected_or_lock_surfaces(self) -> None:
        split_function = extract_split_specialist_dispatch_function()
        skill_routing_common = REPO_ROOT / "scripts" / "runtime" / "VibeSkillRouting.Common.ps1"
        payload = run_powershell_json(
            (
                "& { "
                f". '{HELPER_SCRIPT}'; "
                f". '{skill_routing_common}'; "
                f". '{RUNTIME_COMMON}'; "
                f"{split_function} "
                "$policy = [pscustomobject]@{ "
                "promotion_enabled = $true; "
                "default_mode = 'recall_first'; "
                "allow_auto_dispatch_when_non_destructive = $true; "
                "require_contract_complete = $false; "
                "destructive_prompt_patterns = [pscustomobject]@{}; "
                "degraded_fallback_rules = [pscustomobject]@{ missing_contract = 'explicit_degraded' } "
                "}; "
                "$recommendation = Get-VgoSkillPromotionMetadata "
                "-Prompt 'generic prompt' "
                "-SkillMdPath '' "
                "-Description '' "
                "-RequiredInputs @() "
                "-ExpectedOutputs @() "
                "-VerificationExpectation '' "
                "-PromotionPolicy $policy; "
                "$recommendation | Add-Member -NotePropertyName skill_id -NotePropertyValue 'missing-local-skill'; "
                "$dispatch = Split-VibeSpecialistDispatch -GovernanceScope 'root' -Recommendations @($recommendation); "
                "$routing = New-VibeSkillRoutingFromLegacy "
                "-RouterSelectedSkill '' "
                "-Recommendations @($recommendation) "
                "-StageAssistantHints @() "
                "-SpecialistDispatch $dispatch; "
                "$lock = New-VibeSkillExecutionLockProjection -CurrentSkillRouting $routing -Source 'test'; "
                "[pscustomobject]@{ dispatch = $dispatch; routing = $routing; lock = $lock } | ConvertTo-Json -Depth 30 }"
            )
        )

        self.assertEqual([], as_list(payload["routing"]["selected"]))
        self.assertEqual(["missing-local-skill"], [item["skill_id"] for item in as_list(payload["routing"]["candidates"])])
        self.assertEqual(["missing-local-skill"], [item["skill_id"] for item in as_list(payload["routing"]["rejected"])])
        self.assertEqual("inactive", payload["lock"]["state"])
        self.assertEqual([], as_list(payload["lock"]["locked_dispatch"]))

    def test_split_specialist_dispatch_accepts_partial_host_decision_without_optional_lists(self) -> None:
        split_function = extract_split_specialist_dispatch_function()
        with tempfile.TemporaryDirectory() as tempdir:
            skill_path = Path(tempdir) / "SKILL.md"
            skill_path.write_text("---\nname: demo-skill\n---\n", encoding="utf-8")
            payload = run_powershell_json(
                (
                    "& { "
                    f". '{HELPER_SCRIPT}'; "
                    f"{split_function} "
                    "$policy = [pscustomobject]@{ "
                    "promotion_enabled = $true; "
                    "default_mode = 'recall_first'; "
                    "allow_auto_dispatch_when_non_destructive = $false; "
                    "require_contract_complete = $true; "
                    "destructive_prompt_patterns = [pscustomobject]@{}; "
                    "degraded_fallback_rules = [pscustomobject]@{ missing_contract = 'explicit_degraded' } "
                    "}; "
                    "$recommendation = Get-VgoSkillPromotionMetadata "
                    "-Prompt 'generic prompt' "
                    f"-SkillMdPath '{ps_path(skill_path)}' "
                    f"-SkillRoot '{ps_path(skill_path.parent)}' "
                    "-Description 'desc' "
                    "-RequiredInputs @('input') "
                    "-ExpectedOutputs @('output') "
                    "-VerificationExpectation 'verify' "
                    "-PromotionPolicy $policy; "
                    "$recommendation | Add-Member -NotePropertyName skill_id -NotePropertyValue 'demo-skill'; "
                    f"$recommendation | Add-Member -NotePropertyName native_skill_entrypoint -NotePropertyValue '{ps_path(skill_path)}'; "
                    "$hostDecision = [pscustomobject]@{ selection_mode = 'curated_only' }; "
                    "$dispatch = Split-VibeSpecialistDispatch "
                    "-GovernanceScope 'root' "
                    "-Recommendations @($recommendation) "
                    "-HostSpecialistDispatchDecision $hostDecision; "
                    "$dispatch | ConvertTo-Json -Depth 20 }"
                )
            )

        self.assertEqual([], as_list(payload["approved_dispatch"]))
        self.assertEqual(["demo-skill"], [item["skill_id"] for item in as_list(payload["local_specialist_suggestions"])])
        self.assertFalse(payload["escalation_required"])
        self.assertEqual("not_required", payload["escalation_status"])

    def test_surface_only_recommendation_is_not_auto_approved_in_root_scope(self) -> None:
        split_function = extract_split_specialist_dispatch_function()
        with tempfile.TemporaryDirectory() as tempdir:
            skill_path = Path(tempdir) / "SKILL.md"
            skill_path.write_text("---\nname: demo-skill\n---\n", encoding="utf-8")
            payload = run_powershell_json(
                (
                    "& { "
                    f". '{HELPER_SCRIPT}'; "
                    f"{split_function} "
                    "$policy = [pscustomobject]@{ "
                    "promotion_enabled = $true; "
                    "default_mode = 'recall_first'; "
                    "allow_auto_dispatch_when_non_destructive = $false; "
                    "require_contract_complete = $true; "
                    "destructive_prompt_patterns = [pscustomobject]@{}; "
                    "degraded_fallback_rules = [pscustomobject]@{ missing_contract = 'explicit_degraded' } "
                    "}; "
                    "$recommendation = Get-VgoSkillPromotionMetadata "
                    "-Prompt 'generic prompt' "
                    f"-SkillMdPath '{ps_path(skill_path)}' "
                    f"-SkillRoot '{ps_path(skill_path.parent)}' "
                    "-Description 'desc' "
                    "-RequiredInputs @('input') "
                    "-ExpectedOutputs @('output') "
                    "-VerificationExpectation 'verify' "
                    "-PromotionPolicy $policy; "
                    "$recommendation | Add-Member -NotePropertyName skill_id -NotePropertyValue 'demo-skill'; "
                    f"$recommendation | Add-Member -NotePropertyName native_skill_entrypoint -NotePropertyValue '{ps_path(skill_path)}'; "
                    "$dispatch = Split-VibeSpecialistDispatch -GovernanceScope 'root' -Recommendations @($recommendation); "
                    "$dispatch | ConvertTo-Json -Depth 20 }"
                )
            )

        self.assertEqual([], as_list(payload["approved_dispatch"]))
        self.assertEqual(["demo-skill"], [item["skill_id"] for item in as_list(payload["local_specialist_suggestions"])])
        outcome = next(item for item in as_list(payload["promotion_outcomes"]) if item["skill_id"] == "demo-skill")
        self.assertEqual("local_suggestion", outcome["promotion_state"])
        self.assertEqual("surface_only", outcome["recommended_promotion_action"])
