# Simple Install

The public install path starts from the [GitHub Releases page](https://github.com/foryourhealth111-pixel/Vibe-Skills/releases). The v4.0.0 asset is named `vibe-skills-4.0.0-public.zip`. Download and extract it, then run the wrappers from that release directory. The installer does one thing: it installs `vibe` into a skills directory.

The default directory is `~/.agents/skills`. If a host or your own workflow needs a different skills directory, pass it explicitly, for example `~/.codex/skills` or `~/.claude/skills`.

```powershell
pwsh -NoProfile -File .\install.ps1 -SkillsDir "$HOME\.agents\skills"
pwsh -NoProfile -File .\check.ps1 -SkillsDir "$HOME\.agents\skills"
pwsh -NoProfile -File .\update.ps1 -SkillsDir "$HOME\.agents\skills"
pwsh -NoProfile -File .\uninstall.ps1 -SkillsDir "$HOME\.agents\skills"
```

For a Codex-only install, target the Codex skills directory explicitly:

```powershell
pwsh -NoProfile -File .\install.ps1 -SkillsDir "$HOME\.codex\skills"
pwsh -NoProfile -File .\check.ps1 -SkillsDir "$HOME\.codex\skills"
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

To update, download the newer published release zip first, extract it, run `update` from that newer release copy against the same `SkillsDir`, and then run `check`. Do not extract the new release inside the managed `<SkillsDir>/vibe` directory.

## Upgrading From v3 To v4

1. Record the `SkillsDir` used by the current install.
2. Download and extract `vibe-skills-4.0.0-public.zip`.
3. Run the v4 `update` wrapper against the existing `SkillsDir`.
4. Run `check` and confirm that receipt-owned missing and drifted file counts are both `0`.
5. Use `vibe` for subsequent governed runs. The legacy `vibe-what-do-i-want`, `vibe-how-do-we-do`, `vibe-do-it`, and `vibe-upgrade` entry names are not part of the v4 public runtime.

v4 does not automatically install or recommend the `chrome`, `chrome-devtools`, `playwright`, `context7`, or `claude-flow` MCPs. The installer also does not modify their host configuration.

The installer does not edit Codex, Claude, or Agents settings. It also does not write system prompts or command wrappers. Extra skill scan directories are managed by runtime config:

- User level: `~/.vibeskills/skill-roots.json`
- Workspace level: `<workspace>/.vibeskills/skill-roots.json`

Repo checkout install is a developer/internal path now. The old multi-host install guides were moved to `docs/archive/install-legacy/2026-07-02/`.
