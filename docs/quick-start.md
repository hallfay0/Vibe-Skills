# Quick Start

[English](./quick-start.en.md)

第一次来到这个仓库，不需要先读完所有文档。

你可以先把 VibeSkills 理解成一个给 AI Agent 用的 **工作内核入口**：

> 你给目标，`vibe` 接管推进节奏：先弄清需求，再建立工作模型，只在有帮助的地方绑定合适的 Skills，推动测试和验证，并把关键上下文留下来。

它不是一串让用户自己挑的工具菜单。它更像一个可移植的工作循环，让支持 Skills 的 AI Agent 更容易开始、更少失控、更适合做跨阶段任务。

## 1. 三分钟知道它解决什么

VibeSkills 重点解决五件事：

| 你遇到的问题 | VibeSkills 做什么 |
|:---|:---|
| Skills 太多，不知道该叫哪个 | kernel 会先把工作边界定清楚，再绑定真正有帮助的 Skills |
| AI 容易跳过需求、计划或测试 | `vibe` 把任务推进成有边界的阶段 |
| 用户总要手动提醒“先规划”“去验证” | 用户只给目标，流程控制交给 harness |
| 长任务换会话后上下文丢失 | 需求、计划、决策和证据会结构化保存 |
| 新领域 Skills 接入成本高 | 核心直接扫描已安装的本地 skill 根目录，所以新 skill 能接入同一套流程，而不用把产品再做成更大的中心目录 |

如果你只记一句话：

> **VibeSkills 的核心创新，是把“按工作绑定 Skills + 测试验证 + 跨会话记忆”封装成一个通用、好安装、好上手的工作内核入口。**

## 2. 最快开始使用

先打开简化安装说明：

- [`install/README.md`](./install/README.md)

如果你想走最短路径，就从发布版本 zip 开始，不要从仓库 checkout 开始。若已经安装过 VibeSkills，就先下载更新版本的发布版本 zip，再对同一个 skills 目录执行 `update`。

安装完成后，从宿主的 Skills 入口调用：

| 宿主 | 常见调用方式 |
|:---|:---|
| Codex | 在请求里附上 `$vibe` |
| Claude Code | 在请求里附上 `/vibe` |
| OpenCode | 使用 `/vibe` 或宿主支持的 Skills 调用方式 |
| Cursor / Windsurf / OpenClaw | 参考对应宿主的 Skills 入口说明 |

更新时继续走同一条管理路径，但命令要从新的解压发布目录里运行：

- `update.ps1 -SkillsDir <skills-dir>`
- `update.sh --skills-dir <skills-dir>`

## 3. 当前公开入口

当前公开、宿主可见的入口只有：

- `vibe`

`vibe` 是主入口。它会在需求、计划和执行边界停下来，等到明确确认后再继续推进。

已安装副本的升级走命令路径。请对同一个 skills 目录使用 `update`，而不是再暴露第二个公开运行时入口。

旧阶段专用入口和旧 CLI 入口已经退出公开的宿主可见入口，不应再宣传或安装。

如果你想提高执行强度，只使用公开的轻量覆盖：

- `--l`
- `--xl`

旧的阶段 ID 可能仍保留在运行时元数据里，用于兼容和连续性；但它们不是用户应该调用的 commands / skills。

## 4. 什么时候继续看更多文档

按你的目的选，不用从头读：

| 你想做什么 | 看这里 |
|:---|:---|
| 想看项目完整介绍 | [`../README.zh.md`](../README.zh.md) |
| 想安装或更新 | [`install/README.md`](./install/README.md) |
| 想看完整命令参考 | [`install/README.md`](./install/README.md) |
| 不确定宿主根目录 | [`cold-start-install-paths.md`](./cold-start-install-paths.md) |
| 使用 OpenCode | [`cold-start-install-paths.md`](./cold-start-install-paths.md) |
| 使用 OpenClaw | [`cold-start-install-paths.md`](./cold-start-install-paths.md) |
| 想手动/离线安装 | [`install/README.md`](./install/README.md) |
| 想看安装后的正常 skill 扩展路径 | [`install/README.md`](./install/README.md) |
| 想添加或扫描更多本地 skill 根目录 | [`install/README.md`](./install/README.md) |
| 想理解项目为什么存在 | [`manifesto.md`](./manifesto.md) |

## 5. 几个容易混淆的点

- `$vibe` 或 `/vibe` 只表示进入 governed runtime，不单独证明宿主插件、provider 或在线增强已经完成。
- `check` 证明的是 `installed locally`。
- `runtime coherent` 只会在一次真实的 `vibe` 运行返回 `session_root` 且运行时真相产物齐备之后成立。
- `delivery accepted` 来自 `delivery-acceptance-report.json` / `.md`。
- VibeSkills 是 Skills 格式运行时，不是让你在终端里直接运行的独立 CLI。

## 推荐阅读顺序

如果你只想走最短路径：

1. [`../README.zh.md`](../README.zh.md)
2. [`install/README.md`](./install/README.md)
3. 用一个小任务试试 `vibe`

从一个简单请求开始就好，比如：

> 帮我把这个需求先澄清并拆成计划 `$vibe`

你会更快感受到它和普通 Skills 列表的区别：用户不用一直做调度员，AI 会在 harness 下更有节奏地推进任务。
