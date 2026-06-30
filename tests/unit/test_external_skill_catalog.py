from __future__ import annotations

from pathlib import Path
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_SRC = REPO_ROOT / "packages" / "runtime-core" / "src"
if str(RUNTIME_SRC) not in sys.path:
    sys.path.insert(0, str(RUNTIME_SRC))

from vgo_runtime.kernel.skill_index import build_skill_catalog, build_skill_index


def _write_skill(skill_dir: Path, frontmatter: str, body: str = "# Skill\n") -> Path:
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(frontmatter + "\n" + body, encoding="utf-8")
    return skill_file


def test_build_skill_catalog_collects_local_external_and_starter_entries(tmp_path: Path) -> None:
    agent_root = tmp_path / "agent-root"
    vibe_root = agent_root / "vibe"
    host_root = tmp_path / "host-skills"
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
priority: 5
---""",
    )
    _write_skill(
        host_root / "external-debugger",
        """---
id: external-debugger
name: External Debugger
description: Read-only external debugging guidance.
when_to_use:
  - The local catalog needs a debugger reference.
not_for:
  - Replacing local overrides.
inputs:
  - failure trace
outputs:
  - debugging steps
enabled: true
priority: 25
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
priority: 50
---""",
    )

    catalog = build_skill_catalog(agent_root=agent_root, host_roots=(host_root,))

    assert catalog["catalog_source_kinds"] == ["local", "host_external", "starter"]
    assert catalog["active_source_kinds"] == ["local", "host_external", "starter"]
    assert catalog["catalog_source_roots"] == [
        {
            "source_kind": "local",
            "source_root": "skills/local",
            "resolved_source_root": str((vibe_root / "skills" / "local").resolve()),
            "source_priority": 0,
            "source_order": 0,
        },
        {
            "source_kind": "host_external",
            "source_root": str(host_root.resolve()),
            "resolved_source_root": str(host_root.resolve()),
            "source_priority": 1,
            "source_order": 1,
        },
        {
            "source_kind": "starter",
            "source_root": "skills/starter",
            "resolved_source_root": str((vibe_root / "skills" / "starter").resolve()),
            "source_priority": 2,
            "source_order": 2,
        },
    ]
    assert [entry["id"] for entry in catalog["entries"]] == [
        "code-review",
        "external-debugger",
        "write-plan",
    ]
    assert [entry["source_kind"] for entry in catalog["entries"]] == [
        "local",
        "host_external",
        "starter",
    ]
    assert [entry["active"] for entry in catalog["entries"]] == [True, True, True]
    assert catalog["entries"][0]["root_dir"] == "skills/local/code-review"
    assert catalog["entries"][0]["skill_file"] == "skills/local/code-review/SKILL.md"
    assert catalog["entries"][0]["resolved_root_dir"] == str((vibe_root / "skills" / "local" / "code-review").resolve())
    assert catalog["entries"][0]["resolved_skill_file"] == str(
        (vibe_root / "skills" / "local" / "code-review" / "SKILL.md").resolve()
    )
    assert catalog["entries"][0]["path_contract"] == "vibe_relative"
    assert catalog["entries"][0]["path_base"] == str(vibe_root.resolve())
    assert catalog["entries"][0]["source_root"] == "skills/local"
    assert catalog["entries"][1]["root_dir"] == "external-debugger"
    assert catalog["entries"][1]["skill_file"] == "external-debugger/SKILL.md"
    assert catalog["entries"][1]["resolved_root_dir"] == str((host_root / "external-debugger").resolve())
    assert catalog["entries"][1]["resolved_skill_file"] == str(
        (host_root / "external-debugger" / "SKILL.md").resolve()
    )
    assert catalog["entries"][1]["path_contract"] == "source_root_relative"
    assert catalog["entries"][1]["path_base"] == str(host_root.resolve())
    assert catalog["entries"][1]["source_root"] == str(host_root.resolve())
    assert catalog["entries"][1]["source_priority"] == 1
    assert catalog["entries"][1]["source_order"] == 1
    assert catalog["entries"][2]["source_root"] == "skills/starter"
    assert catalog["entries"][2]["source_priority"] == 2


def test_build_skill_catalog_marks_duplicate_entries_inactive_by_precedence(tmp_path: Path) -> None:
    agent_root = tmp_path / "agent-root"
    vibe_root = agent_root / "vibe"
    host_root = tmp_path / "host-skills"
    _write_skill(
        vibe_root / "skills" / "local" / "duplicate-local",
        """---
id: duplicate-skill
name: Local Duplicate Skill
description: Local should win duplicate resolution.
when_to_use:
  - Local override is available.
not_for:
  - Starter fallback only.
inputs:
  - local input
outputs:
  - local output
enabled: true
priority: 5
---""",
    )
    _write_skill(
        host_root / "duplicate-external",
        """---
id: duplicate-skill
name: External Duplicate Skill
description: External should stay in the catalog but not active.
when_to_use:
  - External reference exists.
not_for:
  - Local override exists.
inputs:
  - external input
outputs:
  - external output
enabled: true
priority: 25
---""",
    )
    _write_skill(
        vibe_root / "skills" / "starter" / "duplicate-starter",
        """---
id: duplicate-skill
name: Starter Duplicate Skill
description: Starter should stay in the catalog but not active.
when_to_use:
  - Starter fallback exists.
