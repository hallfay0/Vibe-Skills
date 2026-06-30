from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess

from .errors import CliError
from .process import print_process_output


def parse_json_output(result: subprocess.CompletedProcess[str]) -> dict:
    if result.returncode != 0:
        print_process_output(result)
        raise CliError('core command failed')
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        print_process_output(result)
        raise CliError(f'Invalid JSON output from core command: {exc}') from exc


def print_install_completion_hint(frontend: str, *, host_id: str, profile: str, target_root: Path) -> None:
    if frontend == 'powershell':
        shell_name = 'pwsh' if shutil.which('pwsh') else 'powershell'
        print('')
        print('Installation complete.')
        print(f'Run: {shell_name} -NoProfile -File .\\check.ps1 -Profile {profile} -HostId {host_id} -TargetRoot {target_root}')
        return
    print(f'Install done. Run: bash check.sh --profile {profile} --host {host_id} --target-root {target_root}')


def print_install_completion_report(
    frontend: str,
    *,
    host_id: str,
    profile: str,
    target_root: Path,
    install_receipt: dict[str, object],
) -> None:
    host_runtime = install_receipt.get('host_runtime') if isinstance(install_receipt, dict) else {}
    vibe_host_ready = 'unknown'
    if isinstance(host_runtime, dict) and 'vibe_host_ready' in host_runtime:
        vibe_host_ready = bool(host_runtime.get('vibe_host_ready'))
    print('')
    print('Install completion summary')
    print(f'- host: {host_id}')
    print(f'- profile: {profile}')
    print(f'- target_root: {target_root}')
    if isinstance(install_receipt, dict):
        runtime_root = install_receipt.get('runtime_root')
        bridge_root = install_receipt.get('host_bridge_root')
        layout_mode = install_receipt.get('runtime_layout_mode')
        if runtime_root:
            print(f'- runtime_root: {runtime_root}')
        if bridge_root:
            print(f'- host_bridge_root: {bridge_root}')
        if layout_mode:
            print(f'- runtime_layout_mode: {layout_mode}')
    print('- installed_locally: True')
    print(f'- vibe_host_ready: {vibe_host_ready}')
    print('- completed_parts: runtime payload installed; post-install gates reconciled')
    print(f'- online_ready: verify separately with the router connectivity probe for {target_root}')
    print('- manual_follow_up: none')



def print_install_banner(host_id: str, install_mode: str, profile: str, target_root: Path, args: object) -> None:
    print('=== VCO Adapter Installer ===')
    print(f'Host   : {host_id}')
    print(f'Mode   : {install_mode}')
    print(f'Profile: {profile}')
    print(f'Target : {target_root}')
    print(f'StrictOffline: {bool(getattr(args, "strict_offline", False))}')
    print(f'RequireClosedReady: {bool(getattr(args, "require_closed_ready", False))}')
    print(f'AllowExternalSkillFallback: {bool(getattr(args, "allow_external_skill_fallback", False))}')
    print(f'SkipRuntimeFreshnessGate: {bool(getattr(args, "skip_runtime_freshness_gate", False))}')



def print_json_payload(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
