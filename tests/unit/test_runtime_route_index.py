from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_SRC = ROOT / "packages" / "runtime-core" / "src"
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
for src in (RUNTIME_SRC, CONTRACTS_SRC):
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))

from vgo_contracts.discoverable_entry_surface import load_discoverable_entry_surface
from vgo_runtime.route_index import load_runtime_route_index


def test_runtime_route_index_is_projected_from_discoverable_entry_surface() -> None:
    surface = load_discoverable_entry_surface(ROOT)
    payload = load_runtime_route_index()

    assert payload["generated_at"] == "discoverable-entry-surface-projection"
    assert payload["roots"] == ["config/vibe-entry-surfaces.json"]

    skills = payload["skills"]
    assert [entry["id"] for entry in skills] == [entry.id for entry in surface.entries]
    assert skills[0]["name"] == surface.entries[0].display_name
    assert skills[0]["source_kind"] == "runtime_surface"
    assert skills[0]["source_root"] == "config/vibe-entry-surfaces.json"
    assert skills[0]["source_order"] == 0
    assert skills[-1]["source_order"] == len(skills) - 1
    assert skills[0]["resolved_skill_file"].endswith("config\\vibe-entry-surfaces.json") or skills[0]["resolved_skill_file"].endswith("config/vibe-entry-surfaces.json")
    assert skills[0]["resolved_root_dir"].endswith("config")
    assert skills[0]["path_contract"] == "runtime_surface_relative"
    assert (Path(skills[0]["path_base"]) / skills[0]["source_root"]).resolve() == Path(skills[0]["resolved_source_root"]).resolve()
    assert next(entry for entry in skills if entry["id"] == "vibe-upgrade")["publicly_exposed"] is True
    assert next(entry for entry in skills if entry["id"] == "vibe-how-do-we-do")["publicly_exposed"] is False
    assert next(entry for entry in skills if entry["id"] == "vibe-upgrade")["tags"] == [
        "upgrade",
        "install",
        "runtime",
    ]
    assert next(entry for entry in skills if entry["id"] == "vibe-how-do-we-do")["when_to_use"] == [
        "plan the work",
        "architecture design",
        "implementation plan",
        "execution design",
    ]


def test_router_readme_marks_router_as_candidate_discovery_surface() -> None:
    text = (ROOT / "scripts" / "router" / "README.md").read_text(encoding="utf-8").lower()

    assert "candidate" in text
    assert "compatibility" in text
    assert "kernel" in text
