# Kernel-First Remediation Phase Summary

## What authority moved

The live runtime meaning is now narrower and more honest.

- task meaning moved into kernel-owned Python modules
- router output was reduced to candidate discovery and compatibility shaping
- skill-use proof now depends on work results and evidence, not route-era mirrors
- PowerShell wrappers no longer rebuild runtime truth or user-facing summary meaning
- starter-set truth is now published from packaging inventory instead of raw bundled folder count

## What stayed compatibility-only

Some older surfaces still remain readable, but they are no longer allowed to act like first truth.

- route-era routing mirrors stay readable only as compatibility projections
- PowerShell still owns launch, receipts, shell-native checks, and host-facing bridge work
- the large repo-owned bundled tree still exists on disk, but it is now documented as reference or migration material unless packaging marks it live
- dated zero-route-authority governance records were moved into archive rather than kept as current entry docs

## What was deferred

This pass did not force every possible cleanup into one change.

- no broad physical move of the remaining repo-owned bundled skill corpus
- only the first bounded governance-history batch was archived
- repo cleanliness is still expected to fail until the current remediation work is committed
- the largest remaining stability risk is parallel install or check interference under `pytest -n auto`, not the original kernel-first blockers

Current closeout status:

- The original false blocker from local `pwsh` script policy is fixed. Runtime-neutral tests that directly invoke PowerShell entrypoints now pass `ExecutionPolicy Bypass` and the shell wrappers preserve that behavior.
- The local canonical smoke fixture was refreshed and now contains the newer kernel-first artifacts needed by `vibe-canonical-entry-truth-gate.ps1`, including `runtime-input-packet.json`, `governance-capsule.json`, and `stage-lineage.json`.
- `scripts/verify/vibe-repo-cleanliness-gate.ps1` still correctly reports the repo as not clean while the remediation work remains uncommitted. On the latest rerun it reported `Dirty paths: 168`.
- A wide parallel slice `py -3 -m pytest tests/unit tests/runtime_neutral -x -n auto` no longer reproduces the original Task 8 blockers. The remaining red state comes from install/check tests that pass when rerun individually, which points to parallel interference rather than the kernel-first remediation defects addressed here.

## Which proof commands passed

Focused proof that passed during this phase:

- `py -3 -m pytest tests/unit/test_canonical_vibe_entry_launcher.py tests/runtime_neutral/test_governed_runtime_bridge.py -q`
  observed result: `99 passed`
- `py -3 -m pytest tests/unit/test_kernel_benchmark.py -q`
  observed result: `9 passed, 1 warning`
- `py -3 -m pytest tests/runtime_neutral/test_documentation_surface_alignment.py tests/runtime_neutral/test_current_routing_debt_gate_docs.py -q`
  observed result: `23 passed`
- `py -3 -m pytest tests/unit -q`
  observed result: `497 passed, 1 warning`
- `py -3 -m pytest tests/unit/test_runtime_truth.py tests/unit/test_runtime_execution.py tests/runtime_neutral/test_bootstrap_shell_target_root_guard.py tests/runtime_neutral/test_check_installed_runtime_root.py tests/runtime_neutral/test_apps_surface_hygiene.py tests/runtime_neutral/test_binary_skill_usage_contract.py tests/runtime_neutral/test_current_routing_debt_gate.py tests/runtime_neutral/test_skill_execution_lock_contract.py tests/runtime_neutral/test_l_xl_native_execution_topology.py -q`
  observed result: `83 passed`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify/vibe-governed-runtime-contract-gate.ps1`
  observed result: `gate_passed = True`, `assertion_count = 75`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify/vibe-canonical-entry-truth-gate.ps1 -SessionRoot (Resolve-Path '.tmp\canonical-local-smoke\vibe\runs\canon-local-smoke') -WriteArtifacts`
  observed result: all printed assertions passed
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify/vibe-runtime-execution-proof-gate.ps1`
  observed result: `gate_passed = True`, `assertion_count = 60`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify/vibe-release-truth-consistency-gate.ps1`
  observed result: all printed assertions passed
- `py -3 -m pytest tests/runtime_neutral/test_discoverable_wrapper_host_visibility.py::DiscoverableWrapperHostVisibilityTests::test_install_ledger_exposes_host_visible_discoverable_entries_for_supported_hosts tests/runtime_neutral/test_discoverable_wrapper_host_visibility.py::DiscoverableWrapperHostVisibilityTests::test_shell_check_accepts_supported_host_discoverable_surfaces tests/runtime_neutral/test_installed_runtime_uninstall.py::InstalledRuntimeUninstallTests::test_codex_uninstall_removes_issue_167_governed_runtime_dependency_surfaces -q`
  observed result: `3 passed`
- `git diff --check`
  observed result: no whitespace or conflict-marker errors; only CRLF normalization warnings from Git

## Next step

If the goal is a fully green machine-level closeout, the remaining work is operational rather than architectural:

- commit or otherwise reduce the current dirty worktree so `vibe-repo-cleanliness-gate.ps1` can pass honestly
- isolate or serialize the remaining install/check tests that only go red under `pytest -n auto`
- if needed, rerun the full `tests/unit` and `tests/runtime_neutral` suites in a non-parallel environment with a larger wall-clock budget than this interactive session
