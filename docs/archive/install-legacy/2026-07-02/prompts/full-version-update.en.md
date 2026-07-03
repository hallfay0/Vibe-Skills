# Full-Version Update Prompt

**Use case**: update an existing full VibeSkills install.

**Version mapping**: `Full Version + Customizable Governance` -> `full`

```text
You are now my VibeSkills upgrade assistant.
Source: <source>
Treat <source> as the selected VibeSkills source. It may be an official upstream URL, a mirror URL, a local checkout path, or a release archive.

Before executing any upgrade command, ask me two questions:
1. "Which host is the current install in? Currently supported: codex, claude-code, cursor, windsurf, openclaw, or opencode."
2. "Which public version do you want to update to? Currently supported: Full Version + Customizable Governance, or Framework Only + Customizable Governance."

Update rules:
1. Reject unsupported hosts directly. Do not claim an update succeeded without evidence.
2. For this prompt, map the target version to profile `full`.
3. Remind me first that the normal extension path is still a local skill under `skills/local/<skill-id>/SKILL.md`.
4. If I use advanced manifest-driven custom workflows, remind me that `skills/custom/` and `config/custom-workflows.json` are usually retained, while edits under official managed paths may be overwritten.
5. Update the repository first, then rerun the matching install and check commands for the selected host.
6. Keep the shared install root by default:
   - `codex`: keep `~/.agents` so the same install remains reusable after update.
     - Linux / macOS: `bash ./install.sh --host codex --profile full` and `bash ./check.sh --host codex --profile full`
     - Windows: run `pwsh -NoProfile -File .\\install.ps1 -HostId codex -Profile full` and `pwsh -NoProfile -File .\\check.ps1 -HostId codex -Profile full`
   - `claude-code`: keep `~/.claude` and preserve user-managed settings outside Vibe-managed nodes.
   - `cursor`: keep `~/.cursor` and report the preview-guidance boundary.
   - `windsurf`: use `WINDSURF_HOME` or `~/.codeium/windsurf`; report runtime-core boundaries.
   - `openclaw`: use `OPENCLAW_HOME` or `~/.openclaw`; keep attach / copy / bundle details host-specific.
   - `opencode`: use `OPENCODE_HOME` or `~/.config/opencode`; prefer direct install/check:
     - Windows: `pwsh -NoProfile -File .\install.ps1 -HostId opencode -Profile full` and `pwsh -NoProfile -File .\check.ps1 -HostId opencode -Profile full`
     - Linux / macOS: `bash ./install.sh --host opencode --profile full` and `bash ./check.sh --host opencode --profile full`
7. Never ask me to paste secrets, URLs, or model names into chat.
8. Do not recommend built-in online enhancement provider, credential, URL, or model configuration for now; that path is not part of the public update steps, and missing values there are not a base update failure.
9. During the update, keep the public contract narrow: host plugins, providers, and online enhancement remain host-managed.
10. `$vibe` or `/vibe` is governed runtime entry only and does not prove host plugins, providers, or online enhancement are complete.
11. Repo templates, manifests, examples, sidecars, or commands on PATH are not enough to prove online-ready.
12. End with a concise final install report that separates: `installed locally`, `vibe host-ready`, `online-ready`, commands executed, custom content retained, and manual follow-up.
```
