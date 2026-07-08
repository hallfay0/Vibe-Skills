from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "verify" / "runtime_neutral" / "runtime_delivery_acceptance.py"
SPEC = importlib.util.spec_from_file_location("runtime_delivery_acceptance", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load runtime delivery acceptance module from {MODULE_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
evaluate = MODULE.evaluate
write_artifacts = MODULE.write_artifacts


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


class RuntimeDeliveryAcceptanceTests(unittest.TestCase):
    def _build_session(
        self,
        *,
        execution_status: str = "completed",
        failed_unit_count: int = 0,
        manual_spot_checks: list[str] | None = None,
        artifact_review_requirements: list[str] | None = None,
        code_task_tdd_evidence_requirements: list[str] | None = None,
        phase_execute_artifact_review: dict[str, object] | None = None,
        phase_execute_tdd_evidence: dict[str, object] | None = None,
        phase_execute_specialist_decision: dict[str, object] | None = None,
        phase_execute_specialist_user_disclosure: dict[str, object] | None = None,
        approved_dispatch: list[dict[str, object]] | None = None,
        specialist_accounting: dict[str, object] | None = None,
        specialist_execution_path: str | None = None,
        artifact_review_path: str | None = None,
        tdd_evidence_path: str | None = None,
        skill_usage: dict[str, object] | None = None,
        work_binding: dict[str, object] | None = None,
    ) -> Path:
        tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(tempdir.cleanup)
        root = Path(tempdir.name)
        session_root = root / "outputs" / "runtime" / "vibe-sessions" / "pytest-runtime-delivery"
        session_root.mkdir(parents=True, exist_ok=True)

        requirement_doc_path = root / "docs" / "requirements" / "pytest.md"
        execution_plan_path = root / "docs" / "plans" / "pytest-plan.md"
        execution_manifest_path = session_root / "execution-manifest.json"
        runtime_input_packet_path = session_root / "runtime-input-packet.json"

        requirement_lines = [
            "# Pytest Delivery Contract",
            "",
            "## Product Acceptance Criteria",
            "- Deliverable behavior matches the frozen requirement.",
            "",
            "## Manual Spot Checks",
        ]
        if manual_spot_checks:
            requirement_lines.extend([f"- {item}" for item in manual_spot_checks])
        else:
            requirement_lines.append("- None required beyond automated verification for this task.")
        requirement_lines += [
            "",
            "## Completion Language Policy",
            "- Full completion wording requires passing delivery truth.",
            "",
            "## Delivery Truth Contract",
            "- Governance truth remains distinct from product acceptance truth.",
            "",
        ]
        if artifact_review_requirements:
            requirement_lines += [
                "## Artifact Review Requirements",
                *[f"- {item}" for item in artifact_review_requirements],
                "",
            ]
        if code_task_tdd_evidence_requirements:
            requirement_lines += [
                "## Code Task TDD Evidence Requirements",
                *[f"- {item}" for item in code_task_tdd_evidence_requirements],
                "",
            ]
        write_text(requirement_doc_path, "\n".join(requirement_lines) + "\n")
        write_text(
            execution_plan_path,
            "# Pytest Plan\n\n## Delivery Acceptance Plan\n- Emit the runtime delivery report.\n",
        )

        selected_skill_execution = list(approved_dispatch or [])
        execution_manifest_payload = {
            "run_id": "pytest-runtime-delivery-run",
            "status": execution_status,
            "governance_scope": "root",
            "executed_unit_count": 3,
            "failed_unit_count": failed_unit_count,
            "timed_out_unit_count": 0,
        }
        execution_manifest_payload["specialist_accounting"] = {
            "selected_skill_execution": selected_skill_execution,
            "selected_skill_execution_count": len(selected_skill_execution),
            "blocked_skill_execution_unit_count": 0,
            "blocked_skill_execution_units": [],
            "degraded_skill_execution_unit_count": 0,
            "degraded_skill_execution_units": [],
            "degraded_skill_ids": [],
            "blocked_skill_ids": [],
            "effective_execution_status": "live_native_executed" if selected_skill_execution else "none",
        }
        if specialist_accounting:
            execution_manifest_payload["specialist_accounting"].update(specialist_accounting)
        write_json(execution_manifest_path, execution_manifest_payload)

        approved_skill_ids = [
            str(item["skill_id"]).strip()
            for item in selected_skill_execution
            if str(item.get("skill_id", "")).strip()
        ]

        runtime_input_packet_payload: dict[str, object] = {
            "authority_flags": {
                "explicit_runtime_skill": "vibe",
            }
        }
        if work_binding is not None:
            runtime_input_packet_payload["work_binding"] = work_binding
        if approved_skill_ids:
            runtime_input_packet_payload["specialist_decision"] = {
                "decision_state": "approved_dispatch",
                "resolution_mode": "approved_dispatch",
                "approved_dispatch_skill_ids": approved_skill_ids,
                "repo_asset_fallback": {
                    "used": False,
                    "asset_paths": [],
                    "reason": "",
                    "legal_basis": "",
                    "traceability_basis": [],
                },
            }
        if skill_usage is not None:
            write_json(session_root / "skill-usage.json", skill_usage)
        write_json(runtime_input_packet_path, runtime_input_packet_payload)

        phase_execute_payload: dict[str, object] = {
            "run_id": "pytest-runtime-delivery-run",
            "requirement_doc_path": str(requirement_doc_path),
            "execution_plan_path": str(execution_plan_path),
            "execution_manifest_path": str(execution_manifest_path),
            "runtime_input_packet_path": str(runtime_input_packet_path),
            "completion_claim_allowed": True,
            "artifact_review": phase_execute_artifact_review or {},
            "tdd_evidence": phase_execute_tdd_evidence or {},
        }
        if phase_execute_specialist_user_disclosure is not None:
            phase_execute_payload["specialist_user_disclosure"] = phase_execute_specialist_user_disclosure
        if phase_execute_specialist_decision is not None:
            phase_execute_payload["specialist_decision"] = phase_execute_specialist_decision
        elif approved_skill_ids:
            phase_execute_payload["specialist_decision"] = {
                "decision_state": "approved_dispatch",
                "resolution_mode": "approved_dispatch",
                "approved_dispatch_skill_ids": approved_skill_ids,
                "repo_asset_fallback": {
                    "used": False,
                    "asset_paths": [],
                    "reason": "",
                    "legal_basis": "",
                    "traceability_basis": [],
                },
            }
        else:
            phase_execute_payload["specialist_decision"] = {
                "decision_state": "no_specialist_recommendations",
                "resolution_mode": "no_specialist_needed",
                "repo_asset_fallback": {
                    "used": False,
                    "asset_paths": [],
                    "reason": "",
                    "legal_basis": "",
                    "traceability_basis": [],
                },
            }
        if artifact_review_path:
            phase_execute_payload["artifact_review_path"] = artifact_review_path
        if tdd_evidence_path:
            phase_execute_payload["tdd_evidence_path"] = tdd_evidence_path
        if specialist_execution_path:
            phase_execute_payload["specialist_execution_path"] = specialist_execution_path
        write_json(session_root / "phase-execute.json", phase_execute_payload)
        write_json(session_root / "cleanup-receipt.json", {"cleanup_mode": "bounded_cleanup_executed"})
        return session_root

    def test_delivery_acceptance_passes_for_clean_root_run(self) -> None:
        session_root = self._build_session()

        report = evaluate(REPO_ROOT, session_root)

        self.assertEqual("PASS", report["summary"]["gate_result"])
        self.assertTrue(report["summary"]["completion_language_allowed"])
        self.assertEqual("passing", report["truth_results"]["product_acceptance_truth"]["state"])
        self.assertEqual("passing", report["truth_results"]["specialist_decision_truth"]["state"])

    def test_delivery_acceptance_fails_when_selected_skill_lacks_load_evidence(self) -> None:
        session_root = self._build_session(
            work_binding={
                "schema_version": "runtime_work_binding_v1",
                "source": "approved_dispatch",
                "task": "debug task",
                "run_id": "pytest-runtime-delivery-run",
                "unit_count": 1,
                "status": "projected_from_approved_dispatch",
                "units": [
                    {
                        "work_unit_id": "wu-1",
                        "bound_skill": "scanpy",
                        "binding_profile": "selected_skill",
                    }
                ],
            },
            skill_usage={
                "schema_version": 2,
                "state_model": "binary_used_unused",
                "used": [],
                "unused": [{"skill_id": "scanpy", "reason": "selected_but_not_loaded"}],
                "loaded_skills": [],
            },
        )

        report = evaluate(REPO_ROOT, session_root)

        self.assertEqual("FAIL", report["skill_usage_truth"]["state"])
        self.assertEqual(["scanpy"], report["execution_context"]["selected_skill_ids"])
        self.assertIn("selected_skill_missing_load_evidence", report["skill_usage_truth"]["failure_reasons"])

    def test_delivery_acceptance_reports_pass_degraded_for_traceable_repo_asset_fallback(self) -> None:
        session_root = self._build_session(
            phase_execute_specialist_decision={
                "decision_state": "no_specialist_recommendations",
                "resolution_mode": "repo_asset_fallback",
                "repo_asset_fallback": {
                    "used": True,
                    "asset_paths": [
                        "outputs/agent-runs/2026-04-14-scheme-a-clean397-paper-report/scripts/plot_style.py"
                    ],
                    "reason": "Reuse the existing paper-report plotting style asset when no dedicated plotting specialist is available.",
                    "legal_basis": "Repo-local plotting asset already present inside governed workspace outputs.",
                    "traceability_basis": [
                        "outputs/agent-runs/2026-04-14-scheme-a-clean397-paper-report/scripts/plot_style.py"
                    ],
                },
            }
        )

        report = evaluate(REPO_ROOT, session_root)

        self.assertEqual("PASS_DEGRADED", report["summary"]["gate_result"])
        self.assertFalse(report["summary"]["completion_language_allowed"])
        self.assertEqual("degraded", report["truth_results"]["specialist_decision_truth"]["state"])

    def test_delivery_acceptance_requires_manual_review_when_host_continuation_is_pending(self) -> None:
        approved_dispatch = [
            {
                "skill_id": "systematic-debugging",
                "native_skill_entrypoint": "/tmp/systematic-debugging/SKILL.md",
            }
        ]
        session_root = self._build_session(
            approved_dispatch=approved_dispatch,
            phase_execute_specialist_user_disclosure={
                "scope": "selected_skill_execution_only",
                "timing": "before_execution",
                "path_source": "native_skill_entrypoint",
                "routed_skills": [
                    {
                        "skill_id": "systematic-debugging",
                        "native_skill_entrypoint": "/tmp/systematic-debugging/SKILL.md",
                        "entrypoint_requirement_satisfied": True,
                    }
                ],
            },
            specialist_accounting={
                "selected_skill_execution": approved_dispatch,
                "selected_skill_execution_count": 1,
                "effective_execution_status": "direct_current_session_routed",
            },
        )

        report = evaluate(REPO_ROOT, session_root)

        self.assertEqual("MANUAL_REVIEW_REQUIRED", report["summary"]["gate_result"])
        self.assertEqual("manual_review_required", report["truth_results"]["workflow_completion_truth"]["state"])
        self.assertTrue(report["execution_context"]["specialist_host_continuation_pending"])

    def test_delivery_acceptance_requires_manual_review_when_spot_checks_pending(self) -> None:
        session_root = self._build_session(
            manual_spot_checks=["Open the primary UI flow and confirm the main path works end-to-end."]
        )

        report = evaluate(REPO_ROOT, session_root)

        self.assertEqual("MANUAL_REVIEW_REQUIRED", report["summary"]["gate_result"])
        self.assertEqual("manual_actions_pending", report["summary"]["readiness_state"])
        self.assertEqual("manual_review_required", report["truth_results"]["product_acceptance_truth"]["state"])

    def test_delivery_acceptance_requires_tdd_evidence_for_code_tasks(self) -> None:
        requirements = [
            "Record failing-first evidence for the changed behavior before implementation or defect correction.",
            "Record the green rerun that proves the targeted behavior passed after implementation.",
        ]
        session_root = self._build_session(
            code_task_tdd_evidence_requirements=requirements,
        )

        report = evaluate(REPO_ROOT, session_root)

        self.assertEqual("MANUAL_REVIEW_REQUIRED", report["summary"]["gate_result"])
        self.assertEqual("manual_review_required", report["truth_results"]["code_task_tdd_evidence_truth"]["state"])
        self.assertEqual(requirements, report["frozen_requirement_sections"]["code_task_tdd_evidence_requirements"])

    def test_delivery_acceptance_rejects_explicit_payload_paths_outside_session_root(self) -> None:
        requirements = [
            "Record failing-first evidence for the changed behavior before implementation or defect correction.",
        ]
        with tempfile.TemporaryDirectory() as tempdir:
            outside_root = Path(tempdir)
            artifact_payload_path = outside_root / "outside-artifact-review.json"
            tdd_payload_path = outside_root / "outside-tdd-evidence.json"
            write_json(
                artifact_payload_path,
                {
                    "status": "passing",
                    "evidence_paths": ["/tmp/outside-artifact-review.md"],
                },
            )
            write_json(
                tdd_payload_path,
                {
                    "status": "passing",
                    "evidence_paths": ["/tmp/outside-tdd-evidence.md"],
                    "covered_code_task_tdd_evidence_requirements": requirements,
                    "red_phase_evidence_paths": ["/tmp/outside-tdd-red.txt"],
                    "green_phase_evidence_paths": ["/tmp/outside-tdd-green.txt"],
                },
            )
            session_root = self._build_session(
                artifact_review_requirements=[
                    "Inspect the final artifact directly and confirm required controls are present."
                ],
                code_task_tdd_evidence_requirements=requirements,
                artifact_review_path=str(artifact_payload_path),
                tdd_evidence_path=str(tdd_payload_path),
            )

            report = evaluate(REPO_ROOT, session_root)

        self.assertEqual("MANUAL_REVIEW_REQUIRED", report["summary"]["gate_result"])
        self.assertEqual("", report["execution_context"]["artifact_review_source_path"])
        self.assertEqual("", report["execution_context"]["tdd_evidence_source_path"])

    def test_delivery_acceptance_markdown_report_surfaces_frozen_sections_and_coverage(self) -> None:
        requirements = [
            "Record failing-first evidence for the changed behavior before implementation or defect correction.",
            "Record the green rerun that proves the targeted behavior passed after implementation.",
        ]
        session_root = self._build_session(
            artifact_review_requirements=[
                "Inspect the final deliverable directly and confirm the primary CTA provides visible feedback."
            ],
            code_task_tdd_evidence_requirements=requirements,
            phase_execute_artifact_review={
                "status": "passing",
                "evidence_paths": ["/tmp/pytest-artifact-review-notes.md"],
                "covered_task_specific_acceptance_extensions": [
                    "The CTA should show a loading state before the success message."
                ],
                "covered_baseline_document_quality_dimensions": [
                    "Structure Integrity",
                    "Formatting Consistency",
                ],
                "covered_baseline_ui_quality_dimensions": [
                    "Structure and visual hierarchy",
                    "Interaction feedback and affordances",
                ],
                "considered_research_augmentation_sources": ["NN/g feedback visibility heuristics"],
                "notes": "Reviewed final artifact against frozen acceptance coverage.",
            },
            phase_execute_tdd_evidence={
                "status": "passing",
                "evidence_paths": ["/tmp/pytest-tdd-evidence.md"],
                "red_phase_evidence_paths": ["/tmp/pytest-tdd-red.txt"],
                "green_phase_evidence_paths": ["/tmp/pytest-tdd-green.txt"],
                "covered_code_task_tdd_evidence_requirements": requirements,
                "notes": "Captured red/green TDD evidence for the code change.",
            },
            skill_usage={
                "schema_version": 1,
                "state_model": "binary_used_unused",
                "used_skills": ["scanpy"],
                "unused_skills": [],
                "loaded_skills": [
                    {
                        "skill_id": "scanpy",
                        "skill_md_path": "bundled/skills/scanpy/SKILL.md",
                        "skill_md_sha256": "a" * 64,
                        "load_status": "loaded_full_skill_md",
                        "loaded_at_stage": "skeleton_check",
                    }
                ],
                "evidence": [
                    {
                        "skill_id": "scanpy",
                        "stage": "xl_plan",
                        "artifact_ref": "xl_plan.md",
                        "impact_summary": "Plan adopts the loaded scanpy workflow.",
                    }
                ],
                "unused_reasons": [],
            },
            work_binding={
                "schema_version": "runtime_work_binding_v1",
                "source": "approved_dispatch",
                "task": "debug task",
                "run_id": "pytest-runtime-delivery-run",
                "unit_count": 1,
                "status": "projected_from_approved_dispatch",
                "units": [
                    {
                        "work_unit_id": "wu-1",
                        "bound_skill": "scanpy",
                        "binding_profile": "selected_skill",
                    }
                ],
            },
        )
        artifact = evaluate(REPO_ROOT, session_root)

        with tempfile.TemporaryDirectory() as tempdir:
            output_root = Path(tempdir)
            write_artifacts(artifact, output_root)
            md_text = (output_root / "delivery-acceptance-report.md").read_text(encoding="utf-8")

        self.assertIn("Frozen Artifact Review Requirements", md_text)
        self.assertIn("Frozen Code Task TDD Evidence Requirements", md_text)
        self.assertIn("Code Task TDD Evidence Coverage", md_text)
        self.assertIn("Artifact Review Coverage", md_text)
        self.assertIn("Selected Skill Truth", md_text)
        self.assertIn("Runtime packet selected skill source", md_text)
        self.assertIn("Covered code-task TDD evidence requirement", md_text)


if __name__ == "__main__":
    unittest.main()