not_for:
  - Local override exists.
inputs:
  - starter input
outputs:
  - starter output
enabled: true
priority: 50
---""",
    )

    catalog = build_skill_catalog(agent_root=agent_root, host_roots=(host_root,))

    assert [entry["source_kind"] for entry in catalog["entries"]] == [
        "local",
        "host_external",
        "starter",
    ]
    assert [entry["active"] for entry in catalog["entries"]] == [True, False, False]


def test_build_skill_catalog_rejects_duplicate_ids_inside_single_external_root(tmp_path: Path) -> None:
    agent_root = tmp_path / "agent-root"
    host_root = tmp_path / "host-skills"
    frontmatter = """---
id: duplicate-skill
name: Duplicate Skill
description: One external root cannot define the same id twice.
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
    _write_skill(host_root / "one", frontmatter)
    _write_skill(host_root / "two", frontmatter)

    with pytest.raises(
        ValueError,
        match="duplicate skill id .* within host_external source root",
    ):
        build_skill_catalog(agent_root=agent_root, host_roots=(host_root,))


def test_build_skill_catalog_keeps_external_root_order_explicit_for_duplicate_ids(tmp_path: Path) -> None:
    agent_root = tmp_path / "agent-root"
    first_host_root = tmp_path / "host-skills-a"
    second_host_root = tmp_path / "host-skills-b"
    _write_skill(
        first_host_root / "duplicate-external",
        """---
id: shared-skill
name: First External Skill
description: The first external root should win.
when_to_use:
  - The first external root is preferred.
not_for:
  - Lower-priority external duplicates.
inputs:
  - first input
outputs:
  - first output
enabled: true
---""",
    )
    _write_skill(
        second_host_root / "duplicate-external",
        """---
id: shared-skill
name: Second External Skill
description: The second external root should stay inactive.
when_to_use:
  - The second external root is available.
not_for:
  - Winning precedence.
inputs:
  - second input
outputs:
  - second output
enabled: true
---""",
    )

    catalog = build_skill_catalog(agent_root=agent_root, host_roots=(first_host_root, second_host_root))

    assert catalog["catalog_source_roots"] == [
        {
            "source_kind": "local",
            "source_root": "skills/local",
            "resolved_source_root": str((agent_root / "vibe" / "skills" / "local").resolve()),
            "source_priority": 0,
            "source_order": 0,
        },
        {
            "source_kind": "host_external",
            "source_root": str(first_host_root.resolve()),
            "resolved_source_root": str(first_host_root.resolve()),
            "source_priority": 1,
            "source_order": 1,
        },
        {
            "source_kind": "host_external",
            "source_root": str(second_host_root.resolve()),
            "resolved_source_root": str(second_host_root.resolve()),
            "source_priority": 1,
            "source_order": 2,
        },
        {
            "source_kind": "starter",
            "source_root": "skills/starter",
            "resolved_source_root": str((agent_root / "vibe" / "skills" / "starter").resolve()),
            "source_priority": 2,
            "source_order": 3,
        },
    ]
    assert [entry["name"] for entry in catalog["entries"]] == [
        "First External Skill",
        "Second External Skill",
    ]
    assert [entry["source_order"] for entry in catalog["entries"]] == [1, 2]
    assert [entry["active"] for entry in catalog["entries"]] == [True, False]
    assert catalog["active_source_kinds"] == ["host_external"]
    assert catalog["active_source_roots"] == [
        {
            "source_kind": "host_external",
            "source_root": str(first_host_root.resolve()),
            "resolved_source_root": str(first_host_root.resolve()),
            "source_priority": 1,
            "source_order": 1,
        }
    ]


def test_build_skill_index_includes_active_host_external_skill_when_host_roots_exist(tmp_path: Path) -> None:
    agent_root = tmp_path / "agent-root"
    host_root = tmp_path / "host-skills"
    _write_skill(
        host_root / "external-debugger",
        """---
id: external-debugger
name: External Debugger
description: Read-only external debugging guidance.
when_to_use:
  - The local catalog needs a debugger reference.
not_for:
  - Replacing local overrides.
inputs:
  - failure trace
outputs:
  - debugging steps
enabled: true
priority: 25
---""",
    )

    payload = build_skill_index(agent_root, host_roots=(host_root,))

    assert payload["roots"] == ["skills/local", "skills/starter"]
    assert payload["catalog_source_kinds"] == ["local", "host_external", "starter"]
    assert payload["active_source_kinds"] == ["host_external"]
    assert [entry["id"] for entry in payload["skills"]] == ["external-debugger"]
    assert payload["skills"][0]["source_kind"] == "host_external"
    assert payload["skills"][0]["source_root"] == str(host_root.resolve())
    assert payload["skills"][0]["source_priority"] == 1
    assert payload["skills"][0]["source_order"] == 1
    assert payload["skills"][0]["root_dir"] == "external-debugger"
    assert payload["skills"][0]["skill_file"] == "external-debugger/SKILL.md"
    assert payload["skills"][0]["resolved_root_dir"] == str((host_root / "external-debugger").resolve())
    assert payload["skills"][0]["resolved_skill_file"] == str(
        (host_root / "external-debugger" / "SKILL.md").resolve()
    )
    assert payload["skills"][0]["path_contract"] == "source_root_relative"
    assert payload["skills"][0]["path_base"] == str(host_root.resolve())
