# Current Runtime Field Contract

Date: 2026-06-24

## Purpose

This document defines the current runtime truth vocabulary for Vibe-Skills.

The important boundary is simple:

- the runtime input packet should freeze only the truth the runtime already knows
- later work-loop truth should stay with the kernel-owned work artifacts that prove what actually happened

Do not treat route-era packet summaries as the main explanation of the system.

## Work-First Truth

Current work-first truth is:

```text
runtime input truth: work_binding + specialist_decision
later work-loop truth: task_card -> work_plan -> work_binding -> work_results -> verification
```

Meaning:

- `work_binding` is the first-class bounded-work truth the runtime must preserve at freeze time.
- `specialist_decision` records whether bounded specialist help was approved, declined, or not needed.
- `task_card`, `work_plan`, `work_results`, and `verification` belong to the kernel work loop. They should stay stable and first-class as run artifacts or summary surfaces.
- The runtime input packet does not need to pretend it already owns later execution truth. It only needs to preserve the bounded-work truth required to enter the loop honestly.

## Runtime Input Truth

Required runtime input truth fields:

```text
work_binding
specialist_decision
```

Meaning:

- `work_binding`: kernel-facing bounded-work truth for the selected or deliberately unowned work units.
- `specialist_decision`: the packet-level explanation for why bounded specialist help is present, absent, or still unnecessary.

`work_binding` should be the first packet surface a maintainer checks when asking "what work was actually bound?"

## Work-Run Truth

Preferred stable work-run truth surfaces:

```text
task_card
work_plan
work_binding
work_results
verification
```

Meaning:

- `task_card`: what job the system believes it is doing.
- `work_plan`: how that job was decomposed into bounded work units.
- `work_binding`: which work units were skill-owned, helper-only, or intentionally left without an exact owner.
- `work_results`: what each work unit produced, checked, and proved.
- `verification`: whether the declared completion criteria were actually closed with evidence.

If a human can only understand the run by reading route-era packet summaries, the work-first transition is still incomplete.

## Compatibility Mirrors

Compatibility-only packet fields may remain readable:

```text
skill_routing
route_snapshot
canonical_router
divergence_shadow
```

Meaning:

- `skill_routing`: compatibility mirror of the selected or rejected skill surface for older readers.
- `route_snapshot`: thin packet summary for routed task type and other older control readers.
- `canonical_router`: historical request mirror that may still help older launch surfaces.
- `divergence_shadow`: compatibility shadow that helps older readers compare route-era and kernel-era authority.

These fields may remain readable, but they must not become the only required truth path for bounded work.

## Routing Layer

Allowed current routing compatibility fields:

```text
skill_routing
skill_routing.candidates
skill_routing.selected
skill_routing.rejected
route_snapshot
```

Meaning:

- `skill_routing.selected` can remain as a readable mirror of bounded selection for older readers.
- `route_snapshot` can remain as a thin summary for routed task type and similar control readers.
- `route_snapshot.selected_skill` is no longer part of the default packet. Selected bounded work now lives in `work_binding` first.
- Neither field should be treated as the main owner of bounded-work truth once `work_binding` already exists.

## Execution Layer

Preferred current execution vocabulary:

```text
skill_execution_lock
selected_skill_execution
skill_execution_units
execution_skill_outcomes
```

Execution anchors: `skill_execution_lock`, `selected_skill_execution`,
`skill_execution_units`, and `execution_skill_outcomes`.

### `skill_execution_lock`

`skill_execution_lock` records specialists that crossed the approved-plan boundary and therefore require execution resolution. It is an execution-obligation field, not a material-use field.

`selected_skill_execution` is the execution-side copy of the active execution source. When `skill_execution_lock` is active, execution uses the locked dispatch; otherwise it should derive from `work_binding` first and only fall back to `skill_routing.selected` for older packets. It connects selected skills to real work, but it is not material-use proof by itself.

## Usage Layer

Allowed current usage fields:

```text
skill_usage
skill_usage.used
skill_usage.unused
skill_usage.evidence
```

Meaning:

- `used`: a selected or loaded skill materially shaped an artifact.
- `unused`: a selected or loaded skill did not materially shape an artifact.
- `evidence`: the stage, artifact, and impact proof for material use.
- `skill_usage` is proof-layer accounting. Prefer the session `skill-usage.json`
  sidecar as the durable source, and treat any runtime-packet copy as an
  optional projection for older readers.

Final used claims require `skill_usage.used` plus matching
`skill_usage.evidence`. Routing and selection alone are not use proof.

## Retired Layer

Retired current-routing fields and sections:

```text
legacy_skill_routing
specialist_recommendations
stage_assistant_hints
specialist_dispatch as root routing packet field
approved_dispatch as current execution accounting field
approved_skill_execution
approved_specialist_dispatch_count as current receipt field
## Specialist Consultation
discussion_specialist_consultation
planning_specialist_consultation
approved_consultation
consulted_units
discussion_consultation
planning_consultation
consultation expert
auxiliary expert
```

Older human-role labels are also retired. They may appear only in
retired-behavior tests, historical fixtures, archived historical docs, or
narrow execution-internal allowlists with an explicit scan reason.

## Current Behavior Rule

Current runtime behavior should:

- preserve `work_binding` as the packet-level bounded-work truth
- preserve `specialist_decision` as the packet-level bounded specialist decision truth
- keep `task_card`, `work_plan`, `work_results`, and `verification` as stable kernel-owned work-loop truth
- treat `skill_routing`, `route_snapshot`, `canonical_router`, and `divergence_shadow` as compatibility mirrors instead of main authority
- record material use in `skill_usage.used`, `skill_usage.unused`, and `skill_usage.evidence`

The system is not fully work-first if the packet is still route-shaped and the later work-loop truth is still hidden behind compatibility summaries.
