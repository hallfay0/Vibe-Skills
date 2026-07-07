from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tempfile

from vgo_contracts.runtime_packet import RuntimePacket

from .governance import build_governance_profile
from .execution_snapshot import KernelExecutionSnapshot
from .kernel.executor import execute_work_unit
from .kernel.verifier import verify_run
from .memory import build_memory_policy
from .planning import build_execution_plan
from .router import RuntimeRoute, resolve_runtime_route_decision
from .stage_machine import RuntimeStageMachine
from .stage_stop import resolve_stage_stop


@dataclass(frozen=True, slots=True)
class RuntimeExecutionResult:
    final_packet: RuntimePacket
    stage_receipts: list[dict[str, object]]
    mode: str
    snapshot: dict[str, object]
    route: dict[str, object]
    plan: dict[str, object]
    memory: dict[str, object]


def build_runtime_route_view(
    route: RuntimeRoute,
    *,
    packet: RuntimePacket,
    requested_skill: str | None,
) -> dict[str, object]:
    payload = route.model_dump()
    if requested_skill is None and packet.entry_intent_id:
        payload["requested_skill"] = packet.entry_intent_id
        payload["router_selected_skill"] = route.runtime_selected_skill
    return payload


def execute_runtime_packet(
    packet: RuntimePacket,
    *,
    mode: str | None = None,
    requested_skill: str | None = None,
    stage_machine: RuntimeStageMachine | None = None,
) -> RuntimeExecutionResult:
    machine = stage_machine or RuntimeStageMachine()
    governance = build_governance_profile(mode)
    effective_requested_skill = requested_skill or packet.entry_intent_id
    route_decision = resolve_runtime_route_decision(packet.goal, requested_skill=effective_requested_skill)
    route = route_decision.route
    kernel_plan = route_decision.kernel_plan
    stage_stop = resolve_stage_stop(
        packet.requested_stage_stop,
        kernel_plan.suggested_stage_stop,
        default_source='kernel_suggested',
    )
    executed_stages = machine.iter_between(packet.stage, stage_stop.effective_requested_stage_stop)
    runtime_work_root = Path(tempfile.mkdtemp(prefix="vgo-runtime-execution-"))
    work_results = tuple(
        execute_work_unit(
            runtime_work_root,
            kernel_plan.task_card,
            work_unit,
            work_root=runtime_work_root / "work-units" / work_unit.id,
        )
        for work_unit in kernel_plan.work_plan.work_units
    )
    verification = verify_run(kernel_plan.task_card, kernel_plan.work_plan, work_results)
    plan = build_execution_plan(
        stages=executed_stages,
        requested_grade_floor=packet.requested_grade_floor,
        kernel_plan=kernel_plan,
        stage_stop_decision=stage_stop,
    )
    terminal_stage = executed_stages[-1] if executed_stages else packet.stage
    snapshot = KernelExecutionSnapshot(
        planning=kernel_plan,
        effective_requested_stage_stop=stage_stop.effective_requested_stage_stop,
        stage_stop_source=stage_stop.stage_stop_source,
        executed_stages=executed_stages,
        work_results=work_results,
        verification=verification,
        terminal_stage=terminal_stage,
    )
    memory = build_memory_policy(len(executed_stages))
    route_view = build_runtime_route_view(route, packet=packet, requested_skill=requested_skill)
    plan_view = plan.model_dump()
    plan_view.pop("kernel", None)
    snapshot_payload = snapshot.model_dump()
    stage_receipts = snapshot.stage_receipts_payload()
    final_packet = RuntimePacket(
        goal=packet.goal,
        stage=terminal_stage,
        entry_intent_id=packet.entry_intent_id,
        requested_stage_stop=packet.requested_stage_stop,
        requested_grade_floor=packet.requested_grade_floor,
    )

    return RuntimeExecutionResult(
        final_packet=final_packet,
        stage_receipts=stage_receipts,
        mode=governance.mode,
        snapshot=snapshot_payload,
        route=route_view,
        plan=plan_view,
        memory=memory.model_dump(),
    )
