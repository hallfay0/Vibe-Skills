from __future__ import annotations

from pathlib import Path
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_CORE_SRC = REPO_ROOT / "packages" / "runtime-core" / "src"
if str(RUNTIME_CORE_SRC) not in sys.path:
    sys.path.insert(0, str(RUNTIME_CORE_SRC))

from vgo_runtime.runtime_summary import build_runtime_summary, build_runtime_summary_from_payload


def test_build_runtime_summary_reports_artifact_paths_and_truth_owner() -> None:
    summary = build_runtime_summary(
        run_id="run-123",
        task="review code",
        artifacts={"runtime_input_packet": "runtime-input-packet.json"},
        work_binding={"units": [{"bound_skill": "code-review"}]},
    )

    assert summary["run_id"] == "run-123"
    assert summary["task"] == "review code"
    assert summary["truth_owner"] == "python"
    assert summary["artifacts"]["runtime_input_packet"] == "runtime-input-packet.json"
    assert summary["bound_skill_ids"] == ["code-review"]


def test_build_runtime_summary_preserves_base_fields() -> None:
    summary = build_runtime_summary(
        run_id="run-123",
        task="review code",
        artifacts={"runtime_input_packet": "runtime-input-packet.json"},
        work_binding={"units": [{"bound_skill": "code-review"}]},
        base_fields={"mode": "interactive_governed", "terminal_stage": "phase_cleanup"},
    )

    assert summary["mode"] == "interactive_governed"
    assert summary["terminal_stage"] == "phase_cleanup"


def test_build_runtime_summary_rejects_malformed_artifacts_contract() -> None:
    with pytest.raises(ValueError, match="artifacts must be an object"):
        build_runtime_summary(
            run_id="run-123",
            task="review code",
            artifacts=[],
            work_binding={"units": []},
        )


def test_build_runtime_summary_rejects_non_string_artifact_value() -> None:
    with pytest.raises(ValueError, match="artifacts.runtime_input_packet must be a string or null"):
        build_runtime_summary(
            run_id="run-123",
            task="review code",
            artifacts={"runtime_input_packet": 123},
            work_binding={"units": []},
        )


def test_build_runtime_summary_from_payload_rejects_malformed_optional_section() -> None:
    with pytest.raises(ValueError, match="specialist_user_disclosure must be an object when present"):
        build_runtime_summary_from_payload(
            {
                "run_id": "run-123",
                "task": "review code",
                "artifacts": {"runtime_input_packet": "runtime-input-packet.json"},
                "work_binding": {"units": []},
                "specialist_user_disclosure": "bad-shape",
            }
        )
