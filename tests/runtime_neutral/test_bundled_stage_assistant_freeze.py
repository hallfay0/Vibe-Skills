from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FREEZE_SCRIPT = REPO_ROOT / "scripts" / "runtime" / "Freeze-RuntimeInputPacket.ps1"


def resolve_powershell() -> str | None:
    candidates = [
        shutil.which("pwsh"),
        shutil.which("pwsh.exe"),
        r"C:\Program Files\PowerShell\7\pwsh.exe",
        r"C:\Program Files\PowerShell\7-preview\pwsh.exe",
        shutil.which("powershell"),
        shutil.which("powershell.exe"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(Path(candidate))
    return None


def selected_skill_ids(packet: dict[str, object]) -> list[str]:
    routing = packet.get("skill_routing")
    if isinstance(routing, dict):
        selected = routing.get("selected")
        if isinstance(selected, list) and selected:
            return [str(item.get("skill_id") or "") for item in selected if isinstance(item, dict) and str(item.get("skill_id") or "")]
    work_binding = packet.get("work_binding")
    if not isinstance(work_binding, dict):
        return []
    units = work_binding.get("units")
    if not isinstance(units, list):
        return []
    return [str(unit.get("bound_skill") or "") for unit in units if isinstance(unit, dict) and str(unit.get("bound_skill") or "")]


class BundledStageAssistantFreezeTests(unittest.TestCase):
    def test_runtime_freeze_keeps_vibe_runtime_authority_and_splits_stage_assistants_from_specialists(self) -> None:
        shell = resolve_powershell()
        if shell is None:
            self.skipTest("PowerShell executable not available in PATH")

        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            target_root = root / "home" / ".agents"
            skill_dir = target_root / "skills" / "scientific-visualization"
            skill_dir.mkdir(parents=True)
            task = "Create a journal-ready multi-panel figure with a colorblind-safe palette and vector export."
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: {task}\ndescription: scientific-visualization handles journal-ready figures.\n---\n# Scientific Visualization\n",
                encoding="utf-8",
                newline="\n",
            )
            env = os.environ.copy()
            env["VCO_HOST_ID"] = "codex"
            env["VIBE_AGENTS_HOME"] = str(target_root)
            artifact_root = root / "artifacts"
            run_id = "pytest-bundled-stage-assistant"
            command = [
                shell,
                "-NoLogo",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(FREEZE_SCRIPT),
                "-Task",
                task,
                "-Mode",
                "interactive_governed",
                "-RunId",
                run_id,
                "-ArtifactRoot",
                str(artifact_root),
            ]
            subprocess.run(command, cwd=REPO_ROOT, env=env, capture_output=True, text=True, encoding="utf-8", check=True)

            packet_path = next(artifact_root.rglob("runtime-input-packet.json"))
            packet = json.loads(packet_path.read_text(encoding="utf-8"))

            self.assertNotIn("runtime_selected_skill", packet["divergence_shadow"])
            self.assertEqual("scientific-visualization", packet["work_binding"]["units"][0]["bound_skill"])
            self.assertNotIn("selected_skill", packet["route_snapshot"])
            self.assertNotIn("legacy_skill_routing", packet)
            self.assertNotIn("specialist_recommendations", packet)
            self.assertNotIn("stage_assistant_hints", packet)

            candidate_ids = [item["skill_id"] for item in packet["skill_routing"]["candidates"]]
            self.assertNotIn("matplotlib", candidate_ids)
            self.assertNotIn("seaborn", candidate_ids)
            self.assertNotIn("plotly", candidate_ids)

            selected_ids = selected_skill_ids(packet)
            self.assertEqual(["scientific-visualization"], selected_ids)


if __name__ == "__main__":
    unittest.main()
