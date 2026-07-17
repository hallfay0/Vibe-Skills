from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_runtime_authority_docs_describe_current_python_and_powershell_roles() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    architecture = (
        REPO_ROOT / "docs" / "architecture" / "local-agent-kernel-v2.md"
    ).read_text(encoding="utf-8")
    forbidden_overclaims = (
        "PowerShell stays only as a thin host wrapper",
        "PowerShell owns launcher wrappers, host receipts, shell-native checks, and leaf execution only",
    )
    readme_claims = (
        "Python owns canonical validation",
        "truth chain from `agent_skill_organization`",
        "PowerShell performs stage orchestration",
        "The current Agent performs the approved module work",
        "Do not add new task semantics or task execution to PowerShell",
        "existing PowerShell stage scripts are transitional orchestration surfaces",
    )
    architecture_claims = (
        "Python owns final truth artifacts",
        "canonical validation",
        "structured runtime result",
        "PowerShell still performs stage orchestration",
        "Do not add new task semantics to PowerShell",
        "existing PowerShell stage scripts are transitional orchestration surfaces",
    )
    forbidden_claims = (
        "Do not let PowerShell own task semantics.",
    )

    for claim in readme_claims:
        assert claim in readme
    for claim in architecture_claims:
        assert claim in architecture
    for content in (readme, architecture):
        for claim in forbidden_overclaims:
            assert claim not in content
        for claim in forbidden_claims:
            assert claim not in content


def test_chinese_readme_routes_internal_runtime_roles_to_the_architecture_docs() -> None:
    content = (REPO_ROOT / "README.zh.md").read_text(encoding="utf-8")

    assert "[架构说明](./docs/architecture/local-agent-kernel-v2.md)" in content
    assert "Python 和 PowerShell 分别负责什么" in content

    internal_phrases = (
        "canonical validation",
        "真相链",
        "阶段编排",
        "迁移期编排面",
    )
    for phrase in internal_phrases:
        assert phrase not in content
