from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_kernel_boundary_demotion_matrix_keeps_router_and_wrapper_out_of_live_semantic_authority() -> None:
    payload = json.loads(
        (REPO_ROOT / "config" / "kernel-boundary-demotion-matrix.json").read_text(encoding="utf-8")
    )
    boundaries = {row["capability"]: row for row in payload["capability_boundaries"]}

    assert boundaries["task_understanding"]["authority_layer"] == "kernel"
    assert "packages/runtime-core/src/vgo_runtime/task_intent.py" in boundaries["task_understanding"]["demoted_layers"]
    assert boundaries["skill_selection"]["authority_layer"] == "kernel"
    assert "packages/runtime-core/src/vgo_runtime/router.py" in boundaries["skill_selection"]["demoted_layers"]
    assert boundaries["public_entry"]["authority_layer"] == "entry_wrapper"
    assert "scripts/router/resolve-pack-route.ps1" in boundaries["public_entry"]["demoted_layers"]
