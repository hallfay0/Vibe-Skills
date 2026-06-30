# Current Routing Compatibility Contract

Date: 2026-06-24

## Purpose

This is not the start-here explanation of the system.

Read [`current-runtime-field-contract.md`](current-runtime-field-contract.md)
first when you want to understand what the runtime really treats as truth.

For a normal run, you usually stop there and read the work artifacts.
You usually do not need this file unless a compatibility reader still exposes
route-era mirrors beside the work-first kernel.

Use this document only for a narrower question:

when route-era compatibility fields are still visible, how do they connect
bounded skill selection to execution and later usage accounting?

## Position In The System

Main system truth lives here:

```text
runtime input truth: work_binding + specialist_decision
later work-loop truth: task_card -> work_plan -> work_binding -> work_results -> verification
```

This document explains only the compatibility and execution follow-on surfaces
that may still appear beside that work truth.

Default reading stop for most runs:

```text
task_card -> work_plan -> work_binding -> work_results -> verification
```

Only continue into this file when a host receipt, older proof reader, or
compatibility gate still needs to interpret route-era mirrors.

## Compatibility Follow-On Chain

Current readable compatibility and execution chain:

```text
skill_candidates -> skill_routing.selected -> skill_execution_lock -> selected_skill_execution -> skill_usage.used / skill_usage.unused
```

This is not a workflow to follow.
It is a surviving reader chain that starts only after bounded work truth
already exists.

This chain may remain visible for older hosts, receipts, and proof readers.
It is not the main explanation of the work kernel.

`work_binding` stays the bounded-work truth.
`skill_routing.selected` is a readable compatibility mirror.
`selected_skill_execution` is an execution-side copy, not material-use proof.

## Operating Rules

1. When `work_binding` exists, read it before any routing mirror.
2. Routing may list possible skills in `skill_candidates`.
3. If a selected skill remains visible in `skill_routing.selected`, it should mirror bounded work already preserved by `work_binding`.
4. Plan approval may preserve selected skills across bounded re-entry through `skill_execution_lock`.
5. Execution may only treat selected or locked skills as work inputs through `selected_skill_execution`.
6. Completion may only claim a skill was used through `skill_usage.used` with matching `skill_usage.evidence`.

For compound tasks, split the work into bounded task segments and bind the
directly relevant skill for each segment. Multiple selected skills are valid
when the task has multiple bounded segments; they do not create ranks or extra
states.

## Terms

| Term | Meaning |
| --- | --- |
| `work_binding` | The first-class bounded-work truth. Read this before routing mirrors. |
| `candidate` | A skill was considered by routing. This is not a use claim. |
| `selected` | A skill remains visible through `skill_routing.selected` as a compatibility mirror of bounded selection. This is not a use claim. |
| `skill_execution_lock` | The approved-plan execution lock that preserves selected specialists across bounded re-entry. It is not a use claim. |
| `selected_skill_execution` | The selected skill list frozen into execution. This connects bounded selection to actual work, but it is still not a use claim. |
| `used` | A selected or loaded skill shaped an artifact and appears in `skill_usage.used` with evidence. |
| `unused` | A selected or loaded skill did not shape an artifact and appears in `skill_usage.unused`. |
| `evidence` | A stage, artifact reference, and impact summary proving material skill use. |
| `retired old-format fields` | Old routing, consultation, and dispatch fields are not current inputs, current outputs, or maintained compatibility targets. |

`skill_execution_lock` exists because bounded re-entry may rerun compatibility
selection logic. Once a plan is approved, selected specialists become execution
obligations and must be executed, marked not applicable, deferred, or failed
before delivery acceptance can pass. The lock does not prove material skill
use; `skill_usage.used` remains the only material-use truth.

## Usage Proof

A skill may be reported as used only when all of these are true:

1. The skill appears in `skill_usage.used`.
2. The skill has at least one `skill_usage.evidence` record.
3. The evidence names a concrete stage and artifact impact.

Routing, selection, execution locks, old consultation receipts, and old dispatch
records are not usage proof.

## Current Output Rules

Current runtime outputs may keep these names as compatibility or execution
surfaces when needed:

```text
work_binding
skill_candidates
skill_routing.selected
skill_execution_lock
selected_skill_execution
skill_usage.used
skill_usage.unused
skill_usage.evidence
```

Main run explanation should still start with work artifacts and work truth,
not this compatibility chain.

## Retired Old-Format Fields

The following old fields are retired. Current runtime code must not use them to
infer selected skills, material skill use, or current execution ownership:

```text
legacy_skill_routing
specialist_recommendations
specialist_dispatch
stage_assistant_hints
discussion_specialist_consultation
planning_specialist_consultation
approved_consultation
consulted_units
discussion_consultation
planning_consultation
```

When current and retired fields are both present in an old artifact, current
runtime code should prefer `work_binding`, `skill_execution_lock`, and
`skill_usage`, and treat routing mirrors as compatibility-only readers.

## Non-Goals

This contract does not delete old artifacts.
It only explains how remaining routing compatibility fields should be read
without taking back authority from the work-first kernel.
If a normal run cannot be understood without this file, the work-first
transition is regressing.
