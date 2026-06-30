from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha1
import re
from typing import Any

from .text_tokens import tokens_from_text


@dataclass(frozen=True, slots=True)
class TaskRevision:
    sequence: int
    prompt: str
    revision_mode: str
    added_deliverables: tuple[str, ...]
    removed_deliverables: tuple[str, ...]
    added_constraints: tuple[str, ...]
    removed_constraints: tuple[str, ...]
    added_completion_criteria: tuple[str, ...]
    removed_completion_criteria: tuple[str, ...]

    def model_dump(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class TaskCard:
    id: str
    goal: str
    deliverables: tuple[str, ...]
    constraints: tuple[str, ...]
    known_context: tuple[str, ...]
    unknowns: tuple[str, ...]
    completion_criteria: tuple[str, ...]
    mode: str
    initial_goal: str
    accepted_revisions: tuple[TaskRevision, ...]

    def model_dump(self) -> dict[str, object]:
        return asdict(self)


CLAUSE_SPLIT_PATTERN = re.compile(r"\s+(?:and|then)\s+|[.;]\s*")
LEADING_ARTICLE_PATTERN = re.compile(r"^(?:a|an|the)\s+", re.IGNORECASE)
MULTISPACE_PATTERN = re.compile(r"\s+")
CONTINUE_PREFIX_PATTERN = re.compile(r"^(?:continue\s+by\s+)", re.IGNORECASE)
_CJK_PATTERN = re.compile(r"[\u3400-\u9fff]")

DELIVERABLE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"^(?:produce|write|create|generate|prepare|provide)\s+(.+)$", re.IGNORECASE), "{value}"),
    (re.compile(r"^(?:add|adding|update|updating)\s+(.+)$", re.IGNORECASE), "{value}"),
    (re.compile(r"^(?:implement|build|change)\b", re.IGNORECASE), "code change"),
    (re.compile(r"^(?:fix|debug|repair)\b", re.IGNORECASE), "code change"),
    (re.compile(r"^(?:review|audit|inspect)\b", re.IGNORECASE), "review notes"),
    (re.compile(r"^(?:plan|design)\b", re.IGNORECASE), "implementation plan"),
    (re.compile(r"^(?:test|verify|prove)\b", re.IGNORECASE), "verification evidence"),
)

_ROUTER_DEBUG_CONTEXT_MARKERS = ("router", "routing", "misroute")
_ROUTER_DEBUG_MARKERS = (
    "fallback",
    "threshold",
    "confidence",
    "candidate-scoring",
    "grade-selection",
    "task-classification",
)

_TASK_TYPE_RULES = (
    ("review", ("review", "code review", "pr review", "audit", "assess", "审查", "评审", "审核", "代码评审")),
    (
        "debug",
        (
            "debug",
            "bug",
            "fix",
            "repair",
            "patch",
            "failure",
            "failing",
            "regression",
            "root cause",
            "diagnos",
            "triage",
            "mismatch",
            "misroute",
            "inaccurate",
            "friction",
            "error",
            "issue",
            "problem",
            "错误",
            "修复",
            "问题",
            "失败",
            "报错",
            "排查",
            "定位",
            "根因",
            "回退",
            "回滚",
            "低置信度",
            "误路由",
        ),
    ),
    ("research", ("research", "survey", "literature", "paper", "investigate", "调研", "研究")),
    (
        "coding",
        (
            "implement",
            "build",
            "upgrade",
            "update",
            "enhance",
            "modify",
            "change",
            "create",
            "add",
            "integrate",
            "integration",
            "install",
            "extract",
            "refactor",
            "runtime",
            "router",
            "routing",
            "code",
            "更新",
            "增强",
            "执行",
            "修改",
            "安装",
            "集成",
            "运行时",
            "路由",
            "工作流",
        ),
    ),
)


def _marker_matches(text: str, marker: str) -> bool:
    candidate = str(marker).strip().lower()
    if not text or not candidate:
        return False
    if _CJK_PATTERN.search(candidate):
        return candidate in text
    if re.search(r"[a-z0-9]", candidate):
        parts = [re.escape(piece) for piece in re.split(r"[-_\s/]+", candidate) if piece]
        if parts:
            pattern = r"(?<![a-z0-9])" + r"[-_\s/]*".join(parts) + r"(?![a-z0-9])"
            return re.search(pattern, text) is not None
    return candidate in text


def _signal_count(text: str, markers: tuple[str, ...]) -> int:
    return sum(1 for marker in markers if _marker_matches(text, marker))


def infer_task_type(task: str | None) -> str:
    task_lower = str(task or "").lower()
    review_markers = _TASK_TYPE_RULES[0][1]
    debug_markers = _TASK_TYPE_RULES[1][1]
    research_markers = _TASK_TYPE_RULES[2][1]
    coding_markers = _TASK_TYPE_RULES[3][1]

    scores = {
        "review": _signal_count(task_lower, review_markers),
        "debug": _signal_count(task_lower, debug_markers),
        "research": _signal_count(task_lower, research_markers),
        "coding": _signal_count(task_lower, coding_markers),
    }
    if _signal_count(task_lower, _ROUTER_DEBUG_CONTEXT_MARKERS) > 0:
        scores["debug"] = max(scores["debug"], _signal_count(task_lower, _ROUTER_DEBUG_MARKERS))

    max_score = max(scores.values(), default=0)
    if max_score <= 0:
        return "planning"
    for task_type in ("review", "debug", "research", "coding"):
        if scores[task_type] == max_score:
            return task_type
    return "planning"


