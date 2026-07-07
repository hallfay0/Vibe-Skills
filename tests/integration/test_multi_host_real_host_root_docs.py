from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_active_install_docs_prefer_skills_roots_not_host_roots() -> None:
    docs = [
        (REPO_ROOT / "docs/install/README.md").read_text(encoding="utf-8"),
        (REPO_ROOT / "docs/install/README.en.md").read_text(encoding="utf-8"),
    ]

    for text in docs:
        assert "~/.agents/skills" in text
        assert "~/.codex/skills" in text
        assert "~/.claude/skills" in text
        assert "~/.cursor" not in text
        assert "~/.codeium/windsurf" not in text
        assert "~/.openclaw" not in text
        assert "~/.config/opencode" not in text


def test_legacy_host_root_install_docs_are_archived() -> None:
    archive = REPO_ROOT / "docs/archive/install-legacy/2026-07-02"

    assert (archive / "installation-rules.md").is_file()
    assert (archive / "recommended-full-path.md").is_file()
    assert (archive / "openclaw-path.md").is_file()
    assert (archive / "opencode-path.md").is_file()
    assert (archive / "configuration-guide.md").is_file()
