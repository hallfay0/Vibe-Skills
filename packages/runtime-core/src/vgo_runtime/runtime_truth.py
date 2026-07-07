from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from vgo_runtime.kernel.work_binding import build_skill_usage_projection


def build_skill_routing_projection(
    *,
    skill_routing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if skill_routing is None:
        routing: dict[str, Any] = {}
    elif isinstance(skill_routing, dict):
        routing = dict(skill_routing)
    else:
        raise ValueError("skill_routing must be an object when present")

    schema_version = routing.get("schema_version")
    if schema_version is None:
        normalized_schema_version = "simplified_skill_routing_v1"
    elif isinstance(schema_version, str) and schema_version.strip():
        normalized_schema_version = schema_version
    else:
        raise ValueError("skill_routing.schema_version must be a non-empty string when present")

    candidates = routing.get("candidates", [])
    if not isinstance(candidates, list):
        raise ValueError("skill_routing.candidates must be a list when present")

    rejected = routing.get("rejected", [])
    if not isinstance(rejected, list):
        raise ValueError("skill_routing.rejected must be a list when present")

    return {
        "schema_version": normalized_schema_version,
        "candidates": list(candidates),
        "rejected": list(rejected),
    }


def build_runtime_truth_packet(
    *,
    run_id: str,
    task: str,
    work_binding: dict[str, Any],
    specialist_decision: dict[str, Any],
    work_results: dict[str, Any] | None = None,
    base_fields: dict[str, Any] | None = None,
    skill_routing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = dict(base_fields or {})
    payload["stage"] = "runtime_input_freeze"
    payload["run_id"] = run_id
    payload["task"] = task
    payload["work_binding"] = work_binding
    payload["specialist_decision"] = specialist_decision
    payload["skill_usage"] = build_skill_usage_projection(
        work_binding=work_binding,
        work_results=_work_result_rows(work_results),
        compatibility_mirror=payload.get("skill_usage") if isinstance(payload.get("skill_usage"), dict) else None,
    )
    payload["skill_routing"] = build_skill_routing_projection(
        skill_routing=skill_routing,
    )
    return payload


def build_runtime_truth_packet_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("runtime truth build payload must be an object")

    run_id = payload.get("run_id")
    task = payload.get("task")
    work_binding = payload.get("work_binding")
    specialist_decision = payload.get("specialist_decision")
    work_results = payload.get("work_results")
    base_fields = payload.get("base_fields")
    skill_routing = payload.get("skill_routing")

    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("runtime truth build payload missing run_id")
    if not isinstance(task, str) or not task.strip():
        raise ValueError("runtime truth build payload missing task")
    if not isinstance(work_binding, dict):
        raise ValueError("runtime truth build payload missing work_binding")
    if not isinstance(specialist_decision, dict):
        raise ValueError("runtime truth build payload missing specialist_decision")
    if work_results is not None and not isinstance(work_results, dict):
        raise ValueError("work_results must be an object when present")
    if base_fields is not None and not isinstance(base_fields, dict):
        raise ValueError("base_fields must be an object when present")
    if skill_routing is not None and not isinstance(skill_routing, dict):
        raise ValueError("skill_routing must be an object when present")

    return build_runtime_truth_packet(
        run_id=run_id,
        task=task,
        work_binding=work_binding,
        specialist_decision=specialist_decision,
        work_results=work_results,
        base_fields=base_fields,
        skill_routing=skill_routing,
    )


def _work_result_rows(work_results: dict[str, Any] | None) -> list[dict[str, Any]] | None:
    if not isinstance(work_results, dict):
        return None
    rows = work_results.get("work_results")
    if not isinstance(rows, list):
        return None
    return [row for row in rows if isinstance(row, dict)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a Python-owned runtime truth packet.")
    parser.add_argument("--input-json-path", required=True)
    parser.add_argument("--output-json-path")
    args = parser.parse_args(argv)

    input_path = Path(args.input_json_path)
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    packet = build_runtime_truth_packet_from_payload(payload)
    text = json.dumps(packet, ensure_ascii=False, indent=2) + "\n"

    if args.output_json_path:
        Path(args.output_json_path).write_text(text, encoding="utf-8")

    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
