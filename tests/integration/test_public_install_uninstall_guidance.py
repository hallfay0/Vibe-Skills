from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_root_readme_uses_skills_dir_uninstall_commands() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "uninstall.ps1 -SkillsDir <skills-dir>" in readme
    assert "uninstall.ps1 -HostId <host>" not in readme
    assert "uninstall.sh --host <host>" not in readme


def test_root_chinese_readme_uses_skills_dir_uninstall_commands() -> None:
    readme = (REPO_ROOT / "README.zh.md").read_text(encoding="utf-8")

    assert "uninstall.ps1 -SkillsDir <skills-dir>" in readme
    assert "uninstall.ps1 -HostId <host>" not in readme
    assert "uninstall.sh --host <host>" not in readme
