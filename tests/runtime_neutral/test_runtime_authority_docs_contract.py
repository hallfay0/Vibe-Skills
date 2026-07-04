from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_runtime_authority_docs_describe_current_python_and_powershell_roles() -> None:
    docs = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "docs" / "architecture" / "local-agent-kernel-v2.md",
    ]
    forbidden_overclaims = (
        "PowerShell stays only as a thin host wrapper",
        "PowerShell owns launcher wrappers, host receipts, shell-native checks, and leaf execution only",
    )
    required_claims = (
        "Python owns final truth artifacts",
        "canonical validation",
        "structured runtime result",
        "PowerShell still performs stage orchestration",
    )

    for path in docs:
        content = path.read_text(encoding="utf-8")
        for claim in required_claims:
            assert claim in content, path
        for claim in forbidden_overclaims:
            assert claim not in content, path


def test_chinese_readme_describes_current_python_and_powershell_roles() -> None:
    content = (REPO_ROOT / "README.zh.md").read_text(encoding="utf-8")

    required_claims = (
        "Python 负责最终 truth artifacts",
        "canonical validation",
        "PowerShell 仍然承担阶段编排",
        "不把它描述成已经只是薄壳",
    )
    for claim in required_claims:
        assert claim in content
