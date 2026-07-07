# Simple Install

The public install path now starts from a published release zip. Download the published release zip, extract it, and run the wrappers from that extracted release directory. The installer then does one thing: it installs `vibe` into a skills directory.

The default directory is `~/.agents/skills`. If a host or your own workflow needs a different skills directory, pass it explicitly, for example `~/.codex/skills` or `~/.claude/skills`.

```powershell
pwsh -NoProfile -File .\install.ps1 -SkillsDir "$HOME\.agents\skills"
pwsh -NoProfile -File .\check.ps1 -SkillsDir "$HOME\.agents\skills"
pwsh -NoProfile -File .\update.ps1 -SkillsDir "$HOME\.agents\skills"
pwsh -NoProfile -File .\uninstall.ps1 -SkillsDir "$HOME\.agents\skills"
```

```bash
bash ./install.sh --skills-dir "$HOME/.agents/skills"
bash ./check.sh --skills-dir "$HOME/.agents/skills"
bash ./update.sh --skills-dir "$HOME/.agents/skills"
bash ./uninstall.sh --skills-dir "$HOME/.agents/skills"
```

After installation, the managed directory is `<SkillsDir>/vibe`. The install receipt lives at `<SkillsDir>/vibe/.vibeskills/install-receipt.json`.

`check` verifies the files recorded in the receipt. `update` refuses to overwrite user edits when drift is detected. `uninstall` removes only files recorded in the receipt and keeps user-added files.
`check` proves `installed locally`. It does not prove `runtime coherent` or `delivery accepted`.

To update, download the newer published release zip first, extract it, and run `update` from that newer release copy against the same `SkillsDir`.

The installer does not edit Codex, Claude, or Agents settings. It also does not write system prompts or command wrappers. Extra skill scan directories are managed by runtime config:

- User level: `~/.vibeskills/skill-roots.json`
- Workspace level: `<workspace>/.vibeskills/skill-roots.json`

Repo checkout install is a developer/internal path now. The old multi-host install guides were moved to `docs/archive/install-legacy/2026-07-02/`.
