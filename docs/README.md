# VCO 文档索引

`docs/` 只负责长期说明、当前状态入口和最小治理导航，不承担运行时真相本身，也不再公开堆放大批个人执行日志。

## Start Here

- [`install/README.md`](./install/README.md)：当前公开安装入口；说明默认 SkillsDir 路径、命令边界与补充文档

| 你要做什么 | 入口 |
| --- | --- |
| 安装或试用 | [`install/README.md`](./install/README.md) |
| 看懂安装边界和命令参考 | [`install/README.md`](./install/README.md) |
| 查看当前状态 | [`status/README.md`](./status/README.md) |
| 查看治理专题和 guardrails | [`governance/README.md`](./governance/README.md) |
| 查看设计说明和 playbook | [`design/README.md`](./design/README.md) |
| 查看外部工具和 overlay 边界 | [`external-tooling/README.md`](./external-tooling/README.md) |
| 理解变更规则 | [`developer-change-governance.md`](./developer-change-governance.md) |
| 理解系统结构 | [`architecture.md`](./architecture.md) |

## 按需再看

- [`cold-start-install-paths.md`](./cold-start-install-paths.md)：其他环境与旧宿主说明；当前安装仍以 install README 为准

## Current Runtime

- 主技能合同：[`../SKILL.md`](../SKILL.md)
- 运行时协议：[`../protocols/runtime.md`](../protocols/runtime.md)
- 运行时真相合同：[`governance/current-runtime-field-contract.md`](./governance/current-runtime-field-contract.md)
- 路由兼容合同：[`governance/current-routing-contract.md`](./governance/current-routing-contract.md)
- 多代理协议：[`../protocols/team.md`](../protocols/team.md)
- bounded re-entry 与 host decision SOP：见 [`../SKILL.md`](../SKILL.md) 的 Structured host decision SOP；`vibe` 会在 `requirement_doc` 和 `xl_plan` 边界返回控制权，宿主需用 `--continue-from-run-id`、`--bounded-reentry-token`、`--host-decision-json` 继续
- 当前 live summary：[`status/current-state.md`](./status/current-state.md)
- 最小 proof contract：[`status/non-regression-proof-bundle.md`](./status/non-regression-proof-bundle.md)

## Governance

- 文档结构规则：[`docs-information-architecture.md`](./docs-information-architecture.md)
- source-neutral 链接规则：[`governance/source-neutral-link-governance.md`](./governance/source-neutral-link-governance.md)
- 打包与兼容拓扑：[`version-packaging-governance.md`](./version-packaging-governance.md)
- 清洁度规则：[`repo-cleanliness-governance.md`](./repo-cleanliness-governance.md)
- 治理专题索引：[`governance/README.md`](./governance/README.md)
- 可观测性规则：[`governance/observability-consistency-governance.md`](./governance/observability-consistency-governance.md)
- 项目交付验收规则：[`governance/vibe-governed-project-delivery-acceptance-governance.md`](./governance/vibe-governed-project-delivery-acceptance-governance.md)

## Cross-Layer Handoff

- 机器可读配置：[`../config/index.md`](../config/index.md)
- 长期 reference：[`../references/index.md`](../references/index.md)
- 治理专题：[`governance/README.md`](./governance/README.md)
- 计划与批次上下文：[`plans/README.md`](./plans/README.md)
- 设计与 playbook：[`design/README.md`](./design/README.md)
- 外部工具边界：[`external-tooling/README.md`](./external-tooling/README.md)
- release 记录：[`releases/README.md`](./releases/README.md)
- 历史归档入口：[`archive/README.md`](./archive/README.md)

## Rules

- 根目录 `docs/*.md` 只放长期文档，不把 dated plans 或 batch reports 升格为长期合同。
- 安装口径以 [`install/README.md`](./install/README.md) 为主；[`cold-start-install-paths.md`](./cold-start-install-paths.md) 只保留其他环境和旧宿主说明，不再充当当前安装主入口。
- specialized governance、design、external-tooling 叶子页优先放入对应 family 目录，而不是继续堆回 `docs/*.md` 根层。
- 当前状态以 [`status/current-state.md`](./status/current-state.md) 和 `outputs/verify/**` 为准，不在索引页手工维护状态表。
- 更低层的脚本 operator surface 仍在 [`../scripts/README.md`](../scripts/README.md)，但它不是 `docs/` 根索引的公开第一跳入口。
- 新增长期入口时更新本页；dated 材料只更新对应子目录 `README.md`。
- 历史 dated 材料默认从 git history 或 [`archive/README.md`](./archive/README.md) 的最小索引恢复，不再把整批日志叶子长期挂在 live docs surface。
