from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _public_entry_ids() -> set[str]:
    payload = json.loads(_read("config/vibe-entry-surfaces.json"))
    return {
        entry["id"]
        for entry in payload["entries"]
        if entry.get("publicly_exposed") is True
    }


def test_readmes_describe_only_public_vibe_entry_surface() -> None:
    assert _public_entry_ids() == {"vibe"}

    for path in ("README.md", "README.zh.md", "docs/quick-start.en.md", "docs/quick-start.md"):
        content = _read(path)
        assert "vibe-upgrade" not in content
        assert "vibe-what-do-i-want" not in content
        assert "vibe-how-do-we-do" not in content
        assert "vibe-do-it" not in content
        assert "host-rendered" not in content
        assert "宿主渲染标签" not in content
        for legacy_alias in ("vibe-want", "vibe-how", "vibe-do"):
            assert re.search(rf"(?<![\w-]){re.escape(legacy_alias)}(?![\w-])", content) is None


def test_readme_heroes_keep_one_release_badge_and_consistent_install_buttons() -> None:
    for path in ("README.md", "README.zh.md"):
        content = _read(path)
        hero = content[content.index('<div align="center">') : content.index("</div>", content.index('<div align="center">'))]
        assert content.count("img.shields.io") == 1
        assert "<kbd>" not in content
        assert "<br><br>" not in hero
        assert "One_Entry" not in content
        assert "Skill_Model" not in content
        assert "Host_Neutral" not in content
        assert "Evidence_Checked" not in content

    for path in (
        "docs/assets/install-cta-en.svg",
        "docs/assets/install-cta-cn.svg",
    ):
        svg_path = REPO_ROOT / path
        root = ET.parse(svg_path).getroot()
        content = svg_path.read_text(encoding="utf-8")

        assert root.attrib["width"] == "327"
        assert root.attrib["height"] == "56"
        assert root.attrib["viewBox"] == "0 0 327 56"
        assert "#0F4C4E" in content
        assert "linearGradient" not in content
        assert "<filter" not in content


def test_root_skill_keeps_update_on_the_command_path_not_a_public_skill() -> None:
    content = _read("SKILL.md")

    assert "vibe-upgrade" not in content
    assert "update" in content
    assert "--skills-dir" in content


def test_governance_navigation_separates_current_contracts_from_archived_history() -> None:
    governance_readme = _read("docs/governance/README.md")
    archive_readme = _read("docs/archive/governance-history/README.md")

    for current_doc in (
        "current-runtime-field-contract.md",
        "current-routing-contract.md",
        "skill-admission-hardening.md",
        "bundled-skill-retention-matrix.md",
        "kernel-first-remediation-baseline.md",
    ):
        assert current_doc in governance_readme

    for archived_doc in (
        "zero-route-authority-pack-consolidation-2026-04-29.md",
        "zero-route-authority-second-pass-2026-04-29.md",
        "zero-route-authority-third-pass-2026-04-30.md",
    ):
        assert archived_doc not in governance_readme
        assert archived_doc in archive_readme
        assert not (REPO_ROOT / "docs" / "governance" / archived_doc).exists()
        assert (REPO_ROOT / "docs" / "archive" / "governance-history" / archived_doc).exists()


def test_status_navigation_keeps_historical_dry_run_out_of_start_here() -> None:
    status_readme = _read("docs/status/README.md")

    start_here = status_readme[status_readme.index("## Start Here"):].split("## Cross-Layer Handoff", 1)[0]
    reading_boundary = status_readme[status_readme.index("## Reading Boundary"):].split("## Rules", 1)[0]
    historical_dry_run = "[`operator-dry-run.md`](operator-dry-run.md)"

    assert historical_dry_run not in start_here
    assert historical_dry_run in reading_boundary


def test_status_navigation_keeps_history_index_out_of_start_here() -> None:
    status_readme = _read("docs/status/README.md")

    start_here = status_readme[status_readme.index("## Start Here"):].split("## Cross-Layer Handoff", 1)[0]
    reading_boundary = status_readme[status_readme.index("## Reading Boundary"):].split("## Rules", 1)[0]
    history_index = "[`history-index.md`](./history-index.md)"

    assert history_index not in start_here
    assert history_index in reading_boundary


def test_status_navigation_keeps_operator_script_index_out_of_cross_layer_handoff() -> None:
    status_readme = _read("docs/status/README.md")

    cross_layer = status_readme[status_readme.index("## Cross-Layer Handoff"):].split("## Reading Boundary", 1)[0]
    rules_section = status_readme[status_readme.index("## Rules"):].splitlines()
    operator_scripts = "[`../../scripts/README.md`](../../scripts/README.md)"

    assert operator_scripts not in cross_layer
    assert any(operator_scripts in line for line in rules_section)


