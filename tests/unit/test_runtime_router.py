from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_SRC = ROOT / 'packages' / 'runtime-core' / 'src'
if str(RUNTIME_SRC) not in sys.path:
    sys.path.insert(0, str(RUNTIME_SRC))

from vgo_runtime.router import infer_task_type, load_allowed_vibe_entry_ids, route_runtime_task
from vgo_runtime.governance import choose_internal_grade


def test_runtime_router_allowed_entry_ids_match_shared_surface_contract() -> None:
    payload = json.loads((ROOT / 'config' / 'vibe-entry-surfaces.json').read_text(encoding='utf-8'))
    expected = frozenset(
        str(entry['id']).strip()
        for entry in payload['entries']
        if str(entry.get('id') or '').strip()
    )

    assert load_allowed_vibe_entry_ids() == expected


def test_router_script_frames_results_as_candidate_data_only() -> None:
    text = (ROOT / "scripts" / "router" / "resolve-pack-route.ps1").read_text(encoding="utf-8")

    assert "router_contract_mode = 'candidate_discovery_only'" in text
    assert "work_binding_truth_source = 'kernel'" in text
    assert "completion_language_allowed" not in text
    assert "work_binding truth" not in text


def test_runtime_router_rejects_entries_outside_shared_surface_contract() -> None:
    try:
        route_runtime_task('plan this change', requested_skill='vibe-xl')
    except ValueError:
        assert True
    else:
        raise AssertionError('expected unsupported entry id failure')


def test_runtime_router_uses_requested_entry_as_router_selection() -> None:
    route = route_runtime_task('implement the approved plan', requested_skill='vibe-do-it')

    assert route.requested_skill == 'vibe-do-it'
    assert route.router_selected_skill == 'vibe-do-it'
    assert route.runtime_selected_skill == 'vibe'


def test_runtime_router_prefers_planning_entry_for_architecture_prompt() -> None:
    route = route_runtime_task('design the architecture and write an implementation plan')

    assert route.router_selected_skill == 'vibe-how-do-we-do'
    assert route.runtime_selected_skill == 'vibe'


def test_runtime_router_prefers_upgrade_entry_for_upgrade_prompt() -> None:
    route = route_runtime_task('upgrade the local vibe runtime installation')

    assert route.router_selected_skill == 'vibe-upgrade'
    assert route.runtime_selected_skill == 'vibe'


def test_runtime_router_uses_kernel_plan_preference_for_runtime_refactor_prompt() -> None:
    route = route_runtime_task('design the runtime router refactor and write an implementation plan')

    assert route.router_selected_skill == 'vibe-how-do-we-do'
    assert route.task_type == 'planning'


def test_runtime_router_uses_kernel_resolved_task_type_for_plan_like_coding_prompt() -> None:
    route = route_runtime_task('need a plan')

    assert route.router_selected_skill == 'vibe-how-do-we-do'
    assert route.task_type == 'planning'


def test_runtime_router_respects_requested_planning_entry_for_task_type() -> None:
    route = route_runtime_task('implement the approved plan', requested_skill='vibe-how-do-we-do')

    assert route.router_selected_skill == 'vibe-how-do-we-do'
    assert route.task_type == 'planning'


def test_runtime_router_infers_debug_from_keyword_style_router_prompt() -> None:
    task = 'router confidence-low fallback misroute task-classification grade-selection candidate-scoring'

    assert infer_task_type(task) == 'debug'


def test_runtime_router_infers_debug_for_dispatch_triage_prompts() -> None:
    assert infer_task_type('triage runtime specialist dispatch duplication') == 'debug'
    assert infer_task_type('root cause specialist dispatch duplication') == 'debug'


def test_runtime_router_avoids_suffix_fix_false_positive_for_docs_cleanup() -> None:
    assert infer_task_type('suffix cleanup in docs') == 'planning'


def test_runtime_router_avoids_codex_code_false_positive_for_docs_copy() -> None:
    assert infer_task_type('codex bootstrap wording in docs') == 'planning'


def test_runtime_router_keeps_clinical_grade_selection_prompt_as_planning() -> None:
    assert infer_task_type('clinical decision support grade selection evidence profile') == 'planning'


def test_runtime_router_keeps_ml_pipeline_prompt_as_planning() -> None:
    assert infer_task_type('ml pipeline workflow pack artifacts for deployment') == 'planning'


def test_runtime_governance_promotes_keyword_style_router_prompt_to_l() -> None:
    task = 'router confidence-low fallback misroute task-classification grade-selection candidate-scoring'

    assert choose_internal_grade('planning', task=task) == 'L'


def test_runtime_governance_keeps_docs_cleanup_prompt_at_m() -> None:
    assert choose_internal_grade('planning', task='suffix cleanup in docs') == 'M'


def test_runtime_governance_keeps_codex_docs_prompt_at_m() -> None:
    assert choose_internal_grade('planning', task='codex bootstrap wording in docs') == 'M'


def test_runtime_governance_keeps_microwave_docs_prompt_at_m() -> None:
    assert choose_internal_grade('planning', task='microwave prompt examples for docs') == 'M'


def test_runtime_governance_preserves_prd_backlog_quality_gate_as_l() -> None:
    assert choose_internal_grade('planning', task='create PRD and backlog with quality gate') == 'L'


def test_runtime_governance_promotes_install_to_runtime_rollout_to_xl() -> None:
    task = 'cross-host install to runtime end-to-end verification workflow'

    assert choose_internal_grade('planning', task=task) == 'XL'
