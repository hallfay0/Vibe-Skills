# Specialist Dispatch Governance

> Historical / Retired Note: This document records a retired execution-wording design. The current work-first truth model is `task_card -> work_plan -> work_binding -> work_results -> verification`. `skill_routing.selected` may remain visible only as an optional compatibility mirror.

Current readers should use:

- `docs/governance/current-routing-contract.md`
- `docs/governance/current-runtime-field-contract.md`
- `docs/governance/historical-routing-terminology.md`

## Preserved Decision

The durable decision from this document is that execution must be tied to the
skill selected for the task slice and must not be treated as hidden advisory
activity.

Current execution language may still use `skill_execution_lock`,
`selected_skill_execution`, `skill_execution_units`, and
`execution_skill_outcomes`, but current truth starts from `work_binding` and
`specialist_decision`.

## Retired Context

Older wording used `specialist dispatch`, `approved_dispatch`, and related
phrases. Those names remain historical audit vocabulary only and must not be
used as current routing truth.