def test_status_navigation_keeps_verify_run_order_index_out_of_cross_layer_handoff() -> None:
    status_readme = _read("docs/status/README.md")

    cross_layer = status_readme[status_readme.index("## Cross-Layer Handoff"):].split("## Reading Boundary", 1)[0]
    rules_section = status_readme[status_readme.index("## Rules"):].splitlines()
    verify_run_order = "[`../../scripts/verify/gate-family-index.md`](../../scripts/verify/gate-family-index.md)"

    assert verify_run_order not in cross_layer
    assert any(verify_run_order in line for line in rules_section)


def test_docs_root_keeps_plans_index_out_of_start_here() -> None:
    docs_readme = _read("docs/README.md")

    start_here = docs_readme[docs_readme.index("## Start Here"):].split("## 按需再看", 1)[0]
    cross_layer = docs_readme[docs_readme.index("## Cross-Layer Handoff"):].split("## Rules", 1)[0]
    plans_link = "[`plans/README.md`](./plans/README.md)"

    assert plans_link not in start_here
    assert plans_link in cross_layer


def test_docs_root_keeps_scripts_index_out_of_cross_layer_handoff() -> None:
    docs_readme = _read("docs/README.md")

    cross_layer = docs_readme[docs_readme.index("## Cross-Layer Handoff"):].split("## Rules", 1)[0]
    rules_section = docs_readme[docs_readme.index("## Rules"):].splitlines()
    scripts_link = "[`../scripts/README.md`](../scripts/README.md)"

    assert scripts_link not in cross_layer
    assert any(scripts_link in line for line in rules_section)


def test_design_readme_keeps_verify_entry_index_out_of_cross_layer_handoff() -> None:
    design_readme = _read("docs/design/README.md")

    cross_layer = design_readme[design_readme.index("## Cross-Layer Handoff"):].split("## Rules", 1)[0]
    rules_section = design_readme[design_readme.index("## Rules"):].splitlines()
    verify_link = "[`../../scripts/verify/README.md`](../../scripts/verify/README.md)"

    assert verify_link not in cross_layer
    assert any(verify_link in line for line in rules_section)


def test_external_tooling_readme_keeps_operator_script_index_out_of_cross_layer_handoff() -> None:
    tooling_readme = _read("docs/external-tooling/README.md")

    cross_layer = tooling_readme[tooling_readme.index("### Cross-Layer Handoff"):].split("## Rules", 1)[0]
    rules_section = tooling_readme[tooling_readme.index("## Rules"):].splitlines()
    scripts_link = "[`../../scripts/README.md`](../../scripts/README.md)"

    assert scripts_link not in cross_layer
    assert any(scripts_link in line for line in rules_section)


def test_public_readmes_do_not_link_directly_to_test_files() -> None:
    english = _read("README.md")
    chinese = _read("README.zh.md")

    assert "./tests/" not in english
    assert "./tests/" not in chinese
    assert "test_codex_memory_user_simulation.py" not in english
    assert "test_codex_memory_user_simulation.py" not in chinese
    assert "docs/status/non-regression-proof-bundle.md" in english
    assert "docs/status/non-regression-proof-bundle.md" in chinese


def test_release_navigation_keeps_archive_links_out_of_runtime_proof_handoff() -> None:
    release_readme = _read("docs/releases/README.md")

    proof_handoff = release_readme[release_readme.index("### Release Runtime / Proof Handoff"):].split(
        "## Recent Governed Releases",
        1,
    )[0]
    historical_archive = release_readme[release_readme.index("## Historical Release Archive"):].split(
        "## Historical Packetization",
        1,
    )[0]
    historical_packetization = release_readme[release_readme.index("## Historical Packetization"):].split(
        "## Release Operator Entry",
        1,
    )[0]

    archive_link = "[`../archive/releases/README.md`](../archive/releases/README.md)"
    packet_link = "[`../archive/releases/wave15-18-release-packet.md`](../archive/releases/wave15-18-release-packet.md)"

    assert archive_link not in proof_handoff
    assert archive_link in historical_archive
    assert packet_link not in proof_handoff
    assert packet_link in historical_packetization


def test_release_navigation_keeps_exact_gate_script_names_out_of_runtime_proof_handoff() -> None:
    release_readme = _read("docs/releases/README.md")

    proof_handoff = release_readme[release_readme.index("### Release Runtime / Proof Handoff"):].split(
        "## Recent Governed Releases",
        1,
    )[0]

    assert "vibe-skill-promotion-execution-gate.ps1" not in proof_handoff
    assert "vibe-release-truth-consistency-gate.ps1" not in proof_handoff
    assert "[`../../scripts/verify/README.md`](../../scripts/verify/README.md)" in proof_handoff
    assert "[`../status/non-regression-proof-bundle.md`](../status/non-regression-proof-bundle.md)" in proof_handoff


