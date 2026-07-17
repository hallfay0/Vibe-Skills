<div align="right">
  <strong>English</strong> | <a href="./README.zh.md">中文</a>
</div>

<div align="center">

<img src="./logo.png" width="230" alt="VibeSkills logo">

<h1>VibeSkills</h1>

<h3>Make local Skills work as a system.</h3>

<p><strong>Complex tasks often trigger only the most obvious Skills.</strong><br>
VibeSkills maps the whole task first, then organizes relevant local Skills around each module,<br>
so more of the capability you already installed can contribute where it actually helps.</p>

<a href="https://github.com/foryourhealth111-pixel/Vibe-Skills/releases/latest">
  <img src="https://img.shields.io/github/v/release/foryourhealth111-pixel/Vibe-Skills?display_name=tag&sort=semver&style=for-the-badge&color=14515B" alt="Latest release">
</a>
<img src="https://img.shields.io/badge/Public_Entry-vibe-45A1FF?style=for-the-badge" alt="Public entry vibe">
<img src="https://img.shields.io/badge/Skill_Model-Module_Organized-F47D6B?style=for-the-badge" alt="Module-organized Skills">
<img src="https://img.shields.io/badge/Core-Host_Neutral-7C3AED?style=for-the-badge" alt="Host-neutral core">
<img src="https://img.shields.io/badge/Delivery-Evidence_Checked-2E8B57?style=for-the-badge" alt="Evidence-checked delivery">

<br><br>

<a href="./docs/install/README.en.md">
  <img src="./docs/assets/install-cta-en.svg" width="327" height="56" alt="Install VibeSkills">
</a>

<br><br>

<a href="./docs/quick-start.en.md">Quick start</a> ·
<a href="https://github.com/foryourhealth111-pixel/Vibe-Skills/releases/tag/v4.0.0">v4.0.0 release</a> ·
<a href="./docs/README.md">Documentation</a> ·
<a href="https://github.com/foryourhealth111-pixel/Vibe-Skills/stargazers">Star the project</a>

<br><br>

<kbd>Task</kbd> &nbsp;→&nbsp;
<kbd>Decompose</kbd> &nbsp;→&nbsp;
<kbd>Match Skills</kbd> &nbsp;→&nbsp;
<kbd>Execute Modules</kbd> &nbsp;→&nbsp;
<kbd>Verify</kbd> &nbsp;→&nbsp;
<kbd>Resume</kbd>

</div>

---

## The Problem: Passive Skill Triggering Leaves Capability Idle

> [!IMPORTANT]
> A task can contain four meaningful modules while passive triggering brings in
> Skills for only two. The remaining modules are handled generically, even when
> better local Skills are already installed. VibeSkills makes Skill use part of
> the work plan instead of leaving it to prompt wording and chance.

| Passive Skill triggering | VibeSkills |
|:---|:---|
| Reacts to the most obvious words in the request | Builds a work map before execution begins |
| Commonly activates one or two familiar Skills | Evaluates every bounded module for relevant Skill support |
| Leaves the rest of the task to generic improvisation | Binds useful Skills to explicit modules with declared outputs |
| Produces separate tool calls without a shared delivery model | Rejoins module results under one verification and continuation chain |

This is the core job of VibeSkills: **turn a collection of local Skills into an
organized working system**. It does not call every Skill for show. It gives each
meaningful module a deliberate chance to use the right Skill, so useful
capability is less likely to sit idle simply because passive triggering missed
it.

## Decompose First, Then Organize Skills

```mermaid
flowchart TB
    task["One complex task"] --> map["VibeSkills builds the work map"]
    map --> m1["01 · Scope / research"]
    map --> m2["02 · Build / change"]
    map --> m3["03 · Test / review"]
    map --> m4["04 · Document / deliver"]

    pool["Installed local Skill library"] --> match["Read contracts and match relevant Skills"]
    match --> m1
    match --> m2
    match --> m3
    match --> m4

    m1 --> integrate["Integrated module delivery"]
    m2 --> integrate
    m3 --> integrate
    m4 --> integrate
    integrate --> proof["Verification evidence + resumable context"]

    classDef task fill:#0F3D3E,stroke:#0F3D3E,color:#FFFFFF,stroke-width:2px
    classDef map fill:#EDE9FE,stroke:#7C3AED,color:#2E1065,stroke-width:2px
    classDef pool fill:#FFF7ED,stroke:#EA580C,color:#7C2D12,stroke-width:2px
    classDef match fill:#FEF3C7,stroke:#CA8A04,color:#713F12,stroke-width:2px
    classDef blue fill:#E0F2FE,stroke:#0284C7,color:#0C4A6E
    classDef coral fill:#FFE4E6,stroke:#E11D48,color:#881337
    classDef green fill:#DCFCE7,stroke:#16A34A,color:#14532D
    classDef violet fill:#F3E8FF,stroke:#9333EA,color:#581C87
    classDef finish fill:#ECFDF5,stroke:#059669,color:#064E3B,stroke-width:2px

    class task task
    class map map
    class pool pool
    class match match
    class m1 blue
    class m2 coral
    class m3 green
    class m4 violet
    class integrate,proof finish
```

