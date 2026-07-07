# 冷启动安装路径

这页过去描述旧的多宿主 one-shot bootstrap 路径。那条路径已经退役。

当前公开安装契约更简单：把 `vibe` skill 安装进一个 skills 目录，然后检查同一个目录。

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
