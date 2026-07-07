from __future__ import annotations

from dataclasses import dataclass, asdict
from functools import lru_cache
from pathlib import Path

from .planning import KernelPlanningResult, build_kernel_plan
from .route_index import load_runtime_route_index as load_shared_runtime_route_index
from .runtime_support import load_json, resolve_repo_root
from .task_intent import infer_task_type


@dataclass(frozen=True, slots=True)
class RuntimeRoute:
    requested_skill: str | None
    router_selected_skill: str
    runtime_selected_skill: str
    task_type: str
    confirm_required: bool = False

    def model_dump(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RuntimeRouteDecision:
    route: RuntimeRoute
    kernel_plan: KernelPlanningResult


@lru_cache(maxsize=1)
def load_allowed_vibe_entry_ids() -> frozenset[str]:
    repo_root = resolve_repo_root(Path(__file__))
    payload = load_json(repo_root / 'config' / 'vibe-entry-surfaces.json')
    entries = payload.get('entries') or []
    allowed = frozenset(
        str(entry.get('id') or '').strip()
        for entry in entries
        if str(entry.get('id') or '').strip()
    )
    if not allowed:
        raise RuntimeError('config/vibe-entry-surfaces.json does not define any discoverable vibe entry ids')
    return allowed


@lru_cache(maxsize=1)
def load_canonical_vibe_entry_id() -> str:
    repo_root = resolve_repo_root(Path(__file__))
    payload = load_json(repo_root / 'config' / 'vibe-entry-surfaces.json')
    canonical = str(payload.get('canonical_runtime_skill') or 'vibe').strip() or 'vibe'
    return canonical

def load_runtime_route_index() -> dict[str, object]:
    return load_shared_runtime_route_index()


def resolve_runtime_route_decision(task: str, requested_skill: str | None = None) -> RuntimeRouteDecision:
    requested_entry = str(requested_skill or '').strip() or None
    if requested_entry and requested_entry not in load_allowed_vibe_entry_ids():
        raise ValueError(f'unsupported vibe entry id: {requested_skill}')
    canonical_skill = load_canonical_vibe_entry_id()
    if requested_entry:
        kernel_plan = build_kernel_plan(task=task, requested_entry_id=requested_entry)
        route = RuntimeRoute(
            requested_skill=requested_entry,
            router_selected_skill=requested_entry,
            runtime_selected_skill=canonical_skill,
            task_type=kernel_plan.resolved_task_type,
        )
        return RuntimeRouteDecision(route=route, kernel_plan=kernel_plan)

    kernel_plan = build_kernel_plan(task=task)
    route = RuntimeRoute(
        requested_skill=None,
        router_selected_skill=kernel_plan.preferred_skill or canonical_skill,
        runtime_selected_skill=canonical_skill,
        task_type=kernel_plan.resolved_task_type,
    )
    return RuntimeRouteDecision(route=route, kernel_plan=kernel_plan)


def route_runtime_task(task: str, requested_skill: str | None = None) -> RuntimeRoute:
    return resolve_runtime_route_decision(task, requested_skill=requested_skill).route