The module map comes first. Skill selection follows that map. If four modules
need four different kinds of help, all four can receive explicit Skill support.
If a module does not need a specialist, it stays Agent-owned. The goal is useful
coverage, not a larger call count.

## What Else VibeSkills Does

- **Confirms the requirement.** Before work begins, VibeSkills confirms the goal,
  constraints, available material, and expected delivery. It does not begin
  execution while the requirement is still waiting for approval.

- **Saves the task record.** The requirement, plan, progress, and final result are
  saved with the run. A later session can continue from those records, and a
  review can trace what was agreed and what was actually done.

- **Recommends a task level.** VibeSkills recommends `L` or `XL` from the task's
  scope, number of steps, dependencies, and opportunities for parallel work. The
  user can also choose. `L` suits multi-step work of manageable size and moves
  through the parts in order, with less overhead. `XL` suits larger work with
  several relatively independent parts; it uses a more detailed breakdown and
  can run up to two non-conflicting work units at the same time, with additional
  coordination and result collection.

- **Checks the final result.** VibeSkills compares every planned item with the
  actual result. If required work is incomplete, failed, or blocked, the task is
  not reported as complete.

- **Plans tests for code work.** When a task involves code, VibeSkills prefers
  test-driven development when appropriate: demonstrate the problem with a
  failing test, make the change, then run the tests again. Test results are saved
  with the rest of the task record.

## Skill Organization, Not Passive Discovery

Installed local Skills are the only specialist reference surface in the public
runtime. A candidate must come from a declared local root and have a readable `SKILL.md` before the Agent can select it.

For composite work, the Agent freezes `agent_skill_organization`; the runtime
projects that decision into `module_assignments`. `module_assignments` is the
runtime truth for the Skill bound to each approved module. Discovery results
remain candidate evidence, not proof that a Skill ran.

Host-declared roots can extend the available local Skills without a new central catalog. This is not a claim that the final architecture is complete; it is the current public boundary for v4.

---

## Evidence You Can Inspect

VibeSkills keeps three public proof layers separate:

| Proof layer | Evidence | What it proves |
|:---|:---|:---|
| `installed locally` | Install receipt plus `check` | The receipt-owned installed files are present and have not drifted. |
| `runtime coherent` | A returned `session_root` with launch, input, governance, lineage, and summary artifacts | A real governed run crossed the runtime boundary coherently. |
| `delivery accepted` | `delivery-acceptance-report.json` or `.md` | The declared work met its delivery criteria. |

These layers are intentionally not interchangeable. A successful install does
not prove task execution, and an execution artifact does not prove acceptance.
A public case should link the complete evidence chain rather than rely on a
screenshot or a success sentence.

For the operator closeout contract, see the
[non-regression proof bundle](docs/status/non-regression-proof-bundle.md).
The normal closeout path should stay small: prove the governed runtime, entry
truth, execution proof, release consistency, and repository cleanliness before
running wider audits.

## Install

Public installation starts from a published release zip. Download the release zip outside the managed `SkillsDir`. The default target is `~/.agents/skills`.

All lifecycle commands now live in one place:

**[Open the install, update, check, uninstall, and migration guide](./docs/install/README.en.md)**

