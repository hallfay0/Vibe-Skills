# Quick Start

[中文](./quick-start.md)

If this is your first time in the repository, you do not need to read every document first.

Think of VibeSkills as a **work-kernel entry** for AI agents:

> You bring the goal. `vibe` manages the work rhythm: clarify the requirement, build a work model, bind the right Skills where they help, push toward testing and verification, and preserve the useful context.

It is not a long tool menu that leaves the user to choose every step. It is one portable work loop that helps Skills-capable agents start faster, stay more disciplined, and handle work across phases.

## 1. What problem does it solve?

VibeSkills focuses on five practical problems:

| Problem | What VibeSkills does |
|:---|:---|
| Too many Skills, unclear which one to call | The kernel binds relevant Skills after the work shape is clear |
| Agents skip requirements, planning, or testing | `vibe` moves work through bounded stages |
| Users keep saying "plan first" or "verify it" | You provide the goal; the harness absorbs more of the control burden |
| Long work loses context across sessions | Requirements, plans, decisions, and evidence are stored in structured places |
| New domain Skills are hard to integrate | The core uses the Skills installed in declared local roots, so users can add capability without turning the product into a bigger central catalog |

If you remember one line:

> **VibeSkills packages skill binding, verification, and cross-session memory into one portable work-kernel entry that is easy to install and easy to start using.**

## 2. Start fast

Open the simple install guide:

- [`install/README.en.md`](./install/README.en.md)

Use the default skills directory if you want the shortest path. Start from the published release zip, not from a repo checkout. If VibeSkills is already installed, download the newer published release zip and run `update` against the same skills directory.

After install, invoke it through your carrier's Skills entry. The core contract
is host-neutral; exact syntax belongs to the adapter. `$vibe` in Codex and
`/vibe` in Claude Code are examples, not a limit on which carriers can consume
the runtime. A new carrier can integrate through a compatible adapter, while
its support status remains unproven until the corresponding host evidence is
recorded.

See the [host capability matrix](./universalization/host-capability-matrix.md)
for current adapter evidence and support labels.

For updates, keep the same management path from the newer extracted release copy:

- `update.ps1 -SkillsDir <skills-dir>`
- `update.sh --skills-dir <skills-dir>`

## 3. Current public entries

The current public, host-visible entry is:

- `vibe`

`vibe` is the main entry. It stops at requirement, plan, and execution boundaries, then continues only after explicit confirmation.

Installed-copy upgrades stay on the command path. Use `update` with the same skills directory instead of a second public runtime entry.

Older stage-specific and legacy CLI entries are retired from the public host-visible surface and should not be advertised or installed.

If you want a stronger execution lane, use only the public lightweight overrides:

- `--l`
- `--xl`

Older stage IDs may still exist in runtime metadata for compatibility and continuity, but they are not commands or skills that users should invoke.

## 4. What to read next

Pick by intent:

| Goal | Read |
|:---|:---|
| Full project introduction | [`../README.md`](../README.md) |
| Install or update | [`install/README.en.md`](./install/README.en.md) |
| Direct command reference | [`install/README.en.md`](./install/README.en.md) |
| Unsure about host roots | [`cold-start-install-paths.en.md`](./cold-start-install-paths.en.md) |
| Using OpenCode | [`cold-start-install-paths.en.md`](./cold-start-install-paths.en.md) |
| Using OpenClaw | [`cold-start-install-paths.en.md`](./cold-start-install-paths.en.md) |
| Manual/offline install | [`install/README.en.md`](./install/README.en.md) |
| Normal skill extension path after install | [`install/README.en.md`](./install/README.en.md) |
| Add or scan more local skill roots | [`install/README.en.md`](./install/README.en.md) |
| Why the project exists | [`manifesto.en.md`](./manifesto.en.md) |

## 5. Common confusion

- `$vibe` or `/vibe` only enters the governed runtime. It does not by itself prove that host plugins, providers, or online enhancement are fully configured.
- `check` proves `installed locally`.
- `runtime coherent` starts only after a real `vibe` run returns a `session_root` with runtime truth artifacts.
- `delivery accepted` comes from `delivery-acceptance-report.json` / `.md`.
- VibeSkills is a Skills-format runtime, not a standalone CLI you run directly in a terminal.

## Recommended reading order

For the shortest path:

1. [`../README.md`](../README.md)
2. [`install/README.en.md`](./install/README.en.md)
3. Try `vibe` on a small task

Start with something simple, for example:

> Clarify this requirement and turn it into a plan `$vibe`

The difference becomes clear quickly: the user does not have to act as the dispatcher, and the agent gets a steadier way to move work through the harness.
