# 重点证明：VibeSkills 能把一个复杂任务拆成模块，并组织用户本地已经安装的不同 Skills 分别完成合适的工作，最后汇总并验收。 主案例优先考虑“机器...

## Execution Summary
Governed runtime execution plan for `vibe` in mode interactive_governed.

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

## Task Modules
- `environment_setup`: Create the isolated Python 3.12 environment and reproduction command.
- `data_audit`: Materialize and audit the built-in Wisconsin Breast Cancer dataset before modeling.
- `baseline_experiment`: Run the frozen DummyClassifier comparator and scaled LogisticRegression baseline.
- `statistical_method_review`: Quantify uncertainty and verify that methods and claims are justified.
- `result_figures`: Create accessible, source-mapped result figures from saved experiment outputs.
- `report_draft`: Draft the scientific report strictly from approved evidence and figure mappings.
- `report_review`: Apply the full scientific-writing review without altering scientific content.
- `group_meeting_slides`: Create and fully render-check a seven-slide group-meeting PowerPoint deck.
- `case_package_and_consistency`: Prepare bilingual README case material and reconcile every number and claim across all outputs without editing README files.

## Candidate Skills By Module
- `environment_setup`: `scikit-learn`
- `data_audit`: `exploratory-data-analysis`, `statistical-analysis`, `scientific-critical-thinking`
- `baseline_experiment`: `scikit-learn`, `statistical-analysis`
- `statistical_method_review`: `statistical-analysis`, `scientific-critical-thinking`, `scikit-learn`
- `result_figures`: `scientific-visualization`, `matplotlib`
- `report_draft`: `sciwrite`
- `report_review`: `sciwrite`
- `group_meeting_slides`: `presentations`
- `case_package_and_consistency`: `sciwrite`, `scientific-critical-thinking`

## Uncovered Modules
- No module is blocked by a Skill gap; `environment_setup`, `report_draft`, `case_package_and_consistency` is explicitly assigned to the current Agent without a local Skill.

## L / XL Organization Difference
- L: Run the nine modules serially in dependency order; the scientific-critical-thinking verifier runs after the statistical-analysis owner, and no module starts before its dependencies pass.
- XL: If later revised to XL, preserve these owners and outputs and parallelize only dependency-ready, non-conflicting work; report, slides, case packaging, and consistency remain serial. XL is not selected.
- Selected workflow level: `L`

## Frozen Inputs
- Requirement doc: <case-root>\docs\requirements\2026-07-18-vibeskills-skills-baseline-slides-skills-vibeskills-skills-skill.md
- Source task: 重点证明：VibeSkills 能把一个复杂任务拆成模块，并组织用户本地已经安装的不同 Skills 分别完成合适的工作，最后汇总并验收。

主案例优先考虑“机器学习实验完整交付”：baseline、统计检查、结果图、科学报告、组会 Slides。它应产生视觉上可展示的真实结果。

这些只是候选方向。若本机材料或 Skills 不足以真实完成，必须基于可验证条件调整案例，不得伪造。使用实际安装的 VibeSkills 运行时和实际本地 Skills，不要手工模拟 Skill 编排。每个案例使用全新的 run ID；不得复用同一个 ID 作为新任务和 continuation 来源。遵守 requirement_doc、xl_plan 等用户批准停点，停点出现时等待我在新任务中确认，不得同轮越过。

把实验文件和证据放在 <case-workspace>\<case-id> 下，保持仓库提交面不变。每个案例最终至少要有：真实用户任务、实际模块拆分、实际选中的本地 Skills 及职责、真实产物、module execution 状态、最终 acceptance 结果，以及可用于 README 的简短中英文摘要和视觉素材建议。

