# 多宿主安装命令参考

> 普通用户优先看：
>
> - [`one-click-install-release-copy.md`](./one-click-install-release-copy.md)
> - [`manual-copy-install.md`](./manual-copy-install.md)
> - [`openclaw-path.md`](./openclaw-path.md)
> - [`opencode-path.md`](./opencode-path.md)

这份文档汇总当前六个公开宿主对应的安装命令、默认目标根目录与 host-mode 说明。

即使走全量路径，产品形态也不变：

- 安装得到的仍然是同一个小工作内核
- 安装后的正常扩展路径仍然是 `skills/local/<skill-id>/SKILL.md`
- manifest 驱动的高级 custom workflow 仍然只是后续更窄的高级路径，不是默认扩展方式

## 公共安装边界

所有六个公开宿主现在都遵循同一条更收敛的公共安装边界：

- 公共安装路径不再自动接入宿主侧插件或在线能力
- `$vibe` 或 `/vibe` 只代表 governed runtime 入口，不代表宿主插件、provider 或在线增强已经完成
- repo template、manifest、`*.json.example`、`.vibeskills/*` sidecar，以及“命令已在 PATH 上”都不能单独算 online-ready
- 宿主插件、provider、凭据和更深的在线增强继续保持宿主管理
- 最终报告会把 `installed locally`、`vibe host-ready`、`manual follow-up`、以及 `online-ready` 分开写清楚

公共平台前置条件：

- Windows：先安装 **PowerShell 7**，并确保 `pwsh` 在 `PATH` 上可用
- Linux：先安装 **PowerShell 7**，并确保 `pwsh` 在 `PATH` 上可用
- macOS：如果要使用 PowerShell 命令面，先安装 **PowerShell 7**，并确保 `pwsh` 在 `PATH` 上可用
- shell 入口按 **macOS 自带 Bash 3.2** 兼容维护
- `python3` / `python` 需要满足 **Python 3.10+**
- 从 `zsh` 启动不是问题本身；真正关键是解析到的 `bash` / `python3` 版本
- shell 入口仍然受支持，但完整 governed runtime 和验证面也依赖 PowerShell 7

## 支持宿主与默认路径

| 宿主 | 默认命令面 | 默认目标根目录 | 当前口径 |
| --- | --- | --- | --- |
| `codex` | one-shot setup + check | 默认共享 `~/.agents`；如需改共享根再设置 `VIBE_AGENTS_HOME` | strongest governed path |
| `claude-code` | one-shot setup + check | 默认真实 `~/.claude`（通过 `CLAUDE_HOME`） | supported install/use path with bounded managed closure |
| `cursor` | one-shot setup + check | 默认真实 `~/.cursor`（通过 `CURSOR_HOME`） | preview-guidance path |
| `windsurf` | one-shot setup + check | `WINDSURF_HOME` 或真实宿主根目录 `~/.codeium/windsurf` | runtime-core path |
| `openclaw` | one-shot setup + check | `OPENCLAW_HOME` 或真实宿主根目录 `~/.openclaw` | preview runtime-core adapter path |
| `opencode` | direct install + check（更薄）或 one-shot wrapper | `OPENCODE_HOME` 或真实宿主根目录 `~/.config/opencode` | 围绕同一个 work kernel 的 preview-guidance adapter path |

`TargetRoot` 只是路径。
`HostId` / `--host` 才决定宿主语义。

## 推荐命令

默认全量安装：

### Codex

如果你的目标是把安装方式收敛成一份全局共享 runtime，Codex 默认就装到 `~/.agents`。
只有在你明确要改共享根目录时，才额外设置 `VIBE_AGENTS_HOME`。

```powershell
pwsh -File .\scripts\bootstrap\one-shot-setup.ps1 -HostId codex -Profile full
pwsh -File .\check.ps1 -HostId codex -Profile full -Deep
```

```bash
bash ./scripts/bootstrap/one-shot-setup.sh --host codex --profile full
bash ./check.sh --host codex --profile full --deep
```

### Claude Code

如果你的目标是安装到真实 Claude 宿主根目录，默认目标根应是 `~/.claude`。

```powershell
$env:CLAUDE_HOME="$HOME\\.claude"
pwsh -File .\scripts\bootstrap\one-shot-setup.ps1 -HostId claude-code -Profile full
pwsh -File .\check.ps1 -HostId claude-code -Profile full -Deep
```

```bash
CLAUDE_HOME="$HOME/.claude" bash ./scripts/bootstrap/one-shot-setup.sh --host claude-code --profile full
CLAUDE_HOME="$HOME/.claude" bash ./check.sh --host claude-code --profile full --deep
```

### Cursor

如果你的目标是安装到真实 Cursor 宿主根目录，默认目标根应是 `~/.cursor`。

```powershell
$env:CURSOR_HOME="$HOME\\.cursor"
pwsh -File .\scripts\bootstrap\one-shot-setup.ps1 -HostId cursor -Profile full
pwsh -File .\check.ps1 -HostId cursor -Profile full -Deep
```

