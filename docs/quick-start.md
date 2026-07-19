# Quick Start

[English](./quick-start.en.md)

第一次来到这个仓库，不需要先读完所有文档。

你可以先把 VibeSkills 理解成一套帮助 AI 把复杂任务做完整的工作方式：

> 你只要给目标。`vibe` 会先把任务问清楚，拆成几部分，为每一部分找合适的
> Skills，然后检查结果，并记住任务做到哪里。

它不是一长串等你自己挑选的工具。它会把需要完成的工作安排好，让 AI 少跳步骤，
也让长任务在换会话以后还能继续。

## 1. 三分钟知道它解决什么

VibeSkills 重点解决五件事：

| 你遇到的问题 | VibeSkills 做什么 |
|:---|:---|
| Skills 太多，不知道该用哪个 | 先把任务拆清楚，再为每一部分找真正有帮助的 Skills |
| AI 容易跳过需求、计划或测试 | 在几个重要节点停下来，确认后再继续 |
| 用户总要反复提醒“先规划”“去检查” | 你只需要说明目标，`vibe` 负责把步骤安排好 |
| 长任务换会话后容易忘记进度 | 把需求、计划、重要决定和结果保存在任务记录里 |
| 新 Skill 很难接进现有流程 | 把 Skill 放进指定的本地文件夹，就可以让 VibeSkills 在合适的任务中找到它 |

如果你只记一句话：

> **VibeSkills 会先把任务拆清楚，再按需要使用 Skills，并把检查结果和任务进度
> 保存下来。**

## 2. 最快开始使用

先打开简化安装说明：

- [`install/README.md`](./install/README.md)

最省事的做法是从发布版本 zip 开始，不要直接从仓库源码安装。正常更新时，
下载新版本的 zip，再对原来的 Skills 文件夹运行 `update`。要重新安装时，
直接删除原来的 `<SkillsDir>/vibe`，再安装当前版本。

安装完成后，从当前 AI 应用的 Skills 入口启动。VibeSkills 的核心不绑定任何
单一工具，凡是支持本地 Skills 的 AI 应用都可以使用；具体可输入 `$vibe`、
`/vibe`，或使用该应用提供的 Skills 入口语法。

所有应用都使用同一种安装模型：

1. 选择当前应用能够扫描的 Skills 目录。
2. 把同一份安装包安装到 `<SkillsDir>/vibe`。
3. 通过当前应用的 Skills 入口调用 `vibe`。

应用使用其他 Skills 路径时，查看[选择 Skills 目录](./cold-start-install-paths.md)。

更新时，请从新版本解压后的文件夹中运行命令：

- `update.ps1 -SkillsDir <skills-dir>`
- `update.sh --skills-dir <skills-dir>`

## 3. 怎么启动

你只需要记住一个入口：

- `vibe`

`vibe` 会先确认需求和计划，在需要你决定的地方停下来，得到确认后再继续。

升级时，对原来的 Skills 文件夹使用 `update`。不需要再记一个专门的升级入口。

旧版本里按阶段区分的入口已经停用，不需要再安装或调用。

如果任务更复杂，可以使用：

- `--l`
- `--xl`

旧名称有时仍会出现在内部记录里，但它们不是需要你调用的命令或 Skills。

## 4. 什么时候继续看更多文档

按你的目的选，不用从头读：

| 你想做什么 | 看这里 |
|:---|:---|
| 想看项目完整介绍 | [`../README.zh.md`](../README.zh.md) |
| 想安装或更新 | [`install/README.md`](./install/README.md) |
| 想看完整命令参考 | [`install/README.md`](./install/README.md) |
| 不确定 Skills 应该装到哪里 | [`cold-start-install-paths.md`](./cold-start-install-paths.md) |
| 使用 OpenCode | [`cold-start-install-paths.md`](./cold-start-install-paths.md) |
| 使用 OpenClaw | [`cold-start-install-paths.md`](./cold-start-install-paths.md) |
| 想手动/离线安装 | [`install/README.md`](./install/README.md) |
| 想让 VibeSkills 找到更多本地 Skills | [`install/README.md`](./install/README.md) |
| 想添加其他本地 Skill 文件夹 | [`install/README.md`](./install/README.md) |
| 想理解项目为什么存在 | [`manifesto.md`](./manifesto.md) |

## 5. 几个容易混淆的点

- `$vibe` 或 `/vibe` 只表示启动 VibeSkills，不代表当前 AI 工具的所有扩展功能都
  已经配置完成。
- `check` 只检查安装器管理的文件是否都在，以及后来有没有被改动。
- `session_root` 是一次任务的记录文件夹，里面保存输入、当前进度、重要决定和摘要。
- `delivery-acceptance-report.json` 或 `.md` 保存最终检查结果，告诉你哪些项目通过、
  失败或被卡住。
- VibeSkills 需要从 AI 工具的 Skills 入口启动，不是一个单独的终端程序。

## 推荐阅读顺序

如果你只想走最短路径：

1. [`../README.zh.md`](../README.zh.md)
2. [`install/README.md`](./install/README.md)
3. 用一个小任务试试 `vibe`

从一个简单请求开始就好，比如：

> 帮我把这个需求先澄清并拆成计划 `$vibe`

你会很快看到它和普通 Skills 列表的区别：你不用一直提醒下一步，AI 会按已经确认
的安排继续完成任务。
