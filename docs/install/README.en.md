# Simple Install

The installer now does one thing: it installs the repo's `vibe` skill into a skills directory.

The default directory is `~/.agents/skills`. You can also install the same `vibe` skill into `~/.codex/skills` or `~/.claude/skills`.

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

The installer does not edit Codex, Claude, or Agents settings. It also does not write system prompts or command wrappers. Extra skill scan directories are managed by runtime config:

- User level: `~/.vibeskills/skill-roots.json`
- Workspace level: `<workspace>/.vibeskills/skill-roots.json`

The old multi-host install guides were moved to `docs/archive/install-legacy/2026-07-02/`.
