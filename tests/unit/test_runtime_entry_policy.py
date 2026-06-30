from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_SRC = ROOT / "packages" / "runtime-core" / "src"
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
for src in (RUNTIME_SRC, CONTRACTS_SRC):
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))

from vgo_runtime.entry_policy import load_runtime_entry_surface, resolve_runtime_task_type, suggest_stage_stop


def test_runtime_entry_policy_uses_shared_discoverable_entry_surface() -> None:
    surface = load_runtime_entry_surface()

    assert surface.canonical_runtime_skill == "vibe"
    assert surface.entry_by_id["vibe-how-do-we-do"].requested_stage_stop == "xl_plan"


def test_runtime_entry_policy_resolves_planning_entries_to_planning() -> None:
    assert resolve_runtime_task_type("coding", requested_entry_id="vibe-what-do-i-want") == "planning"
    assert resolve_runtime_task_type("debug", requested_entry_id="vibe-how-do-we-do") == "planning"


def test_runtime_entry_policy_keeps_upgrade_entry_as_coding() -> None:
    assert resolve_runtime_task_type("planning", requested_entry_id="vibe-upgrade") == "coding"


def test_runtime_entry_policy_uses_shared_entry_surface_for_stage_stop() -> None:
    assert suggest_stage_stop("vibe-what-do-i-want") == "requirement_doc"
    assert suggest_stage_stop("vibe-how-do-we-do") == "xl_plan"
    assert suggest_stage_stop("vibe-do-it") == "phase_cleanup"
