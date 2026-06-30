from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .work_plan import SkillProvenance, WorkPlan


@dataclass(frozen=True, slots=True)
class WorkBindingUnit:
    work_unit_id: str
    bound_skill: str | None
    binding_profile: str
    binding_reason: str | None
    alternative_skills: tuple[str, ...]
    expected_artifacts: tuple[str, ...]
    verification: tuple[str, ...]
    provenance: SkillProvenance | None = None

    def model_dump(self) -> dict[str, object]:
        payload = asdict(self)
        provenance = payload.get("provenance")
        if isinstance(provenance, dict):
            payload["skill_source_kind"] = provenance["source_kind"]
            payload["skill_source_root"] = provenance["source_root"]
            payload["resolved_skill_file"] = provenance["resolved_skill_file"]
            payload["skill_source_priority"] = provenance["source_priority"]
            payload["skill_source_order"] = provenance["source_order"]
            payload["skill_path_contract"] = provenance["path_contract"]
            payload["skill_path_base"] = provenance["path_base"]
        return payload


@dataclass(frozen=True, slots=True)
class WorkBinding:
    task_id: str
    units: tuple[WorkBindingUnit, ...]

    def model_dump(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "units": [unit.model_dump() for unit in self.units],
        }


def build_work_binding(plan: WorkPlan) -> WorkBinding:
    return WorkBinding(
        task_id=plan.task_id,
        units=tuple(
            WorkBindingUnit(
                work_unit_id=work_unit.id,
                bound_skill=work_unit.preferred_skill,
                binding_profile=work_unit.binding_profile,
                binding_reason=work_unit.binding_reason,
                alternative_skills=work_unit.fallback_skills,
                expected_artifacts=work_unit.expected_artifacts,
                verification=work_unit.verification,
                provenance=work_unit.selected_skill_provenance,
            )
            for work_unit in plan.work_units
        ),
    )


def build_skill_usage_projection(
    *,
    work_binding: dict[str, Any] | None,
    work_results: list[dict[str, Any]] | None = None,
    compatibility_mirror: dict[str, Any] | None = None,
    include_binary_compat_fields: bool = False,
) -> dict[str, object]:
    bound_units = work_binding.get("units", []) if isinstance(work_binding, dict) else []
    result_rows = work_results if isinstance(work_results, list) else []

    used: list[dict[str, str]] = []
    evidence: list[dict[str, str]] = []
    seen_used_keys: set[tuple[str, str]] = set()
    used_skill_ids: set[str] = set()
    for row in result_rows:
        if not isinstance(row, dict):
            continue
        skill_id = str(row.get("used_skill") or "").strip()
        work_unit_id = str(row.get("work_unit_id") or "").strip()
        artifact = _first_artifact_evidence(row)
        if not skill_id or not work_unit_id or not artifact:
            continue
        key = (skill_id.casefold(), work_unit_id.casefold())
        if key in seen_used_keys:
            continue
        seen_used_keys.add(key)
        used_skill_ids.add(skill_id.casefold())
        used.append(
            {
                "skill_id": skill_id,
                "work_unit_id": work_unit_id,
            }
        )
        evidence.append(
            {
                "skill_id": skill_id,
                "work_unit_id": work_unit_id,
                "artifact": artifact,
                "stage": "plan_execute",
                "impact": "kernel work-unit artifact evidence recorded the skill use",
            }
        )

    if not used and isinstance(compatibility_mirror, dict):
        used = _normalize_usage_entries(compatibility_mirror.get("used"))
        evidence = _normalize_evidence_entries(compatibility_mirror.get("evidence"))
        used_skill_ids = {str(entry.get("skill_id") or "").strip().casefold() for entry in used if isinstance(entry, dict)}
        used_skill_ids.discard("")

    unused = _build_unused_entries(bound_units=bound_units, used_skill_ids=used_skill_ids)
    if not unused and isinstance(compatibility_mirror, dict):
        unused = _normalize_usage_entries(compatibility_mirror.get("unused"))

    if not include_binary_compat_fields:
        return {
            "used": used,
            "unused": unused,
            "evidence": evidence,
        }

    unused_with_reasons = [_attach_unused_reason(entry) for entry in unused]
    loaded_skills = _loaded_skill_rows_from_work_binding(bound_units)
    used_skills = _unique_skill_ids(used)
    unused_skills = _unique_skill_ids(unused_with_reasons)
    unused_reasons = [
        {
            "skill_id": str(entry.get("skill_id") or "").strip(),
            "work_unit_id": str(entry.get("work_unit_id") or "").strip(),
            "reason": "selected_but_no_artifact_impact",
        }
        for entry in unused_with_reasons
        if isinstance(entry, dict) and str(entry.get("skill_id") or "").strip()
    ]

    return {
        "state_model": "binary_used_unused",
        "loaded_skills": loaded_skills,
        "used": used,
        "unused": unused_with_reasons,
        "used_skills": used_skills,
        "unused_skills": unused_skills,
        "unused_reasons": unused_reasons,
        "evidence": evidence,
    }