禁止使用 Codex 浏览器插件、Chrome、Playwright 或任何浏览器自动化。不要编造指标、截图、终端输出、成功状态或公共链接。没有完整证据就明确标为未完成，不得包装成案例。 Revision delta: Freeze the workflow level as L: use one governed serial main line, while still assigning different modules to the local Skills that actually own them.; Use the scikit-learn built-in Wisconsin Breast Cancer dataset without external downloads. Treat it only as a public, reproducible, non-clinical demonstration and do not make clinical-use claims.; Create an isolated case-local Python 3.12 virtual environment and record pinned dependency versions. Do not silently use the default Python 3.10 environment for the scikit-learn module because the installed scikit-learn Skill declares Python 3.11 or newer.; Build a reproducible classification experiment with a DummyClassifier sanity comparator and a StandardScaler plus LogisticRegression primary baseline. Use fixed random seeds, a stratified holdout split, and repeated stratified cross-validation. Do not add hyperparameter search unless a later approved plan justifies it.; Audit dataset shape, target balance, missingness, duplicate rows, split integrity, and leakage risk. Report at least ROC AUC, balanced accuracy, F1, confusion-matrix results, cross-validation variability, and justified uncertainty intervals. Use formal significance tests only when the statistical Skill confirms that the design supports them.; Write all task-owned deliverables under <case-root>\deliverables. Include environment and reproduction instructions, executable experiment code, machine-readable metrics and fold-level results, data and method audit, at least three clear result figures, a concise scientific Markdown report, a group-meeting PPTX, rendered slide previews, short English and Chinese README summaries, and visual-material recommendations.; Every metric and conclusion in figures, the report, the slide deck, and the README summaries must trace to the same machine-readable experiment results. Clearly disclose limitations, the demonstration-only scope, and any failed or blocked checks.; Render and inspect the slide deck and inspect the result figures without using the Codex browser plugin, Chrome, Playwright, or browser automation. Do not modify Vibe-Skills-main README files or existing docs/assets images.; Completion requires real module-execution evidence, reproducibility verification, cross-deliverable consistency checks, phase cleanup, and a passing final delivery acceptance report. If any required evidence or artifact is missing, keep the case explicitly incomplete and do not present it as a README success case.. Update: 总控补充：保持本轮目标严格为生成可审计的 L 级计划并停在 xl_plan。完整阅读正式保留候选的 SKILL.md 即可；不要在计划阶段制作 Slides、预览图或其他交付物，也不要继续扩展候选集合。计划满足需求、分工、依赖、写入范围和验收合同后立即完成本轮停点。 Update: 总控已审计冻结的执行计划、module-work-plan.json 和 runtime-summary.json，批准案例一计划并允许通过受控 re-entry 执行。请只从 Run ID 20260718T033536Z-7149f0c2 使用当前 token 继续，严格执行冻结的 9 个模块与 10 个串行波次，然后走 canonical phase_cleanup 和最终 delivery acceptance；禁止在 VibeSkills 之外手工伪造执行状态。执行保护：statistical-analysis owner 负责 deliverables/03-statistical-review/statistics/**；scientific-critical-thinking verifier 只新增或更新 deliverables/03-statistical-review/method-review/**，不得覆盖 owner 的 uncertainty.json 或 statistical-review.md。每个自动和人工验收项都必须留下真实证据；任何必需模块、渲染检查、复现检查、跨产物一致性检查或 cleanup/acceptance 失败，就保持案例未完成并清楚记录原因。不要修改 README、现有 docs/assets、分支或提交。持续更新 <case-workspace>\thread_state.md，执行结束或遇到真实阻塞时返回完整状态。

## Wave Plan
- Wave 1 (`sequential`): `environment_setup` via current Agent as `owner`
- Wave 2 (`sequential`): `data_audit` via skill `exploratory-data-analysis` as `owner`
- Wave 3 (`sequential`): `baseline_experiment` via skill `scikit-learn` as `owner`
- Wave 4 (`sequential`): `statistical_method_review` via skill `statistical-analysis` as `owner`
- Wave 5 (`sequential`): `statistical_method_review` via skill `scientific-critical-thinking` as `verifier`
- Wave 6 (`sequential`): `result_figures` via skill `scientific-visualization` as `owner`
- Wave 7 (`sequential`): `report_draft` via current Agent as `owner`
- Wave 8 (`sequential`): `report_review` via skill `sciwrite` as `owner`
- Wave 9 (`sequential`): `group_meeting_slides` via skill `presentations` as `owner`
- Wave 10 (`sequential`): `case_package_and_consistency` via current Agent as `owner`

## Delivery Acceptance Plan
- Freeze downstream product acceptance inside the governed requirement doc and reuse it rather than inventing closeout claims later.
- Emit a per-run delivery-acceptance report during `phase_cleanup` so runtime/process success is kept separate from project-delivery success.
- Delivery-acceptance report: <case-root>\outputs\runtime\vibe-sessions\20260718T041559Z-51996499\delivery-acceptance-report.json
- If manual spot checks are declared in the requirement doc, final completion wording stays blocked until they are cleared or explicitly downgraded to manual review.
- Release truth aggregation remains an outer-layer gate; this run emits the per-run delivery-truth report only.

## Module Work Plan
- `environment_setup`: Create the isolated Python 3.12 environment and reproduction command.
  Required: `True`; dependencies: none; Execution mode: `agent_direct`
  Work: current Agent as `owner` - Create the isolated Python 3.12 environment and reproduction command.
  Acceptance: `environment-contract` (automated) - The case-local Python 3.12 environment imports every required pinned dependency.
  Acceptance: `reproduction-entry` (automated) - One recorded command starts the frozen experiment through that environment.
- `data_audit`: Materialize and audit the built-in Wisconsin Breast Cancer dataset before modeling.
  Required: `True`; dependencies: `environment_setup`; Execution mode: `skill_assigned`
  Work: skill `exploratory-data-analysis` as `owner` - Own dataset materialization and the structure, quality, distribution, and leakage-risk audit.
  Acceptance: `data-snapshot` (automated) - The table and metadata agree with the scikit-learn loader output.
  Acceptance: `data-audit-coverage` (manual) - The audit reports every frozen quality check and separates facts from recommendations.
- `baseline_experiment`: Run the frozen DummyClassifier comparator and scaled LogisticRegression baseline.
  Required: `True`; dependencies: `data_audit`; Execution mode: `skill_assigned`
  Work: skill `scikit-learn` as `owner` - Own the leakage-safe pipeline, frozen models, stratified evaluation, metrics, predictions, and replay.
  Acceptance: `baseline-design` (automated) - The models, pipeline, split, cross-validation, and no-search boundary match the frozen requirement.
  Acceptance: `baseline-results` (automated) - Holdout and fold outputs contain ROC AUC, balanced accuracy, F1, confusion counts, sample counts, and model identities and reproduce under the pinned environment.
- `statistical_method_review`: Quantify uncertainty and verify that methods and claims are justified.
  Required: `True`; dependencies: `baseline_experiment`; Execution mode: `skill_assigned`
  Work: skill `statistical-analysis` as `owner` - Own uncertainty selection, variability summaries, assumption disclosure, and restrained statistical reporting.
  Work: skill `scientific-critical-thinking` as `verifier` - After the statistics owner, verify design validity, bias, leakage, overclaiming, generalization, and non-clinical boundaries.
  Acceptance: `uncertainty-contract` (automated) - Variability and uncertainty intervals state their method, units, assumptions, and source data.
  Acceptance: `claim-boundary` (manual) - The review records limitations and permits only conclusions supported by this demonstration design.
- `result_figures`: Create accessible, source-mapped result figures from saved experiment outputs.
  Required: `True`; dependencies: `statistical_method_review`; Execution mode: `skill_assigned`
  Work: skill `scientific-visualization` as `owner` - Own the accessible, publication-quality, source-mapped PNG and SVG figure set.
  Acceptance: `figure-traceability` (automated) - Four PNG figures and matching vector exports map every plotted value to saved evidence.
  Acceptance: `figure-visual-qa` (manual) - Full-size inspection finds no unreadable, clipped, overlapping, inaccessible, or misleading elements.
- `report_draft`: Draft the scientific report strictly from approved evidence and figure mappings.
  Required: `True`; dependencies: `result_figures`; Execution mode: `agent_direct`
  Work: current Agent as `owner` - Draft the scientific report strictly from approved evidence and figure mappings.
  Acceptance: `report-draft-content` (manual) - The draft covers purpose, data, methods, results, limitations, reproducibility, and conclusion.
  Acceptance: `report-source-map` (automated) - Every result number and figure reference has a machine-readable source mapping.
- `report_review`: Apply the full scientific-writing review without altering scientific content.
  Required: `True`; dependencies: `report_draft`; Execution mode: `skill_assigned`
  Work: skill `sciwrite` as `owner` - Run the five-pass writing review and produce the clear final report without changing scientific content.
  Acceptance: `writing-five-passes` (automated) - The review records all five required passes and concrete revisions.
  Acceptance: `writing-content-boundary` (manual) - The final report is clearer but preserves the approved data, methods, model identities, and claims.
- `group_meeting_slides`: Create and fully render-check a seven-slide group-meeting PowerPoint deck.
  Required: `True`; dependencies: `report_review`, `result_figures`; Execution mode: `skill_assigned`
  Work: skill `presentations` as `owner` - Own the artifact-tool PPTX, seven-slide narrative, rendering, overflow checks, visual QA, and source map.
  Acceptance: `slides-render` (automated) - The seven-slide PPTX opens and every slide renders to a nonblank PNG.
  Acceptance: `slides-content-qa` (manual) - No overflow, clipping, overlap, placeholder, narrative break, or chart-data mismatch remains.
- `case_package_and_consistency`: Prepare bilingual README case material and reconcile every number and claim across all outputs without editing README files.
  Required: `True`; dependencies: `baseline_experiment`, `statistical_method_review`, `result_figures`, `report_review`, `group_meeting_slides`; Execution mode: `agent_direct`
  Work: current Agent as `owner` - Prepare bilingual README case material and reconcile every number and claim across all outputs without editing README files.
  Acceptance: `case-package-truth` (manual) - The aligned English and Chinese summaries and visual guidance use only verified artifacts and make no success claim before canonical acceptance.
  Acceptance: `cross-artifact-consistency` (automated) - All numbers, model names, sample counts, settings, limitations, figure labels, and paths reconcile; missing or contradictory evidence fails the check.
- Dispatch exploratory-data-analysis as owner.
  Binding profile: module_work_unit; dispatch phase: in_execution; lane policy: module_dependency_contract; parallel in XL: False
  Write scope: deliverables/01-data-audit/**; review mode: module_acceptance; execution priority: 50
  Reason: approved_module_work_plan
  Required inputs:
  Expected outputs: deliverables/01-data-audit/wisconsin-breast-cancer.csv, deliverables/01-data-audit/dataset-metadata.json, deliverables/01-data-audit/target-distribution.csv, deliverables/01-data-audit/data-audit.md
  Verification: Compare the snapshot with the loader and check shape, labels, missingness, duplicates, balance, types, and leakage risk.
- Dispatch scikit-learn as owner.
  Binding profile: module_work_unit; dispatch phase: in_execution; lane policy: module_dependency_contract; parallel in XL: False
  Write scope: deliverables/02-baseline/**; review mode: module_acceptance; execution priority: 50
  Reason: approved_module_work_plan
  Required inputs:
  Expected outputs: deliverables/02-baseline/run_experiment.py, deliverables/02-baseline/experiment-config.json, deliverables/02-baseline/metrics.json, deliverables/02-baseline/fold-metrics.csv, deliverables/02-baseline/holdout-predictions.csv, deliverables/02-baseline/reproduction-check.json
  Verification: Verify the in-pipeline scaler, fixed seeds, stratified holdout, repeated stratified CV, required metrics, and a clean replay.
- Dispatch statistical-analysis as owner.
  Binding profile: module_work_unit; dispatch phase: in_execution; lane policy: module_dependency_contract; parallel in XL: False
  Write scope: deliverables/03-statistical-review/**; review mode: module_acceptance; execution priority: 50
  Reason: approved_module_work_plan
  Required inputs:
  Expected outputs: deliverables/03-statistical-review/statistics/uncertainty.json, deliverables/03-statistical-review/statistics/statistical-review.md, deliverables/03-statistical-review/method-review/method-and-claims-review.md
  Verification: Recalculate uncertainty, disclose assumptions, avoid unjustified significance tests, then review leakage, bias, overclaiming, generalization, and non-clinical limits.
- Dispatch scientific-critical-thinking as verifier.
  Binding profile: module_work_unit; dispatch phase: in_execution; lane policy: module_dependency_contract; parallel in XL: False
  Write scope: deliverables/03-statistical-review/**; review mode: independent_verification; execution priority: 50
  Reason: approved_module_work_plan
  Required inputs:
  Expected outputs: deliverables/03-statistical-review/statistics/uncertainty.json, deliverables/03-statistical-review/statistics/statistical-review.md, deliverables/03-statistical-review/method-review/method-and-claims-review.md
  Verification: Recalculate uncertainty, disclose assumptions, avoid unjustified significance tests, then review leakage, bias, overclaiming, generalization, and non-clinical limits.
- Dispatch scientific-visualization as owner.
  Binding profile: module_work_unit; dispatch phase: in_execution; lane policy: module_dependency_contract; parallel in XL: False
  Write scope: deliverables/04-figures/**; review mode: module_acceptance; execution priority: 50
  Reason: approved_module_work_plan
  Required inputs:
  Expected outputs: deliverables/04-figures/class-balance.png, deliverables/04-figures/roc-and-pr-curves.png, deliverables/04-figures/cv-performance-distribution.png, deliverables/04-figures/confusion-matrix.png, deliverables/04-figures/vector/*.svg, deliverables/04-figures/figure-index.json
  Verification: Check source mappings and inspect each full-size PNG for readable labels, accessible colors, defined uncertainty, honest scales, clipping, and overlap.
- Dispatch sciwrite as owner.
  Binding profile: module_work_unit; dispatch phase: in_execution; lane policy: module_dependency_contract; parallel in XL: False
  Write scope: deliverables/05-report/final/**; review mode: module_acceptance; execution priority: 50
  Reason: approved_module_work_plan
  Required inputs:
  Expected outputs: deliverables/05-report/final/scientific-report.md, deliverables/05-report/final/writing-review.md
  Verification: Run all five review passes and recheck terminology, sample counts, metrics, intervals, significant figures, and figure references.
- Dispatch presentations as owner.
  Binding profile: module_work_unit; dispatch phase: in_execution; lane policy: module_dependency_contract; parallel in XL: False
  Write scope: deliverables/06-slides/**; review mode: module_acceptance; execution priority: 50
  Reason: approved_module_work_plan
  Required inputs:
  Expected outputs: deliverables/06-slides/group-meeting-slides.pptx, deliverables/06-slides/rendered/slide-*.png, deliverables/06-slides/slides-montage.png, deliverables/06-slides/slides-qa.txt, deliverables/06-slides/slide-source-map.json
  Verification: Use the local artifact-tool route, run overflow checks, render every slide, inspect each full size, and reconcile every displayed result with its source.

## Verification Commands
- Run every verification command frozen for the module work units and retain its real result.
- Reconcile every module acceptance criterion against the returned execution evidence.
- Review the delivery-acceptance report emitted during `phase_cleanup` before using full completion language.

## Rollback Plan
- If verification fails, revert only changes inside the approved module write scopes.
- Do not roll back unrelated user changes.

## Phase Cleanup Contract
- Remove temporary artifacts created by the approved module work only.
- Write cleanup receipt before completion.
