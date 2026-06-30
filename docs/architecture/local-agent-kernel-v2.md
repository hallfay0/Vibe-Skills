# Local Agent Kernel V2

## Conclusion

The next version should be a small local work kernel, not a router-centered platform.

The public story for this pass is intentionally narrow:

- host-managed external skill folders are the main reference surface
- the built-in starter set is a small fallback
- `work_binding` stays the first runtime truth for what was actually selected

This is a practical next step, not a claim that the final architecture is complete.

## Why This Direction

The old shape asked the router to do too much. It tried to decide intent, choose skills, shape the plan, and act like the control plane. That made normal changes expensive and made extension feel heavier than the work itself.

The new cut is simpler:

- the kernel owns process
- user-owned and host-managed external skills own capability
- discovery only finds candidates
- planning chooses bounded work
- `work_binding` records what was actually bound
- verification decides whether the work is done

The runtime boundary for this pass is also explicit:

- Python owns task semantics, `work_binding`, specialist decision truth, and runtime summary data.
- PowerShell owns launcher wrappers, host receipts, shell-native checks, and leaf execution only.
- A future full-Python runtime is optional. It is not required for this version.

This keeps problems local. If discovery quality is weak, we improve discovery. If plans are weak, we improve planning. If proof is weak, we improve verification.

## Design Rules

- Install into the agent directory and treat that location as the runtime home.
- Prefer convention over configuration.
- Treat host-managed external skill folders and other user-owned skill folders as the main reference surface.
- Keep the starter set small and clearly secondary.
- Keep `work_binding` as the first runtime truth surface.
- Use generated catalog and index files only as derived artifacts.
- Do not require a central skill registry for ordinary skills.
- Do not let an arbitrary directory become active just because it exists.
- Do not let PowerShell own task semantics.
- Do not describe the repo-owned bundled corpus as the main extension story.

## Terminology

### Host-Managed External Skill Root

A skill root declared by the current host adapter. It is read-only from the kernel's point of view and is part of the normal discovery path.

### User-Owned Skill Folder

A skill folder the user or host manages directly. This can live under a host-declared external root or under the installed local root.

### Starter Set

A small built-in fallback set. It is useful for first-run coverage and thin baseline help. It is not the main product story.

For the current package contract, `minimal` keeps exactly two starter helpers: `tdd-guide` and `systematic-debugging`. `full` adds `verification-before-completion` on top of the same small kernel. The repo may still contain many more bundled directories on disk, but they are not counted as the default starter surface unless the packaging inventory says they are live.

### Skill Catalog

A full discovered view of eligible skills. It can show source, precedence, duplicates, and inactive entries. It is for inspection and derived outputs, not for claiming what really ran.

### Active Index

A deduplicated lookup cache projected from the catalog. It is the fast discovery surface, not the runtime truth surface.

### Work Binding

The runtime artifact that says which skill was actually bound to each bounded work unit. This is the first truth surface for selected-skill provenance.

## Runtime Shape

The installed runtime should look like this:

```text
<agent_root>/
  vibe/
    kernel/
      task/
      finder/
      planner/
      executor/
      verifier/
      state/
    skills/
      local/
        <skill-id>/
          SKILL.md
          examples/
          tests/
      starter/
        <skill-id>/
          SKILL.md
    generated/
      skills-catalog.json
      skills-index.json
    runs/
      <run-id>/
        task-card.json
        plan.json
        work-binding.json
        run-state.json
        verification.json
```

Host-managed external skill roots may live outside `<agent_root>`. They are referenced by discovery and catalog artifacts, not copied into a repo-owned central corpus first.

### Meaning Of Each Area

- `kernel/` is the semantic core. It owns process and bounded work.
- `skills/local/` is a normal user-owned surface inside the install root.
- `skills/starter/` is the small built-in fallback set.
- `generated/` contains derived catalog and index artifacts.
- `runs/` contains execution records, including `work_binding`.
- host-managed external roots are the main reference surface when the host declares them.

See [bundled skill retention matrix](../governance/bundled-skill-retention-matrix.md) for the current keep/reference/archive split behind this repo shape.

## Discovery Rules

The system should discover skills by fixed declared roots, not by a layered routing control plane.

### Required Rules

1. Resolve workspace or agent-local user-owned skill roots that belong to the installed runtime.
2. Resolve host-managed external skill roots declared by the current host adapter.
3. Scan the user-owned and host-managed external roots before the starter set.
4. Scan `skills/starter/*/SKILL.md` only as fallback coverage.
5. Read frontmatter from each discovered `SKILL.md`.
6. Validate the frontmatter against the declared contract.
7. Build `generated/skills-catalog.json` as the full discovered view.
8. Project the active entries into `generated/skills-index.json`.
9. Use `work_binding` as the runtime truth for what was actually selected.

### Precedence

The intended precedence for this pass is:

1. workspace or agent-local user-owned skill roots
2. host-managed external skill roots
3. `skills/starter/`

This ordering is about discovery preference, not about claiming the system automatically orchestrates every installed skill.

### Forbidden Rules

- no repo-owned bundled corpus as the main extension surface
- no arbitrary repository path becomes a live route source because it exists
- no central pack manifest for ordinary skill registration
- no alias map as a second source of truth
- no hidden directory scanning outside declared roots
- no separate routing file that re-describes what a skill already says about itself

## Skill Contract

Each skill should stay self-describing. The minimum contract should live in the frontmatter of `SKILL.md`.

Example:

