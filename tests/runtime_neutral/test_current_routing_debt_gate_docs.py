from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_verify_docs_include_current_routing_debt_gate() -> None:
    readme = (REPO_ROOT / "scripts" / "verify" / "README.md").read_text(encoding="utf-8")
    index = (REPO_ROOT / "scripts" / "verify" / "gate-family-index.md").read_text(encoding="utf-8")

    for text in [readme, index]:
        assert "vibe-current-routing-debt-gate.ps1" in text
        assert "current routing debt" in text.lower()


def test_common_verify_sequence_keeps_router_contract_before_debt_gate() -> None:
    readme = (REPO_ROOT / "scripts" / "verify" / "README.md").read_text(encoding="utf-8")
    guidance = (
        "If the change touches retired-routing language or route-era cleanup, "
        "run `vibe-router-contract-gate.ps1` before `vibe-current-routing-debt-gate.ps1`"
    )
    assert guidance in readme


def test_current_routing_docs_point_to_live_contract_and_not_archived_zero_route_passes() -> None:
    governance_readme = (REPO_ROOT / "docs" / "governance" / "README.md").read_text(encoding="utf-8")
    archive_readme = (
        REPO_ROOT / "docs" / "archive" / "governance-history" / "README.md"
    ).read_text(encoding="utf-8")

    assert "current-routing-contract.md" in governance_readme
    assert "zero-route-authority-third-pass-2026-04-30.md" not in governance_readme
    assert "zero-route-authority-third-pass-2026-04-30.md" in archive_readme