def test_release_navigation_keeps_gate_family_index_out_of_runtime_proof_handoff() -> None:
    release_readme = _read("docs/releases/README.md")

    proof_handoff = release_readme[release_readme.index("### Release Runtime / Proof Handoff"):].split(
        "## Recent Governed Releases",
        1,
    )[0]
    rules_section = release_readme[release_readme.index("## Rules"):].splitlines()

    gate_index_link = "[`../../scripts/verify/gate-family-index.md`](../../scripts/verify/gate-family-index.md)"

    assert gate_index_link not in proof_handoff
    assert any(gate_index_link in line for line in rules_section)
    assert "[`../../scripts/verify/README.md`](../../scripts/verify/README.md)" in proof_handoff


def test_readmes_describe_local_installed_skill_story_without_repromoting_a_central_catalog() -> None:
    english = _read("README.md")
    chinese = _read("README.zh.md")
    english_lower = english.lower()
    english_compact = " ".join(english_lower.split())
    chinese_lower = chinese.lower()

    assert "local skill folders you configure" in english_lower
    assert "readable `skill.md`" in english_lower
    assert "agent_skill_organization" in english
    assert "module_assignments" in english
    assert "stores the actual assignment" in english_compact
    assert "without waiting for the vibeskills repository" in english_compact
    assert "does not call every installed skill automatically" in english_lower
    assert "external-first extension" not in english_lower
    assert "starter set" not in english_lower
    assert "local_first_skills" not in english_lower
    assert "Local + starter Skills stay the product surface." not in english

    assert "配置的本地 Skill 目录" in chinese
    assert "SKILL.md" in chinese
    assert "agent_skill_organization" in chinese
    assert "module_assignments" in chinese
    assert "保存实际分配" in chinese
    assert "不需要等待 VibeSkills 项目收录" in chinese
    assert "不会自动调用你安装的所有 Skills" in chinese
    assert "外部优先扩展" not in chinese
    assert "starter" not in chinese_lower
    assert "本地 + starter Skills 仍然是默认产品面。" not in chinese


def test_root_readmes_route_tool_support_details_to_the_support_status_doc() -> None:
    english = _read("README.md")
    chinese = _read("README.zh.md")

    assert "Use it with different AI tools" not in english
    assert "可以配合不同的 AI 工具使用" not in chinese
    assert "| Current support |" not in english
    assert "| 实际支持情况 |" not in chinese
    assert "[Support status](./docs/universalization/host-capability-matrix.md)" in english
    assert "[支持情况说明](./docs/universalization/host-capability-matrix.md)" in chinese


def test_public_readmes_describe_the_supporting_task_features() -> None:
    english = _read("README.md")
    chinese = _read("README.zh.md")

    for phrase in (
        "Confirms the requirement",
        "Recommends a level",
        "Organizes Skills",
        "Executes and records",
        "Checks the result",
        "up to two non-conflicting parts at the same time",
        "test-driven development",
    ):
        assert phrase in english

    for phrase in (
        "确认需求",
        "推荐级别",
        "组织 Skills",
        "执行并记录",
        "检查结果",
        "最多同时推进两项工作",
        "测试驱动开发",
    ):
        assert phrase in chinese

    assert "需求没有确认时" in chinese
    assert "流程会停在这里" in chinese
    assert "中断后也可以从已有进度继续" in chinese
    assert "任务不会通过最终检查" in chinese


def test_public_readmes_explain_passive_triggering_and_bounded_skill_context_cost() -> None:
    english = _read("README.md")
    chinese = _read("README.zh.md")

    for phrase in (
        "Passive Skill triggering",
        "With VibeSkills",
        "The AI reacts to a few obvious words",
        "All results are brought together and checked at the end",
        "Will a large Skill library use a lot of tokens?",
        "Discovery and index generation happen locally",
        "Only retained candidates are then read as complete `SKILL.md` files",
        "This overhead is not zero",
    ):
        assert phrase in english

    for phrase in (
        "只靠被动触发",
        "使用 VibeSkills",
        "AI 临时根据几个关键词决定用什么",
        "最后把所有结果汇总起来一起检查",
        "Skill 很多时，会不会消耗很多 token？",
        "目录发现和索引生成在本机完成",
        "只有保留下来的候选才会由 Agent 继续阅读完整的 `SKILL.md`",
        "这部分开销仍然存在",
    ):
        assert phrase in chinese

    assert "Skill 再多也不增加 token" not in chinese
    assert "zero token overhead" not in english.casefold()


def test_quick_start_does_not_advertise_disabled_stage_labels() -> None:
    disabled_stage_labels = (
        "Vibe: What Do I Want?",
        "Vibe: How Do We Do It?",
        "Vibe: Do It",
    )
    for path in ("docs/quick-start.en.md", "docs/quick-start.md"):
        content = _read(path)
        for label in disabled_stage_labels:
            assert label not in content


