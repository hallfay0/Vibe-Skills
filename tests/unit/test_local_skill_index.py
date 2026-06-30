from __future__ import annotations

from pathlib import Path
import sys


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


def test_build_skill_index_collects_vibe_local_skills(tmp_path: Path) -> None:
    agent_root = tmp_path / "home" / ".agents"
    vibe_root = agent_root / "vibe"
    skill_path = _write_skill(
        vibe_root / "skills" / "local" / "code-review",
        """---
name: Code Review
description: Review implementation risk.
tags:
  - review
  - testing
---""",
    )

    payload = build_skill_index(agent_root)
    index_path = write_skill_index(agent_root, payload)

    assert payload["schema_version"] == "local_skill_index_v2"
    assert payload["roots"] == ["skills/local"]
    assert payload["catalog_source_kinds"] == ["vibe_local"]
    assert payload["active_source_kinds"] == ["vibe_local"]
    assert [entry["skill_id"] for entry in payload["skills"]] == ["code-review"]
    assert payload["skills"][0]["display_name"] == "Code Review"
    assert payload["skills"][0]["source_kind"] == "vibe_local"
    assert payload["skills"][0]["native_skill_entrypoint"] == str(skill_path.resolve())
    assert payload["skills"][0]["tags"] == ["review", "testing"]
    assert index_path == vibe_root / "generated" / "skills-index.json"
    assert index_path.exists()


def test_build_skill_index_host_roots_precede_vibe_local_duplicates(tmp_path: Path) -> None:
    agent_root = tmp_path / "home" / ".agents"
    host_root = tmp_path / "host-skills"
    vibe_root = agent_root / "vibe"
    host_skill = _write_skill(
        host_root / "duplicate-skill",
        """---
name: Host Duplicate Skill
description: The host-installed copy should stay active.
---""",
    )
    _write_skill(
        vibe_root / "skills" / "local" / "duplicate-skill",
        """---
name: Vibe Local Duplicate Skill
description: The Vibe local copy should stay inactive.
---""",
    )

    payload = build_skill_index(agent_root, host_roots=(host_root,))

    assert payload["roots"] == [str(host_root.resolve()), "skills/local"]
    assert [entry["skill_id"] for entry in payload["skills"]] == ["duplicate-skill"]
    assert payload["skills"][0]["display_name"] == "Host Duplicate Skill"
    assert payload["skills"][0]["source_kind"] == "host_installed"
    assert payload["skills"][0]["native_skill_entrypoint"] == str(host_skill.resolve())
    duplicate = payload["discovery_diagnostics"]["duplicates"][0]
    assert duplicate["skill_id"] == "duplicate-skill"
    assert duplicate["active_entrypoint"] == str(host_skill.resolve())


def test_build_skill_index_records_invalid_local_entries_without_activating_them(tmp_path: Path) -> None:
    agent_root = tmp_path / "home" / ".agents"
    vibe_root = agent_root / "vibe"
    _write_skill(
        vibe_root / "skills" / "local" / "missing-description",
        """---
name: Missing Description
---""",
    )
    (vibe_root / "skills" / "local" / "missing-file").mkdir(parents=True)
    _write_skill(
        vibe_root / "skills" / "local" / "usable",
        """---
name: Usable
description: A real local skill.
---""",
    )

    payload = build_skill_index(agent_root)

    assert [entry["skill_id"] for entry in payload["skills"]] == ["usable"]
    reasons = {
        item["skill_id"]: item["reason"]
        for item in payload["discovery_diagnostics"]["invalid_entries"]
    }
    assert reasons["missing-description"] == "missing_required_frontmatter"
    assert reasons["missing-file"] == "missing_skill_md"
