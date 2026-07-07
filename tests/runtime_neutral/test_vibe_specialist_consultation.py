from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_SCRIPT = REPO_ROOT / "scripts" / "runtime" / "invoke-vibe-runtime.ps1"
CONSULTATION_SCRIPT = REPO_ROOT / "scripts" / "runtime" / "VibeConsultation.Common.ps1"
CONSULTATION_POLICY = REPO_ROOT / "config" / "specialist-consultation-policy.json"
SPECIALIST_TASK = "I have a failing test and a stack trace. Help me debug systematically before proposing fixes."


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


def ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def run_runtime(task: str, artifact_root: Path) -> dict[str, object]:
    shell = resolve_powershell()
    if shell is None:
        raise unittest.SkipTest("PowerShell executable not available")

    run_id = "pytest-retired-consultation-" + uuid.uuid4().hex[:10]
    completed = subprocess.run(
        [
            shell,
            "-NoLogo",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            (
                "& { "
                f"$result = & {ps_quote(str(RUNTIME_SCRIPT))} "
                f"-Task {ps_quote(task)} "
                "-Mode interactive_governed "
                f"-RunId {ps_quote(run_id)} "
                f"-ArtifactRoot {ps_quote(str(artifact_root))}; "
                "$result | ConvertTo-Json -Depth 20 }"
            ),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        env={
            **os.environ,
            "VGO_DISABLE_NATIVE_SPECIALIST_EXECUTION": "1",
            "VGO_ENABLE_NATIVE_SPECIALIST_EXECUTION": "0",
            "VGO_SPECIALIST_CONSULTATION_MODE": "",
            "VGO_NATIVE_SPECIALIST_EXECUTION_MODE": "",
        },
    )
    return json.loads(completed.stdout)


class VibeSpecialistConsultationTests(unittest.TestCase):
    def test_consultation_module_declares_retired_old_routing_boundary(self) -> None:
        text = CONSULTATION_SCRIPT.read_text(encoding="utf-8")
        policy = json.loads(CONSULTATION_POLICY.read_text(encoding="utf-8"))
        compatibility_note = str(policy["compatibility_note"])

        self.assertIn("retired_old_routing_compat", text)
        self.assertIn("Old specialist consultation compatibility is retired", text)
        self.assertIn("work_binding", text)
        self.assertIn("optional compatibility mirror", text)
        self.assertNotIn("skill_routing.selected plus skill_usage.used / skill_usage.unused", text)
        self.assertIn("work_binding", compatibility_note)
        self.assertIn("optional compatibility mirror", compatibility_note)
        self.assertNotIn("skill_routing.selected plus skill_usage.used and skill_usage.unused", compatibility_note)

    def test_runtime_keeps_freeze_green_without_default_consultation(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            payload = run_runtime(SPECIALIST_TASK, Path(tempdir))
            artifacts = payload["summary"]["artifacts"]
            session_root = Path(payload["session_root"])

            self.assertIsNone(artifacts.get("discussion_specialist_consultation"))
            self.assertIsNone(artifacts.get("planning_specialist_consultation"))
            self.assertEqual([], sorted(path.name for path in session_root.glob("*specialist-consultation*.json")))


if __name__ == "__main__":
    unittest.main()
