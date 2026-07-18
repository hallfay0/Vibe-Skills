# 重点证明：VibeSkills 能把一个复杂任务拆成模块，并组织用户本地已经安装的不同 Skills 分别完成合适的工作，最后汇总并验收。 主案例优先考虑“机器...

## Goal
重点证明：VibeSkills 能把一个复杂任务拆成模块，并组织用户本地已经安装的不同 Skills 分别完成合适的工作，最后汇总并验收。

主案例优先考虑“机器学习实验完整交付”：baseline、统计检查、结果图、科学报告、组会 Slides。它应产生视觉上可展示的真实结果。

这些只是候选方向。若本机材料或 Skills 不足以真实完成，必须基于可验证条件调整案例，不得伪造。使用实际安装的 VibeSkills 运行时和实际本地 Skills，不要手工模拟 Skill 编排。每个案例使用全新的 run ID；不得复用同一个 ID 作为新任务和 continuation 来源。遵守 requirement_doc、xl_plan 等用户批准停点，停点出现时等待我在新任务中确认，不得同轮越过。

把实验文件和证据放在 <case-workspace>\<case-id> 下，保持仓库提交面不变。每个案例最终至少要有：真实用户任务、实际模块拆分、实际选中的本地 Skills 及职责、真实产物、module execution 状态、最终 acceptance 结果，以及可用于 README 的简短中英文摘要和视觉素材建议。