def test_quick_start_points_normal_skill_extension_to_the_simple_install_docs() -> None:
    english = _read("docs/quick-start.en.md")
    chinese = _read("docs/quick-start.md")

    assert "local-first" not in english
    assert "configured local folders" in english
    assert "Custom Skills onboarding" not in english
    assert "custom-workflow-onboarding" not in english
    assert "install/README.en.md" in english

    assert "本地优先" not in chinese
    assert "把 Skill 放进指定的本地文件夹" in chinese
    assert "想接入自定义 Skills" not in chinese
    assert "custom-workflow-onboarding" not in chinese
    assert "install/README.md" in chinese


def test_simple_install_readmes_treat_pwsh_as_default_power_shell_surface() -> None:
    forbidden_phrases = (
        "must not be treated as the default prerequisite",
        "不要把 `pwsh` 当作默认前提",
    )
    for path in ("docs/install/README.en.md", "docs/install/README.md"):
        content = _read(path)
        assert "pwsh" in content
        assert "docs/install/prompts" not in content
        for phrase in forbidden_phrases:
            assert phrase not in content


def test_runtime_core_packaging_projections_do_not_track_local_repo_root() -> None:
    for path in (
        "config/runtime-core-packaging.full.json",
        "config/runtime-core-packaging.minimal.json",
    ):
        payload = json.loads(_read(path))
        assert "_repo_root" not in payload


def test_public_install_surfaces_point_to_skills_dir_installation() -> None:
    public_paths = (
        "README.md",
        "README.zh.md",
        "docs/install/README.en.md",
        "docs/install/README.md",
    )

    for path in public_paths:
        content = _read(path)
        assert "SkillsDir" in content or "--skills-dir" in content
        assert "skills/local" not in content
        assert "skills/custom/" not in content
        assert "custom-workflows.json" not in content


def test_install_readme_keeps_legacy_custom_workflow_onboarding_out_of_active_install_path() -> None:
    english = _read("docs/install/README.en.md")
    chinese = _read("docs/install/README.md")

    assert "Custom Skill onboarding" not in english
    assert "Advanced manifest-driven custom workflow onboarding" not in english
    assert "custom-workflow-onboarding.en.md" not in english
    assert "skill-roots.json" in english

    assert "自定义 Skill 接入" not in chinese
    assert "高级 manifest 驱动 custom workflow 接入" not in chinese
    assert "custom-workflow-onboarding.md" not in chinese
    assert "skill-roots.json" in chinese


def test_advanced_custom_workflow_doc_is_archived_not_active_install_guidance() -> None:
    for path in (
        "docs/install/custom-workflow-onboarding.en.md",
        "docs/install/custom-workflow-onboarding.md",
    ):
        assert not (REPO_ROOT / path).exists()
        assert (REPO_ROOT / "docs" / "archive" / "install-legacy" / "2026-07-02" / Path(path).name).exists()


def test_update_prompt_recipes_are_archived_not_active_install_guidance() -> None:
    for path in (
        "docs/install/prompts/framework-only-update.en.md",
        "docs/install/prompts/framework-only-update.md",
        "docs/install/prompts/full-version-update.en.md",
        "docs/install/prompts/full-version-update.md",
    ):
        active_path = REPO_ROOT / path
        archived_path = (
            REPO_ROOT
            / "docs"
            / "archive"
            / "install-legacy"
            / "2026-07-02"
            / "prompts"
            / Path(path).name
        )
        assert not active_path.exists()
        assert archived_path.exists()


def test_custom_governance_rules_are_archived_not_active_install_guidance() -> None:
    for path in (
        "docs/install/custom-skill-governance-rules.en.md",
        "docs/install/custom-skill-governance-rules.md",
    ):
        assert not (REPO_ROOT / path).exists()
        assert (REPO_ROOT / "docs" / "archive" / "install-legacy" / "2026-07-02" / Path(path).name).exists()


def test_kernel_architecture_docs_describe_agent_led_binding_truth() -> None:
    architecture = _read("docs/architecture/local-agent-kernel-v2.md")
    interfaces = _read("docs/architecture/local-agent-kernel-v2-interfaces.md")
    architecture_lower = architecture.lower()
    interfaces_lower = interfaces.lower()

    assert "declared local skill roots are the only specialist reference surface" in architecture_lower
    assert "host-declared local roots are the only specialist reference surface" in interfaces_lower
    assert "external-first" not in architecture_lower
    assert "external-first" not in interfaces_lower
    assert "skills/local" not in architecture_lower
    assert "skills/local" not in interfaces_lower
    assert "module_assignments" in architecture
    expected_flow = "candidate discovery -> agent reads `skill.md` -> `agent_skill_organization` -> `module_assignments` -> execution"
    assert expected_flow in architecture_lower
    assert expected_flow in interfaces_lower
    assert "validated execution projection" in architecture_lower
    assert "validated execution projection" in interfaces_lower
    assert "planner preference is candidate audit only" in architecture_lower
    assert "planner preference is candidate audit only" in interfaces_lower
    assert "repo-owned" in architecture_lower and ("not the main extension story" in architecture_lower or "no repo-owned bundled corpus as the main extension surface" in architecture_lower)
    assert "skills-catalog.json" in interfaces
    assert "skills-index.json" in interfaces
    assert "--host-id" in interfaces
    assert "--workspace-root" in interfaces
    assert "provenance" in interfaces_lower
    assert "selected source" in interfaces_lower and "details" in interfaces_lower


