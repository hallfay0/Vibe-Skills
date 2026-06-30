from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


GLOBAL_SKILL_ROOT_KEYS = ("vco.skill_roots.global", "vco.skill_root.global", "vco.skill_root")
PROJECT_SKILL_ROOT_KEYS = ("vco.skill_roots.project", "vco.skill_root.project")


@dataclass(frozen=True, slots=True)
class HostSkillRoot:
    host_id: str
    root_key: str
    path: Path
    source: str


def _normalize_host_id(host_id: str) -> str:
    return str(host_id or "").strip().lower()


def _adapter_index_path(repo_root: Path) -> Path:
    return repo_root.resolve() / "adapters" / "index.json"


def _load_declared_host_ids(repo_root: Path) -> frozenset[str]:
    index_path = _adapter_index_path(repo_root)
    if not index_path.is_file():
        raise FileNotFoundError(f"Adapter index not found: {index_path}")

    payload = json.loads(index_path.read_text(encoding="utf-8"))
    adapters = payload.get("adapters")
    if not isinstance(adapters, list):
        raise ValueError(f"Adapter index adapters must be a list: {index_path}")

    declared_host_ids: set[str] = set()
    for entry in adapters:
        if not isinstance(entry, dict):
            continue
        normalized = _normalize_host_id(entry.get("id"))
        if normalized:
            declared_host_ids.add(normalized)
    return frozenset(declared_host_ids)


def _validate_declared_host(repo_root: Path, host_id: str) -> str:
    normalized_host_id = _normalize_host_id(host_id)
    if not normalized_host_id:
        raise ValueError("Host id is required for host skill root resolution")
    if normalized_host_id not in _load_declared_host_ids(repo_root):
        raise ValueError(f"Host id is not declared in adapters/index.json: {normalized_host_id}")
    return normalized_host_id


def _settings_map_path(repo_root: Path, host_id: str) -> Path:
    return repo_root.resolve() / "adapters" / host_id / "settings-map.json"


def _load_semantics(repo_root: Path, host_id: str) -> tuple[Path, dict[str, object]]:
    settings_map_path = _settings_map_path(repo_root, host_id)
    if not settings_map_path.is_file():
        raise FileNotFoundError(f"Host settings map not found for {host_id}: {settings_map_path}")

    payload = json.loads(settings_map_path.read_text(encoding="utf-8"))
    semantics = payload.get("semantics")
    if not isinstance(semantics, dict):
        raise ValueError(f"Host settings map semantics must be an object for {host_id}: {settings_map_path}")
    return settings_map_path, semantics


def _validate_semantic_string(*, host_id: str, semantic_key: str, settings_map_path: Path, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            "Host skill root semantic must be a non-empty string for "
            f"{host_id} (semantic key: {semantic_key}, settings map: {settings_map_path})"
        )
    return value.strip()


def _validate_semantic_string_list(*, host_id: str, semantic_key: str, settings_map_path: Path, value: object) -> list[str]:
    if semantic_key.endswith("s.global") or semantic_key.endswith("s.project"):
        if not isinstance(value, list) or not value:
            raise ValueError(
                "Host skill roots semantic must be a non-empty list for "
                f"{host_id} (semantic key: {semantic_key}, settings map: {settings_map_path})"
            )
        roots = [
            _validate_semantic_string(
                host_id=host_id,
                semantic_key=semantic_key,
                settings_map_path=settings_map_path,
                value=item,
            )
            for item in value
        ]
    else:
        roots = [
            _validate_semantic_string(
                host_id=host_id,
                semantic_key=semantic_key,
                settings_map_path=settings_map_path,
                value=value,
            )
        ]
    seen: set[str] = set()
    ordered: list[str] = []
    for root in roots:
        key = root.casefold()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(root)
    return ordered


def _pick_semantic(
    *,
    host_id: str,
    semantics: dict[str, object],
    settings_map_path: Path,
    keys: tuple[str, ...],
) -> tuple[str, list[str]] | None:
    for key in keys:
        if key not in semantics:
            continue
        return key, _validate_semantic_string_list(
            host_id=host_id,
            semantic_key=key,
            settings_map_path=settings_map_path,
            value=semantics[key],
        )
    return None


def _is_absolute_path(raw_path: str) -> bool:
    if raw_path.startswith(("/", "\\")):
        return True
    return len(raw_path) >= 3 and raw_path[1] == ":" and raw_path[2] in {"/", "\\"}


def _expand_from_home(agent_root: Path, raw_path: str) -> Path:
    # `~` is resolved from the synthetic host-home anchor represented by `agent_root.parent`.
    # This keeps tests and local-kernel callers deterministic without depending on the machine user profile.
    home_root = agent_root.resolve().parent
    suffix = raw_path[1:].lstrip("/\\")
    if not suffix:
        return home_root.resolve()
    return (home_root / Path(suffix.replace("\\", "/"))).resolve()


def _expand_root_path(
    raw_path: str,
    *,
    agent_root: Path,
    workspace_root: Path | None,
) -> Path:
    text = str(raw_path or "").strip()
    if text == "~" or text.startswith("~/") or text.startswith("~\\"):
        return _expand_from_home(agent_root, text)
    if _is_absolute_path(text):
        return Path(text).resolve()

    base_root = workspace_root.resolve() if workspace_root is not None else agent_root.resolve()
    return (base_root / Path(text.replace("\\", "/"))).resolve()


def _source_text(repo_root: Path, settings_map_path: Path, semantic_key: str) -> str:
    relative_settings_map = settings_map_path.resolve().relative_to(repo_root.resolve()).as_posix()
    return f"{relative_settings_map}:semantics.{semantic_key}"


def resolve_host_skill_roots(
    *,
    repo_root: Path,
    host_id: str,
    agent_root: Path,
    workspace_root: Path | None,
) -> tuple[HostSkillRoot, ...]:
    normalized_host_id = _validate_declared_host(repo_root, host_id)
    settings_map_path, semantics = _load_semantics(repo_root, normalized_host_id)

    roots: list[HostSkillRoot] = []
    global_root = _pick_semantic(
        host_id=normalized_host_id,
        semantics=semantics,
        settings_map_path=settings_map_path,
        keys=GLOBAL_SKILL_ROOT_KEYS,
    )
    if global_root is None:
        expected_keys = ", ".join(GLOBAL_SKILL_ROOT_KEYS)
        raise ValueError(
            "Host skill root semantic is missing for "
            f"{normalized_host_id}. Expected one of: {expected_keys}. Settings map: {settings_map_path}"
        )

    global_key, global_values = global_root
    for global_value in global_values:
        roots.append(
            HostSkillRoot(
                host_id=normalized_host_id,
                root_key="host_global",
                path=_expand_root_path(global_value, agent_root=agent_root, workspace_root=None),
                source=_source_text(repo_root, settings_map_path, global_key),
            )
        )

    project_root = _pick_semantic(
        host_id=normalized_host_id,
        semantics=semantics,
        settings_map_path=settings_map_path,
        keys=PROJECT_SKILL_ROOT_KEYS,
    )
    if project_root is not None and workspace_root is not None:
        project_key, project_values = project_root
        for project_value in project_values:
            roots.append(
                HostSkillRoot(
                    host_id=normalized_host_id,
                    root_key="host_project",
                    path=_expand_root_path(project_value, agent_root=agent_root, workspace_root=workspace_root),
                    source=_source_text(repo_root, settings_map_path, project_key),
                )
            )

    return tuple(roots)
