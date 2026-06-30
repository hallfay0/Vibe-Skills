from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = REPO_ROOT / "config" / "runtime-input-packet-policy.json"
RUNTIME_COMMON = REPO_ROOT / "scripts" / "runtime" / "VibeRuntime.Common.ps1"
FREEZE_SCRIPT = REPO_ROOT / "scripts" / "runtime" / "Freeze-RuntimeInputPacket.ps1"
PLAN_EXECUTE = REPO_ROOT / "scripts" / "runtime" / "Invoke-PlanExecute.ps1"
WRITE_REQUIREMENT_DOC = REPO_ROOT / "scripts" / "runtime" / "Write-RequirementDoc.ps1"
WRITE_XL_PLAN = REPO_ROOT / "scripts" / "runtime" / "Write-XlPlan.ps1"
CURRENT_FIELD_DOC = REPO_ROOT / "docs" / "governance" / "current-runtime-field-contract.md"
ENTRY_PROTOCOL_FILES = [
    REPO_ROOT / "SKILL.md",
    REPO_ROOT / "protocols" / "runtime.md",
    REPO_ROOT / "protocols" / "team.md",
]
CURRENT_USER_VISIBLE_RUNTIME_FILES = [
    WRITE_REQUIREMENT_DOC,
    WRITE_XL_PLAN,
    PLAN_EXECUTE,
    REPO_ROOT / "scripts" / "verify" / "vibe-governed-runtime-contract-gate.ps1",
    REPO_ROOT / "scripts" / "verify" / "vibe-runtime-execution-proof-gate.ps1",
]
RUNTIME_EXECUTION_PROOF_GATE = REPO_ROOT / "scripts" / "verify" / "vibe-runtime-execution-proof-gate.ps1"
NO_SILENT_FALLBACK_GATE = REPO_ROOT / "scripts" / "verify" / "vibe-no-silent-fallback-contract-gate.ps1"
CHILD_SPECIALIST_ESCALATION_GATE = REPO_ROOT / "scripts" / "verify" / "vibe-child-specialist-escalation-gate.ps1"
EXECUTION_CLOSURE_GATE = REPO_ROOT / "scripts" / "verify" / ("vibe-specialist-" + "dispatch-closure-gate.ps1")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class CurrentRoutingVocabularyFinalCleanupTests(unittest.TestCase):
    def test_policy_uses_current_skill_execution_contract_fields(self) -> None:
        policy = json.loads(read(POLICY_PATH))
        required_fields = set(policy["required_fields"])

        self.assertIn("work_binding", required_fields)
        self.assertIn("specialist_decision", required_fields)
        self.assertNotIn("overlay_decisions", required_fields)
        self.assertNotIn("route_snapshot", required_fields)
        self.assertNotIn("skill_usage", required_fields)
        self.assertNotIn("skill_routing", required_fields)
        self.assertNotIn("canonical_router", required_fields)
        self.assertNotIn("divergence_shadow", required_fields)
        self.assertNotIn("specialist_dispatch", required_fields)
        self.assertNotIn("specialist_recommendations", required_fields)

        self.assertIn("skill_execution_contract", policy)
        self.assertIn("host_skill_execution_contract", policy)
        self.assertIn("interactive_skill_execution_disclosure", policy)
        self.assertNotIn("specialist_dispatch_contract", policy)
        self.assertNotIn("host_specialist_dispatch_contract", policy)
        self.assertNotIn("interactive_specialist_disclosure", policy)

        disclosure = policy["interactive_skill_execution_disclosure"]
        self.assertEqual("selected_skill_execution_only", disclosure["scope"])
        self.assertEqual("Pre-execution skill disclosure:", disclosure["header"])

    def test_current_runtime_projection_helper_has_current_name_and_no_root_dispatch_fallback(self) -> None:
        text = read(RUNTIME_COMMON)

        self.assertIn("function Get-VibeRuntimeSelectedSkillExecutionProjection", text)
        self.assertNotIn("function Get-VibeRuntimeSpecialistDispatchProjection", text)
        self.assertNotIn("RuntimeInputPacket.specialist_dispatch", text)
        self.assertNotIn("PropertyName 'specialist_dispatch'", text)

        helper_body = text.split("function Get-VibeRuntimeSelectedSkillExecutionProjection", 1)[1].split(
            "function Get-VibeRuntimeSpecialistRecommendations",
            1,
        )[0]
        for field in [
            "selected_skill_execution",
            "blocked_skill_execution",
            "degraded_skill_execution",
            "selected_skill_ids",
            "blocked_skill_ids",
            "degraded_skill_ids",
            "$executionSource = 'work_binding.units[*].bound_skill'",
            "$executionStatus = 'derived_from_work_binding'",
        ]:
            self.assertIn(field, helper_body)
        for field in [
            "approved_dispatch",
            "local_specialist_suggestions",
            "approved_skill_ids",
        ]:
            self.assertNotIn(field, helper_body)

    def test_active_policy_readers_use_current_contract_names(self) -> None:
        freeze_text = read(FREEZE_SCRIPT)
        self.assertIn("skill_execution_contract", freeze_text)
        self.assertNotIn("specialist_dispatch_contract", freeze_text)

        runtime_text = read(RUNTIME_COMMON)
        self.assertIn("host_skill_execution_contract", runtime_text)
        self.assertIn("interactive_skill_execution_disclosure", runtime_text)
        self.assertNotIn("host_specialist_dispatch_contract", runtime_text)
        self.assertNotIn("interactive_specialist_disclosure", runtime_text)

    def test_generated_current_artifacts_do_not_use_dispatch_headings_or_counts(self) -> None:
        combined = "\n".join(
            [
                read(WRITE_REQUIREMENT_DOC),
                read(WRITE_XL_PLAN),
                read(PLAN_EXECUTE),
            ]
        )

        self.assertIn("Host Skill Execution Decision", combined)
        self.assertIn("selected_skill_execution_count", combined)
        self.assertNotIn("Host Specialist Dispatch Decision", combined)
        self.assertNotIn("approved_specialist_dispatch_count", combined)
        self.assertNotRegex(combined, r"(?m)^\s*dispatch_unit_count\s*=")

    def test_current_user_visible_surfaces_use_skill_execution_wording(self) -> None:
        combined = "\n".join(read(path) for path in ENTRY_PROTOCOL_FILES + CURRENT_USER_VISIBLE_RUNTIME_FILES)

        for forbidden in [
            "## Specialist Dispatch",
            "## Native Specialist Dispatch",
            "## Specialist Decision",
            "## Specialist Decision Plan",
            "## Specialist Skill Dispatch Plan",
            "## Specialist Dispatch Audit",
            "specialist dispatch section",
            "specialist dispatch integrity proof",
            "specialist dispatch accounting",
            "fallback specialist dispatch",
        ]:
            self.assertNotIn(forbidden, combined)

        for required in [
            "Skill Execution",
            "Skill Execution Decision",
            "Selected Skill Execution Plan",
            "selected_skill_execution",
        ]:
            self.assertIn(required, combined)

    def test_current_runtime_field_doc_uses_selected_skill_execution_anchor(self) -> None:
        text = read(CURRENT_FIELD_DOC)
        current_section = text.split("## Retired Layer", 1)[0]

        self.assertIn("selected_skill_execution", current_section)
        self.assertIn("skill_execution_units", current_section)
        self.assertIn("execution_skill_outcomes", current_section)
        self.assertNotIn("approved_skill_execution", current_section)
        self.assertNotIn("specialist_dispatch as root routing packet field", current_section)

    def test_runtime_execution_proof_gate_reads_current_skill_execution_counts(self) -> None:
        text = read(RUNTIME_EXECUTION_PROOF_GATE)

        self.assertIn("executeReceipt.skill_execution_unit_count", text)
        self.assertIn("executionManifest.specialist_accounting.skill_execution_unit_count", text)
        self.assertIn("proofManifest.skill_execution_unit_count", text)
        self.assertIn("compatibility skill mirror subordinate to work_binding", text)
        self.assertIn("legacy specialist recommendations stay subordinate to work_binding", text)
        self.assertNotIn("executeReceipt.specialist_dispatch_unit_count", text)
        self.assertNotIn("executionManifest.specialist_accounting.dispatch_unit_count", text)
        self.assertNotIn("proofManifest.specialist_dispatch_unit_count", text)

    def test_no_silent_fallback_gate_keeps_selected_skill_mirror_subordinate_to_work_binding(self) -> None:
        text = read(NO_SILENT_FALLBACK_GATE)

        self.assertIn("skill_routing stays an optional compatibility mirror", text)
        self.assertIn("compatibility selected skills stay subordinate to work_binding", text)
        self.assertIn("low-signal route stays explicit via non-authoritative fallback guard or explicit host selection", text)
        self.assertNotIn("records selected skills or no-specialist resolution evidence", text)

    def test_child_specialist_escalation_gate_keeps_work_binding_ahead_of_dispatch_residue(self) -> None:
        text = read(CHILD_SPECIALIST_ESCALATION_GATE)

        self.assertIn("child runtime packet includes work_binding", text)
        self.assertIn("child runtime packet keeps root-approved bounded work in work_binding", text)
        self.assertIn("child runtime packet keeps compatibility selected skills subordinate to work_binding", text)
        self.assertIn("residual local specialist suggestion does not mutate current work_binding", text)
        self.assertNotIn("runtime packet exposes specialist dispatch surface", text)

    def test_execution_closure_gate_reads_work_binding_before_closure_proof(self) -> None:
        text = read(EXECUTION_CLOSURE_GATE)

        self.assertIn("official smoke runtime packet includes work_binding", text)
        self.assertIn("official smoke work_binding carries bounded skill truth", text)
        self.assertIn("official smoke compatibility selected skills stay subordinate to work_binding", text)
        self.assertIn("child closure smoke keeps inherited bounded work in work_binding", text)
        self.assertIn("child closure smoke keeps compatibility selected skills subordinate to work_binding", text)
        self.assertIn("child closure smoke residual local suggestion does not mutate work_binding", text)

    def test_team_protocol_frames_selected_skill_execution_as_work_binding_follow_on(self) -> None:
        text = read(REPO_ROOT / "protocols" / "team.md")

        self.assertIn("`work_binding` remains the source of truth", text)
        self.assertIn("`selected_skill_execution` is the execution-side copy", text)
        self.assertIn("execution-side copy of root-approved bounded work from `work_binding`", text)
        self.assertNotIn("skill usage selected by root and frozen in plan; child lanes may execute directly", text)


if __name__ == "__main__":
    unittest.main()
