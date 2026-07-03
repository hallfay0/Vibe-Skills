from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALL_DOCS = REPO_ROOT / "docs" / "install"


def test_active_install_docs_only_describe_simple_skills_dir_install() -> None:
    active_docs = {
        path.relative_to(INSTALL_DOCS).as_posix()
        for path in INSTALL_DOCS.rglob("*")
        if path.is_file()
    }

    assert active_docs == {"README.md", "README.en.md"}

    forbidden_legacy_terms = (
        "-HostId",
        "-Profile",
        "-TargetRoot",
        "--host",
        "--profile",
        "--target-root",
        "vibe-upgrade",
    )
    for doc_name in active_docs:
        text = (INSTALL_DOCS / doc_name).read_text(encoding="utf-8")
        assert "SkillsDir" in text or "--skills-dir" in text
        for term in forbidden_legacy_terms:
            assert term not in text