def test_kernel_docs_keep_external_first_story_narrow_and_do_not_overclaim() -> None:
    readme = _read("README.md").lower()
    readme_zh = _read("README.zh.md")
    interfaces = _read("docs/architecture/local-agent-kernel-v2-interfaces.md").lower()

    assert re.search(
        r"(should not be described as|is not)\s+automatic orchestration of all installed skills",
        interfaces,
    )
    assert "does not call every installed skill automatically" in readme
    assert "不会自动调用你安装的所有 Skills" in readme_zh


def test_default_closure_docs_keep_small_proof_set_story() -> None:
    gate_index = _read("scripts/verify/gate-family-index.md")
    verify_readme = _read("scripts/verify/README.md")
    proof_bundle = _read("docs/status/non-regression-proof-bundle.md")
    readme = _read("README.md").lower()
    architecture = _read("docs/architecture/local-agent-kernel-v2.md").lower()

    assert "1. `vibe-governed-runtime-contract-gate.ps1`" in gate_index
    assert "5. `vibe-repo-cleanliness-gate.ps1`" in gate_index
    assert "10. `vibe-repo-cleanliness-gate.ps1`" not in gate_index
    assert "default closure should stay small" in gate_index.lower()
    assert 'vibe-governed-runtime-contract-gate.ps1' in verify_readme
    assert 'vibe-runtime-execution-proof-gate.ps1' in verify_readme
    assert 'vibe-governed-runtime-contract-gate.ps1' in proof_bundle
    assert 'vibe-runtime-execution-proof-gate.ps1' in proof_bundle
    assert 'Add-on audit commands are opt-in' in proof_bundle
    assert 'small default closure set + routing smoke + router contract' in proof_bundle
    assert 'vibe-current-routing-debt-gate.ps1' in proof_bundle
    assert 'Additional final regression checks stay outside the default closure gate set' in proof_bundle
    assert "run wider audits only when there is a reason" in readme
    assert "default closure story should stay small" in architecture


def test_public_readmes_keep_install_run_and_delivery_records_separate() -> None:
    english = _read("README.md")
    chinese = _read("README.zh.md")
    english_compact = " ".join(english.split())

    for record in (
        "`install-receipt.json`",
        "`session_root`",
        "`module-work-plan.json`",
        "`module-execution.json`",
        "`delivery-acceptance-report.json`",
    ):
        assert record in english
        assert record in chinese
    assert "A successful installation does not mean the task ran" in english_compact
    assert "a task record does not mean the final result passed" in english_compact
    assert "安装成功，不代表任务已经跑完" in chinese
    assert "有运行记录，也不代表" in chinese
    assert "最终结果已经通过检查" in chinese

    assert "current verification surface" not in english.lower()
    assert "当前验证入口" not in chinese


def test_public_readmes_and_quick_starts_avoid_internal_runtime_language() -> None:
    public_docs = (
        _read("README.md"),
        _read("README.zh.md"),
        _read("docs/quick-start.en.md"),
        _read("docs/quick-start.md"),
    )
    internal_phrases = (
        "host-neutral",
        "adapter",
        "carrier",
        "canonical bridge",
        "public boundary",
        "runtime truth",
        "proof layer",
        "work-kernel",
        "governed runtime",
        "宿主中立",
        "载体",
        "适配器",
        "公开边界",
        "可以检查的证据",
        "运行时真相",
        "真相面",
        "工作内核",
    )

    for content in public_docs:
        for phrase in internal_phrases:
            assert phrase.casefold() not in content.casefold()


def test_runtime_protocol_maps_public_proof_layers_without_reintroducing_install_host_ready_states() -> None:
    protocol = _read("protocols/runtime.md")

    assert "`installed locally` belongs to install receipt / `check` and stays outside this protocol." in protocol
    assert "`runtime coherent` starts only after canonical entry returns a `session_root`" in protocol
    assert "`delivery accepted` is decided by the delivery-acceptance report" in protocol
    assert "vibe host-ready" not in protocol
    assert "online-ready" not in protocol