def _normalize_text_list(values: Any, *, field_name: str) -> tuple[str, ...]:
    if values is None:
        return ()
    if not isinstance(values, list):
        raise ValueError(f"task card field {field_name!r} must be a list of strings")
    normalized: list[str] = []
    for value in values:
        text = str(value).strip()
        if not text:
            raise ValueError(f"task card field {field_name!r} cannot contain empty values")
        normalized.append(text)
    return tuple(normalized)


def _build_task_id(goal: str) -> str:
    digest = sha1(goal.encode("utf-8")).hexdigest()[:10]
    return f"task-{digest}"


def _normalize_clause_text(value: str) -> str:
    collapsed = MULTISPACE_PATTERN.sub(" ", value.strip(" ,.;:"))
    without_continue = CONTINUE_PREFIX_PATTERN.sub("", collapsed)
    return LEADING_ARTICLE_PATTERN.sub("", without_continue).strip()


def _dedupe_texts(values: list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        normalized = value.strip()
        if not normalized:
            continue
        key = normalized.casefold()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(normalized)
    return tuple(deduped)


def _infer_mode(goal: str) -> str:
    lowered = goal.casefold()
    if any(keyword in lowered for keyword in ("review", "audit", "inspect")):
        return "review"
    if any(keyword in lowered for keyword in ("report", "summary", "brief", "briefing")):
        return "reporting"
    if any(keyword in lowered for keyword in ("fix", "debug", "repair")):
        return "debug"
    if any(keyword in lowered for keyword in ("plan", "roadmap", "design", "architecture")):
        return "design"
    if any(keyword in lowered for keyword in ("test", "verify", "prove")):
        return "verification"
    if any(keyword in lowered for keyword in ("implement", "build", "add", "update", "change")):
        return "coding"
    return "general"


def _infer_deliverables(goal: str) -> tuple[str, ...]:
    inferred: list[str] = []
    for raw_clause in CLAUSE_SPLIT_PATTERN.split(goal):
        clause = _normalize_clause_text(raw_clause)
        if not clause:
            continue
        for pattern, template in DELIVERABLE_PATTERNS:
            match = pattern.match(clause)
            if match is None:
                continue
            if match.lastindex:
                value = _normalize_clause_text(match.group(1))
                if value:
                    inferred.append(template.format(value=value))
            else:
                inferred.append(template)
            break
    return _dedupe_texts(inferred)


def _infer_completion_criteria(*, goal: str, deliverables: tuple[str, ...], mode: str) -> tuple[str, ...]:
    criteria = [f"{deliverable} exists" for deliverable in deliverables]
    deliverable_tokens = {token for deliverable in deliverables for token in tokens_from_text(deliverable)}
    if "review" in deliverable_tokens or "notes" in deliverable_tokens:
        criteria.append("review findings are explicit")
    if "plan" in deliverable_tokens or "design" in deliverable_tokens:
        criteria.append("plan or design is concrete")
    if "report" in deliverable_tokens or "summary" in deliverable_tokens or "brief" in deliverable_tokens:
        criteria.append("report or summary is concrete")
    if "tests" in deliverable_tokens:
        criteria.append("tests cover the changed behavior")
    if "verification" in deliverable_tokens and "evidence" in deliverable_tokens:
        criteria.append("verification evidence is direct")
    lowered_goal = goal.casefold()
    if mode == "review":
        criteria.append("review findings are explicit")
    if mode == "design":
        criteria.append("plan or design is concrete")
    if mode == "debug":
        criteria.append("changed behavior is fixed")
    if "test" in lowered_goal and "report" not in deliverable_tokens and "summary" not in deliverable_tokens:
        criteria.append("tests cover the changed behavior")
    if any(keyword in lowered_goal for keyword in ("verify", "prove", "evidence")):
        criteria.append("verification evidence is direct")
    return _dedupe_texts(criteria)


def build_task_card(*, prompt: str, context: dict[str, object] | None = None) -> TaskCard:
    goal = str(prompt).strip()
    if not goal:
        raise ValueError("prompt must be a non-empty string")
    payload = context or {}
    deliverables = _normalize_text_list(payload.get("deliverables"), field_name="deliverables")
    inferred_mode = _infer_mode(goal)
    mode = str(payload.get("mode") or inferred_mode).strip() or inferred_mode
    if not deliverables:
        deliverables = _infer_deliverables(goal)
    completion_criteria = _normalize_text_list(payload.get("completion_criteria"), field_name="completion_criteria")
    if not completion_criteria:
        completion_criteria = _infer_completion_criteria(goal=goal, deliverables=deliverables, mode=mode)
    return TaskCard(
        id=_build_task_id(goal),
        goal=goal,
        deliverables=deliverables,
        constraints=_normalize_text_list(payload.get("constraints"), field_name="constraints"),
        known_context=_normalize_text_list(payload.get("known_context"), field_name="known_context"),
        unknowns=_normalize_text_list(payload.get("unknowns"), field_name="unknowns"),
        completion_criteria=completion_criteria,
        mode=mode,
        initial_goal=goal,
        accepted_revisions=(),
    )
