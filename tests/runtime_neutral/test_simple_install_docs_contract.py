from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALL_DOCS = REPO_ROOT / "docs" / "install"
DOCS_INDEX = REPO_ROOT / "docs" / "README.md"
RELEASES_INDEX = REPO_ROOT / "docs" / "releases" / "README.md"
PUBLIC_READMES = (
    REPO_ROOT / "README.md",
    REPO_ROOT / "README.zh.md",
)
ACTIVE_INSTALL_GUIDES = (
    REPO_ROOT / "docs" / "cold-start-install-paths.md",
    REPO_ROOT / "docs" / "cold-start-install-paths.en.md",
    REPO_ROOT / "docs" / "one-shot-setup.md",
)
ONE_SHOT_BOOTSTRAPS = (
    REPO_ROOT / "scripts" / "bootstrap" / "one-shot-setup.sh",
    REPO_ROOT / "scripts" / "bootstrap" / "one-shot-setup.ps1",
)
REMOVED_PUBLIC_INSTALL_TERMS = (
    "-HostId",
    "-Profile",
    "-TargetRoot",
    "--host",
    "--profile",
    "--target-root",
    "--deep",
    "vibe-upgrade",
)


def test_active_install_docs_only_describe_simple_skills_dir_install() -> None:
    active_docs = {
        path.relative_to(INSTALL_DOCS).as_posix()
        for path in INSTALL_DOCS.rglob("*")
        if path.is_file()
    }

    assert active_docs == {"README.md", "README.en.md"}

    for doc_name in active_docs:
        text = (INSTALL_DOCS / doc_name).read_text(encoding="utf-8")
        assert "SkillsDir" in text or "--skills-dir" in text
        for term in REMOVED_PUBLIC_INSTALL_TERMS:
            assert term not in text


def test_public_readmes_do_not_advertise_missing_cli_commands() -> None:
    for path in PUBLIC_READMES:
        text = path.read_text(encoding="utf-8")
        assert "benchmark-kernel" not in text, path


def test_active_install_guides_point_to_simplified_skills_dir_install() -> None:
    for path in ACTIVE_INSTALL_GUIDES:
        text = path.read_text(encoding="utf-8")
        assert "--skills-dir" in text, path
        assert "docs/install/README" in text or "install/README" in text, path
        for term in REMOVED_PUBLIC_INSTALL_TERMS:
            assert term not in text, path


def test_live_docs_indexes_do_not_route_current_install_to_retired_or_missing_pages() -> None:
    docs_index = DOCS_INDEX.read_text(encoding="utf-8")
    assert "install/README.md" in docs_index
    assert "one-click-install-release-copy" not in docs_index
    assert "runtime-freshness-install-sop.md" not in docs_index

    releases_index = RELEASES_INDEX.read_text(encoding="utf-8")
    assert "runtime-freshness-install-sop.md" not in releases_index


def test_public_readmes_keep_other_environments_as_one_auxiliary_install_note() -> None:
    english = PUBLIC_READMES[0].read_text(encoding="utf-8")
    assert "OpenClaw host notes" not in english
    assert "OpenCode host notes" not in english

    chinese = PUBLIC_READMES[1].read_text(encoding="utf-8")
    assert "OpenClaw 宿主说明" not in chinese
    assert "OpenCode 宿主说明" not in chinese


def test_quick_start_explains_install_run_and_delivery_records_without_legacy_status_terms() -> None:
    english = (REPO_ROOT / "docs" / "quick-start.en.md").read_text(encoding="utf-8")
    chinese = (REPO_ROOT / "docs" / "quick-start.md").read_text(encoding="utf-8")

    assert "`check` only checks whether installer-managed files are present" in english
    assert "`session_root` is the record folder for one task" in english
    assert "`delivery-acceptance-report.json` or `.md` stores the final check" in english

    assert "`check` 只检查安装器管理的文件是否都在" in chinese
    assert "`session_root` 是一次任务的记录文件夹" in chinese
    assert "`delivery-acceptance-report.json` 或 `.md` 保存最终检查结果" in chinese

    for content in (english, chinese):
        assert "vibe host-ready" not in content
        assert "online-ready" not in content

    assert "`minimal` is the recommended default" not in english
    assert "choose `full`" not in english
    assert "`minimal` 是默认推荐版本" not in chinese
    assert "再选 `full`" not in chinese


def test_install_readmes_keep_check_at_installed_locally_layer() -> None:
    english = (INSTALL_DOCS / "README.en.md").read_text(encoding="utf-8")
    chinese = (INSTALL_DOCS / "README.md").read_text(encoding="utf-8")

    assert "`check` proves `installed locally`." in english
    assert "It does not prove `runtime coherent` or `delivery accepted`." in english

    assert "`check` 证明的是 `installed locally`。" in chinese
    assert "它不证明 `runtime coherent`，也不证明 `delivery accepted`。" in chinese


def test_one_shot_bootstrap_scripts_are_retired_as_public_install_entrypoints() -> None:
    for path in ONE_SHOT_BOOTSTRAPS:
        text = path.read_text(encoding="utf-8")
        assert "retired" in text.lower(), path
        assert "--skills-dir" in text, path
        assert "install.sh" in text or "install.ps1" in text, path
        for term in REMOVED_PUBLIC_INSTALL_TERMS:
            assert term not in text, path
        assert "adapter_registry_query.py" not in text, path
