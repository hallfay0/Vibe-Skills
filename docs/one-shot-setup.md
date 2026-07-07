# One-Shot Setup

旧的 one-shot setup 路径已经退役。

当前支持的公开路径只做一件事：把 `vibe` skill 安装进一个 skills 目录，并验证收据里记录的文件仍然完整。

```bash
bash ./install.sh --skills-dir "$HOME/.agents/skills"
bash ./check.sh --skills-dir "$HOME/.agents/skills"
```

PowerShell 用户可以运行：

```powershell
.\install.ps1 -SkillsDir "$env:USERPROFILE\.agents\skills"
.\check.ps1 -SkillsDir "$env:USERPROFILE\.agents\skills"
```

当前安装契约以 `docs/install/README.md` 为准。
