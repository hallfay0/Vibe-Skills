# Bundled Skill Retention Matrix

## Conclusion

The current built-in starter set is intentionally small.

The default `minimal` profile keeps only:

- `tdd-guide`
- `systematic-debugging`

The `full` profile adds one extra verification helper:

- `verification-before-completion`

Everything else that still exists under `bundled/skills/` should currently be read as reference corpus or migration-era residue, not as the default public extension story.

## Why This File Exists

The repo still contains many bundled skill directories on disk. That physical count is not the same thing as the live starter surface.

The runtime benchmark, install story, and packaging inventory now use the packaging contract as the source of truth:

- `minimal` is the default profile
- the default live starter count is `2`
- `full` may include a third built-in verification helper
- raw folder count under `bundled/skills/` is not the benchmark's live starter count

## Retention Matrix

| Bucket | Current rule | What belongs here now | Public story |
|:---|:---|:---|:---|
| Starter set kept live | Keep only the small built-in fallback that the package inventory explicitly ships. | `tdd-guide`, `systematic-debugging`, and `verification-before-completion` only when the user chooses `full`. | This is the only built-in helper set that should be described as live by default. |
| External or reference corpus | Keep repo-owned bundled directories that are still useful as source material, migration inputs, or internal mirrors, but are not part of the default starter claim. | All other current `bundled/skills/*` directories that are not named in the starter-set row above. This includes the large on-disk bundled tree that remains in the repo today. | Do not present this bucket as the normal extension path. The normal story is host-managed external roots, user-owned local roots, and a tiny starter fallback. |
| Archive or migration residue | Use this bucket only when a skill or note has been explicitly moved out of the active bundled tree into a history or migration holding area. | No skill directory is moved into this bucket by Task 6. If a later bounded cleanup pass relocates material, it should land under `references/bundled-skill-corpus/` or `docs/archive/bundled-skill-history/` with a narrow proof note. | This bucket exists to keep history honest, not to expand the runtime story. |

## Current Decision

Task 6 does not force a physical move.

That is deliberate:

- the benchmark already measures the live starter count from packaging inventory
- the package contract already makes `minimal` and `full` behavior explicit
- a broad filesystem move would touch guarded surfaces and create more risk than this alignment pass needs

## Impact

This lets the public docs and benchmark say something simple and true:

- the default product story is a small kernel with two built-in starter helpers
- the optional `full` profile adds one verification helper
- the large bundled tree still in the repo is not the main extension story
- any future physical move should happen as a separate bounded cleanup with its own proof
