# VibeSkills v4.0.0 Release Plan

## Goal

Prepare the validated Agent execution-handoff runtime in PR #248 as the next
major public release, synchronize all governed version surfaces, and make the
release and installation path clear for new installs and upgrades.

## Version Decision

Use `4.0.0`. This change removes legacy public wrapper and internal execution
surfaces and replaces the prior execution model with Agent-owned module handoff
and strict canonical re-entry. That is a public migration boundary rather than
a patch or additive minor release.

## Deliverables

- Synchronize governed release, package, Skill, and distribution markers at
  `4.0.0` with release date `2026-07-17`.
- Add detailed `v4.0.0` release notes and update the current release navigator
  and changelog.
- Update English and Chinese installation guidance with the release download,
  new-install, upgrade, verification, and v3-to-v4 migration paths.
- Keep the release preparation on PR #248. Do not claim that a GitHub tag,
  release object, or downloadable asset exists until the PR is merged and the
  release is published.

## Proof

- Run the canonical release-cut preview before apply.
- Run focused release/version/package tests and release gates after apply.
- Build the public release bundle and inspect its versioned asset name.
- Reinstall the resulting runtime into both real local Skill roots and verify
  zero missing and zero drifted receipt-owned files.
- Confirm the PR branch and friend fork remain synchronized after push.
