from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .planning import KernelPlanningResult


@dataclass(frozen=True, slots=True)
class KernelExecutionSnapshot:
    planning: KernelPlanningResult
    effective_requested_stage_stop: str
    stage_stop_source: str
    executed_stages: tuple[str, ...]
    work_results: tuple[Any, ...]
    verification: Any
    terminal_stage: str

    def model_dump(self) -> dict[str, object]:
        return {
            "task_card": self.planning.task_card.model_dump(),
            "candidates": [candidate.model_dump() for candidate in self.planning.candidates],
            "work_plan": self.planning.work_plan.model_dump(),
            "work_binding": self.planning.work_binding.model_dump(),
            "effective_requested_stage_stop": self.effective_requested_stage_stop,
            "stage_stop_source": self.stage_stop_source,
            "executed_stages": self.executed_stages,
            "work_results": [result.model_dump() for result in self.work_results],
            "verification": self.verification.model_dump(),
            "terminal_stage": self.terminal_stage,
        }

    def stage_receipts_payload(self) -> list[dict[str, object]]:
        return [
            {
                "stage": stage,
                "order": order,
            }
            for order, stage in enumerate(self.executed_stages, start=1)
        ]
