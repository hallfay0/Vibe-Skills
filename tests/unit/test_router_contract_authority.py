from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_SRC = ROOT / "packages" / "runtime-core" / "src"
if str(RUNTIME_SRC) not in sys.path:
    sys.path.insert(0, str(RUNTIME_SRC))

from vgo_runtime.router_contract_runtime import choose_authoritative_route


def test_authoritative_route_uses_top_local_skill_row_without_pack_fallback() -> None:
    ranked = [
        {
            "pack_id": "local-skill-index",
            "candidate_source": "local_skill_index",
            "skill": "statistical-analysis",
            "selected_candidate": "statistical-analysis",
            "authority_rejection_reasons": [],
        }
    ]

    decision = choose_authoritative_route(
        ranked=ranked,
        task_type="research",
        requested_canonical=None,
        authority_policy={"global_safe_fallback_by_task": {"research": {"pack_id": "old-pack"}}},
    )

    assert decision["selected_pack_id"] == "local-skill-index"
    assert decision["selected_skill"] == "statistical-analysis"
    assert decision["selected_row"] == ranked[0]
    assert decision["fallback_applied"] is False
    assert decision["fallback_target_pack_id"] is None
    assert decision["rejected_specialist_reasons"] == []


def test_authoritative_route_does_not_select_blank_local_row() -> None:
    ranked = [
        {
            "pack_id": "local-skill-index",
            "candidate_source": "local_skill_index",
            "skill": "spreadsheet-cleanup",
            "selected_candidate": None,
            "authority_rejection_reasons": ["candidate_signal_below_local_threshold"],
        }
    ]

    decision = choose_authoritative_route(
        ranked=ranked,
        task_type="research",
        requested_canonical=None,
        authority_policy={},
    )

    assert decision["selected_pack_id"] == "local-skill-index"
    assert decision["selected_skill"] == "spreadsheet-cleanup"
    assert decision["selected_row"] == ranked[0]
    assert decision["fallback_applied"] is False
    assert decision["pre_fallback_top_pack_id"] == "local-skill-index"
    assert decision["rejected_specialist_reasons"] == ["candidate_signal_below_local_threshold"]


def test_authoritative_route_handles_empty_local_index() -> None:
    decision = choose_authoritative_route(
        ranked=[],
        task_type="planning",
        requested_canonical=None,
        authority_policy={},
    )

    assert decision == {
        "selected_pack_id": None,
        "selected_skill": None,
        "selected_row": None,
        "fallback_applied": False,
        "fallback_target_pack_id": None,
        "fallback_target_skill": None,
        "pre_fallback_top_pack_id": None,
        "pre_fallback_top_skill": None,
        "rejected_specialist_reasons": [],
    }
