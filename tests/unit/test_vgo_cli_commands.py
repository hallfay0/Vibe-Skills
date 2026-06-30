from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
CLI_SRC = REPO_ROOT / 'apps' / 'vgo-cli' / 'src'
if str(CLI_SRC) not in sys.path:
    sys.path.insert(0, str(CLI_SRC))

from vgo_cli.commands import canonical_entry_command, compatibility_exit_command, index_command, inspect_run_command, install_command, locate_entry_command, route_command, run_command, runtime_command, upgrade_command, verify_command
from vgo_cli.errors import CliError
from vgo_cli.main import build_parser
from vgo_cli.output import parse_json_output, print_install_completion_hint, print_json_payload


def test_parse_json_output_returns_payload() -> None:
    result = subprocess.CompletedProcess(args=['x'], returncode=0, stdout='{"ok": true}', stderr='')

    assert parse_json_output(result) == {'ok': True}


def test_parse_json_output_rejects_invalid_json() -> None:
    result = subprocess.CompletedProcess(args=['x'], returncode=0, stdout='not-json', stderr='')

    with pytest.raises(CliError, match='Invalid JSON output from core command'):
        parse_json_output(result)


def test_print_install_completion_hint_for_shell_includes_host(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    print_install_completion_hint('shell', host_id='cursor', profile='full', target_root=tmp_path)

    captured = capsys.readouterr()
    assert f'Install done. Run: bash check.sh --profile full --host cursor --target-root {tmp_path}' in captured.out


def test_print_install_completion_hint_for_powershell_includes_host(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    print_install_completion_hint('powershell', host_id='cursor', profile='full', target_root=tmp_path)

    captured = capsys.readouterr()
    assert '-HostId cursor' in captured.out
    assert f'-TargetRoot {tmp_path}' in captured.out


def test_route_command_delegates_to_runtime_core_bridge(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import vgo_cli.commands as cli_commands

    recorded: dict[str, object] = {}

    def fake_run_router_core(repo_root: Path, argv: list[str]) -> subprocess.CompletedProcess[str]:
        recorded['repo_root'] = repo_root
        recorded['argv'] = list(argv)
        return subprocess.CompletedProcess(args=list(argv), returncode=0, stdout='{"ok": true}\n', stderr='')

    def fake_print(result: subprocess.CompletedProcess[str]) -> None:
        recorded['printed_stdout'] = result.stdout

    monkeypatch.setattr(cli_commands, 'run_router_core', fake_run_router_core)
    monkeypatch.setattr(cli_commands, 'print_process_output', fake_print)

    args = argparse.Namespace(
        repo_root=str(tmp_path),
        prompt='route this',
        grade='XL',
        task_type='debug',
        requested_skill='vibe',
        host_id='codex',
        target_root='/tmp/codex',
        force_runtime_neutral=True,
    )

    assert route_command(args) == 0
    assert recorded['repo_root'] == tmp_path.resolve()
    assert recorded['argv'] == [
        '--prompt', 'route this',
        '--grade', 'XL',
        '--task-type', 'debug',
        '--requested-skill', 'vibe',
        '--host-id', 'codex',
        '--target-root', '/tmp/codex',
        '--force-runtime-neutral',
    ]
    assert recorded['printed_stdout'] == '{"ok": true}\n'


def test_index_command_delegates_to_runtime_core_bridge(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import vgo_cli.commands as cli_commands

    recorded: dict[str, object] = {}

    def fake_run_skill_index_core(repo_root: Path, argv: list[str]) -> subprocess.CompletedProcess[str]:
        recorded["repo_root"] = repo_root
        recorded["argv"] = list(argv)
        return subprocess.CompletedProcess(args=list(argv), returncode=0, stdout='{"skill_count": 1}\n', stderr="")

    def fake_print(result: subprocess.CompletedProcess[str]) -> None:
        recorded["printed_stdout"] = result.stdout

    monkeypatch.setattr(cli_commands, "run_skill_index_core", fake_run_skill_index_core)
    monkeypatch.setattr(cli_commands, "print_process_output", fake_print)

    args = argparse.Namespace(
        repo_root=str(tmp_path / "repo"),
        agent_root=str(tmp_path / "agent"),
        host_id="codex",
        workspace_root=str(tmp_path / "workspace"),
        json=True,
    )

    assert index_command(args) == 0
    assert recorded["repo_root"] == (tmp_path / "repo").resolve()
    assert recorded["argv"] == [
        "--agent-root", str(tmp_path / "agent"),
        "--host-id", "codex",
        "--workspace-root", str(tmp_path / "workspace"),
        "--json",
    ]
    assert recorded["printed_stdout"] == '{"skill_count": 1}\n'


def test_run_command_delegates_to_runtime_core_bridge(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import vgo_cli.commands as cli_commands

    recorded: dict[str, object] = {}

    def fake_run_local_kernel_core(repo_root: Path, argv: list[str]) -> subprocess.CompletedProcess[str]:
        recorded["repo_root"] = repo_root
        recorded["argv"] = list(argv)
        return subprocess.CompletedProcess(args=list(argv), returncode=0, stdout='{"run_id": "run-1"}\n', stderr="")

    def fake_print(result: subprocess.CompletedProcess[str]) -> None:
        recorded["printed_stdout"] = result.stdout

    monkeypatch.setattr(cli_commands, "run_local_kernel_core", fake_run_local_kernel_core)
    monkeypatch.setattr(cli_commands, "print_process_output", fake_print)

    args = argparse.Namespace(
        repo_root=str(tmp_path / "repo"),
        agent_root=str(tmp_path / "agent"),
        prompt="Review the runtime redesign.",
        run_id="run-1",
        host_id="codex",
        workspace_root=str(tmp_path / "workspace"),
        json=True,
    )

    assert run_command(args) == 0
    assert recorded["repo_root"] == (tmp_path / "repo").resolve()
    assert recorded["argv"] == [
        "--agent-root", str(tmp_path / "agent"),
        "--prompt", "Review the runtime redesign.",
        "--run-id", "run-1",
        "--host-id", "codex",
        "--workspace-root", str(tmp_path / "workspace"),
        "--json",
    ]
    assert recorded["printed_stdout"] == '{"run_id": "run-1"}\n'


def test_inspect_run_command_delegates_to_runtime_core_bridge(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import vgo_cli.commands as cli_commands

    recorded: dict[str, object] = {}

    def fake_run_inspect_run_core(repo_root: Path, argv: list[str]) -> subprocess.CompletedProcess[str]:
        recorded["repo_root"] = repo_root
        recorded["argv"] = list(argv)
        return subprocess.CompletedProcess(args=list(argv), returncode=0, stdout='{"run_id": "run-1", "summary": {"proof_ready": true}}\n', stderr="")

    def fake_print(result: subprocess.CompletedProcess[str]) -> None:
        recorded["printed_stdout"] = result.stdout

    monkeypatch.setattr(cli_commands, "run_inspect_run_core", fake_run_inspect_run_core)
    monkeypatch.setattr(cli_commands, "print_process_output", fake_print)

    args = argparse.Namespace(
        repo_root=str(tmp_path / "repo"),
        agent_root=str(tmp_path / "agent"),
        run_id="run-1",
        host_id="codex",
        workspace_root=str(tmp_path / "workspace"),
    )

    assert inspect_run_command(args) == 0
    assert recorded["repo_root"] == (tmp_path / "repo").resolve()
    assert recorded["argv"] == [
        "--agent-root", str(tmp_path / "agent"),
        "--run-id", "run-1",
        "--host-id", "codex",
        "--workspace-root", str(tmp_path / "workspace"),
    ]
    assert recorded["printed_stdout"] == '{"run_id": "run-1", "summary": {"proof_ready": true}}\n'


def test_locate_entry_command_delegates_to_runtime_core_bridge(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import vgo_cli.commands as cli_commands

    recorded: dict[str, object] = {}

    def fake_run_entry_locator_core(repo_root: Path, argv: list[str]) -> subprocess.CompletedProcess[str]:
        recorded["repo_root"] = repo_root
        recorded["argv"] = list(argv)
        return subprocess.CompletedProcess(args=list(argv), returncode=0, stdout='{"primary_entry_file":"x.py"}\n', stderr="")

    def fake_print(result: subprocess.CompletedProcess[str]) -> None:
        recorded["printed_stdout"] = result.stdout

    monkeypatch.setattr(cli_commands, "run_entry_locator_core", fake_run_entry_locator_core)
    monkeypatch.setattr(cli_commands, "print_process_output", fake_print)

    args = argparse.Namespace(
        repo_root=str(tmp_path / "repo"),
        change_kind="planning",
    )

    assert locate_entry_command(args) == 0
    assert recorded["repo_root"] == (tmp_path / "repo").resolve()
    assert recorded["argv"] == [
        "--repo-root", str((tmp_path / "repo").resolve()),
        "--change-kind", "planning",
    ]
    assert recorded["printed_stdout"] == '{"primary_entry_file":"x.py"}\n'


def test_compatibility_exit_command_delegates_to_runtime_core_bridge(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import vgo_cli.commands as cli_commands

    recorded: dict[str, object] = {}

    def fake_run_compatibility_exit_core(repo_root: Path, argv: list[str]) -> subprocess.CompletedProcess[str]:
        recorded["repo_root"] = repo_root
        recorded["argv"] = list(argv)
        return subprocess.CompletedProcess(args=list(argv), returncode=0, stdout='{"controlled_capabilities":[]}\n', stderr="")

    def fake_print(result: subprocess.CompletedProcess[str]) -> None:
        recorded["printed_stdout"] = result.stdout

    monkeypatch.setattr(cli_commands, "run_compatibility_exit_core", fake_run_compatibility_exit_core)
    monkeypatch.setattr(cli_commands, "print_process_output", fake_print)

    args = argparse.Namespace(
        repo_root=str(tmp_path / "repo"),
    )

    assert compatibility_exit_command(args) == 0
    assert recorded["repo_root"] == (tmp_path / "repo").resolve()
    assert recorded["argv"] == [
        "--repo-root", str((tmp_path / "repo").resolve()),
    ]
    assert recorded["printed_stdout"] == '{"controlled_capabilities":[]}\n'


def test_canonical_entry_command_delegates_to_runtime_core_bridge(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import vgo_cli.commands as cli_commands

    recorded: dict[str, object] = {}

    def fake_run_canonical_entry_core(repo_root: Path, argv: list[str]) -> subprocess.CompletedProcess[str]:
        recorded['repo_root'] = repo_root
        recorded['argv'] = list(argv)
        return subprocess.CompletedProcess(args=list(argv), returncode=0, stdout='{"run_id":"r1"}\n', stderr='')

    def fake_print(result: subprocess.CompletedProcess[str]) -> None:
        recorded['printed_stdout'] = result.stdout

    monkeypatch.setattr(cli_commands, 'run_canonical_entry_core', fake_run_canonical_entry_core)
    monkeypatch.setattr(cli_commands, 'print_process_output', fake_print)
    monkeypatch.setattr(cli_commands, 'normalize_host_id', lambda host_id: 'codex')

    args = argparse.Namespace(
        repo_root=str(tmp_path),
        prompt='plan runtime entry hardening',
        host_id='CoDeX',
        entry_id='vibe',
        requested_stage_stop='phase_cleanup',
        requested_grade_floor='XL',
        artifact_root=str(tmp_path / 'artifacts'),
        local_agent_root=str(tmp_path / 'agent-root'),
        run_id='run-123',
        continue_from_run_id='prior-run',
        bounded_reentry_token='token-123',
        host_decision_json_file=str(tmp_path / 'host-decision.json'),
        force_runtime_neutral=True,
    )

    assert canonical_entry_command(args) == 0
    assert recorded['repo_root'] == tmp_path.resolve()
    assert recorded['argv'] == [
        '--repo-root', str(tmp_path.resolve()),
        '--host-id', 'codex',
        '--entry-id', 'vibe',
        '--prompt', 'plan runtime entry hardening',
        '--requested-stage-stop', 'phase_cleanup',
        '--requested-grade-floor', 'XL',
        '--run-id', 'run-123',
        '--artifact-root', str((tmp_path / 'artifacts')),
        '--local-agent-root', str(tmp_path / 'agent-root'),
        '--continue-from-run-id', 'prior-run',
        '--bounded-reentry-token', 'token-123',
        '--host-decision-json-file', str(tmp_path / 'host-decision.json'),
        '--force-runtime-neutral',
    ]
    assert recorded['printed_stdout'] == '{"run_id":"r1"}\n'



def test_print_json_payload_emits_pretty_json(capsys: pytest.CaptureFixture[str]) -> None:
    print_json_payload({'ok': True})

    captured = capsys.readouterr()
    assert '{\n  "ok": true\n}' in captured.out



def test_verify_command_uses_runtime_contract_for_powershell_dispatch(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import vgo_cli.commands as cli_commands

    recorded: dict[str, object] = {}

    def fake_get_installed_runtime_config(repo_root: Path) -> dict[str, object]:
        recorded['repo_root'] = repo_root
        return {'coherence_gate': 'scripts/verify/custom-coherence-gate.ps1'}

    def fake_passthrough(args: argparse.Namespace, *, shell_script: str, powershell_script: str) -> int:
        recorded['frontend'] = args.frontend
        recorded['shell_script'] = shell_script
        recorded['powershell_script'] = powershell_script
        recorded['rest'] = list(args.rest)
        return 0

    monkeypatch.setattr(cli_commands, 'get_installed_runtime_config', fake_get_installed_runtime_config)
    monkeypatch.setattr(cli_commands, 'passthrough_command', fake_passthrough)

    args = argparse.Namespace(
        repo_root=str(tmp_path),
        frontend='powershell',
        rest=['--artifacts'],
    )

    assert verify_command(args) == 0
    assert recorded['repo_root'] == tmp_path.resolve()
    assert recorded['frontend'] == 'powershell'
    assert recorded['shell_script'] == 'check.sh'
    assert recorded['powershell_script'] == 'scripts/verify/custom-coherence-gate.ps1'
    assert recorded['rest'] == ['--artifacts']



def test_runtime_command_uses_runtime_contract_for_powershell_dispatch(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import vgo_cli.commands as cli_commands

    recorded: dict[str, object] = {}

    def fake_get_installed_runtime_config(repo_root: Path) -> dict[str, object]:
        recorded['repo_root'] = repo_root
        return {'runtime_entrypoint': 'scripts/runtime/custom-runtime-entrypoint.ps1'}

    def fake_passthrough(args: argparse.Namespace, *, shell_script: str, powershell_script: str) -> int:
        recorded['frontend'] = args.frontend
        recorded['shell_script'] = shell_script
        recorded['powershell_script'] = powershell_script
        recorded['rest'] = list(args.rest)
        return 0

    monkeypatch.setattr(cli_commands, 'get_installed_runtime_config', fake_get_installed_runtime_config)
    monkeypatch.setattr(cli_commands, 'passthrough_command', fake_passthrough)

    args = argparse.Namespace(
        repo_root=str(tmp_path),
        frontend='powershell',
        rest=['--task', 'smoke'],
    )

    assert runtime_command(args) == 0
    assert recorded['repo_root'] == tmp_path.resolve()
    assert recorded['frontend'] == 'powershell'
    assert recorded['shell_script'] == 'check.sh'
    assert recorded['powershell_script'] == 'scripts/runtime/custom-runtime-entrypoint.ps1'
    assert recorded['rest'] == ['--task', 'smoke']


def test_upgrade_command_delegates_to_upgrade_service(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import vgo_cli.commands as cli_commands

    recorded: dict[str, object] = {}

    monkeypatch.setattr(cli_commands, 'normalize_host_id', lambda host: host)
    monkeypatch.setattr(cli_commands, 'resolve_target_root', lambda host_id, target_root: Path(target_root or tmp_path / 'target').resolve())
    monkeypatch.setattr(
        cli_commands,
        'assert_target_root_matches_host_intent',
        lambda target_root, host_id: recorded.setdefault('intent_checked', (target_root, host_id)),
    )

    def fake_upgrade_runtime(**kwargs: object) -> dict[str, object]:
        recorded['kwargs'] = kwargs
        return {'changed': False}

    monkeypatch.setattr(cli_commands, 'upgrade_runtime', fake_upgrade_runtime)

    args = argparse.Namespace(
        repo_root=str(tmp_path / 'repo'),
        host='codex',
        target_root=str(tmp_path / 'target'),
        profile='full',
        frontend='shell',
        install_external=False,
        strict_offline=False,
        require_closed_ready=False,
        allow_external_skill_fallback=False,
        skip_runtime_freshness_gate=False,
    )

    assert upgrade_command(args) == 0
    assert recorded['kwargs']['repo_root'] == (tmp_path / 'repo').resolve()
    assert recorded['kwargs']['target_root'] == (tmp_path / 'target').resolve()
    assert recorded['kwargs']['host_id'] == 'codex'


def test_build_parser_includes_upgrade_subcommand() -> None:
    parser = build_parser()
    args = parser.parse_args(['upgrade', '--repo-root', '/tmp/repo'])

    assert args.command == 'upgrade'
    assert args.handler is upgrade_command
    assert args.frontend == 'shell'


def test_build_parser_defaults_profile_bearing_subcommands_to_minimal() -> None:
    parser = build_parser()

    install_args = parser.parse_args(['install', '--repo-root', '/tmp/repo'])
    uninstall_args = parser.parse_args(['uninstall', '--repo-root', '/tmp/repo'])
    upgrade_args = parser.parse_args(['upgrade', '--repo-root', '/tmp/repo'])

    assert install_args.profile == 'minimal'
    assert uninstall_args.profile == 'minimal'
    assert upgrade_args.profile == 'minimal'


def test_build_parser_includes_index_subcommand() -> None:
    parser = build_parser()
    args = parser.parse_args([
        'index',
        '--repo-root',
        '/tmp/repo',
        '--agent-root',
        '/tmp/agent',
        '--host-id',
        'codex',
        '--workspace-root',
        '/tmp/workspace',
    ])

    assert args.command == 'index'
    assert args.handler is index_command
    assert args.host_id == 'codex'
    assert args.workspace_root == '/tmp/workspace'
    assert args.json is False


def test_build_parser_includes_run_subcommand() -> None:
    parser = build_parser()
    args = parser.parse_args([
        'run',
        '--repo-root',
        '/tmp/repo',
        '--agent-root',
        '/tmp/agent',
        '--prompt',
        'review this',
        '--host-id',
        'codex',
        '--workspace-root',
        '/tmp/workspace',
    ])

    assert args.command == 'run'
    assert args.handler is run_command
    assert args.host_id == 'codex'
    assert args.workspace_root == '/tmp/workspace'
    assert args.run_id is None


def test_build_parser_includes_inspect_run_subcommand() -> None:
    parser = build_parser()
    args = parser.parse_args([
        'inspect-run',
        '--repo-root',
        '/tmp/repo',
        '--agent-root',
        '/tmp/agent',
        '--run-id',
        'run-1',
        '--host-id',
        'codex',
        '--workspace-root',
        '/tmp/workspace',
    ])

    assert args.command == 'inspect-run'
    assert args.handler is inspect_run_command
    assert args.host_id == 'codex'
    assert args.workspace_root == '/tmp/workspace'
    assert args.run_id == 'run-1'


def test_build_parser_includes_locate_entry_subcommand() -> None:
    parser = build_parser()
    args = parser.parse_args(['locate-entry', '--repo-root', '/tmp/repo', '--change-kind', 'execution'])

    assert args.command == 'locate-entry'
    assert args.handler is locate_entry_command
    assert args.change_kind == 'execution'


def test_build_parser_accepts_local_skill_extension_locate_entry() -> None:
    parser = build_parser()
    args = parser.parse_args(['locate-entry', '--repo-root', '/tmp/repo', '--change-kind', 'local-skill-extension'])

    assert args.command == 'locate-entry'
    assert args.change_kind == 'local-skill-extension'


def test_build_parser_includes_compatibility_exit_subcommand() -> None:
    parser = build_parser()
    args = parser.parse_args(['compatibility-exit', '--repo-root', '/tmp/repo'])

    assert args.command == 'compatibility-exit'
    assert args.handler is compatibility_exit_command


def test_build_parser_includes_canonical_entry_subcommand() -> None:
    parser = build_parser()
    args = parser.parse_args(['canonical-entry', '--repo-root', '/tmp/repo', '--prompt', 'enter canonical vibe'])

    assert args.command == 'canonical-entry'
    assert args.handler is canonical_entry_command
    assert args.host_id == 'codex'
    assert args.entry_id == 'vibe'


def test_build_parser_accepts_canonical_entry_host_decision_json_file() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            'canonical-entry',
            '--repo-root',
            '/tmp/repo',
            '--prompt',
            'continue canonical vibe',
            '--host-decision-json-file',
            '/tmp/decision.json',
        ]
    )

    assert args.command == 'canonical-entry'
    assert args.host_decision_json_file == '/tmp/decision.json'


def test_build_parser_accepts_canonical_entry_local_agent_root() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            'canonical-entry',
            '--repo-root',
            '/tmp/repo',
            '--prompt',
            'continue canonical vibe',
            '--local-agent-root',
            '/tmp/agent-root',
        ]
    )

    assert args.command == 'canonical-entry'
    assert args.local_agent_root == '/tmp/agent-root'


def test_build_parser_accepts_legacy_wrapper_metadata_flag_for_canonical_entry() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            'canonical-entry',
            '--repo-root',
            '/tmp/repo',
            '--prompt',
            'enter canonical vibe',
            '--allow-public-grade-flags',
            'false',
        ]
    )

    assert args.command == 'canonical-entry'
    assert args.allow_public_grade_flags == 'false'


def test_install_command_skips_external_dependency_install_when_strict_offline(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    import vgo_cli.commands as cli_commands

    recorded: dict[str, object] = {}

    def fake_normalize_host_id(host: str) -> str:
        return host

    def fake_resolve_target_root(host_id: str, target_root: str | None) -> Path:
        recorded['resolved_host'] = host_id
        return Path(target_root or tmp_path / 'target').resolve()

    def fake_assert_target_root_matches_host_intent(target_root: Path, host_id: str) -> None:
        recorded['intent_checked'] = (target_root, host_id)

    def fake_install_mode_for_host(host_id: str) -> str:
        return 'preview-guidance'

    def fake_run_installer_core(repo_root: Path, argv: list[str]) -> subprocess.CompletedProcess[str]:
        recorded['installer_repo_root'] = repo_root
        recorded['installer_argv'] = list(argv)
        return subprocess.CompletedProcess(
            args=list(argv),
            returncode=0,
            stdout='{"install_mode":"preview-guidance","external_fallback_used":[]}\n',
            stderr='',
        )

    def fake_reconcile_install_postconditions(
        repo_root: Path,
        target_root: Path,
        host_id: str,
        **kwargs: object,
    ) -> dict[str, object]:
        recorded['reconcile'] = {
            'repo_root': repo_root,
            'target_root': target_root,
            'host_id': host_id,
            **kwargs,
        }
        return {'install_receipt': {}, 'mcp_receipt': {}}

    def fake_maybe_install_external_dependencies(repo_root: Path, install_mode: str, *, strict_offline: bool = False) -> None:
        recorded['external_called'] = {
            'repo_root': repo_root,
            'install_mode': install_mode,
            'strict_offline': strict_offline,
        }

    monkeypatch.setattr(cli_commands, 'normalize_host_id', fake_normalize_host_id)
    monkeypatch.setattr(cli_commands, 'resolve_target_root', fake_resolve_target_root)
    monkeypatch.setattr(cli_commands, 'assert_target_root_matches_host_intent', fake_assert_target_root_matches_host_intent)
    monkeypatch.setattr(cli_commands, 'install_mode_for_host', fake_install_mode_for_host)
    monkeypatch.setattr(cli_commands, 'run_installer_core', fake_run_installer_core)
    monkeypatch.setattr(cli_commands, 'reconcile_install_postconditions', fake_reconcile_install_postconditions)
    monkeypatch.setattr(cli_commands, 'maybe_install_external_dependencies', fake_maybe_install_external_dependencies)
    monkeypatch.setattr(cli_commands, 'print_install_banner', lambda *args, **kwargs: None)
    monkeypatch.setattr(cli_commands, 'print_install_completion_hint', lambda *args, **kwargs: None)

    args = argparse.Namespace(
        repo_root=str(tmp_path),
        host='cursor',
        target_root=str(tmp_path / 'target'),
        profile='full',
        require_closed_ready=False,
        allow_external_skill_fallback=False,
        install_external=True,
        strict_offline=True,
        skip_runtime_freshness_gate=False,
        frontend='shell',
    )

    assert install_command(args) == 0
    assert 'external_called' not in recorded
    assert recorded['reconcile']['strict_offline'] is True