```md
---
id: code-review
name: Code Review
description: Review an implementation for behavior risk, design drift, and missing tests.
when_to_use:
  - The user asks for a review.
  - The result looks correct but may hide regressions.
not_for:
  - Building a feature from scratch.
inputs:
  - task goal
  - changed files
outputs:
  - findings
  - test gaps
  - next recommendation
plan_hints:
  - inspect change surface first
  - test the highest-risk path before summarizing
verify_hints:
  - confirm each finding against code or tests
tags:
  - review
  - testing
  - architecture
enabled: true
priority: 50
---
```

### Required Fields

- `id`
- `name`
- `description`
- `when_to_use`
- `not_for`
- `inputs`
- `outputs`
- `enabled`

### Optional Fields

- `plan_hints`
- `verify_hints`
- `tags`
- `examples`
- `priority`

The source root, source kind, and provenance fields are derived by the kernel from where the skill was discovered. They should not be duplicated as a second manual registration layer.

## Kernel Modules

The kernel should stay small. It only needs six core modules plus a binding artifact.

### Task Module

Turns a user request into a task card.

### Finder Module

Retrieves candidate skills from the active index, with external and user-owned roots ahead of the starter fallback.

### Planner Module

Builds bounded work units from the task card and candidates.

### Executor Module

Runs work units and records artifacts, outputs, and failures.

### Verifier Module

Checks whether the work satisfies the completion criteria.

### State Module

Owns the runtime loop and current status.

### Work Binding Artifact

Records which skill was actually selected for each work unit and where that skill came from.

## Runtime Contracts

The new system should keep the runtime contracts small and inspectable.

### Catalog

`generated/skills-catalog.json`

This file shows the full discovered view, including source information and inactive or shadowed entries.

### Active Index

`generated/skills-index.json`

This file is the fast lookup view projected from the catalog.

### Task Card

`runs/<run-id>/task-card.json`

This records goal, deliverables, constraints, missing information, completion criteria, and mode.

### Plan

`runs/<run-id>/plan.json`

This records bounded work units and the preferred skill choice for each unit.

### Work Binding

`runs/<run-id>/work-binding.json`

This is the first runtime truth for selected skill provenance. It records the final binding, alternatives, expected artifacts, verification needs, and selected-source details.

### Run State

`runs/<run-id>/run-state.json`

This records current progress through the loop.

### Verification

`runs/<run-id>/verification.json`

This records whether the work is done, needs rework, or needs replanning.

## State Machine

The state machine should stay explicit and small.

```text
capture -> clarify -> find_skills -> plan -> execute -> verify -> close
                          ^              |         |
                          |              v         v
                          +--------- replan <- rework
```

### State Meanings

- `capture`: create the first task card from the user request
- `clarify`: fill missing information when the task card is incomplete
- `find_skills`: retrieve candidate skills from declared user-owned and host-managed external roots first, then starter fallback
- `plan`: generate work units
- `execute`: perform the work
- `verify`: compare outputs against completion criteria
- `close`: summarize and persist results

The router disappears as a top-level state because it is no longer the owner of process.

## Language Split

Python should own the kernel because it is better suited for data contracts, planning logic, testing, and semantic modules.

PowerShell should stay only where it has real leverage:

- install
- check
- Windows host wiring
- leaf execution when a specific step truly needs PowerShell

This keeps one semantic core and thin host adapters.

## Small Hot Path

The hot path should stay short:

1. read task
2. resolve eligible skill roots
3. build or load the skill catalog and active index
4. retrieve candidates
5. build plan
6. execute work units
7. verify
8. read `work_binding` when you need the runtime truth

Anything not needed for that path should stay out of it.

The default closure story should stay small too: governed runtime contract, canonical entry truth, runtime execution proof, release truth consistency, and repo cleanliness. Wider packaging or retired-routing audit gates are still useful, but they are not the normal closeout path.

## Large Extension Surface

The extension surface should be wide even while the kernel stays small.

A new ordinary skill should require only:

1. put a skill folder under a declared user-owned root or `skills/local/<skill-id>/`
2. write `SKILL.md`
3. optionally add examples or tests
4. let the catalog and index rebuild

No router surgery and no repo-owned corpus promotion should be needed.

## What To Delete Or Retire

The following ideas should lose authority in v2:

- repo-owned bundled skill growth as the public product story
- router-led plan ownership
- central routing config as the normal way to add ordinary skills
- PowerShell as semantic authority
- duplicated descriptions of the same skill across multiple files

This does not mean every old file must disappear on day one. It means those files must stop being the source of truth.

## Migration Plan

### Phase 1: Freeze Growth In The Old Shape

- stop expanding bundled skills as the main product story
- stop adding new routing rules for ordinary skill admission
- keep the old runtime working, but do not deepen it

### Phase 2: Add External-First Discovery

- resolve host-managed external skill roots
- keep `skills/local/` as a normal user-owned surface
- keep `skills/starter/` as a small fallback
- add `generated/skills-catalog.json`
- add `generated/skills-index.json`

### Phase 3: Build The Kernel Loop

- implement task card creation
- implement finder against the active index
- implement planner that outputs bounded work units
- implement `work_binding` as the runtime truth artifact
- implement verifier against completion criteria

### Phase 4: Demote The Router

- convert router authority into discovery support
- keep legacy PowerShell only as a compatibility adapter
- remove plan ownership from the old route layer

### Phase 5: Keep The Public Story Small

- keep only a small starter set
- move public value toward external or user-owned skill composition
- keep docs focused on how to install, inspect, and extend the kernel without a bigger central catalog

## Non-Negotiable Outcome

The next version succeeds only if a user can install the kernel into an agent directory, make a skill visible through a declared user-owned root, and get useful bounded work without editing a stack of routing files.

If that is not true, the design is still too heavy.
