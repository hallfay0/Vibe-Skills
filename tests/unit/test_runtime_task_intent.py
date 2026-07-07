from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_SRC = ROOT / "packages" / "runtime-core" / "src"
if str(RUNTIME_SRC) not in sys.path:
    sys.path.insert(0, str(RUNTIME_SRC))

import vgo_runtime.task_intent as task_intent_module
from vgo_runtime.kernel.task_card import infer_task_type as kernel_infer_task_type
from vgo_runtime.task_intent import infer_task_type


def test_infer_task_type_marks_router_misroute_prompt_as_debug() -> None:
    task = "router confidence-low fallback misroute task-classification grade-selection candidate-scoring"

    assert infer_task_type(task) == "debug"


def test_infer_task_type_marks_dispatch_triage_prompt_as_debug() -> None:
    assert infer_task_type("triage runtime specialist dispatch duplication") == "debug"


def test_infer_task_type_avoids_docs_false_positive() -> None:
    assert infer_task_type("suffix cleanup in docs") == "planning"
    assert infer_task_type("codex bootstrap wording in docs") == "planning"


def test_infer_task_type_keeps_ml_pipeline_prompt_as_planning() -> None:
    assert infer_task_type("ml pipeline workflow pack artifacts for deployment") == "planning"


def test_task_intent_module_delegates_to_kernel_authority() -> None:
    assert task_intent_module.infer_task_type is kernel_infer_task_type


def test_task_intent_module_is_not_documented_as_live_task_authority() -> None:
    text = Path("packages/runtime-core/src/vgo_runtime/task_intent.py").read_text(encoding="utf-8")
    assert "authoritative task understanding" not in text.lower()
