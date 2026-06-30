from __future__ import annotations

from pathlib import Path
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_SRC = REPO_ROOT / "packages" / "runtime-core" / "src"
if str(RUNTIME_SRC) not in sys.path:
    sys.path.insert(0, str(RUNTIME_SRC))

from vgo_runtime.kernel import HostSkillRoot, resolve_host_skill_roots


def _write_adapter_index(repo_root: Path, host_ids: list[str]) -> Path:
    entries = ",\n".join(f'    {{"id": "{host_id}"}}' for host_id in host_ids)
    index_path = repo_root / "adapters" / "index.json"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(
        "{\n"
        '  "schema_version": 1,\n'
        '  "adapters": [\n'
        f"{entries}\n"
        "  ]\n"
        "}\n",
        encoding="utf-8",
    )
    return index_path


def _write_settings_map(repo_root: Path, host_id: str, payload: str) -> Path:
    settings_map_path = repo_root / "adapters" / host_id / "settings-map.json"
    settings_map_path.parent.mkdir(parents=True, exist_ok=True)
    settings_map_path.write_text(payload, encoding="utf-8")
    return settings_map_path


def test_resolve_host_skill_roots_returns_codex_global_root() -> None:
    agent_root = Path("D:/tmp/test-home/.agents")

    roots = resolve_host_skill_roots(
        repo_root=REPO_ROOT,
        host_id="codex",
        agent_root=agent_root,
        workspace_root=None,
    )

    assert roots == (
        HostSkillRoot(
            host_id="codex",
            root_key="host_global",
            path=(agent_root / "skills").resolve(),
            source="adapters/codex/settings-map.json:semantics.vco.skill_root",
        ),
    )


def test_resolve_host_skill_roots_normalizes_host_id_text() -> None:
    agent_root = Path("D:/tmp/test-home/.agents")

    roots = resolve_host_skill_roots(
        repo_root=REPO_ROOT,
        host_id="  CoDeX  ",
        agent_root=agent_root,
        workspace_root=None,
    )

    assert roots[0].host_id == "codex"
    assert roots[0].path == (agent_root / "skills").resolve()


def test_resolve_host_skill_roots_returns_opencode_global_then_project_root(tmp_path: Path) -> None:
    agent_root = tmp_path / "agent-root"
    workspace_root = tmp_path / "workspace"

    roots = resolve_host_skill_roots(
        repo_root=REPO_ROOT,
        host_id="opencode",
        agent_root=agent_root,
        workspace_root=workspace_root,
    )

    assert roots == (
        HostSkillRoot(
            host_id="opencode",
            root_key="host_global",
            path=(tmp_path / ".config" / "opencode" / "skills").resolve(),
            source="adapters/opencode/settings-map.json:semantics.vco.skill_root.global",
        ),
        HostSkillRoot(
            host_id="opencode",
            root_key="host_project",
            path=(workspace_root / ".opencode" / "skills").resolve(),
            source="adapters/opencode/settings-map.json:semantics.vco.skill_root.project",
        ),
    )