Current asset:
[vibe-skills-4.0.0-public.zip](https://github.com/foryourhealth111-pixel/Vibe-Skills/releases/download/v4.0.0/vibe-skills-4.0.0-public.zip)

## Portable Core, Adapter-Based Hosts

VibeSkills is not tied to Codex, Claude Code, Cursor, or any other single host.
The runtime contract and public release bundle are host-neutral. A carrier can
integrate VibeSkills when it can expose declared Skill roots, invoke the
canonical `vibe` entry, preserve bounded stops, and return the required runtime
artifacts.

| Portable surface | Honest boundary |
|:---|:---|
| Ordinary local Skill | Any Skill can participate when it lives in a declared root, has a readable and valid `SKILL.md`, has an unambiguous ID, and matches a module's work. |
| Host or carrier | A new host can integrate through an adapter or compatible canonical bridge; the core does not depend on one vendor's UI or command syntax. |
| Support claim | Host-neutral design does not mean every host is already verified as plug-and-play. Each adapter keeps its own measured support status. |

<details>
<summary><strong>Current adapter evidence</strong></summary>

The repository currently carries explicit adapters for Codex, Claude Code,
Cursor, Windsurf, OpenClaw, and OpenCode. Codex and Claude Code are marked
`supported-with-constraints`; the other named adapters are preview paths. The
generic host contract is `advisory-only`, so a new carrier can consume the
contract without being presented as fully verified.

See the [host capability matrix](./docs/universalization/host-capability-matrix.md)
for the exact support vocabulary.

</details>

Invocation syntax belongs to the host. `$vibe`, `/vibe`, and other Skills entry
forms are adapter examples, not product boundaries.

## Public Boundaries

- The public runtime entry is `vibe`.
- The release installs Vibe-owned files under `<SkillsDir>/vibe`; it does not
  install a separate built-in Skill catalog.
- Additional Skills come from the shared Skills directory or configured local
  roots in `~/.vibeskills/skill-roots.json` and
  `<workspace>/.vibeskills/skill-roots.json`.
- The installer does not rewrite host settings, system prompts, or command
  wrappers, and it does not automatically provision MCP servers.
- The current Agent performs the approved work. Runtime artifacts record what
  was assigned, returned, verified, failed, or blocked.
- Git, source documents, requirement files, plans, and verification receipts
  remain the source of record; workspace memory helps continuation but does not
  replace them.

<details>
<summary><strong>Current runtime ownership</strong></summary>

Python owns canonical validation, task semantics, `module_assignments`, and the
truth chain from `agent_skill_organization` through `module-work-plan.json`,
`agent-execution-handoff.json`, and `module-execution.json`.

PowerShell performs stage orchestration, environment setup, script bridging,
host receipts, and shell-native checks. The current Agent performs the approved module work.

Do not add new task semantics or task execution to PowerShell; existing PowerShell stage scripts are transitional orchestration surfaces. A future full-Python runtime is optional, not required for this release.

</details>

## Documentation

| Need | Start here |
|:---|:---|
| Install, update, uninstall | [Simple install](./docs/install/README.en.md) |
| First governed run | [Quick start](./docs/quick-start.en.md) |
| Current release | [v4.0.0 notes](./docs/releases/v4.0.0.md) |
| Runtime and design contracts | [Documentation index](./docs/README.md) |
| Troubleshooting | [Troubleshooting guide](./docs/troubleshooting.md) |
| Contributing | [Contribution guide](./CONTRIBUTING.md) |

## Community And Credits

Questions, corrections, and well-scoped contributions are welcome through
[GitHub Issues](https://github.com/foryourhealth111-pixel/Vibe-Skills/issues)
and pull requests. The project reuses and adapts ideas from open-source work
including Superpowers, Get Shit Done, OpenSpec, spec-kit, mem0, Scrapling, and
Serena; attribution details live in [NOTICE](./NOTICE) and
[third-party licenses](./THIRD_PARTY_LICENSES.md).

Community contributors include
[xiaozhongyaonvli](https://github.com/xiaozhongyaonvli) and
[ruirui2345](https://github.com/ruirui2345).

## Star History

<p align="center">
  <a href="https://www.star-history.com/?repos=foryourhealth111-pixel%2FVibe-Skills&type=date&legend=top-left">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/image?repos=foryourhealth111-pixel/Vibe-Skills&type=date&theme=dark&legend=top-left">
      <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/image?repos=foryourhealth111-pixel/Vibe-Skills&type=date&legend=top-left">
      <img alt="VibeSkills star history" src="https://api.star-history.com/image?repos=foryourhealth111-pixel/Vibe-Skills&type=date&legend=top-left">
    </picture>
  </a>
</p>
