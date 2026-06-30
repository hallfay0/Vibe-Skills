from __future__ import annotations

from pathlib import Path
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_SRC = REPO_ROOT / "packages" / "runtime-core" / "src"
if str(RUNTIME_SRC) not in sys.path:
    sys.path.insert(0, str(RUNTIME_SRC))

from vgo_runtime.kernel.skill_index import build_skill_index, write_skill_index
from vgo_runtime.kernel.skill_manifest import parse_skill_manifest


def _write_skill(skill_dir: Path, frontmatter: str, body: str = "# Skill\n") -> Path:
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(frontmatter + "\n" + body, encoding="utf-8")
    return skill_file


def test_parse_skill_manifest_reads_required_contract_fields(tmp_path: Path) -> None:
    skill_file = _write_skill(
        tmp_path / "skill-a",
        """---
id: code-review
name: Code Review
description: Review implementation risk.
when_to_use:
  - The user asks for a review.
not_for:
  - Building a feature from scratch.
inputs:
  - changed files
outputs:
  - findings
enabled: true
priority: 50
---""",
    )

    manifest = parse_skill_manifest(skill_file)

    assert manifest.id == "code-review"
    assert manifest.name == "Code Review"
    assert manifest.description == "Review implementation risk."
    assert manifest.when_to_use == ("The user asks for a review.",)
    assert manifest.not_for == ("Building a feature from scratch.",)
    assert manifest.inputs == ("changed files",)
    assert manifest.outputs == ("findings",)
    assert manifest.enabled is True
    assert manifest.priority == 50


def test_build_skill_index_collects_local_and_starter_skills(tmp_path: Path) -> None:
    agent_root = tmp_path / "agent-root"
    vibe_root = agent_root / "vibe"
    _write_skill(
        vibe_root / "skills" / "local" / "code-review",
        """---
id: code-review
name: Code Review
description: Review implementation risk.
when_to_use:
  - The user asks for a review.
not_for:
  - Building a feature from scratch.
inputs:
  - changed files
outputs:
  - findings
enabled: true
---""",
    )
    _write_skill(
        vibe_root / "skills" / "starter" / "write-plan",
        """---
id: write-plan
name: Write Plan
description: Turn a task into explicit work steps.
when_to_use:
  - The user needs a plan.
not_for:
  - Final verification.
inputs:
  - task goal
outputs:
  - work plan
enabled: true
---""",
    )

    payload = build_skill_index(agent_root)
    index_path = write_skill_index(agent_root, payload)

    assert payload["roots"] == ["skills/local", "skills/starter"]
    assert payload["catalog_source_kinds"] == ["local", "starter"]
    assert payload["active_source_kinds"] == ["local", "starter"]
    assert payload["catalog_source_roots"] == [
        {
            "source_kind": "local",
            "source_root": "skills/local",
            "resolved_source_root": str((vibe_root / "skills" / "local").resolve()),
            "source_priority": 0,
            "source_order": 0,
        },
        {
            "source_kind": "starter",
            "source_root": "skills/starter",
            "resolved_source_root": str((vibe_root / "skills" / "starter").resolve()),
            "source_priority": 2,
            "source_order": 1,
        },
    ]
    assert [entry["id"] for entry in payload["skills"]] == ["code-review", "write-plan"]
    assert payload["skills"][0]["root_dir"] == "skills/local/code-review"
    assert payload["skills"][0]["path_contract"] == "vibe_relative"
    assert payload["skills"][0]["path_base"] == str(vibe_root.resolve())
    assert payload["skills"][0]["resolved_root_dir"] == str((vibe_root / "skills" / "local" / "code-review").resolve())
    assert payload["skills"][0]["resolved_skill_file"] == str(
        (vibe_root / "skills" / "local" / "code-review" / "SKILL.md").resolve()
    )
    assert payload["skills"][0]["outputs"] == ["findings"]
    assert payload["skills"][1]["outputs"] == ["work plan"]
    assert payload["skills"][1]["skill_file"] == "skills/starter/write-plan/SKILL.md"
    assert payload["skills"][1]["resolved_root_dir"] == str((vibe_root / "skills" / "starter" / "write-plan").resolve())
    assert payload["skills"][1]["resolved_skill_file"] == str(
        (vibe_root / "skills" / "starter" / "write-plan" / "SKILL.md").resolve()
    )
    assert index_path == vibe_root / "generated" / "skills-index.json"
    assert index_path.exists()


def test_build_skill_index_prefers_local_skill_over_starter_duplicate(tmp_path: Path) -> None:
    agent_root = tmp_path / "agent-root"
    vibe_root = agent_root / "vibe"
    local_frontmatter = """---
id: duplicate-skill
name: Local Duplicate Skill
description: The local copy should stay active.
when_to_use:
  - Use the local copy.
not_for:
  - Starter-only fallback.
inputs:
  - local input
outputs:
  - local output
enabled: true
priority: 10
---"""
    starter_frontmatter = """---
id: duplicate-skill
name: Starter Duplicate Skill
description: The starter copy should stay in the catalog but not active.
when_to_use:
  - Use the starter copy.
not_for:
  - Local overrides.
inputs:
  - starter input
outputs:
  - starter output
enabled: true
priority: 90
---"""
    _write_skill(vibe_root / "skills" / "local" / "one", local_frontmatter)
    _write_skill(vibe_root / "skills" / "starter" / "two", starter_frontmatter)

    payload = build_skill_index(agent_root)

    assert payload["roots"] == ["skills/local", "skills/starter"]
    assert [entry["id"] for entry in payload["skills"]] == ["duplicate-skill"]
    assert payload["skills"][0]["name"] == "Local Duplicate Skill"
    assert payload["skills"][0]["root_dir"] == "skills/local/one"
    assert payload["skills"][0]["skill_file"] == "skills/local/one/SKILL.md"
    assert payload["skills"][0]["source_kind"] == "local"
    assert payload["skills"][0]["source_root"] == "skills/local"
    assert payload["skills"][0]["source_priority"] == 0


def test_build_skill_index_rejects_duplicate_ids_inside_local_source(tmp_path: Path) -> None:
    agent_root = tmp_path / "agent-root"
    vibe_root = agent_root / "vibe"
    frontmatter = """---
id: duplicate-skill
name: Duplicate Skill
description: The local source cannot contain duplicate ids.
when_to_use:
  - Use it.
not_for:
  - Something else.
inputs:
  - input
outputs:
  - output
enabled: true
---"""
    _write_skill(vibe_root / "skills" / "local" / "one", frontmatter)
    _write_skill(vibe_root / "skills" / "local" / "two", frontmatter)

    with pytest.raises(ValueError, match="duplicate skill id .* within local source root 'skills/local'"):
        build_skill_index(agent_root)


def test_build_skill_index_rejects_duplicate_ids_inside_starter_source(tmp_path: Path) -> None:
    agent_root = tmp_path / "agent-root"
    vibe_root = agent_root / "vibe"
    frontmatter = """---
id: duplicate-skill
name: Duplicate Skill
description: The starter source cannot contain duplicate ids.
when_to_use:
  - Use it.
not_for:
  - Something else.
inputs:
  - input
outputs:
  - output
enabled: true
---"""
    _write_skill(vibe_root / "skills" / "starter" / "one", frontmatter)
    _write_skill(vibe_root / "skills" / "starter" / "two", frontmatter)

    with pytest.raises(ValueError, match="duplicate skill id .* within starter source root 'skills/starter'"):
        build_skill_index(agent_root)
