from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_shell_frontends_advertise_windows_powershell_handoff() -> None:
    bootstrap_shell = (REPO_ROOT / "scripts" / "bootstrap" / "one-shot-setup.sh").read_text(encoding="utf-8")
    check_shell = (REPO_ROOT / "check.sh").read_text(encoding="utf-8")

    assert "Windows shell frontend detected; switching to PowerShell-first supported path." in bootstrap_shell
    assert "one-shot-setup.ps1" in bootstrap_shell
    assert "Windows shell frontend detected; switching to PowerShell-first supported path." in check_shell
    assert "check.ps1" in check_shell


def test_windows_support_matrix_mentions_powershell_first_shell_handoff() -> None:
    content = (REPO_ROOT / "docs" / "universalization" / "platform-support-matrix.md").read_text(encoding="utf-8")
    assert "Windows shell frontends should hand off to PowerShell-first when a PowerShell host is available." in content


def test_installation_rules_explain_windows_shell_blocking_behavior() -> None:
    content = (REPO_ROOT / "docs" / "install" / "installation-rules.md").read_text(encoding="utf-8")
    assert "Windows bash frontends are convenience wrappers, not the authoritative lane." in content
