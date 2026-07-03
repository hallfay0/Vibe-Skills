from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "packages" / "runtime-core" / "src"))

from vgo_runtime.router_contract_runtime import route_prompt  # noqa: E402


def load_manifest() -> dict[str, object]:
    return json.loads((REPO_ROOT / "config" / "pack-manifest.json").read_text(encoding="utf-8-sig"))


def load_pack(pack_id: str) -> dict[str, object]:
    manifest = load_manifest()
    return next(pack for pack in manifest["packs"] if pack["id"] == pack_id)


def route(prompt: str, task_type: str = "research", grade: str = "L") -> dict[str, object]:
    return route_prompt(prompt=prompt, grade=grade, task_type=task_type, repo_root=REPO_ROOT)


def write_local_skill(skills_root: Path, skill_id: str, description: str, name: str | None = None) -> None:
    skill_file = skills_root / skill_id / "SKILL.md"
    skill_file.parent.mkdir(parents=True, exist_ok=True)
    skill_file.write_text(
        f"---\nname: {name or skill_id}\ndescription: {description}\n---\n# {skill_id}\n",
        encoding="utf-8",
    )


def route_with_local_code_review_skills(
    prompt: str,
    task_type: str = "review",
    grade: str = "L",
) -> dict[str, object]:
    temp_dir = tempfile.TemporaryDirectory()
    agent_root = Path(temp_dir.name) / "home" / ".agents"
    skills_root = agent_root / "skills"
    write_local_skill(
        skills_root,
        "code-reviewer",
        "Review code changes for bugs, bug risk, regression risk, and implementation defects.",
        name="bug risk",
    )
    write_local_skill(
        skills_root,
        "requesting-code-review",
        "Prepare code review requests, merge review materials, and reviewer context.",
        name="request code review",
    )
    write_local_skill(
        skills_root,
        "receiving-code-review",
        "Handle received review comments, CodeRabbit comments, and reviewer feedback.",
        name="review comments",
    )
    result = route_prompt(
        prompt=prompt,
        grade=grade,
        task_type=task_type,
        target_root=str(agent_root),
        host_id="codex",
        repo_root=REPO_ROOT,
    )
    result["_temp_dir"] = temp_dir
    return result


def route_with_local_ml_skills(
    prompt: str,
    task_type: str = "planning",
    grade: str = "L",
) -> dict[str, object]:
    temp_dir = tempfile.TemporaryDirectory()
    agent_root = Path(temp_dir.name) / "home" / ".agents"
    skills_root = agent_root / "skills"
    write_local_skill(
        skills_root,
        "ml-pipeline-workflow",
        "Plan complete 机器学习建模流程, model training, evaluation, model comparison, and result reporting.",
        name="机器学习建模流程",
    )
    write_local_skill(
        skills_root,
        "preprocessing-data-with-automated-pipelines",
        "Build data preprocessing pipelines for cleaning, feature encoding, standardization, and input validation.",
        name="data preprocessing",
    )
    write_local_skill(
        skills_root,
        "ml-data-leakage-guard",
        "Review train test leakage, fit before split, prediction time leakage, and validation contamination.",
        name="数据泄漏",
    )
    result = route_prompt(
        prompt=prompt,
        grade=grade,
        task_type=task_type,
        target_root=str(agent_root),
        host_id="codex",
        repo_root=REPO_ROOT,
    )
    result["_temp_dir"] = temp_dir
    return result


def selected(result: dict[str, object]) -> tuple[str, str]:
    selected_row = result.get("selected")
    if not isinstance(selected_row, dict):
        return "", ""
    return str(selected_row.get("pack_id") or ""), str(selected_row.get("skill") or "")


def pack_row(result: dict[str, object], pack_id: str) -> dict[str, object]:
    ranked = result.get("ranked")
    assert isinstance(ranked, list), result
    row = next((item for item in ranked if isinstance(item, dict) and item.get("pack_id") == pack_id), None)
    assert isinstance(row, dict), result
    return row


def ranked_summary(result: dict[str, object]) -> list[tuple[str, str, float, str]]:
    ranked = result.get("ranked")
    assert isinstance(ranked, list), result
    rows: list[tuple[str, str, float, str]] = []
    for row in ranked[:8]:
        assert isinstance(row, dict), row
        rows.append(
            (
                str(row.get("pack_id") or ""),
                str(row.get("selected_candidate") or ""),
                float(row.get("score") or 0.0),
                str(row.get("candidate_selection_reason") or ""),
            )
        )
    return rows


