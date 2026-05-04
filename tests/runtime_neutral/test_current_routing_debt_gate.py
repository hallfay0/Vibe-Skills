from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
GATE = REPO_ROOT / "scripts" / "verify" / "vibe-current-routing-debt-gate.ps1"
POLICY = REPO_ROOT / "config" / "current-routing-debt-erasure.json"
OLD_ROLE_TERMS = [
    "route_authority_candidates",
    "stage_assistant_candidates",
    "route_authority_eligible",
    "legacy_role",
    "_legacy_role",
    "_legacy_stage_assistant_candidates",
]


def powershell() -> str:
    shell = (
        shutil.which("pwsh")
        or shutil.which("pwsh.exe")
        or shutil.which("powershell")
        or shutil.which("powershell.exe")
    )
    if not shell:
        pytest.skip("PowerShell executable not available")
    return shell


def run_gate(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [powershell(), "-NoLogo", "-NoProfile", "-File", str(GATE), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )


def test_gate_reports_json_and_clean_current_surfaces() -> None:
    result = run_gate("-Json")
    assert result.returncode == 0, result.stdout + result.stderr

    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["policy_path"].replace("\\", "/").endswith("config/current-routing-debt-erasure.json")
    assert payload["summary"]["P0"] == 0
    assert payload["summary"]["P1"] == 0
    assert payload["summary"]["P2"] == 0
    assert payload["summary"]["legacy_allowed_hits"] > 0
    assert "legacy_skill_routing" in payload["retired_terms"]
    assert "skill_routing.selected" in payload["current_fields"]
    assert payload["current_model"] == [
        "skill_candidates",
        "skill_routing.selected",
        "selected_skill_execution",
        "skill_usage.used",
        "skill_usage.unused",
        "skill_usage.evidence",
    ]


def test_gate_does_not_leave_python_bytecode_in_repo_owned_contracts() -> None:
    pycache = REPO_ROOT / "packages" / "contracts" / "src" / "vgo_contracts" / "__pycache__"
    if pycache.exists():
        shutil.rmtree(pycache)

    env = os.environ.copy()
    env.pop("PYTHONDONTWRITEBYTECODE", None)
    env.pop("PYTHONPYCACHEPREFIX", None)
    result = run_gate("-Json", env=env)
    assert result.returncode == 0, result.stdout + result.stderr
    assert not pycache.exists()


def test_gate_writes_audit_artifacts(tmp_path: Path) -> None:
    result = run_gate("-WriteArtifacts", "-ArtifactRoot", str(tmp_path))
    assert result.returncode == 0, result.stdout + result.stderr

    json_path = tmp_path / "outputs" / "verify" / "current-routing-debt-gate.json"
    audit_json_path = tmp_path / "outputs" / "verify" / "current-routing-debt-audit.json"
    audit_md_path = tmp_path / "docs" / "audits" / "2026-05-02-current-routing-debt-audit.md"
    repo_audit_md_path = REPO_ROOT / "docs" / "audits" / "2026-05-02-current-routing-debt-audit.md"

    assert json_path.exists()
    assert audit_json_path.exists()
    assert audit_md_path.exists()
    assert not repo_audit_md_path.exists()

    gate_payload = json.loads(json_path.read_text(encoding="utf-8"))
    audit_payload = json.loads(audit_json_path.read_text(encoding="utf-8"))
    audit_markdown = audit_md_path.read_text(encoding="utf-8")

    assert gate_payload["status"] == "pass"
    assert audit_payload["status"] == "pass"
    assert "# Current Routing Debt Audit" in audit_markdown
    assert "P0 Current Output Pollution: 0" in audit_markdown
    assert "P1 Current Code Dependency: 0" in audit_markdown
    assert "P2 Current Documentation Pollution: 0" in audit_markdown


def test_gate_policy_file_exists_and_is_valid_json() -> None:
    payload = json.loads(POLICY.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["success_thresholds"] == {"P0": 0, "P1": 0, "P2": 0}


def test_gate_policy_scans_retired_old_role_fields() -> None:
    payload = json.loads(POLICY.read_text(encoding="utf-8"))
    retired_terms = set(payload["retired_terms"])
    high_risk_terms = set(payload["high_risk_retired_fields"])

    for term in OLD_ROLE_TERMS:
        assert term in retired_terms
        assert term in high_risk_terms


def test_current_router_runtime_sources_do_not_contain_retired_old_role_fields() -> None:
    source_files = [
        REPO_ROOT / "packages" / "runtime-core" / "src" / "vgo_runtime" / "router_contract_selection.py",
        REPO_ROOT / "packages" / "runtime-core" / "src" / "vgo_runtime" / "router_contract_runtime.py",
        REPO_ROOT / "packages" / "runtime-core" / "src" / "vgo_runtime" / "custom_admission.py",
        REPO_ROOT / "scripts" / "router" / "modules" / "19-custom-admission.ps1",
        REPO_ROOT / "scripts" / "router" / "modules" / "41-candidate-selection.ps1",
        REPO_ROOT / "scripts" / "router" / "resolve-pack-route.ps1",
        REPO_ROOT / "scripts" / "runtime" / "Freeze-RuntimeInputPacket.ps1",
    ]
    for path in source_files:
        text = path.read_text(encoding="utf-8")
        for term in OLD_ROLE_TERMS:
            assert term not in text, f"{term} remains in {path}"


def test_runtime_packet_sibling_recommendations_use_neutral_ranking_language() -> None:
    text = (REPO_ROOT / "scripts" / "runtime" / "Freeze-RuntimeInputPacket.ps1").read_text(encoding="utf-8")

    assert "route_authority_eligible" not in text
    assert "additional XL route-authority specialist candidate" not in text
    assert "additional XL ranked specialist candidate" in text


def test_current_unit_and_integration_fixtures_do_not_write_retired_root_fields() -> None:
    current_fixture_files = [
        REPO_ROOT / "tests" / "unit" / "test_canonical_vibe_entry_launcher.py",
        REPO_ROOT / "tests" / "integration" / "test_verification_runtime_entrypoint_contract_cutover.py",
    ]
    for path in current_fixture_files:
        text = path.read_text(encoding="utf-8")
        assert '"specialist_recommendations"' not in text, path
        assert '"specialist_dispatch"' not in text, path
        assert '"legacy_skill_routing"' not in text, path


def test_truth_gate_legacy_fixture_is_named_as_retired_fixture() -> None:
    text = (REPO_ROOT / "tests" / "integration" / "test_canonical_vibe_truth_gate.py").read_text(encoding="utf-8")
    assert "def _write_retired_legacy_truth_artifacts(" in text
    assert "def _write_valid_canonical_entry_artifacts(" in text
    valid_helper = text.split("def _write_valid_canonical_entry_artifacts(", 1)[1].split(
        "def _write_retired_legacy_truth_artifacts(",
        1,
    )[0]
    assert '"legacy_skill_routing"' not in valid_helper
    assert '"specialist_recommendations"' not in valid_helper
    assert '"specialist_dispatch"' not in valid_helper
