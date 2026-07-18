# Case 01 User Task

The governed prompt below preserves the user's relevant wording and excludes the unrelated second case.

> 重点证明：VibeSkills 能把一个复杂任务拆成模块，并组织用户本地已经安装的不同 Skills 分别完成合适的工作，最后汇总并验收。
>
> 主案例优先考虑“机器学习实验完整交付”：baseline、统计检查、结果图、科学报告、组会 Slides。它应产生视觉上可展示的真实结果。
>
> 这些只是候选方向。若本机材料或 Skills 不足以真实完成，必须基于可验证条件调整案例，不得伪造。使用实际安装的 VibeSkills 运行时和实际本地 Skills，不要手工模拟 Skill 编排。每个案例使用全新的 run ID；不得复用同一个 ID 作为新任务和 continuation 来源。遵守 requirement_doc、xl_plan 等用户批准停点，停点出现时等待我在新任务中确认，不得同轮越过。
>
> 把实验文件和证据放在 <case-workspace>\<case-id> 下，保持仓库提交面不变。每个案例最终至少要有：真实用户任务、实际模块拆分、实际选中的本地 Skills 及职责、真实产物、module execution 状态、最终 acceptance 结果，以及可用于 README 的简短中英文摘要和视觉素材建议。
>
> 禁止使用 Codex 浏览器插件、Chrome、Playwright 或任何浏览器自动化。不要编造指标、截图、终端输出、成功状态或公共链接。没有完整证据就明确标为未完成，不得包装成案例。
