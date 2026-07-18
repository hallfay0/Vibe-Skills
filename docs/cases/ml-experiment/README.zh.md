<div align="right">
  <a href="./README.md">English</a> | <strong>中文</strong>
</div>

# 实际案例：完成一项机器学习实验

这个目录保存了 VibeSkills 一次已经通过最终验收的公开案例。任务使用
scikit-learn 自带的 Wisconsin Breast Cancer 数据集，完成数据审计、基线建模、
统计复核、结果图、科学报告和组会 Slides。运行编号为
`20260718T041559Z-51996499`。

这是一个软件复现案例，不是临床验证，也不用于诊断或患者决策。

## 结果概览

| 项目 | 结果 |
|:---|:---|
| 本地 Skill 范围 | 发布准备时，在本机已配置目录中统计到 100 多个可用 Skills |
| 本次实际选择 | 7 个 Skills |
| 任务安排 | 9 个模块，按 10 个工作单元顺序完成 |
| 执行结果 | 10 个完成，0 个失败，0 个阻塞 |
| 模块验收 | 18 项通过 |
| 跨产物检查 | 17 / 17 通过 |
| 最终验收 | `PASS`，状态为 `fully_ready` |

首页把 9 个模块归成了 5 组，方便快速阅读；原始计划和执行记录仍保留完整的
模块与工作单元。

## Skills 怎样参与

VibeSkills 先从已配置的本地 Skill 目录查找候选，再读取筛选后的候选 `SKILL.md`，
核对用途和限制。这个案例最后使用了下面 7 个 Skills。

| Skill | 负责的工作 |
|:---|:---|
| `exploratory-data-analysis` | 整理公开数据并检查结构、质量、类别分布、重复和泄漏风险 |
| `scikit-learn` | 建立固定的对照模型与逻辑回归基线，并检查能否精确复跑 |
| `statistical-analysis` | 计算变异性和不确定区间，并写清方法假设 |
| `scientific-critical-thinking` | 复核偏倚、泄漏、泛化范围和不能下的结论 |
| `scientific-visualization` | 生成 4 张可追溯到源数据的 PNG 图和对应 SVG |
| `sciwrite` | 分 5 轮检查科学报告，不改动已经确认的科学内容 |
| `presentations` | 制作 7 页 Slides，逐页渲染并检查版面和数据 |

完整选择记录见 [`selected-skills.json`](./evidence/selected-skills.json)。本机 Skill
数量来自同一台主机在案例发布准备阶段保存的
[`skill-inventory-snapshot.json`](./evidence/skill-inventory-snapshot.json)，不是运行时
自动写出的计数。

## 实际产物

| 数据与模型结果 | 交付检查 |
|:---:|:---:|
| ![类别分布图](./assets/class-balance.png) | ![混淆矩阵](./assets/confusion-matrix.png) |
| ![ROC 和精确率召回率曲线](./assets/roc-and-pr-curves.png) | ![交叉验证结果分布](./assets/cv-performance-distribution.png) |

4 张图同时提供了 [SVG 版本](./assets/vector/)。最终文字报告见
[`scientific-report.md`](./outputs/scientific-report.md)。7 页组会 Slides 可以直接查看
[`PPTX`](./outputs/group-meeting-slides.pptx)，下面是逐页渲染后的总览。

![7 页组会 Slides 总览](./assets/slides-montage.png)

## 原始材料

这些文件按任务从提出到验收的顺序保留，首页上的数字都可以在这里找到对应记录。

| 阶段 | 材料 |
|:---|:---|
| 原始任务 | [`original-task.md`](./evidence/original-task.md) |
| 需求确认 | [`requirement.md`](./evidence/requirement.md) |
| 执行计划 | [`execution-plan.md`](./evidence/execution-plan.md) · [`module-work-plan.json`](./evidence/module-work-plan.json) |
| Skill 选择 | [`selected-skills.json`](./evidence/selected-skills.json) · [`skill-inventory-snapshot.json`](./evidence/skill-inventory-snapshot.json) |
| 实际执行 | [`module-execution.json`](./evidence/module-execution.json) |
| 产物一致性 | [`consistency-check.json`](./evidence/consistency-check.json) |
| 最终验收 | [`delivery-acceptance-report.md`](./evidence/delivery-acceptance-report.md) · [`JSON`](./evidence/delivery-acceptance-report.json) |
| 公开副本说明 | [`PUBLICATION-NOTES.md`](./PUBLICATION-NOTES.md) |

[`case-manifest.json`](./evidence/case-manifest.json) 和
[`consistency-check.json`](./evidence/consistency-check.json) 是最终验收前生成的过程
快照，因此其中保留了当时的待验收状态。最终状态以随后生成的
`module-execution.json` 和 `delivery-acceptance-report.*` 为准。

## 复现实验核心

公开包保留了数据整理、基线实验、不确定性计算和制图脚本。先确认当前 `python`
指向 Python 3.12.12，再在仓库根目录运行：

```powershell
python --version
python -m venv .\docs\cases\ml-experiment\reproduce\.venv
.\docs\cases\ml-experiment\reproduce\.venv\Scripts\python.exe -m pip install -r .\docs\cases\ml-experiment\reproduce\requirements.lock
pwsh .\docs\cases\ml-experiment\reproduce\reproduce.ps1
```

脚本会把结果写到 `reproduce/generated/`，连续运行两次固定基线，并核对生成的
`metrics.json` 是否与已验收结果完全一致。生成目录和虚拟环境不会提交到 Git。
