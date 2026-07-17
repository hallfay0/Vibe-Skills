from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_root_readme_routes_lifecycle_commands_to_install_guide() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "The default target is `~/.agents/skills`" in readme
    assert "Some hosts may choose defaults such as" not in readme
    assert "./docs/install/README.en.md" in readme
    assert "install.ps1 -SkillsDir" not in readme
    assert "uninstall.ps1 -SkillsDir" not in readme
    assert "uninstall.ps1 -HostId <host>" not in readme
    assert "uninstall.sh --host <host>" not in readme


def test_root_chinese_readme_routes_lifecycle_commands_to_install_guide() -> None:
    readme = (REPO_ROOT / "README.zh.md").read_text(encoding="utf-8")

    assert "默认目录是 `~/.agents/skills`" in readme
    assert "你也可以显式安装到 `~/.codex/skills` 或 `~/.claude/skills`" not in readme
    assert "有些宿主可以选择 `~/.agents/skills`、`~/.codex/skills` 或 `~/.claude/skills` 作为默认值" not in readme
    assert "./docs/install/README.md" in readme
    assert "install.ps1 -SkillsDir" not in readme
    assert "uninstall.ps1 -SkillsDir" not in readme
    assert "uninstall.ps1 -HostId <host>" not in readme
    assert "uninstall.sh --host <host>" not in readme


def test_root_readme_points_public_install_to_versioned_release_zip() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "published release zip" in readme
    assert "download the release zip" in readme.lower()
    assert "installs the repo's `vibe` skill" not in readme


def test_install_readmes_describe_release_zip_not_repo_source_install() -> None:
    english = (REPO_ROOT / "docs" / "install" / "README.en.md").read_text(encoding="utf-8")
    chinese = (REPO_ROOT / "docs" / "install" / "README.md").read_text(encoding="utf-8")

    assert "published release zip" in english
    assert "repo's `vibe` skill" not in english
    assert "发布版本 zip" in chinese
    assert "仓库里的 `vibe` skill" not in chinese
