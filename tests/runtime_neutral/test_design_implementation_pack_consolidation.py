from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "packages" / "runtime-core" / "src"))

from vgo_runtime.router_contract_runtime import route_prompt  # noqa: E402


DESIGN_IMPLEMENTATION_SKILLS = ["figma-implement-design"]


def load_json(relative_path: str) -> dict[str, object]:
    return json.loads((REPO_ROOT / relative_path).read_text(encoding="utf-8-sig"))


def pack_by_id(pack_id: str) -> dict[str, object]:
    manifest = load_json("config/pack-manifest.json")
    packs = manifest.get("packs")
    assert isinstance(packs, list), manifest
    for pack in packs:
        assert isinstance(pack, dict), pack
        if pack.get("id") == pack_id:
            return pack
    raise AssertionError(f"pack missing: {pack_id}")


def route(prompt: str, task_type: str = "planning", grade: str = "L", installed_skill: str | None = None) -> dict[str, object]:
    with tempfile.TemporaryDirectory() as temp_dir:
        agent_root = Path(temp_dir) / "home" / ".agents"
        if installed_skill is not None:
            skill_dir = agent_root / "skills" / installed_skill
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: {prompt}\ndescription: {installed_skill} handles this local workflow.\n---\n# {installed_skill}\n",
                encoding="utf-8",
                newline="\n",
            )
        return route_prompt(
            prompt=prompt,
            grade=grade,
            task_type=task_type,
            target_root=str(agent_root),
            host_id="codex",
            repo_root=REPO_ROOT,
        )


def selected(result: dict[str, object]) -> tuple[str, str]:
    selected_row = result.get("selected")
    if not isinstance(selected_row, dict):
        return "", ""
    return str(selected_row.get("pack_id") or ""), str(selected_row.get("skill") or "")


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


class DesignImplementationPackConsolidationTests(unittest.TestCase):
    def assert_selected(
        self,
        prompt: str,
        expected_pack: str,
        expected_skill: str,
        *,
        task_type: str = "planning",
        grade: str = "L",
    ) -> None:
        result = route(prompt, task_type=task_type, grade=grade, installed_skill=expected_skill)
        self.assertEqual(("local-skill-index", expected_skill), selected(result), (expected_pack, ranked_summary(result)))

    def test_design_implementation_manifest_has_single_owner(self) -> None:
        pack = pack_by_id("design-implementation")

        self.assertEqual(DESIGN_IMPLEMENTATION_SKILLS, pack.get("skill_candidates"))
        self.assertNotIn("route_authority_candidates", pack)
        self.assertNotIn("figma", pack.get("skill_candidates") or [])
        self.assertNotIn("stage_assistant_candidates", pack)
        self.assertEqual("figma-implement-design", (pack.get("defaults_by_task") or {}).get("planning"))
        self.assertEqual("figma-implement-design", (pack.get("defaults_by_task") or {}).get("coding"))

    def test_figma_tool_skill_is_not_exposed_as_separate_live_skill(self) -> None:
        self.assertFalse((REPO_ROOT / "config" / "skill-keyword-index.json").exists())
        self.assertFalse((REPO_ROOT / "config" / "skill-routing-rules.json").exists())
        self.assertFalse((REPO_ROOT / "config" / "skills-lock.json").exists())
        self.assertFalse((REPO_ROOT / "bundled" / "skills" / "figma").exists())

    def test_figma_implementation_still_routes_to_design_owner(self) -> None:
        self.assert_selected(
            "把这个 Figma 设计稿还原为可运行代码",
            "design-implementation",
            "figma-implement-design",
            task_type="coding",
        )

    def test_figma_mcp_setup_with_implementation_context_routes_to_design_owner(self) -> None:
        self.assert_selected(
            "配置 Figma MCP 后把当前 node id 的设计稿实现成前端组件",
            "design-implementation",
            "figma-implement-design",
            task_type="planning",
        )


if __name__ == "__main__":
    unittest.main()
