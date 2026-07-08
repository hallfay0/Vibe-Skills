from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_SRC = ROOT / "packages" / "runtime-core" / "src"
if str(RUNTIME_SRC) not in sys.path:
    sys.path.insert(0, str(RUNTIME_SRC))

from vgo_runtime.governance import choose_internal_grade
from vgo_runtime.router import infer_task_type, load_allowed_vibe_entry_ids, route_runtime_task
import vgo_runtime.runtime_bridge as runtime_bridge


def test_runtime_router_allowed_entry_ids_match_shared_surface_contract() -> None:
    payload = json.loads((ROOT / "config" / "vibe-entry-surfaces.json").read_text(encoding="utf-8"))
    expected = frozenset(
        str(entry["id"]).strip()
        for entry in payload["entries"]
        if str(entry.get("id") or "").strip()
    )

    assert load_allowed_vibe_entry_ids() == expected


def test_runtime_bridge_prefers_python_owner_before_powershell_bridge(
    monkeypatch,
    capsys,
) -> None:
    recorded: dict[str, object] = {}

    monkeypatch.setattr(runtime_bridge, "resolve_powershell_host", lambda: "pwsh")

    def fake_route_prompt(**kwargs):
        recorded["route_prompt"] = kwargs
        return {"driver": "python-owner"}

    def fail_invoke(*args, **kwargs):
        raise AssertionError("powershell bridge should not own the happy path")

    monkeypatch.setattr(runtime_bridge, "route_prompt", fake_route_prompt)
    monkeypatch.setattr(runtime_bridge, "invoke_canonical_router", fail_invoke)

    exit_code = runtime_bridge.main(["--prompt", "plan this task"])

    assert exit_code == 0
    assert recorded["route_prompt"] == {
        "prompt": "plan this task",
        "grade": "M",
        "task_type": "planning",
        "requested_skill": None,
        "entry_intent_id": None,
        "requested_grade_floor": None,
        "target_root": None,
        "host_id": None,
        "repo_root": ROOT,
    }
    assert json.loads(capsys.readouterr().out) == {"driver": "python-owner"}


def test_runtime_bridge_uses_powershell_only_as_fallback_for_owner_failure(
    monkeypatch,
    capsys,
) -> None:
    recorded = {"route_prompt": 0, "bridge": 0}

    monkeypatch.setattr(runtime_bridge, "resolve_powershell_host", lambda: "pwsh")

    def fail_route_prompt(**kwargs):
        recorded["route_prompt"] += 1
        raise RuntimeError("python owner failed")

    def fake_invoke(args, shell):
        recorded["bridge"] += 1
        assert shell == "pwsh"
        assert args.prompt == "route with fallback"
        return {"driver": "powershell-fallback"}

    monkeypatch.setattr(runtime_bridge, "route_prompt", fail_route_prompt)
    monkeypatch.setattr(runtime_bridge, "invoke_canonical_router", fake_invoke)

    exit_code = runtime_bridge.main(["--prompt", "route with fallback"])

    assert exit_code == 0
    assert recorded == {"route_prompt": 1, "bridge": 1}
    assert json.loads(capsys.readouterr().out) == {"driver": "powershell-fallback"}


def test_runtime_router_rejects_entries_outside_shared_surface_contract() -> None:
    try:
        route_runtime_task("plan this change", requested_skill="vibe-xl")
    except ValueError:
        assert True
    else:
        raise AssertionError("expected unsupported entry id failure")


def test_requested_execution_entry_is_router_selection_but_runtime_stays_canonical() -> None:
    route = route_runtime_task("implement the approved plan", requested_skill="vibe-do-it")

    assert route.requested_skill == "vibe-do-it"
    assert route.router_selected_skill == "vibe-do-it"
    assert route.runtime_selected_skill == "vibe"


def test_requested_planning_entry_forces_planning_route() -> None:
    route = route_runtime_task("implement the approved plan", requested_skill="vibe-how-do-we-do")

    assert route.router_selected_skill == "vibe-how-do-we-do"
    assert route.runtime_selected_skill == "vibe"
    assert route.task_type == "planning"


def test_planning_prompt_prefers_planning_entry() -> None:
    route = route_runtime_task("design the architecture and write an implementation plan")

    assert route.router_selected_skill == "vibe-how-do-we-do"
    assert route.runtime_selected_skill == "vibe"


def test_upgrade_prompt_prefers_upgrade_entry() -> None:
    route = route_runtime_task("upgrade the local vibe runtime installation")

    assert route.router_selected_skill == "vibe-upgrade"
    assert route.runtime_selected_skill == "vibe"


def test_docs_cleanup_prompts_stay_small_planning_work() -> None:
    for prompt in ("suffix cleanup in docs", "codex bootstrap wording in docs"):
        assert infer_task_type(prompt) == "planning"
        assert choose_internal_grade("planning", task=prompt) == "M"


def test_router_debug_prompt_resolves_to_debug_at_l() -> None:
    task = "router confidence-low fallback misroute task-classification grade-selection candidate-scoring"

    assert infer_task_type(task) == "debug"
    assert choose_internal_grade("planning", task=task) == "L"


def test_install_rollout_prompt_resolves_to_xl() -> None:
    task = "cross-host install to runtime end-to-end verification workflow"

    assert choose_internal_grade("planning", task=task) == "XL"
