# Choose A Skills Directory

This page used to describe the old multi-host one-shot bootstrap path. That path is retired.

The current install contract has one interface for every AI application:

```text
install <same VibeSkills package> into <SkillsDir>/vibe
```

Choose a `SkillsDir` that the current application scans. The application may
use its own directory name, but that changes only the destination path. It does
not select a host-specific package, runtime, or workflow.

The shared default is `~/.agents/skills`:

```bash
bash ./install.sh --skills-dir "$HOME/.agents/skills"
bash ./check.sh --skills-dir "$HOME/.agents/skills"
```

PowerShell users can run:

```powershell
.\install.ps1 -SkillsDir "$env:USERPROFILE\.agents\skills"
.\check.ps1 -SkillsDir "$env:USERPROFILE\.agents\skills"
```

If the application scans another Skills directory, replace only the path passed
to `--skills-dir` or `-SkillsDir`. After installation, every application uses
the same `<SkillsDir>/vibe` layout and invokes `vibe` through its own Skills
entry.

Read `docs/install/README.en.md` for the current install contract.
