from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_public_docs_do_not_present_router_modules_as_current_user_path() -> None:
    public_docs = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "README.zh.md",
        REPO_ROOT / "SKILL.md",
    ]

    for path in public_docs:
        content = path.read_text(encoding="utf-8")
        assert "scripts/router/modules" not in content, path


def test_router_readme_names_python_runtime_as_current_routing_owner() -> None:
    content = (REPO_ROOT / "scripts" / "router" / "README.md").read_text(encoding="utf-8")

    required_claims = (
        "Current routing semantic owner",
        "packages/runtime-core/src/vgo_runtime/router_contract_runtime.py",
        "resolve-pack-route.ps1 is a compatibility bridge",
        "modules/ is legacy/helper/compatibility",
    )
    for claim in required_claims:
        assert claim in content
