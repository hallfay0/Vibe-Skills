from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
GOVERNANCE_DIR = REPO_ROOT / "docs" / "governance"


def read_doc(name: str) -> str:
    return (GOVERNANCE_DIR / name).read_text(encoding="utf-8")


def test_current_routing_contract_frames_route_chain_as_compatibility_only() -> None:
    text = read_doc("current-routing-contract.md")

    assert "This is not the start-here explanation of the system." in text
    assert "[`current-runtime-field-contract.md`](current-runtime-field-contract.md)" in text
    assert "You usually do not need this file unless a compatibility reader still exposes" in text
    assert "Default reading stop for most runs:" in text
    assert "task_card -> work_plan -> work_binding -> work_results -> verification" in text
    assert "Compatibility Follow-On Chain" in text
    assert (
        "skill_candidates -> skill_routing.selected -> skill_execution_lock -> "
        "selected_skill_execution -> "
        "skill_usage.used / skill_usage.unused"
    ) in text
    assert "This is not a workflow to follow." in text
    assert "`work_binding` stays the bounded-work truth." in text
    assert "`skill_execution_lock` | The approved-plan execution lock that preserves selected specialists across bounded re-entry. It is not a use claim." in text
    assert "If a normal run cannot be understood without this file, the work-first" in text
    assert "This is the only model current user-facing docs and generated runtime outputs should teach." not in text
    assert "skill_routing.selected -> skill_usage.used" not in text


def test_runtime_field_contract_puts_work_truth_before_compatibility_chain() -> None:
    text = read_doc("current-runtime-field-contract.md")

    assert "## Work-First Truth" in text
    assert "runtime input truth: work_binding + specialist_decision" in text
    assert "later work-loop truth: task_card -> work_plan -> work_binding -> work_results -> verification" in text
    assert "## Compatibility Mirrors" in text
    assert "`skill_execution_lock` records specialists that crossed the approved-plan boundary" in text
    assert "Do not treat route-era packet summaries as the main explanation of the system." in text


def test_governance_readme_points_to_work_truth_before_routing_history() -> None:
    text = read_doc("README.md")

    current_index = text.index("current runtime truth and routing compatibility contracts")
    current_fields_index = text.index(
        "[`current-runtime-field-contract.md`](current-runtime-field-contract.md)"
    )
    current_route_index = text.index("[`current-routing-contract.md`](current-routing-contract.md)")
    history_index = text.index(
        "[`historical-routing-terminology.md`](historical-routing-terminology.md)"
    )

    assert current_index < current_fields_index < current_route_index < history_index
    assert current_index < current_fields_index < history_index
    assert "specialist-dispatch-governance.md" not in text


def test_docs_root_readme_points_current_runtime_to_work_truth_contracts() -> None:
    text = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")

    current_runtime_index = text.index("## Current Runtime")
    current_runtime_section = text[current_runtime_index:].split("## Governance", 1)[0]

    runtime_protocol_index = current_runtime_section.index("[`../protocols/runtime.md`](../protocols/runtime.md)")
    field_contract_index = current_runtime_section.index(
        "[`governance/current-runtime-field-contract.md`](./governance/current-runtime-field-contract.md)"
    )
    routing_contract_index = current_runtime_section.index(
        "[`governance/current-routing-contract.md`](./governance/current-routing-contract.md)"
    )

    assert runtime_protocol_index < field_contract_index < routing_contract_index
    assert "[`governance/specialist-dispatch-governance.md`](./governance/specialist-dispatch-governance.md)" not in current_runtime_section


def test_docs_root_readme_keeps_delivery_acceptance_out_of_current_runtime_entrypoints() -> None:
    text = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")

    current_runtime_section = text[text.index("## Current Runtime"):].split("## Governance", 1)[0]
    governance_section = text[text.index("## Governance"):].split("## Cross-Layer Handoff", 1)[0]

    delivery_acceptance_link = (
        "[`governance/vibe-governed-project-delivery-acceptance-governance.md`]"
        "(./governance/vibe-governed-project-delivery-acceptance-governance.md)"
    )

    assert delivery_acceptance_link not in current_runtime_section
    assert delivery_acceptance_link in governance_section


def test_delivery_acceptance_governance_page_uses_work_first_truth_lead() -> None:
    text = read_doc("vibe-governed-project-delivery-acceptance-governance.md")

    assert "task_card -> work_plan -> work_binding -> work_results -> verification" in text
    assert "`work_binding`" in text
    assert (
        "skill_candidates -> skill_routing.selected -> selected_skill_execution -> skill_usage"
    ) not in text


def test_runtime_protocol_sets_work_truth_reading_order_before_routing_compatibility() -> None:
    text = (REPO_ROOT / "protocols" / "runtime.md").read_text(encoding="utf-8")

    assert "When you need to explain a run or inspect artifacts, use this reading order:" in text
    assert "start with `current-runtime-field-contract.md` plus the run's work artifacts" in text
    assert "for most normal runs, stop there and read the work truth" in text
    assert "read `current-routing-contract.md` only if you still need the compatibility selection or execution chain" in text
