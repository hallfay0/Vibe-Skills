from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_bootstrap_shell_no_longer_hands_off_to_legacy_powershell_one_shot() -> None:
    bootstrap_shell = (REPO_ROOT / "scripts" / "bootstrap" / "one-shot-setup.sh").read_text(encoding="utf-8")

    assert "retired" in bootstrap_shell.lower()
    assert "Windows shell frontend detected; switching to PowerShell-first supported path." not in bootstrap_shell
    assert "handoff_to_windows_powershell_frontend" not in bootstrap_shell


def test_check_shell_uses_portable_simple_cli_wrapper() -> None:
    check_shell = (REPO_ROOT / "check.sh").read_text(encoding="utf-8")

    assert "vgo_cli.main check" in check_shell
    assert "Windows shell frontend detected; switching to PowerShell-first supported path." not in check_shell
    assert "handoff_to_windows_powershell_frontend" not in check_shell


def test_windows_support_matrix_mentions_powershell_first_shell_handoff() -> None:
    content = (REPO_ROOT / "docs" / "universalization" / "platform-support-matrix.md").read_text(encoding="utf-8")
    assert "Windows shell frontends should hand off to PowerShell-first when a PowerShell host is available." in content


def test_legacy_installation_rules_are_archived() -> None:
    archived = REPO_ROOT / "docs/archive/install-legacy/2026-07-02/installation-rules.md"

    assert archived.is_file()
    assert "Windows bash frontends are convenience wrappers" in archived.read_text(encoding="utf-8")
