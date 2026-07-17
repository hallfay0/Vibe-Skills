<div align="right">
  <a href="./README.md">English</a> | <strong>中文</strong>
</div>

<div align="center">

<img src="./logo.png" width="230" alt="VibeSkills Logo">

<h1>VibeSkills</h1>

<h3>让本地 Skills 成体系地工作起来。</h3>

<p><strong>复杂任务经常只触发最显眼的那几个 Skills。</strong><br>
VibeSkills 先把整个任务拆开，再逐模块组织相关的本地 Skills，<br>
让你已经安装的能力真正参与到适合它的工作里。</p>

<a href="https://github.com/foryourhealth111-pixel/Vibe-Skills/releases/latest">
  <img src="https://img.shields.io/github/v/release/foryourhealth111-pixel/Vibe-Skills?display_name=tag&sort=semver&style=for-the-badge&color=14515B" alt="最新版本">
</a>

<br>

<a href="./docs/install/README.md">
  <img src="./docs/assets/install-cta-cn.svg" width="327" height="56" alt="安装 VibeSkills">
</a>

<br>

<a href="./docs/quick-start.md">快速开始</a> ·
<a href="https://github.com/foryourhealth111-pixel/Vibe-Skills/releases/tag/v4.0.0">v4.0.0 发布页</a> ·
<a href="./docs/README.md">文档索引</a> ·
<a href="https://github.com/foryourhealth111-pixel/Vibe-Skills/stargazers">Star 项目</a>

</div>

---

## 为什么需要 VibeSkills

> [!IMPORTANT]
> 一个复杂任务通常不止一件事。如果任务有四部分，AI 可能只在其中两部分想到
> 使用 Skill，剩下两部分仍然临场处理，即使你已经装了更合适的 Skill。
> VibeSkills 会先看完整任务，再决定每一部分需要什么帮助。

| 只靠被动触发 | 使用 VibeSkills |
|:---|:---|
| AI 临时根据几个关键词决定用什么 | 先把整个任务完整拆开 |
| 容易反复使用最熟悉的一两个 Skills | 每一部分都看看有没有更合适的 Skill |
| 没匹配到的部分继续临场处理 | 把合适的 Skill 安排到具体工作上，并写清要做出什么 |
| 各次调用互不衔接 | 最后把所有结果汇总起来一起检查 |

VibeSkills 做的事情很直接：**先把任务拆清楚，再让合适的 Skills 去帮助合适的
部分**。它不会为了显得热闹而把所有 Skills 都叫一遍。某一部分不需要专门的
Skill，就由当前 AI 继续完成；需要时，则不会因为被动触发没碰上而错过。

## 先拆任务，再组织 Skills

```mermaid
flowchart TB
    task["一个复杂任务"] --> map["VibeSkills 先把任务拆开"]
    map --> m1["01 · 范围 / 调研"]
    map --> m2["02 · 实现 / 修改"]
    map --> m3["03 · 测试 / 审查"]
    map --> m4["04 · 文档 / 交付"]

    pool["你已经安装的本地 Skills"] --> match["查看每个 Skill 的说明，按工作需要选择"]
    match --> m1
    match --> m2
    match --> m3
    match --> m4

    m1 --> integrate["汇总各部分结果"]
    m2 --> integrate
    m3 --> integrate
    m4 --> integrate
    integrate --> proof["检查结果，并记住做到哪里"]

    classDef task fill:#0F3D3E,stroke:#0F3D3E,color:#FFFFFF,stroke-width:2px
    classDef map fill:#EDE9FE,stroke:#7C3AED,color:#2E1065,stroke-width:2px
    classDef pool fill:#FFF7ED,stroke:#EA580C,color:#7C2D12,stroke-width:2px
    classDef match fill:#FEF3C7,stroke:#CA8A04,color:#713F12,stroke-width:2px
    classDef blue fill:#E0F2FE,stroke:#0284C7,color:#0C4A6E
    classDef coral fill:#FFE4E6,stroke:#E11D48,color:#881337
    classDef green fill:#DCFCE7,stroke:#16A34A,color:#14532D
    classDef violet fill:#F3E8FF,stroke:#9333EA,color:#581C87
    classDef finish fill:#ECFDF5,stroke:#059669,color:#064E3B,stroke-width:2px

    class task task
    class map map
    class pool pool
    class match match
    class m1 blue
    class m2 coral
    class m3 green
    class m4 violet
    class integrate,proof finish
```

