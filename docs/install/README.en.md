# Install Docs Index

This folder contains the install, update, uninstall, and custom-integration docs.

Normal users have two paths:

- **Prompt-based install**: copy one prompt into the AI app and let it confirm host, version, install, and check.
- **Command install**: run install/check directly in a terminal when you already know the host root and command flow.

If you are unsure, start with prompt-based install:

1. Open [`one-click-install-release-copy.en.md`](./one-click-install-release-copy.en.md).
2. Choose host, action, and version.
3. Copy one prompt into the AI app you want to install VibeSkills into.

After install, the normal extension path is simple: add or edit a local skill under `<target-root>/skills/local/<skill-id>/SKILL.md`. Treat manifest-driven custom workflows as an advanced path, not the default way to extend the kernel.

If you prefer direct commands, open [`recommended-full-path.en.md`](./recommended-full-path.en.md).

## Requirements

- Python 3.10+
- PowerShell 7 (`pwsh`) for the full governed verification path
- Git access to this repository

Linux and macOS can still use the `bash` install scripts. PowerShell 7 is recommended because several governed verification gates use the PowerShell command surface.

## Main Pages

| Need | Read |
|:---|:---|
| Public install/update entry | [`one-click-install-release-copy.en.md`](./one-click-install-release-copy.en.md) |
| Command install reference | [`recommended-full-path.en.md`](./recommended-full-path.en.md) |
| Host root decision help | [`../cold-start-install-paths.en.md`](../cold-start-install-paths.en.md) |
| Offline/manual install | [`manual-copy-install.en.md`](./manual-copy-install.en.md) |
| OpenClaw details | [`openclaw-path.en.md`](./openclaw-path.en.md) |
| OpenCode details | [`opencode-path.en.md`](./opencode-path.en.md) |
| Post-install configuration boundaries | [`configuration-guide.en.md`](./configuration-guide.en.md) |
| Advanced manifest-driven custom workflow onboarding | [`custom-workflow-onboarding.en.md`](./custom-workflow-onboarding.en.md) |

Maintainer/reference pages:

- [`installation-rules.en.md`](./installation-rules.en.md): truth-first install assistant rules
- [`host-plugin-policy.en.md`](./host-plugin-policy.en.md): host/plugin boundary notes
- [`../one-shot-setup.md`](../one-shot-setup.md): one-shot setup behavior and install reporting contract

## Prompt Library

The public prompt set is intentionally small:

- [`prompts/full-version-install.en.md`](./prompts/full-version-install.en.md)
- [`prompts/framework-only-install.en.md`](./prompts/framework-only-install.en.md)
- [`prompts/full-version-update.en.md`](./prompts/full-version-update.en.md)
- [`prompts/framework-only-update.en.md`](./prompts/framework-only-update.en.md)

Other pages in this folder are reference docs, compatibility notes, or host-specific supplements. They are not separate public landing pages.

## Public Versions

| Public wording | Runtime profile |
|:---|:---|
| `Full Version + Customizable Governance` | `full` |
| `Framework Only + Customizable Governance` | `minimal` |

Use `minimal` for the normal VibeSkills experience. It keeps the default surface small, leaves local skills under `<target-root>/skills/local/<skill-id>/SKILL.md` as the normal extension path, and keeps only `tdd-guide` and `systematic-debugging` as built-in starter helpers. Choose `full` only when you also want `verification-before-completion` preinstalled.

## Public Hosts

Current public host ids:

- `codex`
- `claude-code`
- `cursor`
- `windsurf`
- `openclaw`
- `opencode`

The install modes are not identical across hosts. `codex` and `claude-code` are the clearest install-and-use paths; `cursor`, `windsurf`, `openclaw`, and `opencode` have host-specific or preview-oriented boundaries. Keep those boundaries visible in install reports.

## Truth Model For Install Reports

Do not collapse install state into one vague success line. Report these separately:

- `installed locally`
- `vibe host-ready`
- `online-ready`

`$vibe` or `/vibe` proves the governed runtime entry only. It does not by itself prove that providers, credentials, plugins, or online enhancement are fully configured.

The public install flow does not currently guide users through built-in online enhancement configuration. Install assistants should not ask users for providers, credentials, URLs, or model names; when that path is not configured through public docs, keep `online-ready` separate and report it as not ready or not verified.

## Uninstall

Use the repo-root uninstall entrypoint:

- Windows: `uninstall.ps1 -HostId <host>`
- Linux / macOS: `uninstall.sh --host <host>`

See [`../uninstall-governance.md`](../uninstall-governance.md) for the owned-only cleanup contract.
