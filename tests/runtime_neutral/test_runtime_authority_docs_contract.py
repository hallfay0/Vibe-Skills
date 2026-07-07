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
        "Do not add new task semantics to PowerShell",
        "existing PowerShell stage scripts are transitional orchestration surfaces",
    )
    forbidden_claims = (
        "Do not let PowerShell own task semantics.",
    )

    for path in docs:
        content = path.read_text(encoding="utf-8")
        for claim in required_claims:
            assert claim in content, path
        for claim in forbidden_overclaims:
            assert claim not in content, path
        for claim in forbidden_claims:
            assert claim not in content, path


def test_chinese_readme_describes_current_python_and_powershell_roles() -> None:
    content = (REPO_ROOT / "README.zh.md").read_text(encoding="utf-8")

    required_claims = (
        "Python 负责最终 truth artifacts",
        "canonical validation",
        "PowerShell 仍然承担阶段编排",
        "不要把新的任务语义继续加到 PowerShell",
        "现有 PowerShell 阶段脚本只是迁移期编排面",
    )
    for claim in required_claims:
        assert claim in content
