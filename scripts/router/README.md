# Router Surface

- Scripts root: [`../README.md`](../README.md)
- Config index: [`../../config/index.md`](../../config/index.md)

## What Lives Here

`scripts/router/` 保存内部专家候选发现面，也就是 candidate discovery surface。这里负责给出候选项、补充澄清问题、整理确认界面，以及保留旧调用方仍需要的 compatibility projection。它不负责声明真正的工作归属、执行事实或完成结论；这些事实应由 kernel 侧产物给出。公开治理入口仍然是 `$vibe` / `/vibe`。

## Current Layout

| Path | Role |
| --- | --- |
| [`resolve-pack-route.ps1`](resolve-pack-route.ps1) | 内部候选发现入口；产出候选项、确认需要、确认选项与探针数据，并保留兼容字段 |
| [`legacy/`](legacy) | 兼容旧 routing 路径的辅助实现 |
| [`modules/`](modules) | router 可复用模块：规则候选、澄清提示、候选排序、确认界面 |

## Rule

- router 目录只解释“如何找候选、何时需要确认、如何展示确认面”。
- 兼容字段可以继续存在，但只能当作旧调用方的镜像，不能当作工作真相。
- 公开执行、阶段治理与验证仍分别落到 `SKILL.md`、`protocols/`、`scripts/governance/` 与 `scripts/verify/`。
- 新增 router helper 时，优先补 `modules/` 级文档，而不是把说明塞进单个脚本顶部。