先拆任务，再选 Skill。四部分工作如果分别需要不同的帮助，就可以分别安排；
某一部分不需要专门的 Skill，就继续由当前 AI 负责。重点是把事情做好，不是
单纯增加调用次数。

## 除了组织 Skills，它还会做这些事

VibeSkills 把 harness 工程的一种基本做法用在了 Skills 的组织和调用上。简单说，
就是给任务加上一套从开始到结束都能照着走的流程：先确认需求，再安排工作并保存
记录，最后对照计划检查结果。Skills 的选择、分工和执行，也放在这套流程里进行。

<p align="center">
  <img src="./docs/assets/vibeskills-harness-overview-cn.svg" width="920" alt="VibeSkills 从确认需求开始，经过 L 或 XL 分级、组织 Skills、执行并保存记录，最后检查结果；代码任务可以进入 TDD 循环">
</p>

- **确认需求。** 开始工作前，VibeSkills 会先确认任务目标、限制条件、已有材料和
  最后需要交付的内容。需求没有确认时，它会停在这里，不会直接开始执行。

- **保存任务记录。** 需求、计划、执行进度和最终结果都会保存在这次任务的记录中。
  更换会话后，可以从已有记录继续；以后复查任务时，也能知道当时确认了什么、
  实际做了什么。

- **自动推荐任务级别。** VibeSkills 会根据任务的范围、步骤、依赖关系和是否适合
  同时推进，推荐 `L` 或 `XL`。用户也可以自己选择。

| 级别 | 适合的任务 | 处理方式 |
|:---|:---|:---|
| `L` | 步骤较多，但规模仍然可控 | 拆分后按顺序推进，处理过程较简单，使用的时间和上下文较少 |
| `XL` | 包含多个相对独立部分的大任务 | 拆得更细，互不影响时最多同时推进两项工作，并增加协调和结果汇总 |

- **检查最终结果。** 工作完成后，VibeSkills 会把计划中的每一项与实际结果逐一
  对照。只要仍有必做项目未完成、失败或被卡住，任务就不会被写成已经完成。

- **安排测试。** 如果任务涉及代码，VibeSkills 会在适合时优先采用测试驱动开发
  （TDD）：先用失败测试确认问题，再完成修改并重新运行测试。测试结果会和其他
  任务结果一起记录。

## 它怎样找到合适的 Skill

VibeSkills 只会从你指定的本地 Skill 文件夹里寻找。一个 Skill 至少要有可读取的
`SKILL.md`，名称不能和另一个 Skill 重复，而且要真的适合当前这部分工作，AI
才会选择它。

你也可以在配置里增加其他本地文件夹。这样添加自己的 Skill 或第三方 Skill 时，
不必等 VibeSkills 项目本身收录它。VibeSkills 不会自动调用你安装的所有 Skills，
只会选择当前任务真正用得上的部分。

<details>
<summary><strong>开发者：这些选择保存在哪里</strong></summary>

计划阶段，`agent_skill_organization` 保存每一部分准备使用哪些 Skills。开始执行后，
`module_assignments` 保存实际分配。发现一个 Skill 只说明它可以考虑，不代表它
已经参与了工作。

</details>

---

## 运行后会保存什么

VibeSkills 会把安装情况、任务过程和最终检查分别保存下来。每个文件回答的问题
不同，不需要靠一张截图或一句“已经完成”来猜。

<details>
<summary><strong>查看保存的文件</strong></summary>

| 文件或目录 | 用来做什么 |
|:---|:---|
| `install-receipt.json` | 记录安装器写入的文件，供 `check` 检查安装是否完整、文件有没有被改动 |
| `session_root` | 保存一次任务的输入、进度、重要决定和运行摘要 |
| `module-work-plan.json` | 保存已经确认的任务安排，包括各部分由谁负责、需要交付什么、怎样检查 |
| `module-execution.json` | 保存各部分实际完成的结果，以及完成、失败或被卡住的状态 |
| `delivery-acceptance-report.json` 或 `.md` | 保存最终检查结果，说明哪些项目已经通过 |

