from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / 'packages' / 'runtime-core' / 'src' / 'vgo_runtime' / 'runtime_support.py'


def _load_module():
    spec = importlib.util.spec_from_file_location('router_contract_support_unit', MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'unable to load module from {MODULE_PATH}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_skill(path: Path, name: str, description: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n",
        encoding='utf-8',
    )
    return path


def _write_runtime_core_packaging(repo_root: Path) -> None:
    config_root = repo_root / 'config'
    config_root.mkdir(parents=True, exist_ok=True)
    (config_root / 'runtime-core-packaging.json').write_text(
        json.dumps(
            {
                'public_skill_surface': {
                    'mode': 'discoverable_wrapper_projection',
                    'canonical_entrypoint_relpath': 'skills/vibe',
                    'root_relpath': 'skills',
                    'discoverable_entry_surface': 'config/vibe-entry-surfaces.json',
                    'projected_skill_names': ['vibe'],
                },
                'internal_skill_corpus': {
                    'enabled': False,
                    'resident_skill_names': [],
                    'resolver_roots': [],
                },
                'compatibility_skill_projections': {
                    'resolver_roots': ['skills'],
                },
            },
            ensure_ascii=False,
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )


def _write_adapter_settings(repo_root: Path) -> None:
    adapters_root = repo_root / 'adapters'
    adapters_root.mkdir(parents=True, exist_ok=True)
    (adapters_root / 'index.json').write_text(
        json.dumps({'schema_version': 1, 'adapters': [{'id': 'codex'}]}, indent=2) + '\n',
        encoding='utf-8',
    )
    settings_map = adapters_root / 'codex' / 'settings-map.json'
    settings_map.parent.mkdir(parents=True, exist_ok=True)
    settings_map.write_text(
        json.dumps(
            {
                'adapter_id': 'codex',
                'semantics': {
                    'vco.skill_roots.global': ['~/.agents/skills', '~/.codex/skills'],
                },
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )


def test_resolver_prefers_first_host_declared_local_root(tmp_path: Path) -> None:
    module = _load_module()
    repo_root = tmp_path / 'repo'
    target_root = tmp_path / 'home' / '.agents'
    _write_runtime_core_packaging(repo_root)
    _write_adapter_settings(repo_root)

    agents_skill = _write_skill(
        tmp_path / 'home' / '.agents' / 'skills' / 'skill-alpha' / 'SKILL.md',
        'skill-alpha',
        'agents root',
    )
    _write_skill(
        tmp_path / 'home' / '.codex' / 'skills' / 'skill-alpha' / 'SKILL.md',
        'skill-alpha',
        'codex root',
    )

    repo = module.RepoContext(
        repo_root=repo_root,
        config_root=repo_root / 'config',
        bundled_skills_root=repo_root / 'bundled' / 'skills',
    )
    resolved = module.resolve_skill_md_path(repo, 'skill-alpha', str(target_root))
    assert resolved == agents_skill

    descriptor = module.read_skill_descriptor(repo, 'skill-alpha', str(target_root))
    assert descriptor['skill_md_path'] == str(resolved)
    assert descriptor['description'] == 'agents root'

    public_surface = module.resolve_public_skill_surface(repo)
    assert public_surface['discoverable_entry_surface'] == 'config/vibe-entry-surfaces.json'
    assert public_surface['projected_skill_names'] == ['vibe']


def test_resolver_uses_custom_subdirectory_under_host_root(tmp_path: Path) -> None:
    module = _load_module()
    repo_root = tmp_path / 'repo'
    target_root = tmp_path / 'home' / '.agents'
    _write_runtime_core_packaging(repo_root)
    _write_adapter_settings(repo_root)

    custom_skill = _write_skill(
        tmp_path / 'home' / '.agents' / 'skills' / 'custom' / 'skill-beta' / 'SKILL.md',
        'skill-beta',
        'custom local skill',
    )
    repo = module.RepoContext(
        repo_root=repo_root,
        config_root=repo_root / 'config',
        bundled_skills_root=repo_root / 'bundled' / 'skills',
    )

    resolved = module.resolve_skill_md_path(repo, 'skill-beta', str(target_root))
    assert resolved == custom_skill

    descriptor = module.read_skill_descriptor(repo, 'skill-beta', str(target_root))
    assert descriptor['skill_md_path'] == str(custom_skill)
    assert descriptor['description'] == 'custom local skill'

    public_surface = module.resolve_public_skill_surface(repo)
    assert public_surface['discoverable_entry_surface'] == 'config/vibe-entry-surfaces.json'
    assert public_surface['projected_skill_names'] == ['vibe']


def test_resolver_keeps_legacy_installed_skill_fallback_when_split_semantics_available(tmp_path: Path) -> None:
    module = _load_module()
    repo_root = tmp_path / 'repo'
    target_root = tmp_path / 'home' / '.agents'
    _write_runtime_core_packaging(repo_root)
    _write_adapter_settings(repo_root)

    installed_public = _write_skill(
        tmp_path / 'home' / '.agents' / 'skills' / 'legacy-skill' / 'SKILL.md',
        'legacy-skill',
        'local installed skill',
    )
    repo = module.RepoContext(
        repo_root=repo_root,
        config_root=repo_root / 'config',
        bundled_skills_root=repo_root / 'bundled' / 'skills',
    )

    resolved = module.resolve_skill_md_path(repo, 'legacy-skill', str(target_root))
    assert resolved == installed_public
