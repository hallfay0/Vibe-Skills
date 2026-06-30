from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re


REQUIRED_LIST_FIELDS = ("when_to_use", "not_for", "inputs", "outputs")
REQUIRED_STRING_FIELDS = ("id", "name", "description")
OPTIONAL_LIST_FIELDS = ("plan_hints", "verify_hints", "tags")
ALLOWED_FIELDS = frozenset(
    REQUIRED_STRING_FIELDS
    + REQUIRED_LIST_FIELDS
    + OPTIONAL_LIST_FIELDS
    + ("enabled", "priority")
)
INTEGER_PATTERN = re.compile(r"^-?\d+$")


@dataclass(frozen=True, slots=True)
class SkillManifest:
    id: str
    name: str
    description: str
    when_to_use: tuple[str, ...]
    not_for: tuple[str, ...]
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    plan_hints: tuple[str, ...] = ()
    verify_hints: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    enabled: bool = True
    priority: int = 50
    root_dir: str = ""
    skill_file: str = ""

    def model_dump(self) -> dict[str, object]:
        return asdict(self)


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _parse_scalar(value: str) -> object:
    normalized = value.strip()
    lowered = normalized.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if INTEGER_PATTERN.match(normalized):
        return int(normalized)
    return _strip_quotes(normalized)


def _extract_frontmatter_lines(skill_file: Path) -> list[str]:
    lines = skill_file.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"skill file missing frontmatter start: {skill_file}")
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index]
    raise ValueError(f"skill file missing frontmatter end: {skill_file}")


def _parse_frontmatter(frontmatter_lines: list[str], *, skill_file: Path) -> dict[str, object]:
    payload: dict[str, object] = {}
    index = 0
    while index < len(frontmatter_lines):
        raw_line = frontmatter_lines[index]
        stripped = raw_line.strip()
        if not stripped:
            index += 1
            continue
        if raw_line[:1].isspace():
            raise ValueError(f"unexpected indentation in skill frontmatter: {skill_file}")
        if ":" not in raw_line:
            raise ValueError(f"invalid frontmatter line in {skill_file}: {raw_line}")
        key, remainder = raw_line.split(":", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"empty frontmatter key in {skill_file}")
        if key not in ALLOWED_FIELDS:
            raise ValueError(f"unsupported frontmatter field {key!r} in {skill_file}")
        value_text = remainder.strip()
        if value_text:
            payload[key] = _parse_scalar(value_text)
            index += 1
            continue
        items: list[str] = []
        index += 1
        while index < len(frontmatter_lines):
            candidate = frontmatter_lines[index]
            if not candidate.strip():
                index += 1
                continue
            if not candidate[:1].isspace():
                break
            stripped_candidate = candidate.lstrip()
            if not stripped_candidate.startswith("- "):
                raise ValueError(f"invalid list item in {skill_file}: {candidate}")
            item_value = stripped_candidate[2:].strip()
            if not item_value:
                raise ValueError(f"empty list item in {skill_file}: {candidate}")
            items.append(_strip_quotes(item_value))
            index += 1
        payload[key] = items
    return payload


def validate_skill_manifest(manifest: SkillManifest) -> None:
    for field_name in REQUIRED_STRING_FIELDS:
        value = getattr(manifest, field_name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"skill manifest field {field_name!r} must be a non-empty string")
    for field_name in REQUIRED_LIST_FIELDS + OPTIONAL_LIST_FIELDS:
        value = getattr(manifest, field_name)
        if not isinstance(value, tuple) or any(not isinstance(item, str) or not item.strip() for item in value):
            raise ValueError(f"skill manifest field {field_name!r} must be a list of non-empty strings")
    if not isinstance(manifest.enabled, bool):
        raise ValueError("skill manifest field 'enabled' must be boolean")
    if not isinstance(manifest.priority, int):
        raise ValueError("skill manifest field 'priority' must be an integer")


def parse_skill_manifest(skill_file: Path) -> SkillManifest:
    resolved_file = skill_file.resolve()
    frontmatter = _parse_frontmatter(_extract_frontmatter_lines(resolved_file), skill_file=resolved_file)
    for field_name in REQUIRED_STRING_FIELDS:
        if field_name not in frontmatter:
            raise ValueError(f"missing required skill field {field_name!r} in {resolved_file}")
        if not isinstance(frontmatter[field_name], str):
            raise ValueError(f"skill field {field_name!r} must be a string in {resolved_file}")
    for field_name in REQUIRED_LIST_FIELDS:
        if field_name not in frontmatter:
            raise ValueError(f"missing required skill field {field_name!r} in {resolved_file}")
        if not isinstance(frontmatter[field_name], list):
            raise ValueError(f"skill field {field_name!r} must be a list in {resolved_file}")
    enabled = frontmatter.get("enabled", True)
    if not isinstance(enabled, bool):
        raise ValueError(f"skill field 'enabled' must be boolean in {resolved_file}")
    priority = frontmatter.get("priority", 50)
    if not isinstance(priority, int):
        raise ValueError(f"skill field 'priority' must be an integer in {resolved_file}")
    manifest = SkillManifest(
        id=str(frontmatter["id"]).strip(),
        name=str(frontmatter["name"]).strip(),
        description=str(frontmatter["description"]).strip(),
        when_to_use=tuple(frontmatter["when_to_use"]),
        not_for=tuple(frontmatter["not_for"]),
        inputs=tuple(frontmatter["inputs"]),
        outputs=tuple(frontmatter["outputs"]),
        plan_hints=tuple(frontmatter.get("plan_hints", [])),
        verify_hints=tuple(frontmatter.get("verify_hints", [])),
        tags=tuple(frontmatter.get("tags", [])),
        enabled=enabled,
        priority=priority,
        root_dir=str(resolved_file.parent),
        skill_file=str(resolved_file),
    )
    validate_skill_manifest(manifest)
    return manifest
