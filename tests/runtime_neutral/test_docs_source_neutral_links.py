from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SELF_REPO_GITHUB = "https://github.com/foryourhealth111-pixel/Vibe-Skills"
SELF_REPO_RAW = "https://raw.githubusercontent.com/foryourhealth111-pixel/Vibe-Skills"

DOC_SCRIPT_SUFFIXES = {".md", ".ps1", ".py", ".sh", ".yml", ".yaml", ".json"}
DOC_SCRIPT_ROOTS = ("docs", "scripts", ".github")

def _repo_relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _documentation_surfaces() -> list[Path]:
    surfaces: list[Path] = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in DOC_SCRIPT_SUFFIXES:
            continue
        relative = _repo_relative(path)
        if path.suffix == ".md" or relative.startswith(DOC_SCRIPT_ROOTS):
            surfaces.append(path)
    return surfaces


def test_documentation_surfaces_do_not_bind_internal_links_to_github_blob_or_raw_urls() -> None:
    forbidden = (
        re.compile(rf"{re.escape(SELF_REPO_GITHUB)}/blob/[^)\s>\"']+"),
        re.compile(rf"{re.escape(SELF_REPO_RAW)}/[^)\s>\"']+"),
    )
    violations: list[str] = []

    for path in _documentation_surfaces():
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            for pattern in forbidden:
                if pattern.search(line):
                    violations.append(f"{_repo_relative(path)}:{line_number}: {line.strip()}")

    assert violations == []


def test_active_install_docs_do_not_keep_legacy_prompt_install_recipes() -> None:
    assert not (REPO_ROOT / "docs" / "install" / "prompts").exists()
