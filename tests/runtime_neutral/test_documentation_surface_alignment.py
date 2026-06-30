from __future__ import annotations

import json
import re
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
    assert _public_entry_ids() == {"vibe", "vibe-upgrade"}

    for path in ("README.md", "README.zh.md", "docs/quick-start.en.md", "docs/quick-start.md"):
        content = _read(path)
        assert "vibe-upgrade" in content
        assert "host-rendered" not in content
        assert "宿主渲染标签" not in content
        for legacy_alias in ("vibe-want", "vibe-how", "vibe-do"):
            assert re.search(rf"(?<![\w-]){re.escape(legacy_alias)}(?![\w-])", content) is None


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


def test_readmes_describe_external_skill_first_story_without_repromoting_a_central_catalog() -> None:
    english = _read("README.md")
    chinese = _read("README.zh.md")
    english_lower = english.lower()
    chinese_lower = chinese.lower()

    assert "host-managed external skills" in english_lower
    assert "starter set" in english_lower
    assert "work_binding" in english
    assert "runtime truth" in english_lower or "first truth surface" in english_lower
    assert "local user-owned overrides still win" in english_lower
    assert (
        "without a new central catalog" in english_lower
        or "not a bigger central catalog" in english_lower
        or "without turning the product into a giant central catalog again" in english_lower
    )
    assert "local_first_skills" not in english_lower
    assert "not a claim" in english_lower and "final architecture" in english_lower
    assert "Local + starter Skills stay the product surface." not in english

    assert "宿主管理的外部 skills" in chinese or "外部 skills 优先" in chinese
    assert "starter" in chinese_lower
    assert "work_binding" in chinese
    assert "第一真相面" in chinese or "真相面" in chinese
    assert "本地用户自管 override 仍然先赢" in chinese
    assert "不长出新的中心目录" in chinese or "不是更大的中心技能目录" in chinese
    assert "不是" in chinese and "最终架构已经完成" in chinese
    assert "本地 + starter Skills 仍然是默认产品面。" not in chinese


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


def test_quick_start_keeps_normal_skill_extension_ahead_of_advanced_custom_workflow_lane() -> None:
    english = _read("docs/quick-start.en.md")
    chinese = _read("docs/quick-start.md")

    assert "local-first" not in english
    assert "host-managed external skill folders" in english or "external-skill-friendly" in english
    assert "Custom Skills onboarding" not in english
    assert "Advanced manifest-driven custom workflow onboarding" in english
    assert english.index("install/README.en.md") < english.index("install/custom-workflow-onboarding.en.md")

    assert "本地优先" not in chinese
    assert "宿主管理的外部 skill 文件夹" in chinese or "外部 skill 友好" in chinese
    assert "想接入自定义 Skills" not in chinese
    assert "想接高级 manifest 驱动 custom workflow" in chinese
    assert chinese.index("install/README.md") < chinese.index("install/custom-workflow-onboarding.md")


def test_install_prompts_treat_pwsh_as_default_power_shell_surface() -> None:
    prompt_paths = (
        "docs/install/prompts/full-version-install.en.md",
        "docs/install/prompts/full-version-install.md",
        "docs/install/prompts/framework-only-install.en.md",
        "docs/install/prompts/framework-only-install.md",
    )

    forbidden_phrases = (
        "must not be treated as the default prerequisite",
        "不要把 `pwsh` 当作默认前提",
    )
    for path in prompt_paths:
        content = _read(path)
        assert "pwsh" in content
        for phrase in forbidden_phrases:
            assert phrase not in content


def test_runtime_core_packaging_projections_do_not_track_local_repo_root() -> None:
    for path in (
        "config/runtime-core-packaging.full.json",
        "config/runtime-core-packaging.minimal.json",
    ):
        payload = json.loads(_read(path))
        assert "_repo_root" not in payload


def test_public_install_surfaces_point_to_local_skill_extension_first() -> None:
    public_paths = (
        "README.md",
        "README.zh.md",
        "docs/install/README.en.md",
        "docs/install/README.md",
        "docs/install/one-click-install-release-copy.en.md",
        "docs/install/one-click-install-release-copy.md",
    )

    for path in public_paths:
        content = _read(path)
        assert "skills/local" in content
        assert "skills/custom/" not in content
        assert "custom-workflows.json" not in content


def test_install_readme_keeps_advanced_custom_workflow_label_explicit() -> None:
    english = _read("docs/install/README.en.md")
    chinese = _read("docs/install/README.md")

    assert "Custom Skill onboarding" not in english
    assert "Advanced manifest-driven custom workflow onboarding" in english
    assert "custom-workflow-onboarding.en.md" in english

    assert "自定义 Skill 接入" not in chinese
    assert "高级 manifest 驱动 custom workflow 接入" in chinese
    assert "custom-workflow-onboarding.md" in chinese


def test_advanced_custom_workflow_doc_is_demoted_below_local_skill_path() -> None:
    for path in (
        "docs/install/custom-workflow-onboarding.en.md",
        "docs/install/custom-workflow-onboarding.md",
    ):
        content = _read(path)
        lowered = content.lower()
        assert "skills/local" in content
        assert "advanced" in lowered or "高级" in content
        assert "`workflow` (default recommendation)" not in content
        assert "`workflow`（默认推荐）" not in content


