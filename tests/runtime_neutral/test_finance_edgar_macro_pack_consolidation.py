from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "packages" / "runtime-core" / "src"))

from vgo_runtime.router_contract_runtime import route_prompt  # noqa: E402


FINANCE_SKILLS = [
    "edgartools",
    "alpha-vantage",
    "fred-economic-data",
    "usfiscaldata",
    "hedgefundmonitor",
    "market-research-reports",
    "datacommons-client",
]


def route(prompt: str, task_type: str = "research", grade: str = "M") -> dict[str, object]:
    return route_prompt(prompt=prompt, grade=grade, task_type=task_type, repo_root=REPO_ROOT)


def write_local_skill(skills_root: Path, skill_id: str, description: str, name: str | None = None) -> None:
    skill_file = skills_root / skill_id / "SKILL.md"
    skill_file.parent.mkdir(parents=True, exist_ok=True)
    skill_file.write_text(
        f"---\nname: {name or skill_id}\ndescription: {description}\n---\n# {skill_id}\n",
        encoding="utf-8",
    )


def route_with_local_finance_skills(
    prompt: str,
    task_type: str = "research",
    grade: str = "M",
) -> dict[str, object]:
    temp_dir = tempfile.TemporaryDirectory()
    agent_root = Path(temp_dir.name) / "home" / ".agents"
    skills_root = agent_root / "skills"
    write_local_skill(skills_root, "edgartools", "Use EDGAR for SEC filings, AAPL 10-K, revenue, gross margin, segment tables, 13F holdings, and institutional holdings.", name="EDGAR")
    write_local_skill(skills_root, "alpha-vantage", "Use Alpha Vantage for AAPL OHLCV daily prices and technical indicators.", name="Alpha Vantage")
    write_local_skill(skills_root, "fred-economic-data", "Use FRED for CPI, PCE, GDP, unemployment, fed funds rate, and Federal Reserve Economic Data.", name="FRED")
    write_local_skill(skills_root, "usfiscaldata", "Use U.S. Treasury Fiscal Data for national debt, federal spending, deficit, and Treasury datasets.", name="U.S. Treasury Fiscal Data")
    write_local_skill(skills_root, "hedgefundmonitor", "Use OFR Hedge Fund Monitor and Form PF aggregate statistics.", name="Hedge Fund Monitor")
    write_local_skill(skills_root, "market-research-reports", "Create consulting-style market research reports, industry reports, and competitive analysis.", name="market research report")
    write_local_skill(skills_root, "datacommons-client", "Use Data Commons for public statistical data, statistical variables, population indicators, and 人口经济指标.", name="Data Commons")
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


def pack_by_id(pack_id: str) -> dict[str, object]:
    manifest_path = REPO_ROOT / "config" / "pack-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    packs = manifest.get("packs")
    assert isinstance(packs, list), manifest
    for pack in packs:
        assert isinstance(pack, dict), pack
        if pack.get("id") == pack_id:
            return pack
    raise AssertionError(f"pack missing: {pack_id}")


def skill_keywords(skill_id: str) -> list[str]:
    path = REPO_ROOT / "config" / "skill-keyword-index.json"
    index = json.loads(path.read_text(encoding="utf-8-sig"))
    skill = index.get("skills", {}).get(skill_id)
    assert isinstance(skill, dict), skill_id
    keywords = skill.get("keywords")
    assert isinstance(keywords, list), skill
    return [str(keyword).lower() for keyword in keywords]


def routing_rule(skill_id: str) -> dict[str, object]:
    path = REPO_ROOT / "config" / "skill-routing-rules.json"
    rules = json.loads(path.read_text(encoding="utf-8-sig"))
    skill = rules.get("skills", {}).get(skill_id)
    assert isinstance(skill, dict), skill_id
    return skill


def negative_keywords(skill_id: str) -> list[str]:
    keywords = routing_rule(skill_id).get("negative_keywords")
    assert isinstance(keywords, list), skill_id
    return [str(keyword).lower() for keyword in keywords]


def skill_body(skill_id: str) -> str:
    path = REPO_ROOT / "bundled" / "skills" / skill_id / "SKILL.md"
    text = path.read_text(encoding="utf-8-sig")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2].lower()
    return text.lower()


