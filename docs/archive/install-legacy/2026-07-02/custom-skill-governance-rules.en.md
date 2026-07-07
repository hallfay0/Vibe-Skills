# Custom Skill / Workflow Governance Rules (Advanced Path)

Goal: allow extension without losing control. You may add custom capabilities, but they must not break the canonical runtime or override the kernel-owned bounded-work truth.

This page is for the advanced governed path only. It is not the normal path for ordinary skills.

For ordinary skills, the normal extension path is still a local skill under `<TARGET_ROOT>/skills/local/<skill-id>/SKILL.md`.

If a plain local skill is enough, stop there. Only continue when you truly need a manifest-driven custom workflow or another advanced admitted custom surface.

In other words:

- ordinary skill: use `skills/local/<skill-id>/SKILL.md`
- manifest-driven custom workflow: advanced lane only

Do not send normal skill authors to the manifest-driven path by default.

If you do need this advanced path, prefer `full`. The framework profile `minimal` can still host it, but you must verify that the required dependencies are actually present.

## Hard Rules That Must Not Be Broken

1. There is only one runtime: `vibe`
2. There is only one canonical runtime controller: the `vibe` work kernel
3. Custom content can join routing only after a manifest declaration
4. A directory must not become active just because it exists
5. An external repository must not become a live route source directly

## Governed Directory Conventions

- normal local skill path: `<TARGET_ROOT>/skills/local/<skill-id>/SKILL.md`
- content directory: `<TARGET_ROOT>/skills/custom/<name>/`
- workflow manifest: `<TARGET_ROOT>/config/custom-workflows.json`
- custom-skill manifest, if enabled: `<TARGET_ROOT>/config/custom-skills.json`

## Choose The Right Path First

Use the smallest path that matches the real need.

### Normal Path For Ordinary Skills

Use this path when you are adding one ordinary skill that should be discovered like other user-owned skills:

- create `<TARGET_ROOT>/skills/local/<skill-id>/SKILL.md`
- keep the capability self-described in `SKILL.md`
- let the normal skill discovery flow pick it up

This is the default path for normal extension work.

### Advanced Lane For Manifest-Driven Custom Workflows

Use the advanced lane only when a plain local skill is not enough, for example when you need:

- a separately admitted workflow surface
- trigger governance beyond the normal skill contract
- explicit dependency declarations for a custom admitted flow
- long-lived custom workflow manifests that must survive overwrite-style updates

If those needs are not real, do not introduce `custom-workflows.json` or `custom-skills.json`.

## Update Governance Rules

### Custom Surfaces Users May Keep Long Term

The following paths should be treated as user-owned custom-governance surfaces and should be preserved first during updates:

- `skills/custom/`
- `config/custom-workflows.json`
- `config/custom-skills.json` (if enabled)

### Official Managed Surfaces That Should Not Be Edited Directly

The following paths are official managed surfaces and may be rewritten during overwrite-style updates:

- `skills/vibe/`
- official skill directories such as `skills/<official-skill>/`
- official `rules/`
- official `agents/templates/`

Rules:

- extend through user custom paths
- do not expect direct edits to official managed directories to survive overwrite updates automatically

### Profile-Change Governance

When the installed version changes together with the profile, you must re-check the custom workflow `requires` fields.

Especially:

- downgrading from `full` to framework-only (`minimal`)
- moving from a richer custom-workflow setup back to framework-only (`minimal`)

These changes most often cause:

- `custom_dependencies_missing`
- what looks like routing failure but is actually a dependency break

### Required Validation After Updates

1. rerun `check --deep`
2. verify that the manifest is still valid
3. verify that the custom workflow path and `SKILL.md` still exist
4. verify that `requires` is still satisfied

If validation fails, inspect in this order:

1. whether `config/custom-workflows.json` still exists
2. whether `skills/custom/<id>/SKILL.md` still exists
3. whether the required skills still exist in the current install profile
4. whether custom changes were mistakenly written into official managed directories

## Routing And Trigger Governance

This section applies to the advanced lane only. Ordinary skills under `skills/local/<skill-id>/SKILL.md` should not need these manifest trigger controls.

Advanced admission may shape discovery and eligibility, but it must not replace the kernel-owned work loop or `work_binding` as the final record of what was actually selected.

- default `trigger_mode`: `advisory`
- use `explicit_only` for high-risk or low-frequency flows
- use `auto` only when evidence is strong enough

Every admitted custom workflow must provide:

- `keywords`
- `intent_tags`
- `non_goals`
- `requires`

If those fields are missing, the workflow must not enter a callable state.

## Dependency Governance

Advanced-lane custom workflows must not assume that baseline capabilities are always present.
Declare dependencies explicitly through `requires`, for example:

- `vibe`
- `writing-plans`
- `systematic-debugging`

If dependencies are missing, doctor/check should report `custom_dependencies_missing` instead of silently degrading.

Ordinary skills should still prefer the normal local-skill path instead of being turned into manifest-managed workflows just to express simple capability metadata.

## Readiness Wording Governance

Keep these states clearly separated:

- `lane_complete`
- `lane_complete_with_optional_gaps`
- `core_install_incomplete`
- `custom_manifest_invalid`
- `custom_dependencies_missing`

If provider setup, host-side capability setup, or host-side manual items are still missing, do not claim online readiness.

## Codex And Claude Code Boundaries

- Codex: official governed host; hooks are not installed right now
- Claude Code: supported install-and-use path; the installer preserves existing Claude settings while writing a bounded managed `vibeskills` stanza

For both hosts, never ask users to paste key/url/model values into chat. Only guide them to local `settings.json` `env` fields or local environment variables.

## Governance AI Online Layer Boundary

Baseline online provider access does not automatically mean the governance AI online layer is ready.

The public install flow does not currently expose built-in online enhancement configuration. Custom Skill governance docs should not list provider, credential, URL, or model configuration for users, and missing values for that path must not be described as a custom Skill onboarding failure.

If related online capabilities are not configured through the public path, describe them only as "base install complete" or "related online capability not ready/not verified", not as online enhancement ready.

## Minimal Acceptance Checklist

- ordinary skills can still use `skills/local/<skill-id>/SKILL.md` without entering the advanced lane
- manifest schema validation passes
- undeclared directories do not become routable
- explicit user choice can override automatic suggestions
- canonical `vibe`, the work kernel, and `work_binding` truth remain authoritative
- doctor status matches the real configuration without overstating readiness