def test_update_prompts_keep_local_skill_path_ahead_of_advanced_custom_workflow_retention() -> None:
    for path in (
        "docs/install/prompts/framework-only-update.en.md",
        "docs/install/prompts/framework-only-update.md",
        "docs/install/prompts/full-version-update.en.md",
        "docs/install/prompts/full-version-update.md",
    ):
        content = _read(path)
        local_index = content.index("skills/local")
        custom_index = content.index("skills/custom/")
        manifest_index = content.index("custom-workflows.json")

        assert local_index < custom_index
        assert local_index < manifest_index
        assert "advanced manifest-driven custom workflow" in content or "高级 manifest 驱动 custom workflow" in content


def test_advanced_custom_governance_rules_stay_below_local_skill_path() -> None:
    english = _read("docs/install/custom-skill-governance-rules.en.md")
    chinese = _read("docs/install/custom-skill-governance-rules.md")

    for content in (english, chinese):
        lowered = content.lower()
        assert "skills/local" in content
        assert "advanced" in lowered or "高级" in content
        assert content.index("skills/local") < content.index("skills/custom/")

    assert "downgrading from `workflow`" not in english.lower()
    assert "from `workflow` to framework-only" not in english.lower()
    assert "从 `workflow`" not in chinese


def test_kernel_architecture_docs_describe_host_aware_catalog_and_work_binding_truth() -> None:
    architecture = _read("docs/architecture/local-agent-kernel-v2.md")
    interfaces = _read("docs/architecture/local-agent-kernel-v2-interfaces.md")
    architecture_lower = architecture.lower()
    interfaces_lower = interfaces.lower()

    assert "host-managed external skill folders" in architecture_lower or "host external" in architecture_lower
    assert "starter" in architecture_lower
    assert "work_binding" in architecture
    assert "first runtime truth" in architecture_lower or "first truth surface" in architecture_lower
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
    assert "not a claim" in readme and "final architecture" in readme
    assert "不是" in readme_zh and "最终架构已经完成" in readme_zh


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
    assert "normal closeout path should stay small" in readme
    assert "default closure story should stay small" in architecture


def test_advanced_custom_governance_doc_keeps_manifest_driven_admission_in_the_advanced_lane() -> None:
    english = _read("docs/install/custom-skill-governance-rules.en.md")
    english_lowered = english.lower()
    chinese = _read("docs/install/custom-skill-governance-rules.md")

    assert "advanced path" in english_lowered
    assert "normal extension path is still a local skill" in english_lowered
    assert "manifest-driven custom workflow" in english_lowered
    assert "downgrading from `workflow`" not in english_lowered
    assert "not the normal path for ordinary skills" in english_lowered or "only continue when you truly need" in english_lowered
    assert "ordinary skills can still use `skills/local/<skill-id>/skill.md` without entering the advanced lane" in english_lowered

    assert "高级路径" in chinese
    assert "正常扩展路径仍然是本地 skill" in chinese
    assert "manifest 驱动的 custom workflow" in chinese
    assert "从 `workflow`" not in chinese
    assert "work_binding" in chinese
    assert "只有一个 canonical runtime controller" in chinese
    assert "普通 skill 仍可直接走 `skills/local/<skill-id>/skill.md`" in chinese.lower()


def test_framework_only_reference_pages_describe_local_skill_extension_before_advanced_custom_workflows() -> None:
    for path in (
        "docs/install/framework-only-path.en.md",
        "docs/install/framework-only-path.md",
    ):
        content = _read(path)
        lowered = content.lower()
        assert "skills/local" in content
        assert "compatibility" in lowered or "兼容" in content
        assert content.index("skills/local") < content.index("custom-workflow-onboarding")


def test_installation_rules_and_minimal_path_keep_minimal_tied_to_local_skill_extension() -> None:
    rule_paths = (
        "docs/install/installation-rules.en.md",
        "docs/install/installation-rules.md",
    )
    minimal_paths = (
        "docs/install/minimal-path.en.md",
        "docs/install/minimal-path.md",
    )

    for path in rule_paths:
        content = _read(path)
        assert "skills/local" in content
        assert "custom-workflow-onboarding" in content
        assert content.index("skills/local") < content.index("custom-workflow-onboarding")

    for path in minimal_paths:
        content = _read(path)
        assert "skills/local" in content


def test_recommended_full_and_enterprise_reference_pages_keep_local_kernel_shape_visible() -> None:
    for path in (
        "docs/install/recommended-full-path.en.md",
        "docs/install/enterprise-governed-path.en.md",
    ):
        content = _read(path)
        assert "skills/local" in content
        assert "small work kernel" in content

    for path in (
        "docs/install/recommended-full-path.md",
        "docs/install/enterprise-governed-path.md",
    ):
        content = _read(path)
        assert "skills/local" in content
        assert "小工作内核" in content


def test_opencode_reference_page_keeps_vibe_primary_and_helper_aliases_secondary() -> None:
    for path in (
        "docs/install/opencode-path.en.md",
        "docs/install/opencode-path.md",
    ):
        content = _read(path)
        assert "skills/local" in content
        assert "/vibe" in content
        assert "/vibe-implement" in content
        assert "/vibe-review" in content
        assert content.index("/vibe") < content.index("/vibe-implement")