class FinalStageAssistantRemovalTests(unittest.TestCase):
    def assert_selected(
        self,
        prompt: str,
        expected_pack: str,
        expected_skill: str,
        *,
        task_type: str = "research",
        grade: str = "L",
    ) -> dict[str, object]:
        result = route(prompt, task_type=task_type, grade=grade)
        self.assertEqual((expected_pack, expected_skill), selected(result), ranked_summary(result))
        return result

    def test_manifest_has_no_legacy_candidate_fields(self) -> None:
        manifest = load_manifest()
        for pack in manifest["packs"]:
            self.assertNotIn("route_authority_candidates", pack)
            self.assertNotIn("stage_assistant_candidates", pack)

    def test_code_quality_manifest_makes_requesting_review_direct_owner(self) -> None:
        pack = load_pack("code-quality")
        expected = [
            "code-reviewer",
            "deslop",
            "generating-test-reports",
            "receiving-code-review",
            "requesting-code-review",
            "security-reviewer",
            "systematic-debugging",
            "tdd-guide",
            "verification-before-completion",
            "windows-hook-debugging",
        ]
        self.assertEqual(expected, pack["skill_candidates"])
        self.assertNotIn("route_authority_candidates", pack)
        self.assertNotIn("stage_assistant_candidates", pack)

    def test_review_request_preparation_routes_to_requesting_code_review(self) -> None:
        result = route_with_local_code_review_skills(
            "request code review before merge：请整理提交评审材料，准备 code review request",
            task_type="review",
        )
        self.assertEqual(("local-skill-index", "requesting-code-review"), selected(result), ranked_summary(result))
        ranked = result.get("ranked")
        assert isinstance(ranked, list), result
        row = next(
            item
            for item in ranked
            if isinstance(item, dict) and item.get("skill") == "requesting-code-review"
        )
        self.assertNotIn("legacy_role", row)
        self.assertNotIn("stage_assistant_candidates", row)
        self.assertNotIn("route_authority_eligible", row)

    def test_actual_code_review_stays_with_code_reviewer(self) -> None:
        result = route_with_local_code_review_skills(
            "请做 code review，审查这次代码改动 code change 有没有 bug risk 和回归风险",
            task_type="review",
        )
        self.assertEqual(("local-skill-index", "code-reviewer"), selected(result), ranked_summary(result))

    def test_received_review_feedback_routes_to_receiving_code_review(self) -> None:
        result = route_with_local_code_review_skills(
            "我收到了 CodeRabbit review comments 和评审意见，请逐条判断并处理",
            task_type="review",
        )
        self.assertEqual(("local-skill-index", "receiving-code-review"), selected(result), ranked_summary(result))

    def test_data_ml_manifest_makes_preprocessing_direct_owner(self) -> None:
        pack = load_pack("data-ml")
        expected = [
            "aeon",
            "evaluating-machine-learning-models",
            "exploratory-data-analysis",
            "ml-data-leakage-guard",
            "ml-pipeline-workflow",
            "preprocessing-data-with-automated-pipelines",
            "scikit-learn",
            "shap",
        ]
        self.assertEqual(expected, pack["skill_candidates"])
        self.assertNotIn("route_authority_candidates", pack)
        self.assertNotIn("stage_assistant_candidates", pack)

    def test_preprocessing_pipeline_routes_directly_and_has_no_stage_metadata(self) -> None:
        result = route_with_local_ml_skills(
            "机器学习 data preprocessing pipeline：清洗数据、feature encoding、standardize data、validate input data，输出可复用预处理流水线",
            task_type="coding",
        )
        self.assertEqual(
            ("local-skill-index", "preprocessing-data-with-automated-pipelines"),
            selected(result),
            ranked_summary(result),
        )
        ranked = result.get("ranked")
        assert isinstance(ranked, list), result
        row = next(
            item
            for item in ranked
            if isinstance(item, dict) and item.get("skill") == "preprocessing-data-with-automated-pipelines"
        )
        self.assertNotIn("legacy_role", row)
        self.assertNotIn("stage_assistant_candidates", row)
        self.assertNotIn("route_authority_eligible", row)

    def test_broad_ml_workflow_does_not_route_to_preprocessing(self) -> None:
        result = route_with_local_ml_skills(
            "我需要一个完整机器学习建模流程，包括训练、评估、模型比较和结果汇报",
            task_type="planning",
        )
        self.assertEqual(("local-skill-index", "ml-pipeline-workflow"), selected(result), ranked_summary(result))
        self.assertNotEqual("preprocessing-data-with-automated-pipelines", selected(result)[1])

    def test_data_leakage_stays_with_guard(self) -> None:
        result = route_with_local_ml_skills(
            "请检查训练集和测试集是否发生数据泄漏，尤其是 fit before split 和 prediction time 问题",
            task_type="review",
        )
        self.assertEqual(("local-skill-index", "ml-data-leakage-guard"), selected(result), ranked_summary(result))

    def test_retained_target_skill_docs_do_not_describe_stage_assistant_roles(self) -> None:
        forbidden = [
            "stage assistant",
            "stage-assistant",
            "阶段助手",
            "辅助专家",
            "次技能",
        ]
        for skill_id in [
            "requesting-code-review",
            "preprocessing-data-with-automated-pipelines",
        ]:
            path = REPO_ROOT / "bundled" / "skills" / skill_id / "SKILL.md"
            text = path.read_text(encoding="utf-8").lower()
            with self.subTest(skill_id=skill_id):
                for phrase in forbidden:
                    self.assertNotIn(phrase.lower(), text)


if __name__ == "__main__":
    unittest.main()
