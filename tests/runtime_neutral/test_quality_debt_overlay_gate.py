from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class QualityDebtOverlayGateTests(unittest.TestCase):
    @unittest.skipIf(shutil.which("powershell") is None, "PowerShell executable not available in PATH")
    def test_quality_debt_overlay_gate_restores_policy_bytes(self) -> None:
        policy_path = REPO_ROOT / "config" / "quality-debt-overlay.json"
        script_path = REPO_ROOT / "scripts" / "verify" / "vibe-quality-debt-overlay-gate.ps1"
        original_bytes = policy_path.read_bytes()

        try:
            completed = subprocess.run(
                ["powershell", "-NoLogo", "-NoProfile", "-File", str(script_path)],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,
                check=False,
            )

            self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
            self.assertEqual(original_bytes, policy_path.read_bytes())

            diff = subprocess.run(
                ["git", "diff", "--quiet", "--", "config/quality-debt-overlay.json"],
                cwd=REPO_ROOT,
                check=False,
            )
            self.assertEqual(0, diff.returncode)
        finally:
            policy_path.write_bytes(original_bytes)


if __name__ == "__main__":
    unittest.main()
