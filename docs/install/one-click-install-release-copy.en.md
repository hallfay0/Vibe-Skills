# Install VibeSkills

This is the public install entry. If you are new here, start with the defaults:

- Host: the AI app you actually use
- Action: `install`
- Version: `Framework Only + Customizable Governance`

## Before You Start

You need:

- PowerShell 7 (`pwsh`) available in `PATH` for the full governed verification path
- Python 3.10+ (`python3` / `python`) for the wrapper-driven install surface
- Git access to this repository

Linux and macOS can still use the `bash` install entrypoints. PowerShell 7 is recommended because the full governed check surface uses it.

> Prefer to run commands yourself? Open [`recommended-full-path.en.md`](./recommended-full-path.en.md). This page is the prompt-based install path.

## Choose Three Things

| Choice | Options | Default |
|:---|:---|:---|
| Host | `codex`, `claude-code`, `cursor`, `windsurf`, `openclaw`, `opencode` | the app you use |
| Action | `install`, `update` | `install` |
| Version | `Full Version + Customizable Governance`, `Framework Only + Customizable Governance` | `Framework Only + Customizable Governance` |

Public version mapping:

- `Full Version + Customizable Governance` -> `full`
- `Framework Only + Customizable Governance` -> `minimal`

Use `minimal` as the recommended default. It keeps the work kernel small, leaves local skills under `<target-root>/skills/local/<skill-id>/SKILL.md` as the normal extension path, and keeps only `tdd-guide` and `systematic-debugging` as built-in starter helpers. Choose `full` only when you also want `verification-before-completion`.

## Copy One Prompt

Pick the one matching your action and version, then paste it into your AI app:

| Need | Prompt |
|:---|:---|
| First install, recommended | [`prompts/framework-only-install.en.md`](./prompts/framework-only-install.en.md) |
| First install, framework only | [`prompts/framework-only-install.en.md`](./prompts/framework-only-install.en.md) |
| Update existing minimal install | [`prompts/framework-only-update.en.md`](./prompts/framework-only-update.en.md) |
| Update existing framework install | [`prompts/framework-only-update.en.md`](./prompts/framework-only-update.en.md) |

## What The Prompt Will Do

The prompt asks the assistant to:

1. confirm host and public version before running install commands;
2. install into the shared root `~/.agents` by default so different hosts can reuse the same install;
3. run the matching install and check commands;
4. keep secrets, URLs, and model names out of chat;
5. avoid guiding users through built-in online enhancement configuration that is not publicly open yet;
6. report these states separately: `installed locally`, `vibe host-ready`, and `online-ready`.

`$vibe` or `/vibe` means the governed runtime entry is available. It does not by itself prove that host plugins, providers, or online enhancement are fully configured.

## Read More Only If Needed

- Unsure which host root to use: [`../cold-start-install-paths.en.md`](../cold-start-install-paths.en.md)
- Prefer direct commands: [`recommended-full-path.en.md`](./recommended-full-path.en.md)
- OpenClaw details: [`openclaw-path.en.md`](./openclaw-path.en.md)
- OpenCode details: [`opencode-path.en.md`](./opencode-path.en.md)
- Offline/manual install: [`manual-copy-install.en.md`](./manual-copy-install.en.md)
- Advanced custom workflow onboarding after install: [`custom-workflow-onboarding.en.md`](./custom-workflow-onboarding.en.md)
- Post-install configuration boundaries: [`configuration-guide.en.md`](./configuration-guide.en.md)

## Uninstall

Use the repo-root uninstall entrypoint:

- Windows: `uninstall.ps1 -HostId <host>`
- Linux / macOS: `uninstall.sh --host <host>`

Uninstall removes only Vibe-managed payloads and does not roll back host login state, provider credentials, plugin state, or user-maintained config by default.
