# Terminology Governance

> Historical / Retired Note: This document records prior terminology cleanup. The current work-first truth model is `task_card -> work_plan -> work_binding -> work_results -> verification`. `skill_routing.selected` may remain only as an optional compatibility mirror.

Current readers should use:

- `docs/governance/current-routing-contract.md`
- `docs/governance/current-runtime-field-contract.md`
- `docs/governance/historical-routing-terminology.md`

## Current Rule

Use work-first truth names in active docs, runtime output, tests, and
user-visible messages. Compatibility fields may stay visible, but they are not
the primary architecture story.

| Current term | Meaning |
| --- | --- |
| `task_card` | Kernel-owned statement of the job the run is trying to complete. |
| `work_plan` | Kernel-owned bounded plan for that job. |
| `work_binding` | First-class bounded-work truth for what was actually bound. |
| `specialist_decision` | Packet-level explanation for why specialist help was approved, skipped, or unnecessary. |
| `work_results` | Kernel-owned record of what each bound unit produced. |
| `verification` | Kernel-owned closure and proof that declared completion was checked. |
| `skill_candidates` | Compatibility-facing candidate list that may still inform routing reports. |
| `skill_routing.selected` | Optional compatibility mirror of skills already preserved in `work_binding`. |
| `skill_execution_lock` | Execution-obligation view preserved across bounded re-entry; not top-level truth. |
| `selected_skill_execution` | Execution-intent projection shown to users and hosts. |
| `skill_usage.used` | Skills materially used in the run. |
| `skill_usage.unused` | Candidate or selected skills that were not materially used. |
| `skill_usage.evidence` | Evidence tying usage claims to concrete artifacts, files, or receipts. |

## Retired Context

Older terms are retired vocabulary. They can appear in historical records,
compatibility readers, and negative tests, but active docs and reports must not
use them as current architecture names.