def _first_artifact_evidence(row: dict[str, Any]) -> str | None:
    for field_name in ("artifact_paths", "proof_artifact_paths"):
        values = row.get(field_name)
        if not isinstance(values, list):
            continue
        for value in values:
            text = str(value).strip()
            if text:
                return text
    return None


def _build_unused_entries(
    *,
    bound_units: object,
    used_skill_ids: set[str],
) -> list[dict[str, str]]:
    if not isinstance(bound_units, list):
        return []

    unused: list[dict[str, str]] = []
    seen_unused_keys: set[tuple[str, str]] = set()
    for unit in bound_units:
        if not isinstance(unit, dict):
            continue
        skill_id = str(unit.get("bound_skill") or "").strip()
        work_unit_id = str(unit.get("work_unit_id") or "").strip()
        if not skill_id or skill_id.casefold() in used_skill_ids:
            continue
        key = (skill_id.casefold(), work_unit_id.casefold())
        if key in seen_unused_keys:
            continue
        seen_unused_keys.add(key)
        entry = {"skill_id": skill_id}
        if work_unit_id:
            entry["work_unit_id"] = work_unit_id
        unused.append(entry)
    return unused


def _attach_unused_reason(entry: dict[str, str]) -> dict[str, str]:
    row = dict(entry)
    row["reason"] = "selected_but_no_artifact_impact"
    return row


def _normalize_usage_entries(value: object) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    normalized: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        skill_id = str(item.get("skill_id") or "").strip()
        if not skill_id:
            continue
        entry = {"skill_id": skill_id}
        work_unit_id = str(item.get("work_unit_id") or "").strip()
        if work_unit_id:
            entry["work_unit_id"] = work_unit_id
        normalized.append(entry)
    return normalized


def _normalize_evidence_entries(value: object) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    normalized: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        skill_id = str(item.get("skill_id") or "").strip()
        artifact = str(item.get("artifact") or "").strip()
        if not skill_id or not artifact:
            continue
        entry = {
            "skill_id": skill_id,
            "artifact": artifact,
            "stage": str(item.get("stage") or "plan_execute").strip() or "plan_execute",
            "impact": str(item.get("impact") or "compatibility skill usage evidence").strip()
            or "compatibility skill usage evidence",
        }
        work_unit_id = str(item.get("work_unit_id") or "").strip()
        if work_unit_id:
            entry["work_unit_id"] = work_unit_id
        normalized.append(entry)
    return normalized


def _unique_skill_ids(rows: list[dict[str, Any]]) -> list[str]:
    skill_ids: list[str] = []
    for row in rows:
        skill_id = str(row.get("skill_id") or "").strip()
        if skill_id and skill_id not in skill_ids:
            skill_ids.append(skill_id)
    return skill_ids


def _loaded_skill_rows_from_work_binding(bound_units: object) -> list[dict[str, object]]:
    if not isinstance(bound_units, list):
        return []

    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    for unit in bound_units:
        if not isinstance(unit, dict):
            continue
        skill_id = str(unit.get("bound_skill") or "").strip()
        if not skill_id or skill_id in seen:
            continue
        seen.add(skill_id)
        skill_md_path = str(unit.get("skill_md_path") or "").strip() or str(unit.get("native_skill_entrypoint") or "").strip()
        skill_md_sha256 = str(unit.get("skill_md_sha256") or "").strip()
        if skill_md_path and not skill_md_sha256:
            path = Path(skill_md_path)
            if path.is_file():
                skill_md_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
        row: dict[str, object] = {
            "skill_id": skill_id,
            "load_status": "loaded_full_skill_md",
            "loaded_at_stage": "runtime_input_freeze",
            "skill_md_path": skill_md_path or None,
            "skill_md_sha256": skill_md_sha256 or None,
        }
        rows.append(row)
    return rows
