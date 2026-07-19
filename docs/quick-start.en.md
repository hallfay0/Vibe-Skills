# Quick Start

[中文](./quick-start.md)

You do not need to read every document before trying VibeSkills.

Think of it as a way to help an AI complete a complex task from beginning to
end:

> You provide the goal. `vibe` clarifies the task, splits it into parts, finds
> useful Skills for each part, checks the result, and saves the progress.

VibeSkills arranges the work so the AI is less likely to skip steps and a long
task can continue in a later session.

## 1. What it helps with

| Common problem | What VibeSkills does |
|:---|:---|
| There are many Skills and it is unclear which one to use | Splits the task first, then finds useful Skills for each part |
| The AI skips requirements, planning, or tests | Stops at important points and continues after confirmation |
| The user has to keep saying "plan first" or "check it" | Lets the user state the goal while `vibe` arranges the steps |
| A long task loses its progress between sessions | Saves the requirement, plan, important decisions, progress, and result |
| A new Skill is hard to add to the workflow | Finds Skills placed in configured local folders when they fit the task |

The short version:

> **VibeSkills makes the task clear, uses Skills where they help, checks the
> result, and saves enough information to continue later.**

## 2. Start quickly

Open the installation guide:

- [`install/README.en.md`](./install/README.en.md)

The simplest path starts from the published release zip, not a repository
checkout. For a normal update, download the newer zip and run `update` against
the same Skills folder. For a clean reinstall, delete `<SkillsDir>/vibe` and
install the current release.

After installation, start VibeSkills from the Skills entry in your current AI
application. Its host-neutral core works with any application that supports
local Skills; use `$vibe`, `/vibe`, or the invocation syntax provided by that
application.

The installation model is the same in every application:

1. Choose a Skills directory scanned by the application.
2. Install the same package to `<SkillsDir>/vibe`.
3. Invoke `vibe` through the application's Skills entry.

See [Choose A Skills Directory](./cold-start-install-paths.en.md) when the
application uses a different Skills path.

For an update, run the command from the newly extracted release folder:

- `update.ps1 -SkillsDir <skills-dir>`
- `update.sh --skills-dir <skills-dir>`

## 3. How to start it

You only need one entry:

- `vibe`

`vibe` confirms the requirement and plan, stops when it needs your decision,
and continues after confirmation.

Use `update` against the existing Skills folder when upgrading. There is no
separate upgrade Skill to remember.

Stage-specific entries from older versions are retired and should not be
installed or called.

For a more complex task, you can use:

- `--l`
- `--xl`

Older names may still appear in internal records, but they are not commands or
Skills for users to call.

## 4. What to read next

| Goal | Read |
|:---|:---|
| Read the full project introduction | [`../README.md`](../README.md) |
| Install or update | [`install/README.en.md`](./install/README.en.md) |
| See every installation command | [`install/README.en.md`](./install/README.en.md) |
| Find the right Skills folder | [`cold-start-install-paths.en.md`](./cold-start-install-paths.en.md) |
| Use OpenCode | [`cold-start-install-paths.en.md`](./cold-start-install-paths.en.md) |
| Use OpenClaw | [`cold-start-install-paths.en.md`](./cold-start-install-paths.en.md) |
| Install manually or offline | [`install/README.en.md`](./install/README.en.md) |
| Let VibeSkills find more local Skills | [`install/README.en.md`](./install/README.en.md) |
| Add another local Skill folder | [`install/README.en.md`](./install/README.en.md) |
| Read why the project exists | [`manifesto.en.md`](./manifesto.en.md) |

## 5. Common questions

- `$vibe` and `/vibe` start VibeSkills. Tool-specific extensions may still need
  separate setup.
- `check` only checks whether installer-managed files are present and unchanged.
- `session_root` is the record folder for one task. It stores the input,
  progress, important decisions, and summary.
- `delivery-acceptance-report.json` or `.md` stores the final check and shows
  which items passed, failed, or were blocked.
- VibeSkills starts from an AI tool's Skills entry. It is not a separate terminal
  application.

## Recommended reading order

For the shortest path:

1. [`../README.md`](../README.md)
2. [`install/README.en.md`](./install/README.en.md)
3. Try `vibe` on a small task

For example:

> Clarify this requirement and turn it into a plan `$vibe`

You should quickly see the difference from a normal list of Skills: the AI can
continue from the confirmed plan without needing a reminder for every next step.