def test_active_runtime_docs_use_agent_skill_organization_as_skill_truth() -> None:
    english = _read("README.md")
    chinese = _read("README.zh.md")
    protocol = _read("protocols/runtime.md")
    team = _read("protocols/team.md")
    routing_contract = _read("docs/governance/current-routing-contract.md")
    field_contract = _read("docs/governance/current-runtime-field-contract.md")
    remediation = _read("docs/governance/built-in-skill-routing-remediation.md")

    for content in (english, chinese, protocol, team, routing_contract, field_contract):
        assert "agent_skill_organization" in content

    assert "route candidates are compatibility audit evidence only" in protocol
    assert "Agent-confirmed skill organization" in routing_contract
    assert "agent_skill_organization -> module-work-plan.json" in field_contract
    assert "module-work-plan.json -> agent-execution-handoff.json" in field_contract
    assert "agent-execution-handoff.json -> module-execution.json" in field_contract
    assert "Agent-led skill discovery cutover" in remediation
    assert "runtime 实际上已经由 router / canonical `vibe` 决定能力入口" not in remediation
    assert "eligible route candidates should auto-promote" not in protocol
    assert "route truth points at a selected skill" not in protocol
    assert "skill_candidates -> skill_routing.selected" not in routing_contract


def test_non_regression_proof_bundle_is_positioned_as_operator_closeout_contract() -> None:
    proof_bundle = _read("docs/status/non-regression-proof-bundle.md")

    assert "operator and contributor closeout contract" in proof_bundle
    assert "It is not the everyday public proof ladder" in proof_bundle
    assert "`installed locally` -> `check`" in proof_bundle
    assert "`runtime coherent` -> returned `session_root` truth artifacts" in proof_bundle
    assert "`delivery accepted` -> delivery-acceptance report" in proof_bundle


def test_manifest_driven_custom_governance_doc_is_legacy_archive_only() -> None:
    for path in (
        "docs/install/custom-skill-governance-rules.en.md",
        "docs/install/custom-skill-governance-rules.md",
    ):
        assert not (REPO_ROOT / path).exists()
        assert (REPO_ROOT / "docs" / "archive" / "install-legacy" / "2026-07-02" / Path(path).name).exists()


def test_framework_only_reference_pages_are_archived_not_active_install_guidance() -> None:
    for path in (
        "docs/install/framework-only-path.en.md",
        "docs/install/framework-only-path.md",
    ):
        assert not (REPO_ROOT / path).exists()
        assert (REPO_ROOT / "docs" / "archive" / "install-legacy" / "2026-07-02" / Path(path).name).exists()


def test_installation_rules_and_minimal_path_are_archived_not_active_install_guidance() -> None:
    for path in (
        "docs/install/installation-rules.en.md",
        "docs/install/installation-rules.md",
        "docs/install/minimal-path.en.md",
        "docs/install/minimal-path.md",
    ):
        assert not (REPO_ROOT / path).exists()
        assert (REPO_ROOT / "docs" / "archive" / "install-legacy" / "2026-07-02" / Path(path).name).exists()


