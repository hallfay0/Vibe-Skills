# 简化安装

公开安装从 [GitHub Releases 页面](https://github.com/foryourhealth111-pixel/Vibe-Skills/releases) 开始。v4.0.0 的发布文件名是 `vibe-skills-4.0.0-public.zip`。下载并解压后，在这个发布目录里运行脚本。安装器随后只做一件事：把 `vibe` 安装到一个 skills 目录下。

默认目录是 `~/.agents/skills`。如果某个宿主或你自己的工作流需要别的 skills 目录，也可以显式传入，例如 `~/.codex/skills` 或 `~/.claude/skills`。

```powershell
pwsh -NoProfile -File .\install.ps1 -SkillsDir "$HOME\.agents\skills"
pwsh -NoProfile -File .\check.ps1 -SkillsDir "$HOME\.agents\skills"
pwsh -NoProfile -File .\update.ps1 -SkillsDir "$HOME\.agents\skills"
pwsh -NoProfile -File .\uninstall.ps1 -SkillsDir "$HOME\.agents\skills"
```

只在 Codex 中使用时，可以显式安装到 Codex 的 skills 目录：

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

安装后，受管目录是 `<SkillsDir>/vibe`。安装收据位于 `<SkillsDir>/vibe/.vibeskills/install-receipt.json`。

`check` 只检查收据登记的文件是否仍然完整。`update` 会在发现用户改动时拒绝覆盖。`uninstall` 只删除收据登记的文件，保留用户额外添加的文件。
`check` 证明的是 `installed locally`。它不证明 `runtime coherent`，也不证明 `delivery accepted`。

如果要更新，先下载更新版本的发布版本 zip，再解压，然后在新的发布目录里对同一个 `SkillsDir` 运行 `update`，最后运行 `check`。不要把新版本解压到受管目录 `<SkillsDir>/vibe` 里面。

## 从 v3 升级到 v4

1. 记录当前安装使用的 `SkillsDir`。
2. 下载并解压 `vibe-skills-4.0.0-public.zip`。
3. 从 v4 解压目录对原来的 `SkillsDir` 运行 `update`。
4. 运行 `check`，确认收据登记文件缺失为 `0`、漂移为 `0`。
5. 后续统一调用 `vibe`。旧的 `vibe-what-do-i-want`、`vibe-how-do-we-do`、`vibe-do-it` 和 `vibe-upgrade` 入口不再属于 v4 公开运行时。

v4 不会自动安装或推荐 `chrome`、`chrome-devtools`、`playwright`、`context7` 或 `claude-flow` MCP。安装器也不会替用户修改这些 MCP 的主机配置。

安装器不会改 Codex、Claude 或 Agents 的设置，也不会写入系统提示词或命令包装文件。额外 skill 扫描目录由运行时配置管理：

- 用户级：`~/.vibeskills/skill-roots.json`
- 项目级：`<workspace>/.vibeskills/skill-roots.json`

仓库 checkout 安装现在只属于 developer/internal 路径。旧的多宿主安装说明已经移到 `docs/archive/install-legacy/2026-07-02/`。