```bash
CURSOR_HOME="$HOME/.cursor" bash ./scripts/bootstrap/one-shot-setup.sh --host cursor --profile full
CURSOR_HOME="$HOME/.cursor" bash ./check.sh --host cursor --profile full --deep
```

### Windsurf

默认目标根目录是 `~/.codeium/windsurf`，除非你显式设置 `WINDSURF_HOME`。

```powershell
pwsh -File .\scripts\bootstrap\one-shot-setup.ps1 -HostId windsurf -Profile full
pwsh -File .\check.ps1 -HostId windsurf -Profile full -Deep
```

```bash
bash ./scripts/bootstrap/one-shot-setup.sh --host windsurf --profile full
bash ./check.sh --host windsurf --profile full --deep
```

### OpenClaw

默认目标根目录是 `~/.openclaw`，除非你显式设置 `OPENCLAW_HOME`。

```powershell
pwsh -File .\scripts\bootstrap\one-shot-setup.ps1 -HostId openclaw -Profile full
pwsh -File .\check.ps1 -HostId openclaw -Profile full -Deep
```

```bash
bash ./scripts/bootstrap/one-shot-setup.sh --host openclaw --profile full
bash ./check.sh --host openclaw --profile full --deep
```

### OpenCode

更薄的默认路径：

默认目标根目录是 `~/.config/opencode`，除非你显式设置 `OPENCODE_HOME`。

```powershell
pwsh -NoProfile -File .\install.ps1 -HostId opencode -Profile full
pwsh -NoProfile -File .\check.ps1 -HostId opencode -Profile full
```

```bash
bash ./install.sh --host opencode --profile full
bash ./check.sh --host opencode --profile full
```

如果你更希望沿用统一 bootstrap wrapper，也可以：

```powershell
pwsh -File .\scripts\bootstrap\one-shot-setup.ps1 -HostId opencode -Profile full
pwsh -File .\check.ps1 -HostId opencode -Profile full -Deep
```

```bash
bash ./scripts/bootstrap/one-shot-setup.sh --host opencode --profile full
bash ./check.sh --host opencode --profile full --deep
```

如果你要装“仅核心框架 + 可自定义添加治理”，把上面的 `full` 改成 `minimal`。
这不会改变 local-first work kernel 的形态，只会继续收缩内置 helper 面。

## 更新方式

如果本地还保留仓库，先更新仓库再重跑同一组命令：

```bash
git pull origin main
```

如果你跟随 tag 发布版本而不是 `main`，则：

```bash
git fetch --tags --force
git checkout vX.Y.Z
```

## 安装后仍需你本地处理的内容

命令安装只负责把 VibeSkills 安装到目标宿主根目录并运行检查。公开文档暂时不引导用户配置内置在线增强能力；不要在安装后步骤里要求用户补 provider、凭据、URL 或模型名。若这类能力没有通过公开路径配置好，最终报告只需要把 `online-ready` 单独标记为未就绪或未验证。

### Codex

- hook 当前冻结；这不是安装失败
- 如需查看这份共享安装里的受管设置面，默认检查 `~/.agents/settings.json`
- 不要把 `$vibe` 可发现性说成宿主插件或在线增强能力已完成

### Claude Code

- 会在保留真实 `~/.claude/settings.json` 的前提下，增量合并受约束的 `vibeskills` 设置面
- 更广的 Claude 插件、宿主侧能力配置、凭据和宿主行为仍由宿主侧管理
- 不要在安装报告里声称宿主侧 provider、插件或在线能力已经自动全部就绪

### Cursor

- 当前是 preview-guidance 路径
- 不覆盖真实 `~/.cursor/settings.json`
- Cursor 的宿主原生设置与扩展面仍按 Cursor 自身方式管理

### Windsurf

- 默认目标根目录是 `WINDSURF_HOME`，否则是真实宿主根目录 `~/.codeium/windsurf`
- repo 当前只负责 shared runtime payload，以及 `.vibeskills/host-settings.json` / `.vibeskills/host-closure.json` 这类 sidecar 状态
- Windsurf 宿主自身的本地设置仍按 Windsurf 自身方式管理

### OpenClaw

- 默认目标根目录是 `OPENCLAW_HOME` 或真实宿主根目录 `~/.openclaw`
- 宿主专页会展开 attach / copy / bundle 等细节
- OpenClaw 宿主自身的本地配置仍按 OpenClaw 自身方式管理

### OpenCode

- 默认目标根目录是 `OPENCODE_HOME`，否则是真实宿主根目录 `~/.config/opencode`
- 真实宿主配置目录 `~/.config/opencode` 仍由 OpenCode 自身管理
- direct install/check 与 one-shot wrapper 都保持 host-managed 边界
- 真实 `opencode.json`、provider 凭据、plugin 安装和在线能力授权仍按宿主自身方式管理
- 如需项目内隔离安装，使用 `--target-root ./.opencode`