def test_root_readmes_present_the_verified_ml_case_with_source_materials() -> None:
    english = _read("README.md")
    chinese = _read("README.zh.md")
    english_case = _read("docs/cases/ml-experiment/README.md")
    chinese_case = _read("docs/cases/ml-experiment/README.zh.md")

    english_blocks = re.findall(r"```mermaid\r?\n(.*?)\r?\n```", english, flags=re.DOTALL)
    chinese_blocks = re.findall(r"```mermaid\r?\n(.*?)\r?\n```", chinese, flags=re.DOTALL)
    assert len(english_blocks) == len(chinese_blocks) == 1
    english_diagram = english_blocks[0]
    chinese_diagram = chinese_blocks[0]

    for content in (english, chinese):
        assert "./docs/cases/ml-experiment/" in content
        assert ".gif" not in content.casefold()

    assert "Organize the right local Skills and carry complex tasks through to delivery." in english
    assert "组织合适的本地 Skills，把复杂任务做完整。" in chinese
    assert "You can start with the task without deciding which Skills to combine first." in english
    assert "先说清楚任务，不必先想好该用哪些 Skills。" in chinese
    assert "A real run: completing a machine-learning experiment" in english
    assert "一次真实运行：完成一项机器学习实验" in chinese
    assert "[View case execution](./docs/cases/ml-experiment/README.md#case-execution)" in english
    assert "[View final delivery](./docs/cases/ml-experiment/README.md#final-delivery)" in english
    assert "[查看案例执行过程](./docs/cases/ml-experiment/README.zh.md#案例执行过程)" in chinese
    assert "[查看最终交付结果](./docs/cases/ml-experiment/README.zh.md#最终交付结果)" in chinese
    assert "View the source materials" not in english
    assert "查看原始材料" not in chinese
    assert "View final acceptance" not in english
    assert "查看最终验收" not in chinese
    assert "## Case execution" in english_case
    assert "## Final delivery" in english_case
    assert "## Execution records and reproduction materials" in english_case
    assert "## 案例执行过程" in chinese_case
    assert "## 最终交付结果" in chinese_case
    assert "## 执行记录与复现材料" in chinese_case
    assert "./evidence/delivery-acceptance-report.md" in english_case
    assert "./evidence/delivery-acceptance-report.md" in chinese_case
    for diagram in (english_diagram, chinese_diagram):
        assert "flowchart LR" in diagram
        assert "flowchart TB" not in diagram
        for index in range(1, 11):
            assert len(re.findall(rf"\bU{index:02d}\b", diagram)) == 1
        for index in range(1, 18):
            assert len(re.findall(rf"\bT{index:02d}\b", diagram)) == 1

    assert "Run status<br/>10 / 10 completed<br/>0 failed · 0 blocked" in english_diagram
    assert "运行状态<br/>10 / 10 完成<br/>0 失败 · 0 阻塞" in chinese_diagram
    assert "Final acceptance<br/>17 / 17 checks passed<br/>PASS" in english_diagram
    assert "最终验收<br/>17 / 17 检查通过<br/>PASS" in chinese_diagram

    for group in (
        "G1 · 01 Environment and data",
        "G2 · 02 Modeling and reproduction",
        "G3 · 03 Statistics and scientific review",
        "G4 · 04 Figures and report",
        "G5 · 05 Slides and acceptance",
    ):
        assert group in english_diagram
    for group in (
        "G1 · 01 环境与数据",
        "G2 · 02 建模与复现",
        "G3 · 03 统计与科学复核",
        "G4 · 04 图表与报告",
        "G5 · 05 Slides 与验收",
    ):
        assert group in chinese_diagram

    for unit in (
        "environment setup",
        "data audit",
        "baseline experiment",
        "statistical analysis",
        "scientific review",
        "result figures",
        "report draft",
        "report review",
        "group-meeting slides",
        "case package and consistency",
    ):
        assert unit in english_diagram.casefold()

    english_checks = english_diagram.replace("<br/>", "")
    for check_id in (
        "required-files",
        "module-output-patterns",
        "runtime-plan-binding",
        "environment-contract",
        "dataset-contract",
        "split-and-model-contract",
        "baseline-results",
        "exact-reproduction",
        "uncertainty-consistency",
        "statistics-write-protection",
        "figure-traceability",
        "report-consistency",
        "slides-consistency",
        "bilingual-summary-consistency",
        "visual-material-guidance",
        "manifest-boundary",
        "artifact-path-boundary",
    ):
        assert check_id in english_checks

    for check_label in (
        "必需文件",
        "模块输出匹配",
        "运行与计划绑定",
        "环境合同",
        "数据集合同",
        "数据拆分与模型合同",
        "基线结果",
        "精确复现",
        "不确定性一致性",
        "统计文件写入保护",
        "图表可追溯性",
        "报告一致性",
        "Slides 一致性",
        "中英文摘要一致性",
        "可视材料指引",
        "Manifest 边界",
        "产物路径边界",
    ):
        assert check_label in chinese_diagram

    def mermaid_ids(diagram: str) -> set[str]:
        subgraph_ids = re.findall(
            r"^\s*subgraph\s+([A-Za-z][A-Za-z0-9_]*)",
            diagram,
            flags=re.MULTILINE,
        )
        node_ids = re.findall(
            r"^\s*([A-Za-z][A-Za-z0-9_]*)\s*(?:\[|\()",
            diagram,
            flags=re.MULTILINE,
        )
        return set(subgraph_ids) | set(node_ids)

    def mermaid_edges(diagram: str) -> set[tuple[str, str]]:
        return set(
            re.findall(
                r"^\s*([A-Za-z][A-Za-z0-9_]*)\s*-->\s*"
                r"([A-Za-z][A-Za-z0-9_]*)\s*$",
                diagram,
                flags=re.MULTILINE,
            )
        )

    english_ids = mermaid_ids(english_diagram)
    chinese_ids = mermaid_ids(chinese_diagram)
    english_edges = mermaid_edges(english_diagram)
    chinese_edges = mermaid_edges(chinese_diagram)
    assert english_ids == chinese_ids
    assert english_edges == chinese_edges
    assert {f"u{index:02d}" for index in range(1, 11)} <= english_ids
    assert {f"t{index:02d}" for index in range(1, 18)} <= english_ids
    assert {
        ("DISC", "EXEC"),
        ("EXEC", "MID"),
        ("MID", "VERIFY"),
        ("VERIFY", "E"),
    } <= english_edges
    assert "How VibeSkills carries a task through to delivery" in english
    assert "VibeSkills 如何把任务推进到可交付" in chinese
    for step in (
        "Confirms the requirement.",
        "Recommends a level.",
        "Organizes Skills.",
        "Executes and records.",
        "Checks the result.",
    ):
        assert step in english
    for step in (
        "确认需求。",
        "推荐级别。",
        "组织 Skills。",
        "执行并记录。",
        "检查结果。",
    ):
        assert step in chinese
    assert "How local Skills take part" in english
    assert "本地 Skills 如何参与任务" in chinese
    assert "How a task can continue and be reviewed" in english
    assert "任务中断后怎样继续，完成后怎样复查" in chinese
    assert "U01` through `U10`" not in english
    assert "`U01` 到 `U10`" not in chinese
    assert "From requirement to final checks" not in english
    assert "从需求确认到最终检查" not in chinese
    assert "How it finds the right Skill" not in english
    assert "它怎样找到合适的 Skill" not in chinese
    assert "What gets saved" not in english
    assert "运行后会保存什么" not in chinese
    for project_name in (
        "Superpowers",
        "Get Shit Done",
        "OpenSpec",
        "spec-kit",
        "mem0",
        "Scrapling",
        "Serena",
    ):
        assert project_name not in english
        assert project_name not in chinese
    assert "What else VibeSkills does" not in english
    assert "除了组织 Skills，它还会做这些事" not in chinese


