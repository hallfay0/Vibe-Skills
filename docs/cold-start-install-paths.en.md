# Cold Start Install Paths

This page used to describe the old multi-host one-shot bootstrap path. That path is retired.

The current public install contract is simpler: install the `vibe` skill into a skills directory, then check that same directory.

```bash
bash ./install.sh --skills-dir "$HOME/.agents/skills"
bash ./check.sh --skills-dir "$HOME/.agents/skills"
```

PowerShell users can run:

```powershell
.\install.ps1 -SkillsDir "$env:USERPROFILE\.agents\skills"
.\check.ps1 -SkillsDir "$env:USERPROFILE\.agents\skills"
```

Read `docs/install/README.en.md` for the current install contract.
