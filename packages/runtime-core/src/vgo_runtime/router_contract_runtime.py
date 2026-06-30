from __future__ import annotations

from pathlib import Path
from typing import Any

from .kernel.host_skill_roots import resolve_host_skill_roots
from .kernel.skill_index import build_skill_catalog, build_skill_index_from_catalog
from .kernel.text_tokens import SKILL_MATCH_STOPWORDS, tokens_from_text, tokens_from_values
from .runtime_support import (
    RepoContext,
    keyword_hit,
    load_json,
    normalize_text,
    resolve_host_id,
    resolve_target_root,
)


LOCAL_PACK_ID = "local-skill-index"
LOCAL_CANDIDATE_SOURCE = "local_skill_index"
AUTO_ROUTE_MIN_SCORE = 0.35
CONFIRM_ROUTE_MIN_SCORE = 0.18
CONFIRM_UI_ROUTE_PREFIX = "Bounded work suggested local skill options"
CONFIRM_UI_SIMPLE_INSTRUCTION = "Reply with an option number or `$<skill>` to make the selection explicit."


def _dedupe_strings(values: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        deduped.append(text)
        seen.add(text)
    return deduped


def _normalize_requested_skill(requested_skill: str | None) -> str | None:
    requested = normalize_text(str(requested_skill or "").lstrip("$"))
    return requested or None


def _load_local_thresholds(repo_root: Path) -> dict[str, float]:
    path = repo_root / "config" / "router-thresholds.json"
    if not path.exists():
        return {
            "auto_route": AUTO_ROUTE_MIN_SCORE,
            "confirm_required": CONFIRM_ROUTE_MIN_SCORE,
        }
    payload = load_json(path)
    thresholds = payload.get("thresholds") if isinstance(payload, dict) else {}
    if not isinstance(thresholds, dict):
        thresholds = {}
    return {
        "auto_route": float(thresholds.get("auto_route", AUTO_ROUTE_MIN_SCORE)),
        "confirm_required": float(thresholds.get("confirm_required", CONFIRM_ROUTE_MIN_SCORE)),
        "min_top1_top2_gap": float(thresholds.get("min_top1_top2_gap", 0.0)),
        "min_candidate_signal_for_confirm_override": float(
            thresholds.get("min_candidate_signal_for_confirm_override", CONFIRM_ROUTE_MIN_SCORE)
        ),
        "min_candidate_signal_for_auto_route": float(
            thresholds.get("min_candidate_signal_for_auto_route", AUTO_ROUTE_MIN_SCORE)
        ),
    }


def _resolve_local_host_roots(*, repo_root: Path, host_id: str | None, target_root: Path) -> tuple[Path, ...]:
    normalized_host_id = resolve_host_id(host_id)
    return tuple(
        root.path
        for root in resolve_host_skill_roots(
            repo_root=repo_root,
            host_id=normalized_host_id,
            agent_root=target_root,
            workspace_root=None,
        )
    )


def _entry_search_tokens(entry: dict[str, Any]) -> set[str]:
    tokens: set[str] = set()
    tokens.update(tokens_from_text(str(entry.get("skill_id") or entry.get("id") or ""), stem=True, stopwords=SKILL_MATCH_STOPWORDS))
    tokens.update(tokens_from_text(str(entry.get("display_name") or entry.get("name") or ""), stem=True, stopwords=SKILL_MATCH_STOPWORDS))
    tokens.update(tokens_from_text(str(entry.get("description") or ""), stem=True, stopwords=SKILL_MATCH_STOPWORDS))
    tokens.update(tokens_from_values(entry.get("tags"), stem=True, stopwords=SKILL_MATCH_STOPWORDS))
    tokens.update(tokens_from_values(entry.get("when_to_use"), stem=True, stopwords=SKILL_MATCH_STOPWORDS))
    return tokens


def _score_entry(prompt: str, prompt_lower: str, entry: dict[str, Any]) -> dict[str, Any]:
    query_tokens = tokens_from_text(prompt, stem=True, stopwords=SKILL_MATCH_STOPWORDS)
    search_tokens = _entry_search_tokens(entry)
    matched_tokens = sorted(query_tokens & search_tokens)
    token_score = min(1.0, len(matched_tokens) / float(min(4, max(1, len(query_tokens)))))
    skill_id = str(entry.get("skill_id") or entry.get("id") or "").strip()
    name = str(entry.get("display_name") or entry.get("name") or "").strip()
    name_score = 1.0 if any(keyword_hit(prompt_lower, value) for value in (skill_id, skill_id.replace("-", " "), name)) else 0.0
    tag_score = min(1.0, len(set(tokens_from_values(entry.get("tags"), stem=True, stopwords=SKILL_MATCH_STOPWORDS)) & query_tokens) / 2.0)
    score = round(max(name_score, (0.75 * token_score) + (0.25 * tag_score)), 4)
    return {
        "score": score,
        "matched_tokens": matched_tokens,
        "keyword_score": round(token_score, 4),
        "name_score": round(name_score, 4),
        "tag_score": round(tag_score, 4),
    }


def _candidate_row(entry: dict[str, Any], score: dict[str, Any], *, selected: bool) -> dict[str, Any]:
    skill_id = str(entry.get("skill_id") or entry.get("id") or "").strip()
    return {
        "pack_id": LOCAL_PACK_ID,
        "candidate_source": LOCAL_CANDIDATE_SOURCE,
        "source_root": entry.get("source_root"),
        "source_kind": entry.get("source_kind"),
        "source_priority": entry.get("source_priority"),
        "source_order": entry.get("source_order"),
        "skill": skill_id,
        "selected_candidate": skill_id if selected else None,
        "score": score["score"],
        "selection_score": score["score"],
        "candidate_selection_score": score["score"],
        "candidate_selection_reason": "keyword_ranked" if selected else "below_local_threshold",
        "candidate_signal": score["score"],
        "candidate_ranking": [
            {
                "skill": skill_id,
                "score": score["score"],
                "matched_tokens": score["matched_tokens"],
            }
        ],
        "candidate_top1_top2_gap": score["score"],
        "candidate_filtered_out_by_task": [],
        "native_skill_entrypoint": entry.get("native_skill_entrypoint"),
        "skill_root": entry.get("skill_root"),
        "description": entry.get("description"),
        "matched_tokens": score["matched_tokens"],
        "authority_tier": "local_installed",
        "authority_eligible": bool(selected),
        "authority_rejection_reasons": [] if selected else ["candidate_signal_below_local_threshold"],
    }


def _selected_payload(row: dict[str, Any], *, reason: str) -> dict[str, Any]:
    return {
        "pack_id": LOCAL_PACK_ID,
        "candidate_source": LOCAL_CANDIDATE_SOURCE,
        "skill": row["skill"],
        "selection_reason": reason,
        "selection_score": row["score"],
        "top1_top2_gap": row["candidate_top1_top2_gap"],
        "candidate_signal": row["candidate_signal"],
        "filtered_out_by_task": [],
        "native_skill_entrypoint": row.get("native_skill_entrypoint"),
        "skill_root": row.get("skill_root"),
        "source_root": row.get("source_root"),
        "source_kind": row.get("source_kind"),
        "authority": {
            "tier": "local_installed",
            "eligible": True,
        },
    }


def _empty_custom_admission(target_root: Path | None) -> dict[str, Any]:
    return {
        "status": "disabled_default_local_index_only",
        "target_root": str(target_root) if target_root is not None else None,
        "manifest_paths": {},
        "manifests_present": {},
        "invalid_entries": [],
        "dependency_failures": [],
        "admitted_candidates": [],
    }


def _public_admitted_candidates(rows: object) -> list[dict[str, object]]:
    return [dict(row) for row in rows or [] if isinstance(row, dict)]


def _public_pack_row(row: dict[str, object]) -> dict[str, object]:
    return dict(row)


def _public_custom_metadata(value: object) -> object:
    return dict(value) if isinstance(value, dict) else value


def _public_nested_pack_metadata(value: object) -> object:
    return dict(value) if isinstance(value, dict) else value


def _build_deep_discovery_advice(repo: RepoContext, prompt_lower: str, grade: str, task_type: str) -> dict[str, object] | None:
    return None


def choose_authoritative_route(
    ranked: list[dict[str, Any]],
    task_type: str,
    requested_canonical: str | None,
    authority_policy: dict[str, Any],
) -> dict[str, Any]:
    top = ranked[0] if ranked else None
    if top is None:
        return {
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
    selected_skill = str(top.get("selected_candidate") or top.get("skill") or "").strip() or None
    return {
        "selected_pack_id": str(top.get("pack_id") or LOCAL_PACK_ID),
        "selected_skill": selected_skill,
        "selected_row": top if selected_skill else None,
        "fallback_applied": False,
        "fallback_target_pack_id": None,
        "fallback_target_skill": None,
        "pre_fallback_top_pack_id": str(top.get("pack_id") or LOCAL_PACK_ID),
        "pre_fallback_top_skill": str(top.get("skill") or ""),
        "rejected_specialist_reasons": list(top.get("authority_rejection_reasons") or []),
    }


def _build_route_decision_contract(
    *,
    selected_pack: str,
    selected_skill: str,
    options: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "decision_kind": "route_selection",
        "selected_pack": selected_pack,
        "selected_skill": selected_skill,
        "options": options,
        "preferred_payload": {
            "decision_kind": "route_selection",
            "selected_pack": selected_pack,
            "selected_skill": selected_skill,
        },
    }


def build_confirm_ui(
    repo: RepoContext,
    route_result: dict[str, Any],
    target_root: str | None,
    host_id: str | None = None,
) -> dict[str, object] | None:
    selected = route_result.get("selected")
    if not isinstance(selected, dict):
        return None
    selected_skill = str(selected.get("skill") or "").strip()
    if not selected_skill:
        return None

    options: list[dict[str, object]] = []
    for index, row in enumerate(route_result.get("ranked", [])[:6], start=1):
        if not isinstance(row, dict):
            continue
        skill = str(row.get("skill") or row.get("selected_candidate") or "").strip()
        if not skill:
            continue
        options.append(
            {
                "option_id": str(index),
                "pack_id": LOCAL_PACK_ID,
                "skill": skill,
                "score": row.get("score"),
                "description": row.get("description"),
                "native_skill_entrypoint": row.get("native_skill_entrypoint"),
            }
        )
    if not options:
        return None

    rendered = [f"{CONFIRM_UI_ROUTE_PREFIX} `{LOCAL_PACK_ID}`."]
    for option in options:
        score = option["score"]
        score_text = f" (score={round(float(score), 4)})" if score is not None else ""
        description = str(option.get("description") or "").strip()
        if description:
            rendered.append(f"{option['option_id']}. `{option['skill']}`{score_text} - {description}")
        else:
            rendered.append(f"{option['option_id']}. `{option['skill']}`{score_text}")
    rendered.append(CONFIRM_UI_SIMPLE_INSTRUCTION)

    return {
        "enabled": True,
        "pack_id": LOCAL_PACK_ID,
        "selected_skill": selected_skill,
        "options": options,
        "route_decision_contract": _build_route_decision_contract(
            selected_pack=LOCAL_PACK_ID,
            selected_skill=selected_skill,
            options=options,
        ),
        "clarification_questions": [],
        "rendered_text": "\n".join(rendered),
        "hazard_alert_required": False,
        "truth_level": route_result.get("truth_level"),
        "degradation_state": route_result.get("degradation_state"),
        "hazard_alert": None,
    }


def build_fallback_truth(route_result: dict[str, Any], fallback_policy: dict[str, Any] | None) -> dict[str, Any]:
    fallback_active = str(route_result.get("route_mode") or "") == "no_local_candidate"
    return {
        "fallback_active": False,
        "hazard_alert_required": False,
        "truth_level": "authoritative" if not fallback_active else "local_index_no_match",
        "degradation_state": "standard" if not fallback_active else "no_local_candidate",
        "non_authoritative": False,
        "hazard_alert": None,
    }


def route_prompt(
    prompt: str,
    grade: str,
    task_type: str,
    requested_skill: str | None = None,
    entry_intent_id: str | None = None,
    requested_grade_floor: str | None = None,
    target_root: str | None = None,
    host_id: str | None = None,
    repo_root: Path | None = None,
) -> dict[str, object]:
    repo_path = repo_root or Path(__file__).resolve().parents[4]
    normalized_host_id = resolve_host_id(host_id)
    resolved_target_root = resolve_target_root(target_root, normalized_host_id)
    thresholds = _load_local_thresholds(repo_path)
    host_roots = _resolve_local_host_roots(
        repo_root=repo_path,
        host_id=normalized_host_id,
        target_root=resolved_target_root,
    )
    catalog = build_skill_catalog(agent_root=resolved_target_root, host_roots=host_roots)
    index = build_skill_index_from_catalog(catalog)
    prompt_lower = normalize_text(prompt)
    requested_canonical = _normalize_requested_skill(requested_skill)

    active_entries = [entry for entry in index.get("skills", []) if isinstance(entry, dict)]
    by_skill_id = {
        normalize_text(entry.get("skill_id") or entry.get("id")): entry
        for entry in active_entries
        if normalize_text(entry.get("skill_id") or entry.get("id"))
    }

    scored_rows: list[dict[str, Any]] = []
    for entry in active_entries:
        score = _score_entry(prompt, prompt_lower, entry)
        scored_rows.append(_candidate_row(entry, score, selected=False))
    scored_rows.sort(
        key=lambda row: (
            -float(row["score"]),
            int(row.get("source_priority") or 0),
            int(row.get("source_order") or 0),
            str(row["skill"]),
        )
    )

    selected_row: dict[str, Any] | None = None
    route_reason = "no_local_candidate_above_threshold"
    selection_reason = "no_local_candidate"
    rejected_reasons: list[str] = []

    if requested_canonical:
        requested_entry = by_skill_id.get(requested_canonical)
        if requested_entry is not None:
            selected_row = _candidate_row(
                requested_entry,
                {"score": 1.0, "matched_tokens": [requested_canonical], "keyword_score": 1.0, "name_score": 1.0, "tag_score": 0.0},
                selected=True,
            )
            route_reason = "explicit_local_skill"
            selection_reason = "requested_skill"
        else:
            route_reason = "requested_local_skill_not_found"
            selection_reason = "requested_skill_missing"
            rejected_reasons.append(requested_canonical)
    elif scored_rows and float(scored_rows[0]["score"]) >= float(thresholds["min_candidate_signal_for_auto_route"]):
        selected_row = dict(scored_rows[0])
        selected_row["selected_candidate"] = selected_row["skill"]
        selected_row["candidate_selection_reason"] = "keyword_ranked"
        selected_row["authority_eligible"] = True
        selected_row["authority_rejection_reasons"] = []
        route_reason = "auto_route"
        selection_reason = "keyword_ranked"
    elif scored_rows and float(scored_rows[0]["score"]) >= float(thresholds["confirm_required"]):
        selected_row = dict(scored_rows[0])
        selected_row["selected_candidate"] = selected_row["skill"]
        selected_row["candidate_selection_reason"] = "keyword_ranked"
        selected_row["authority_eligible"] = True
        selected_row["authority_rejection_reasons"] = []
        route_reason = "candidate_signal_host_selection"
        selection_reason = "keyword_ranked"

    ranked_rows = scored_rows
    if selected_row is not None:
        ranked_rows = [selected_row] + [
            row for row in scored_rows if str(row.get("skill") or "") != str(selected_row.get("skill") or "")
        ]

    selected = _selected_payload(selected_row, reason=selection_reason) if selected_row is not None else None
    confidence = float(selected_row["score"]) if selected_row is not None else (float(ranked_rows[0]["score"]) if ranked_rows else 0.0)
    route_mode = "local_skill_overlay" if selected is not None else "no_local_candidate"
    result: dict[str, Any] = {
        "prompt": prompt,
        "grade": normalize_text(grade).upper() or "M",
        "task_type": normalize_text(task_type) or "planning",
        "router_contract_mode": "candidate_discovery_only",
        "work_binding_truth_source": "kernel",
        "candidate_source": LOCAL_CANDIDATE_SOURCE,
        "route_mode": route_mode,
        "route_reason": route_reason,
        "confidence": round(confidence, 4),
        "top1_top2_gap": round(confidence, 4),
        "candidate_signal": round(confidence, 4),
        "legacy_fallback_guard_applied": False,
        "legacy_fallback_original_reason": None,
        "fallback_applied": False,
        "fallback_target": {
            "pack_id": None,
            "skill": None,
        },
        "pre_fallback_top": {
            "pack_id": LOCAL_PACK_ID if ranked_rows else None,
            "skill": str(ranked_rows[0]["skill"]) if ranked_rows else None,
        },
        "rejected_specialist_reasons": rejected_reasons,
        "thresholds": thresholds,
        "alias": {
            "requested_input": requested_skill,
            "requested_canonical": requested_canonical,
            "entry_intent_id": entry_intent_id,
            "requested_grade_floor": requested_grade_floor,
        },
        "local_skill_index": {
            "schema_version": index["schema_version"],
            "host_id": normalized_host_id,
            "target_root": str(resolved_target_root),
            "host_roots": [str(path.resolve()) for path in host_roots],
            "skill_count": len(active_entries),
            "discovery_diagnostics": index["discovery_diagnostics"],
        },
        "custom_admission": _empty_custom_admission(resolved_target_root),
        "candidates": ranked_rows[:6],
        "primary_candidate": selected,
        "selected": selected,
        "ranked": ranked_rows[:6],
        "confirm_required": False,
        "confirm_options": [],
    }
    result.update(build_fallback_truth(result, None))
    confirm_ui = build_confirm_ui(
        RepoContext(repo_root=repo_path, config_root=repo_path / "config", bundled_skills_root=repo_path / "bundled" / "skills"),
        result,
        str(resolved_target_root),
        normalized_host_id,
    )
    if confirm_ui and selected is not None and route_reason == "candidate_signal_host_selection":
        result["confirm_required"] = True
        result["confirm_options"] = confirm_ui["options"]
        result["confirm_ui"] = confirm_ui
    return result