</details>

这些记录不能互相代替。安装成功，不代表任务已经跑完；有运行记录，也不代表
最终结果已经通过检查。公开案例应该让人能顺着需求、计划、实际结果和最终检查
一路看下来。

维护项目时，可以使用这份[提交前检查清单](docs/status/non-regression-proof-bundle.md)。
一般先完成清单里的基础检查；只有发现风险时，再扩大检查范围。

## 安装

请从发布页面下载发布版本 zip，并先解压到准备安装 Skills 的文件夹之外。
默认目录是 `~/.agents/skills`。

安装、更新、检查、卸载和旧版本升级的命令都放在这里：

**[打开完整安装说明](./docs/install/README.md)**

当前版本下载：
[vibe-skills-4.0.0-public.zip](https://github.com/foryourhealth111-pixel/Vibe-Skills/releases/download/v4.0.0/vibe-skills-4.0.0-public.zip)

## 安装后会发生什么

- 你只需要记住一个入口：`vibe`。
- 安装器只会在 `<SkillsDir>/vibe` 中管理 VibeSkills 自己的文件，不会再安装一套
  内置 Skill 集合。
- 你自己的其他 Skills 保持原位。VibeSkills 会从共享 Skills 目录，或从
  `~/.vibeskills/skill-roots.json` 与
  `<workspace>/.vibeskills/skill-roots.json` 指定的本地文件夹中寻找。
- 安装器不会替你修改 AI 工具的设置、系统提示词或命令，也不会自动配置 MCP 服务。
- 你确认计划后，当前正在工作的 AI 会按计划完成任务。VibeSkills 会记下哪些部分完成了、
  哪些失败了、哪些被卡住。
- 需求、计划和源码仍然以项目文件与 Git 记录为准。工作区记忆只负责帮助你接着
  上次的进度继续，不会替代这些文件。

想了解内部实现，以及 Python 和 PowerShell 分别负责什么，请看
[架构说明](./docs/architecture/local-agent-kernel-v2.md)。

## 接下来可以看什么

| 你想做什么 | 从这里开始 |
|:---|:---|
| 安装、更新、卸载 | [简明安装指南](./docs/install/README.md) |
| 第一次使用 | [快速开始](./docs/quick-start.md) |
| 当前发布版本 | [v4.0.0 发布说明](./docs/releases/v4.0.0.md) |
| 查看哪些 AI 工具已经测试过 | [支持情况说明](./docs/universalization/host-capability-matrix.md) |
| 了解它怎么工作 | [文档索引](./docs/README.md) |
| 排查问题 | [故障排查](./docs/troubleshooting.md) |
| 参与贡献 | [贡献指南](./CONTRIBUTING.md) |

## 社区与致谢

问题、纠错和范围清晰的贡献都可以通过
[GitHub Issues](https://github.com/foryourhealth111-pixel/Vibe-Skills/issues)
与 Pull Request 提交。项目参考并适配了 Superpowers、Get Shit Done、OpenSpec、
spec-kit、mem0、Scrapling、Serena 等开源项目的思路；归属说明见
[NOTICE](./NOTICE) 与 [第三方许可证](./THIRD_PARTY_LICENSES.md)。

社区贡献者包括
[xiaozhongyaonvli](https://github.com/xiaozhongyaonvli) 和
[ruirui2345](https://github.com/ruirui2345)。

## Star History

<p align="center">
  <a href="https://www.star-history.com/?repos=foryourhealth111-pixel%2FVibe-Skills&type=date&legend=top-left">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/image?repos=foryourhealth111-pixel/Vibe-Skills&type=date&theme=dark&legend=top-left">
      <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/image?repos=foryourhealth111-pixel/Vibe-Skills&type=date&legend=top-left">
      <img alt="VibeSkills Star History" src="https://api.star-history.com/image?repos=foryourhealth111-pixel/Vibe-Skills&type=date&legend=top-left">
    </picture>
  </a>
</p>