禁止使用 Codex 浏览器插件、Chrome、Playwright 或任何浏览器自动化。不要编造指标、截图、终端输出、成功状态或公共链接。没有完整证据就明确标为未完成，不得包装成案例。 Revision delta: Freeze the workflow level as L: use one governed serial main line, while still assigning different modules to the local Skills that actually own them.; Use the scikit-learn built-in Wisconsin Breast Cancer dataset without external downloads. Treat it only as a public, reproducible, non-clinical demonstration and do not make clinical-use claims.; Create an isolated case-local Python 3.12 virtual environment and record pinned dependency versions. Do not silently use the default Python 3.10 environment for the scikit-learn module because the installed scikit-learn Skill declares Python 3.11 or newer.; Build a reproducible classification experiment with a DummyClassifier sanity comparator and a StandardScaler plus LogisticRegression primary baseline. Use fixed random seeds, a stratified holdout split, and repeated stratified cross-validation. Do not add hyperparameter search unless a later approved plan justifies it.; Audit dataset shape, target balance, missingness, duplicate rows, split integrity, and leakage risk. Report at least ROC AUC, balanced accuracy, F1, confusion-matrix results, cross-validation variability, and justified uncertainty intervals. Use formal significance tests only when the statistical Skill confirms that the design supports them.; Write all task-owned deliverables under <case-root>\deliverables. Include environment and reproduction instructions, executable experiment code, machine-readable metrics and fold-level results, data and method audit, at least three clear result figures, a concise scientific Markdown report, a group-meeting PPTX, rendered slide previews, short English and Chinese README summaries, and visual-material recommendations.; Every metric and conclusion in figures, the report, the slide deck, and the README summaries must trace to the same machine-readable experiment results. Clearly disclose limitations, the demonstration-only scope, and any failed or blocked checks.; Render and inspect the slide deck and inspect the result figures without using the Codex browser plugin, Chrome, Playwright, or browser automation. Do not modify Vibe-Skills-main README files or existing docs/assets images.; Completion requires real module-execution evidence, reproducibility verification, cross-deliverable consistency checks, phase cleanup, and a passing final delivery acceptance report. If any required evidence or artifact is missing, keep the case explicitly incomplete and do not present it as a README success case.. Update: 总控补充：保持本轮目标严格为生成可审计的 L 级计划并停在 xl_plan。完整阅读正式保留候选的 SKILL.md 即可；不要在计划阶段制作 Slides、预览图或其他交付物，也不要继续扩展候选集合。计划满足需求、分工、依赖、写入范围和验收合同后立即完成本轮停点。 Update: 总控已审计冻结的执行计划、module-work-plan.json 和 runtime-summary.json，批准案例一计划并允许通过受控 re-entry 执行。请只从 Run ID 20260718T033536Z-7149f0c2 使用当前 token 继续，严格执行冻结的 9 个模块与 10 个串行波次，然后走 canonical phase_cleanup 和最终 delivery acceptance；禁止在 VibeSkills 之外手工伪造执行状态。执行保护：statistical-analysis owner 负责 deliverables/03-statistical-review/statistics/**；scientific-critical-thinking verifier 只新增或更新 deliverables/03-statistical-review/method-review/**，不得覆盖 owner 的 uncertainty.json 或 statistical-review.md。每个自动和人工验收项都必须留下真实证据；任何必需模块、渲染检查、复现检查、跨产物一致性检查或 cleanup/acceptance 失败，就保持案例未完成并清楚记录原因。不要修改 README、现有 docs/assets、分支或提交。持续更新 <case-workspace>\thread_state.md，执行结束或遇到真实阻塞时返回完整状态。

## Deliverable
The user-requested outcome described in the full goal, with supporting evidence appropriate to that outcome

## Constraints
- Do not bypass the fixed six-stage governed runtime.
- Do not widen scope silently beyond the frozen requirement document.

## Acceptance Criteria
- Requirement document is frozen before execution.
- Execution plan exists before task execution.
- Verification evidence exists before completion claims.
- Phase cleanup receipt is produced.

## Product Acceptance Criteria
- Requirement document is frozen before execution.
- Execution plan exists before task execution.
- Verification evidence exists before completion claims.
- Phase cleanup receipt is produced.
- The delivered output must satisfy observable behavior implied by the frozen goal and deliverable, not only internal runtime progress.
- Full completion wording is allowed only after downstream delivery truth is passing.

## Manual Spot Checks
- None required beyond automated verification for this task unless the execution scope expands to a user-visible or interactive flow.

## Completion Language Policy
- Full completion wording is allowed only when governance truth, engineering verification truth, workflow completion truth, and product acceptance truth are all passing.
- `completed_with_failures`, degraded execution, or pending manual actions must be reported as non-complete states.
- If manual spot checks remain pending, the run must be described as requiring manual review rather than fully ready.

## Delivery Truth Contract
- Governance truth: requirement, plan, execution, and cleanup artifacts remain traceable and authoritative.
- Engineering verification truth: targeted verification passes or fails explicitly; silence does not count as success.
- Workflow completion truth: planned units, delegated lanes, and specialist outputs reconcile back into the governed plan.
- Product acceptance truth: observable deliverable behavior satisfies frozen acceptance criteria before full completion language is allowed.

Non-goals:
- Do not create separate M/L/XL entry commands.
- Do not introduce a second router or control plane.

## Skill Search Guide
- 先拆任务，再拆模块
- 会按模块搜索本地 skills
- 每个模块单独搜索本地 skills
- 会先看候选 skill 名和短描述，再打开并阅读候选 `SKILL.md`
- 每个模块最多保留 3 个候选，避免上下文污染
- 以候选 `SKILL.md` 的真实用途为准，不按词面碰撞判断
- 会给出 `L` / `XL` 两套 skills 组织方案，并说明每个 skill 的职责
- 优先选择真正负责该模块的 owner，不选只沾边的 helper
- 一个 skill 可以覆盖多个模块
- explicit_only skills 只有在用户明确点名时才可入选
- 不得跨越候选 skill 声明的负边界或适用限制
- 没有 owner 时必须报缺口，不得伪装覆盖
- 没有 owner 的模块会明确标出缺口
- requirement 阶段公开搜索办法，并在请用户选择前由 Agent 分别给出 L / XL 的具体工作流和候选 skill 名称；这些名称必须标为尚未正式选定或使用，不得公开程序候选排名或预选结果
- xl_plan 阶段公开模块、候选、最终采用和缺口
- execute 阶段公开本次实际启用的 skills

## Workflow Level Confirmation
- User-visible: True
- Recommended level: XL
- Recommendation reason: 当前任务看起来更像高协调成本交付：需要先冻结需求和计划，再把多技能或多产物工作拆成分波次执行，避免执行中途再回头重排分工。
- Why this decision matters: L 和 XL 会直接改变后续的协作深度、是否进入分波次执行，以及证据和回归边界的强度。
- Before asking the user to choose L or XL, explain each task-specific workflow and list its task-specific candidate skill names. Label those names as candidates that are not yet selected or used.
- L: L 级适合多步骤但主要串行的工作：会确认需求和计划，证据要求完整，但一般由一个主流程推进。
- L workflow: 先冻结需求和计划，再由一个主流程串行推进 Agent 组织出的方案。
- L skills: 会先按模块搜索本地 skills、阅读候选 `SKILL.md`，再给出较轻量的 L 级组织方案；涉及代码改动或缺陷修复时，会补充 `tdd` 这类 failure-first 验证 skill，但不默认拆成多代理。
- L rationale: 适合仍然是一个主交付物、依赖链较短、并行收益不高的任务，可以把沟通成本压低，同时保留完整的冻结与验证边界。
- L confirm reply: 如果你认可这个较轻量但证据完整的流程，请回复：`走 L 级`。
- XL: XL 级适合研究交付、多产物、多技能协作或风险更高的任务：会有更严格的需求冻结、计划冻结、分阶段执行、证据清单和收尾检查。
- XL workflow: 先冻结需求和计划，再把 Agent 组织出的方案拆成分波次执行；只有在依赖安全时才允许小步并行，最后统一回到验证和收尾。
- XL skills: 会先按模块组织更完整的本地 Skills；确需多代理时，由当前 Agent 依据已冻结计划分波次协调，不额外假定一个协调 Skill。
- XL rationale: 适合多产物、多技能协作、研究交付或高风险改动，因为它能先讲清分工、阶段边界和证据清单，再进入执行。
- XL confirm reply: 如果你希望先把分工和波次讲清楚，再进入更重的执行流程，请回复：`走 XL 级`。
- Question: 先确认任务级别：这次任务走 L 级还是 XL 级？
- Selection prompt: 请根据上面的说明选择并确认这次任务级别。

## Assumptions
- Interactive clarification is allowed if unresolved ambiguity materially changes the requested outcome.
