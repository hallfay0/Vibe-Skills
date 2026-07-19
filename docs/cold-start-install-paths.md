# 选择 Skills 目录

当前安装契约对所有 AI 应用都只有一个接口：

```text
把同一份 VibeSkills 安装到 <SkillsDir>/vibe
```

选择当前应用能够扫描的 `SkillsDir`。应用可以使用自己的目录名称，但这只会改变
目标路径，不会选择宿主专用的安装包、运行时或工作流。

共享默认目录是 `~/.agents/skills`：

```bash
bash ./install.sh --skills-dir "$HOME/.agents/skills"
bash ./check.sh --skills-dir "$HOME/.agents/skills"
```

PowerShell 用户可以运行：

```powershell
.\install.ps1 -SkillsDir "$env:USERPROFILE\.agents\skills"
.\check.ps1 -SkillsDir "$env:USERPROFILE\.agents\skills"
```

如果应用扫描另一个 Skills 目录，只需要替换传给 `--skills-dir` 或 `-SkillsDir`
的路径。安装后，所有应用都使用相同的 `<SkillsDir>/vibe` 结构，再通过应用自己的
Skills 入口调用 `vibe`。

当前安装契约以 `docs/install/README.md` 为准。
