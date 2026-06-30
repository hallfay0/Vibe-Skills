from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from .host_skill_roots import resolve_host_skill_roots
from .skill_manifest import parse_skill_manifest


INDEX_VERSION = 1
DISCOVERY_ROOTS = ("skills/local", "skills/starter")
LOCAL_SOURCE_KIND = "local"
HOST_EXTERNAL_SOURCE_KIND = "host_external"
STARTER_SOURCE_KIND = "starter"
VIBE_RELATIVE_PATH_CONTRACT = "vibe_relative"
SOURCE_ROOT_RELATIVE_PATH_CONTRACT = "source_root_relative"
SOURCE_PRIORITY = {
    LOCAL_SOURCE_KIND: 0,
    HOST_EXTERNAL_SOURCE_KIND: 1,
    STARTER_SOURCE_KIND: 2,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _vibe_root(agent_root: Path) -> Path:
    return agent_root.resolve() / "vibe"


def _ensure_runtime_dirs(agent_root: Path) -> Path:
    vibe_root = _vibe_root(agent_root)
    for relative_dir in ("skills/local", "skills/starter", "generated", "runs"):
        (vibe_root / relative_dir).mkdir(parents=True, exist_ok=True)
    return vibe_root


def _discover_relative_skill_files(vibe_root: Path, relative_root: str) -> list[Path]:
    return sorted(path.resolve() for path in (vibe_root / relative_root).glob("*/SKILL.md"))


def discover_skill_files(agent_root: Path) -> list[Path]:
    vibe_root = _ensure_runtime_dirs(agent_root)
    discovered: list[Path] = []
    for relative_root in DISCOVERY_ROOTS:
        discovered.extend(_discover_relative_skill_files(vibe_root, relative_root))
    return discovered


def _public_source_root(source_spec: dict[str, object]) -> dict[str, object]:
    return {
        "source_kind": source_spec["source_kind"],
        "source_root": source_spec["source_root"],
        "resolved_source_root": source_spec["resolved_source_root"],
        "source_priority": source_spec["source_priority"],
        "source_order": source_spec["source_order"],
    }


def _unique_ordered(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _build_source_specs(vibe_root: Path, host_roots: tuple[Path, ...]) -> list[dict[str, object]]:
    source_specs: list[dict[str, object]] = []

    source_specs.append(
        {
            "source_kind": LOCAL_SOURCE_KIND,
            "source_root": "skills/local",
            "resolved_source_root": str((vibe_root / "skills" / "local").resolve()),
            "source_priority": SOURCE_PRIORITY[LOCAL_SOURCE_KIND],
            "source_order": 0,
            "path_contract": VIBE_RELATIVE_PATH_CONTRACT,
            "path_base": str(vibe_root.resolve()),
        }
    )

    for index, host_root in enumerate(host_roots, start=1):
        resolved_host_root = host_root.resolve()
        source_specs.append(
            {
                "source_kind": HOST_EXTERNAL_SOURCE_KIND,
                "source_root": str(resolved_host_root),
                "resolved_source_root": str(resolved_host_root),
                "source_priority": SOURCE_PRIORITY[HOST_EXTERNAL_SOURCE_KIND],
                "source_order": index,
                "path_contract": SOURCE_ROOT_RELATIVE_PATH_CONTRACT,
                "path_base": str(resolved_host_root),
            }
        )

    source_specs.append(
        {
            "source_kind": STARTER_SOURCE_KIND,
            "source_root": "skills/starter",
            "resolved_source_root": str((vibe_root / "skills" / "starter").resolve()),
            "source_priority": SOURCE_PRIORITY[STARTER_SOURCE_KIND],
            "source_order": len(source_specs),
            "path_contract": VIBE_RELATIVE_PATH_CONTRACT,
            "path_base": str(vibe_root.resolve()),
        }
    )
    return source_specs


def _discover_skill_files_for_source(source_spec: dict[str, object]) -> list[Path]:
    return sorted(Path(str(source_spec["resolved_source_root"])).glob("*/SKILL.md"))


def _build_entry_paths(
    *,
    vibe_root: Path,
    source_spec: dict[str, object],
    manifest_root_dir: str,
    manifest_skill_file: str,
) -> tuple[str, str]:
    root_dir = Path(manifest_root_dir).resolve()
    skill_file = Path(manifest_skill_file).resolve()
    if str(source_spec["path_contract"]) == SOURCE_ROOT_RELATIVE_PATH_CONTRACT:
        source_root = Path(str(source_spec["resolved_source_root"]))
        return (
            root_dir.relative_to(source_root).as_posix(),
            skill_file.relative_to(source_root).as_posix(),
        )
    return (
        root_dir.relative_to(vibe_root).as_posix(),
        skill_file.relative_to(vibe_root).as_posix(),
    )


def _build_catalog_entry(
    *,
    vibe_root: Path,
    skill_file: Path,
    source_spec: dict[str, object],
) -> dict[str, object]:
    manifest = parse_skill_manifest(skill_file)
    root_dir, skill_file_value = _build_entry_paths(
        vibe_root=vibe_root,
        source_spec=source_spec,
        manifest_root_dir=manifest.root_dir,
        manifest_skill_file=manifest.skill_file,
    )
    return {
        "id": manifest.id,
        "name": manifest.name,
        "description": manifest.description,
        "when_to_use": list(manifest.when_to_use),
        "not_for": list(manifest.not_for),
        "outputs": list(manifest.outputs),
        "tags": list(manifest.tags),
        "enabled": manifest.enabled,
        "priority": manifest.priority,
        "root_dir": root_dir,
        "skill_file": skill_file_value,
        "resolved_root_dir": str(Path(manifest.root_dir).resolve()),
        "resolved_skill_file": str(Path(manifest.skill_file).resolve()),
        "path_contract": source_spec["path_contract"],
        "path_base": source_spec["path_base"],
        "source_kind": source_spec["source_kind"],
        "source_root": source_spec["source_root"],
        "resolved_source_root": source_spec["resolved_source_root"],
        "source_priority": source_spec["source_priority"],
        "source_order": source_spec["source_order"],
        "active": False,
    }


def _load_source_entries(vibe_root: Path, source_spec: dict[str, object]) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    seen_ids: dict[str, Path] = {}
    for skill_file in _discover_skill_files_for_source(source_spec):
        entry = _build_catalog_entry(
            vibe_root=vibe_root,
            skill_file=skill_file,
            source_spec=source_spec,
        )
        skill_id = str(entry["id"])
        if skill_id in seen_ids:
            raise ValueError(
                f"duplicate skill id {skill_id!r} within {source_spec['source_kind']} source root "
                f"{source_spec['source_root']!r}: {seen_ids[skill_id]} and {skill_file.resolve()}"
            )
        seen_ids[skill_id] = skill_file.resolve()
        entries.append(entry)
    return entries


def build_skill_catalog(*, agent_root: Path, host_roots: tuple[Path, ...] = ()) -> dict[str, object]:
    vibe_root = _ensure_runtime_dirs(agent_root)
    source_specs = _build_source_specs(vibe_root, host_roots)
    entries: list[dict[str, object]] = []
    active_ids: set[str] = set()

    for source_spec in source_specs:
        for entry in _load_source_entries(vibe_root, source_spec):
            skill_id = str(entry["id"])
            if skill_id not in active_ids:
                entry["active"] = True
                active_ids.add(skill_id)
            entries.append(entry)

    active_source_roots = [
        _public_source_root(source_spec)
        for source_spec in source_specs
        if any(
            entry["active"]
            and entry["source_kind"] == source_spec["source_kind"]
            and entry["source_root"] == source_spec["source_root"]
            for entry in entries
        )
    ]

    return {
        "version": INDEX_VERSION,
        "generated_at": _utc_now(),
        "roots": list(DISCOVERY_ROOTS),
        "host_roots": [str(path.resolve()) for path in host_roots],
        "catalog_source_kinds": _unique_ordered(
            [str(source_spec["source_kind"]) for source_spec in source_specs]
        ),
        "catalog_source_roots": [_public_source_root(source_spec) for source_spec in source_specs],
        "active_source_kinds": _unique_ordered(
            [str(source_root["source_kind"]) for source_root in active_source_roots]
        ),
        "active_source_roots": active_source_roots,
        "entries": entries,
    }


def _build_skill_index_payload(catalog: dict[str, object]) -> dict[str, object]:
    entries = [entry for entry in catalog["entries"] if entry["active"]]
    return {
        "version": INDEX_VERSION,
        "generated_at": catalog["generated_at"],
        "roots": list(DISCOVERY_ROOTS),
        "catalog_source_kinds": list(catalog["catalog_source_kinds"]),
        "catalog_source_roots": list(catalog["catalog_source_roots"]),
        "active_source_kinds": list(catalog["active_source_kinds"]),
        "active_source_roots": list(catalog["active_source_roots"]),
        "skills": entries,
    }


def build_skill_index_from_catalog(catalog: dict[str, object]) -> dict[str, object]:
    return _build_skill_index_payload(catalog)


def build_skill_index(agent_root: Path, *, host_roots: tuple[Path, ...] = ()) -> dict[str, object]:
    catalog = build_skill_catalog(agent_root=agent_root, host_roots=host_roots)
    return build_skill_index_from_catalog(catalog)


def write_skill_catalog(agent_root: Path, payload: dict[str, object]) -> Path:
    vibe_root = _ensure_runtime_dirs(agent_root)
    catalog_path = vibe_root / "generated" / "skills-catalog.json"
    catalog_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return catalog_path


def write_skill_index(agent_root: Path, payload: dict[str, object]) -> Path:
    vibe_root = _ensure_runtime_dirs(agent_root)
    index_path = vibe_root / "generated" / "skills-index.json"
    index_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return index_path


def load_skill_index(agent_root: Path) -> dict[str, object]:
    index_path = _vibe_root(agent_root) / "generated" / "skills-index.json"
    return json.loads(index_path.read_text(encoding="utf-8"))


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-root", required=True)
    parser.add_argument("--host-id")
    parser.add_argument("--workspace-root")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    agent_root = Path(args.agent_root).resolve()
    workspace_root = Path(args.workspace_root).resolve() if args.workspace_root else None
    host_roots = ()
    if args.host_id:
        host_roots = tuple(
            root.path
            for root in resolve_host_skill_roots(
                repo_root=_repo_root(),
                host_id=args.host_id,
                agent_root=agent_root,
                workspace_root=workspace_root,
            )
        )
    catalog = build_skill_catalog(agent_root=agent_root, host_roots=host_roots)
    catalog_path = write_skill_catalog(agent_root, catalog)
    payload = build_skill_index_from_catalog(catalog)
    index_path = write_skill_index(agent_root, payload)
    result = {
        "agent_root": str(agent_root),
        "host_id": str(args.host_id).strip().lower() if args.host_id else None,
        "workspace_root": str(workspace_root) if workspace_root is not None else None,
        "host_roots": [str(path) for path in host_roots],
        "catalog_path": str(catalog_path),
        "catalog_count": len(catalog["entries"]),
        "index_path": str(index_path),
        "skill_count": len(payload["skills"]),
        "skills": payload["skills"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0