def test_public_ml_case_claims_match_its_published_evidence() -> None:
    case_root = REPO_ROOT / "docs" / "cases" / "ml-experiment"
    selected = json.loads((case_root / "evidence" / "selected-skills.json").read_text(encoding="utf-8"))
    inventory = json.loads((case_root / "evidence" / "skill-inventory-snapshot.json").read_text(encoding="utf-8"))
    work_plan = json.loads((case_root / "evidence" / "module-work-plan.json").read_text(encoding="utf-8"))
    execution = json.loads((case_root / "evidence" / "module-execution.json").read_text(encoding="utf-8"))
    consistency = json.loads((case_root / "evidence" / "consistency-check.json").read_text(encoding="utf-8"))
    acceptance = json.loads((case_root / "evidence" / "delivery-acceptance-report.json").read_text(encoding="utf-8"))

    assert selected["source_run_id"] == "20260718T041559Z-51996499"
    assert selected["selected_count"] == len(selected["skills"]) == 7
    assert inventory["totals"]["unique_names"] > 100
    assert inventory["totals"]["selected_for_case"] == 7
    assert len(work_plan["modules"]) == 9
    assert len(work_plan["work_units"]) == 10
    assert len(execution["units"]) == 10
    assert all(unit["state"] == "completed" for unit in execution["units"])
    assert sum(len(module["criterion_results"]) for module in execution["modules"]) == 18
    assert all(
        criterion["state"] == "passing"
        for module in execution["modules"]
        for criterion in module["criterion_results"]
    )
    assert consistency["passing_check_count"] == 17
    assert consistency["failing_check_count"] == 0
    assert acceptance["summary"]["gate_result"] == "PASS"
    assert acceptance["summary"]["runtime_status"] == "completed"
    assert acceptance["summary"]["readiness_state"] == "fully_ready"
    assert acceptance["execution_context"]["completed_unit_count"] == 10
    assert acceptance["execution_context"]["failed_unit_count"] == 0
    assert acceptance["execution_context"]["blocked_unit_count"] == 0


def test_public_ml_case_keeps_private_paths_out() -> None:
    case_root = REPO_ROOT / "docs" / "cases" / "ml-experiment"
    for path in case_root.rglob("*"):
        if path.suffix.lower() not in {".json", ".md", ".ps1", ".py", ".txt", ".lock"}:
            continue
        content = path.read_text(encoding="utf-8")
        assert "D:\\Documents\\vibeskills" not in content
        assert "C:\\Users\\" not in content
        assert re.search(r"work[\\/]+readme-cases", content, flags=re.IGNORECASE) is None

def test_recommended_full_and_enterprise_reference_pages_are_archived_not_active_install_guidance() -> None:
    for path in (
        "docs/install/recommended-full-path.en.md",
        "docs/install/enterprise-governed-path.en.md",
        "docs/install/recommended-full-path.md",
        "docs/install/enterprise-governed-path.md",
    ):
        assert not (REPO_ROOT / path).exists()
        assert (REPO_ROOT / "docs" / "archive" / "install-legacy" / "2026-07-02" / Path(path).name).exists()


def test_opencode_reference_page_is_archived_not_active_install_guidance() -> None:
    active_note = REPO_ROOT / "docs/install/opencode-path.en.md"
    archived_note = REPO_ROOT / "docs/archive/install-legacy/2026-07-02/opencode-path.en.md"
    archived_cn_note = REPO_ROOT / "docs/archive/install-legacy/2026-07-02/opencode-path.md"

    assert not active_note.exists()
    assert archived_note.exists()
    assert archived_cn_note.exists()
    assert not (REPO_ROOT / "docs/install/opencode-path.md").exists()
