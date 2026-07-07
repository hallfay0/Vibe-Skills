from __future__ import annotations

from pathlib import Path
import sys
import json


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_SRC = ROOT / "packages" / "runtime-core" / "src"
if str(RUNTIME_SRC) not in sys.path:
    sys.path.insert(0, str(RUNTIME_SRC))

from vgo_runtime import router_contract_runtime as runtime
from vgo_runtime.runtime_support import RepoContext


def test_route_prompt_reports_no_local_candidate_without_pack_fallback(tmp_path: Path) -> None:
    agent_root = tmp_path / "home" / ".agents"

    result = runtime.route_prompt(
        prompt="Use manuscript-as-code to write the paper.",
        grade="L",
        task_type="writing",
        requested_skill="manuscript-as-code",
        target_root=str(agent_root),
        host_id="codex",
        repo_root=ROOT,
    )

    assert result["candidate_source"] == "local_skill_index"
    assert result["route_mode"] == "no_local_candidate"
    assert result["route_reason"] == "requested_local_skill_not_found"
    assert result["selected"] is None
    assert result["fallback_applied"] is False
    assert result["local_skill_index"]["skill_count"] == 0
    assert result["rejected_specialist_reasons"] == ["manuscript-as-code"]


def test_deep_discovery_off_does_not_require_capability_catalog(tmp_path: Path) -> None:
    config_root = tmp_path / "config"
    config_root.mkdir()
    (config_root / "deep-discovery-policy.json").write_text(
        json.dumps({"enabled": True, "mode": "off"}, ensure_ascii=False),
        encoding="utf-8",
    )
    repo = RepoContext(
        repo_root=tmp_path,
        config_root=config_root,
        bundled_skills_root=tmp_path / "bundled" / "skills",
    )

    advice = runtime._build_deep_discovery_advice(
        repo=repo,
        prompt_lower="plan and implement this task end to end",
        grade="L",
        task_type="planning",
    )

    assert advice is None
