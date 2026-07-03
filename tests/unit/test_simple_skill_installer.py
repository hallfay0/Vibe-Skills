from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
INSTALLER_SRC = ROOT / "packages" / "installer-core" / "src"
for src in (CONTRACTS_SRC, INSTALLER_SRC):
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))

from vgo_installer.simple_skill_installer import (
    check_vibe_skill,
    install_vibe_skill,
    uninstall_vibe_skill,
    update_vibe_skill,
)


def _write(path: Path, text: str = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_install_copies_only_the_simplified_vibe_package(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    skills_dir = tmp_path / "skills"
    for relpath in (
        "SKILL.md",
        "config/runtime.json",
        "protocols/runtime.md",
        "apps/vgo-cli/src/vgo_cli/main.py",
        "apps/vgo-cli/src/vgo_cli/__pycache__/main.cpython-310.pyc",
        "packages/contracts/src/vgo_contracts/__init__.py",
        "packages/runtime-core/src/vgo_runtime/__init__.py",
        "adapters/index.json",
        "scripts/common/vibe-governance-helpers.ps1",
        "scripts/runtime/VibeRuntime.Common.ps1",
        "scripts/router/modules/46-confirm-ui.ps1",
        "scripts/verify/vibe-release-install-runtime-coherence-gate.ps1",
    ):
        _write(repo_root / relpath)
    for relpath in (
        "agents/openai.yaml",
        "commands/vibe.md",
        "docs/install/README.md",
        "dist/archive.zip",
        "bundled/skills/brainstorming/SKILL.md",
        "tests/unit/test_old.py",
        "outputs/runtime/log.txt",
        ".vibeskills/install-ledger.json",
    ):
        _write(repo_root / relpath)

    receipt = install_vibe_skill(
        repo_root=repo_root,
        skills_dir=skills_dir,
        installed_at_utc="2026-07-02T08:00:00Z",
        source_git_commit="abc123",
        source_git_dirty=True,
    )

    install_root = skills_dir / "vibe"
    assert (install_root / "SKILL.md").is_file()
    assert (install_root / "config/runtime.json").is_file()
    assert (install_root / "protocols/runtime.md").is_file()
    assert not (install_root / "adapters").exists()
    assert not (install_root / "apps" / "vgo-cli" / "src" / "vgo_cli" / "__pycache__").exists()
    assert (install_root / "scripts" / "common" / "vibe-governance-helpers.ps1").is_file()
    assert (install_root / "scripts" / "verify" / "vibe-release-install-runtime-coherence-gate.ps1").is_file()
    assert not (install_root / "docs").exists()
    assert not (install_root / "tests").exists()
    assert not (install_root / "bundled").exists()
    assert receipt["receipt_kind"] == "vibe-skill-install"
    assert receipt["skill_id"] == "vibe"
    assert receipt["install_root"] == str(install_root.resolve())
    assert receipt["source_git_commit"] == "abc123"
    assert receipt["source_git_dirty"] is True
    assert any(entry["path"] == "SKILL.md" for entry in receipt["files"])
    assert (install_root / ".vibeskills" / "install-receipt.json").is_file()


def test_check_reports_drift_when_receipt_owned_file_changes(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    skills_dir = tmp_path / "skills"
    _write(repo_root / "SKILL.md", "# vibe\n")

    install_vibe_skill(
        repo_root=repo_root,
        skills_dir=skills_dir,
        installed_at_utc="2026-07-02T08:00:00Z",
        source_git_commit="abc123",
        source_git_dirty=False,
    )

    assert check_vibe_skill(skills_dir=skills_dir)["ok"] is True

    (skills_dir / "vibe" / "SKILL.md").write_text("# changed\n", encoding="utf-8")
    result = check_vibe_skill(skills_dir=skills_dir)

    assert result["ok"] is False
    assert result["drifted_files"] == ["SKILL.md"]


def test_update_refuses_to_overwrite_drifted_install(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    next_repo_root = tmp_path / "next-repo"
    skills_dir = tmp_path / "skills"
    _write(repo_root / "SKILL.md", "# vibe\n")
    _write(next_repo_root / "SKILL.md", "# next vibe\n")
    install_vibe_skill(
        repo_root=repo_root,
        skills_dir=skills_dir,
        installed_at_utc="2026-07-02T08:00:00Z",
        source_git_commit="abc123",
        source_git_dirty=False,
    )
    (skills_dir / "vibe" / "SKILL.md").write_text("# local edit\n", encoding="utf-8")

    try:
        update_vibe_skill(
            repo_root=next_repo_root,
            skills_dir=skills_dir,
            installed_at_utc="2026-07-02T09:00:00Z",
            source_git_commit="def456",
            source_git_dirty=False,
        )
    except RuntimeError as exc:
        assert "drift" in str(exc)
    else:
        raise AssertionError("update should refuse a drifted install")

    assert (skills_dir / "vibe" / "SKILL.md").read_text(encoding="utf-8") == "# local edit\n"


def test_uninstall_removes_owned_files_but_keeps_user_files(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    skills_dir = tmp_path / "skills"
    _write(repo_root / "SKILL.md", "# vibe\n")
    install_vibe_skill(
        repo_root=repo_root,
        skills_dir=skills_dir,
        installed_at_utc="2026-07-02T08:00:00Z",
        source_git_commit="abc123",
        source_git_dirty=False,
    )
    user_file = skills_dir / "vibe" / "notes.md"
    user_file.write_text("keep me\n", encoding="utf-8")

    result = uninstall_vibe_skill(skills_dir=skills_dir)

    assert result["removed_files"] == ["SKILL.md"]
    assert user_file.read_text(encoding="utf-8") == "keep me\n"
    assert (skills_dir / "vibe").is_dir()