class FinanceEdgarMacroPackConsolidationTests(unittest.TestCase):
    def assert_selected(
        self,
        prompt: str,
        expected_pack: str,
        expected_skill: str,
        *,
        task_type: str = "research",
        grade: str = "M",
    ) -> None:
        result = route(prompt, task_type=task_type, grade=grade)
        self.assertEqual((expected_pack, expected_skill), selected(result), ranked_summary(result))

    def assert_not_selected(
        self,
        prompt: str,
        blocked_pack: str | None = None,
        blocked_skill: str | None = None,
        *,
        task_type: str = "research",
        grade: str = "M",
    ) -> None:
        result = route(prompt, task_type=task_type, grade=grade)
        chosen_pack, chosen_skill = selected(result)
        if blocked_pack is not None:
            self.assertNotEqual(blocked_pack, chosen_pack, ranked_summary(result))
        if blocked_skill is not None:
            self.assertNotEqual(blocked_skill, chosen_skill, ranked_summary(result))

    def test_manifest_keeps_seven_direct_owners_and_no_stage_assistants(self) -> None:
        pack = pack_by_id("finance-edgar-macro")
        self.assertEqual(FINANCE_SKILLS, pack.get("skill_candidates"))
        self.assertNotIn("route_authority_candidates", pack)
        self.assertNotIn("stage_assistant_candidates", pack)
        defaults = pack.get("defaults_by_task")
        self.assertIsInstance(defaults, dict)
        for task_name in ["planning", "coding", "research"]:
            self.assertIn(defaults.get(task_name), FINANCE_SKILLS, defaults)

    def test_finance_positive_routes_hit_direct_owners(self) -> None:
        cases = [
            ("用 EDGAR 拉取 AAPL 10-K，提取收入/毛利率/分部信息并输出表格", "edgartools", "research"),
            ("用 Alpha Vantage 获取 AAPL 日线 OHLCV 行情和 technical indicators 并输出 CSV", "alpha-vantage", "coding"),
            ("用 FRED 获取 CPI、PCE、GDP、unemployment 和 fed funds rate 时间序列", "fred-economic-data", "research"),
            ("用 U.S. Treasury Fiscal Data 查询 national debt、federal spending 和 deficit", "usfiscaldata", "research"),
            ("查询 OFR Hedge Fund Monitor 和 Form PF aggregate statistics", "hedgefundmonitor", "research"),
            ("生成 consulting-style market research report、industry report 和 competitive analysis", "market-research-reports", "planning"),
            ("用 Data Commons 查询 public statistical data、statistical variables 和人口经济指标", "datacommons-client", "research"),
        ]
        for prompt, expected_skill, task_type in cases:
            with self.subTest(expected_skill=expected_skill):
                result = route_with_local_finance_skills(prompt, task_type=task_type)
                self.assertEqual(("local-skill-index", expected_skill), selected(result), ranked_summary(result))

    def test_generic_public_data_does_not_select_datacommons_client(self) -> None:
        self.assert_not_selected(
            "搜索公共数据集和 open dataset 下载链接，不限定 Data Commons 或人口经济指标",
            blocked_pack="finance-edgar-macro",
            blocked_skill="datacommons-client",
        )

    def test_scientific_and_publishing_reports_do_not_select_market_research(self) -> None:
        self.assert_not_selected(
            "写一篇科研报告，包含 methods results discussion 并导出 PDF",
            blocked_pack="finance-edgar-macro",
            blocked_skill="market-research-reports",
            task_type="planning",
            grade="L",
        )
        self.assert_not_selected(
            "写 LaTeX 论文并用 latexmk 构建 submission PDF",
            blocked_skill="market-research-reports",
            task_type="coding",
            grade="XL",
        )

    def test_biomedical_literature_and_clinical_prompts_do_not_select_finance(self) -> None:
        self.assert_not_selected(
            "查询 PubMed 文献并整理 evidence table 和 PMID citations",
            blocked_pack="finance-edgar-macro",
        )
        self.assert_not_selected(
            "从 ClinicalTrials.gov 查询 NCT01234567 试验终点和入排标准",
            blocked_pack="finance-edgar-macro",
        )

    def test_fred_and_treasury_do_not_cross_select_each_other(self) -> None:
        self.assert_not_selected(
            "用 FRED 获取 CPI from FRED 和 Federal Reserve Economic Data 时间序列",
            blocked_skill="usfiscaldata",
        )
        self.assert_not_selected(
            "用 U.S. Treasury Fiscal Data 查 national debt 和 federal spending",
            blocked_skill="fred-economic-data",
        )

    def test_sec_13f_does_not_select_hedgefundmonitor(self) -> None:
        result = route_with_local_finance_skills(
            "查询 SEC 13F holdings 和 institutional holdings",
        )
        self.assertEqual(("local-skill-index", "edgartools"), selected(result), ranked_summary(result))
        self.assertNotEqual("hedgefundmonitor", selected(result)[1])

    def test_static_keyword_index_is_not_an_active_finance_route_source(self) -> None:
        self.assertFalse((REPO_ROOT / "config" / "skill-keyword-index.json").exists())

    def test_static_routing_rules_are_not_an_active_finance_route_source(self) -> None:
        self.assertFalse((REPO_ROOT / "config" / "skill-routing-rules.json").exists())

    def test_kept_skill_docs_do_not_inline_cross_call_other_skills(self) -> None:
        market_body = skill_body("market-research-reports")
        forbidden_market_phrases = [
            "deep integration with research-lookup",
            "use `research-lookup`",
            "use research-lookup",
            "use `scientific-schematics`",
            "use scientific-schematics",
            "use `generate-image`",
            "use generate-image",
            "use the peer-review skill",
            "works synergistically with",
            "integration with other skills",
        ]
        for phrase in forbidden_market_phrases:
            self.assertNotIn(phrase, market_body)

        datacommons_body = skill_body("datacommons-client")
        self.assertIn("generic public data", datacommons_body)
        self.assertIn("not enough", datacommons_body)


if __name__ == "__main__":
    unittest.main()
