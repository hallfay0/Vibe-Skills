from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "packages" / "runtime-core" / "src"))

from vgo_runtime.router_contract_runtime import route_prompt  # noqa: E402


def load_pack(pack_id: str) -> dict[str, object]:
    manifest = json.loads((REPO_ROOT / "config" / "pack-manifest.json").read_text(encoding="utf-8-sig"))
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


def route_with_local_science_figure_skills(
    prompt: str,
    task_type: str = "research",
    grade: str = "L",
) -> dict[str, object]:
    temp_dir = tempfile.TemporaryDirectory()
    agent_root = Path(temp_dir.name) / "home" / ".agents"
    skills_root = agent_root / "skills"
    write_local_skill(
        skills_root,
        "scientific-visualization",
        "Create publication-ready scientific figures, matplotlib plots, seaborn charts, plotly dashboards, colorblind panels, vector export, and journal visualization.",
    )
    write_local_skill(
        skills_root,
        "scientific-schematics",
        "Create Mermaid flowcharts, experiment schematics, scientific diagrams, and reproducible markdown diagrams.",
        name="Mermaid",
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


def route_with_local_scientific_writing_skill(
    prompt: str,
    task_type: str = "research",
    grade: str = "L",
) -> dict[str, object]:
    temp_dir = tempfile.TemporaryDirectory()
    agent_root = Path(temp_dir.name) / "home" / ".agents"
    skills_root = agent_root / "skills"
    write_local_skill(
        skills_root,
        "scientific-writing",
        "Write IMRAD scientific manuscript prose, research paper正文, introduction, methods, results, discussion, and journal article drafts.",
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


def route_with_local_plotting_skills(
    prompt: str,
    task_type: str = "coding",
    grade: str = "L",
) -> dict[str, object]:
    temp_dir = tempfile.TemporaryDirectory()
    agent_root = Path(temp_dir.name) / "home" / ".agents"
    skills_root = agent_root / "skills"
    write_local_skill(skills_root, "matplotlib", "Create matplotlib publication-ready result figures and 600dpi plots.")
    write_local_skill(skills_root, "seaborn", "Create seaborn model evaluation figures and colorblind-friendly charts.")
    write_local_skill(skills_root, "plotly", "Create interactive plotly result figures and export HTML reports.")
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


def route_with_local_reporting_skills(
    prompt: str,
    task_type: str = "research",
    grade: str = "L",
) -> dict[str, object]:
    temp_dir = tempfile.TemporaryDirectory()
    agent_root = Path(temp_dir.name) / "home" / ".agents"
    skills_root = agent_root / "skills"
    write_local_skill(
        skills_root,
        "scientific-reporting",
        "Create 科研技术报告, research reports, methods, results, discussion, HTML, PDF, appendices, Quarto exports, and reproducibility steps.",
    )
    write_local_skill(
        skills_root,
        "scientific-writing",
        "Write scientific prose, manuscript sections, research discussion, and journal-ready methods text.",
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


class FiguresReportingStageAssistantRemovalTests(unittest.TestCase):
    def assert_selected(
        self,
        prompt: str,
        expected_pack: str,
        expected_skill: str,
        *,
        task_type: str = "research",
        grade: str = "L",
    ) -> None:
        result = route(prompt, task_type=task_type, grade=grade)
        self.assertEqual((expected_pack, expected_skill), selected(result), ranked_summary(result))

    def test_figures_pack_has_only_direct_problem_owners(self) -> None:
        pack = load_pack("science-figures-visualization")
        expected = ["scientific-visualization", "scientific-schematics"]
        self.assertEqual(expected, pack["skill_candidates"])
        self.assertNotIn("route_authority_candidates", pack)
        self.assertNotIn("stage_assistant_candidates", pack)

    def test_reporting_pack_has_only_direct_problem_owners(self) -> None:
        pack = load_pack("science-reporting")
        expected = ["scientific-reporting", "scientific-writing"]
        self.assertEqual(expected, pack["skill_candidates"])
        self.assertNotIn("route_authority_candidates", pack)
        self.assertNotIn("stage_assistant_candidates", pack)

    def test_plotting_library_words_route_to_matching_installed_plotting_skill(self) -> None:
        prompts = [
            ("用 matplotlib 绘制 publication-ready result figure，600dpi TIFF，带误差棒和显著性标注", "matplotlib"),
            ("用 seaborn 画模型评估结果图和投稿图，要求色盲友好配色", "seaborn"),
            ("用 plotly 做 interactive result figure，并导出 HTML figure 给科研报告使用", "plotly"),
        ]
        for prompt, expected_skill in prompts:
            with self.subTest(prompt=prompt):
                result = route_with_local_plotting_skills(prompt, task_type="coding")
                self.assertEqual(("local-skill-index", expected_skill), selected(result), ranked_summary(result))

    def test_figures_candidate_metadata_has_no_plotting_stage_assistants(self) -> None:
        result = route_with_local_science_figure_skills(
            "帮我做科研绘图，产出期刊级 figure，多面板、颜色无障碍、矢量导出",
            task_type="research",
            grade="L",
        )
        ranked = result.get("ranked")
        assert isinstance(ranked, list), result
        rows = [row for row in ranked if isinstance(row, dict)]
        ranking_skills = {str(row.get("skill") or "") for row in rows}
        self.assertEqual({"scientific-visualization", "scientific-schematics"}, ranking_skills)
        for row in rows:
            self.assertEqual("local-skill-index", row.get("pack_id"))
            self.assertNotIn("stage_assistant_candidates", row)
            self.assertNotIn("route_authority_eligible", row)

    def test_schematics_route_to_scientific_schematics(self) -> None:
        result = route_with_local_science_figure_skills(
            "用 Mermaid 写一个实验流程图 flowchart，并给出可复制 markdown",
            task_type="coding",
            grade="M",
        )
        self.assertEqual(("local-skill-index", "scientific-schematics"), selected(result), ranked_summary(result))

    def test_reporting_routes_remain_stable(self) -> None:
        result = route_with_local_reporting_skills(
            "科研技术报告：包含方法结果讨论，输出 HTML 和 PDF，附录写清复现步骤",
            task_type="planning",
            grade="L",
        )
        self.assertEqual(("local-skill-index", "scientific-reporting"), selected(result), ranked_summary(result))

    def test_reporting_candidate_metadata_has_no_figure_or_mermaid_stage_assistants(self) -> None:
        result = route_with_local_reporting_skills(
            "请把我们现有实验结果整理成 research report，带 executive summary、appendix、Quarto/PDF 导出",
            task_type="research",
            grade="L",
        )
        ranked = result.get("ranked")
        assert isinstance(ranked, list), result
        rows = [row for row in ranked if isinstance(row, dict)]
        ranking_skills = {str(row.get("skill") or "") for row in rows}
        self.assertEqual({"scientific-reporting", "scientific-writing"}, ranking_skills)
        for row in rows:
            self.assertEqual("local-skill-index", row.get("pack_id"))
            self.assertNotIn("stage_assistant_candidates", row)
            self.assertNotIn("route_authority_eligible", row)

    def test_manuscript_prose_still_selects_scientific_writing(self) -> None:
        result = route_with_local_scientific_writing_skill("请按 IMRAD 结构写科研论文正文", task_type="research", grade="L")
        self.assertEqual(("local-skill-index", "scientific-writing"), selected(result), ranked_summary(result))


if __name__ == "__main__":
    unittest.main()