def test_resolve_host_skill_roots_rejects_host_not_declared_in_adapter_index(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    _write_adapter_index(repo_root, ["codex"])
    _write_settings_map(
        repo_root,
        "custom-host",
        """{
  "adapter_id": "custom-host",
  "semantics": {
    "vco.skill_root": "~/global-skills",
    "vco.skill_root.project": ".project-skills"
  }
}""",
    )
    with pytest.raises(
        ValueError,
        match="Host id is not declared in adapters/index.json: custom-host",
    ):
        resolve_host_skill_roots(
            repo_root=repo_root,
            host_id="custom-host",
            agent_root=tmp_path / "agent-root",
            workspace_root=tmp_path / "workspace",
        )


def test_resolve_host_skill_roots_skips_project_root_without_workspace() -> None:
    agent_root = Path("D:/tmp/test-home/agent-root")

    roots = resolve_host_skill_roots(
        repo_root=REPO_ROOT,
        host_id="opencode",
        agent_root=agent_root,
        workspace_root=None,
    )

    assert roots == (
        HostSkillRoot(
            host_id="opencode",
            root_key="host_global",
            path=Path("D:/tmp/test-home/.config/opencode/skills").resolve(),
            source="adapters/opencode/settings-map.json:semantics.vco.skill_root.global",
        ),
    )


def test_resolve_host_skill_roots_rejects_missing_host_settings_map() -> None:
    with pytest.raises(ValueError, match="Host id is not declared in adapters/index.json: unknown-host"):
        resolve_host_skill_roots(
            repo_root=REPO_ROOT,
            host_id="unknown-host",
            agent_root=Path("D:/tmp/test-home/.unknown"),
            workspace_root=None,
        )


def test_resolve_host_skill_roots_requires_settings_map(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    _write_adapter_index(repo_root, ["codex"])

    with pytest.raises(FileNotFoundError, match="Host settings map not found for codex"):
        resolve_host_skill_roots(
            repo_root=repo_root,
            host_id="codex",
            agent_root=tmp_path / ".agents",
            workspace_root=None,
        )


def test_resolve_host_skill_roots_requires_semantics_object(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    _write_adapter_index(repo_root, ["broken-host"])
    settings_map_path = _write_settings_map(
        repo_root,
        "broken-host",
        """{
  "adapter_id": "broken-host",
  "semantics": []
}""",
    )

    with pytest.raises(
        ValueError,
        match=(
            "Host settings map semantics must be an object for broken-host: "
            + str(settings_map_path.resolve()).replace("\\", "\\\\")
        ),
    ):
        resolve_host_skill_roots(
            repo_root=repo_root,
            host_id="broken-host",
            agent_root=tmp_path / "agent-root",
            workspace_root=None,
        )


def test_resolve_host_skill_roots_requires_declared_skill_root_key(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    _write_adapter_index(repo_root, ["missing-skill-root"])
    settings_map_path = _write_settings_map(
        repo_root,
        "missing-skill-root",
        """{
  "adapter_id": "missing-skill-root",
  "semantics": {
    "vco.command_root": "~/commands"
  }
}""",
    )

    with pytest.raises(
        ValueError,
        match=(
            "Host skill root semantic is missing for missing-skill-root. "
            "Expected one of: vco.skill_root.global, vco.skill_root. "
            "Settings map: "
            + str(settings_map_path.resolve()).replace("\\", "\\\\")
        ),
    ):
        resolve_host_skill_roots(
            repo_root=repo_root,
            host_id="missing-skill-root",
            agent_root=tmp_path / "agent-root",
            workspace_root=None,
        )


def test_resolve_host_skill_roots_rejects_non_string_semantic_value(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    _write_adapter_index(repo_root, ["bad-type-host"])
    settings_map_path = _write_settings_map(
        repo_root,
        "bad-type-host",
        """{
  "adapter_id": "bad-type-host",
  "semantics": {
    "vco.skill_root": 123
  }
}""",
    )

    with pytest.raises(
        ValueError,
        match=(
            "Host skill root semantic must be a non-empty string for bad-type-host "
            "\\(semantic key: vco.skill_root, settings map: "
            + str(settings_map_path.resolve()).replace("\\", "\\\\")
            + "\\)"
        ),
    ):
        resolve_host_skill_roots(
            repo_root=repo_root,
            host_id="bad-type-host",
            agent_root=tmp_path / "agent-root",
            workspace_root=None,
        )


def test_resolve_host_skill_roots_keeps_windows_absolute_path_as_is(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    _write_adapter_index(repo_root, ["abs-win-host"])
    _write_settings_map(
        repo_root,
        "abs-win-host",
        """{
  "adapter_id": "abs-win-host",
  "semantics": {
    "vco.skill_root": "C:/Vibe/Skills"
  }
}""",
    )

    roots = resolve_host_skill_roots(
        repo_root=repo_root,
        host_id="abs-win-host",
        agent_root=tmp_path / "agent-root",
        workspace_root=None,
    )

    assert roots[0].path == Path("C:/Vibe/Skills").resolve()


def test_resolve_host_skill_roots_keeps_posix_absolute_path_as_is(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    _write_adapter_index(repo_root, ["abs-posix-host"])
    _write_settings_map(
        repo_root,
        "abs-posix-host",
        """{
  "adapter_id": "abs-posix-host",
  "semantics": {
    "vco.skill_root": "/opt/vibe/skills"
  }
}""",
    )

    roots = resolve_host_skill_roots(
        repo_root=repo_root,
        host_id="abs-posix-host",
        agent_root=tmp_path / "agent-root",
        workspace_root=None,
    )

    assert roots[0].path == Path("/opt/vibe/skills").resolve()


def test_resolve_host_skill_roots_expands_tilde_from_agent_root_parent(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    _write_adapter_index(repo_root, ["tilde-host"])
    _write_settings_map(
        repo_root,
        "tilde-host",
        """{
  "adapter_id": "tilde-host",
  "semantics": {
    "vco.skill_root": "~/skills"
  }
}""",
    )
    agent_root = tmp_path / "nested" / "agent-root"

    roots = resolve_host_skill_roots(
        repo_root=repo_root,
        host_id="tilde-host",
        agent_root=agent_root,
        workspace_root=None,
    )

    assert roots[0].path == (agent_root.resolve().parent / "skills").resolve()


def test_resolve_host_skill_roots_requires_adapter_index(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    _write_settings_map(
        repo_root,
        "codex",
        """{
  "adapter_id": "codex",
  "semantics": {
    "vco.skill_root": "~/.agents/skills"
  }
}""",
    )

    with pytest.raises(FileNotFoundError, match="Adapter index not found:"):
        resolve_host_skill_roots(
            repo_root=repo_root,
            host_id="codex",
            agent_root=tmp_path / "agent-root",
            workspace_root=None,
        )


def test_resolve_host_skill_roots_allows_existing_host_outside_old_manual_list() -> None:
    agent_root = Path("D:/tmp/test-home/.openclaw")

    roots = resolve_host_skill_roots(
        repo_root=REPO_ROOT,
        host_id="openclaw",
        agent_root=agent_root,
        workspace_root=None,
    )

    assert roots == (
        HostSkillRoot(
            host_id="openclaw",
            root_key="host_global",
            path=(agent_root / "skills").resolve(),
            source="adapters/openclaw/settings-map.json:semantics.vco.skill_root",
        ),
    )
