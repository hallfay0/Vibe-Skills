# Publication notes

This directory is a public snapshot of the accepted local case run
`20260718T041559Z-51996499`.

The accepted source artifacts remain unchanged in the local case workspace.
Evidence text, JSON, and SVG copies normalize machine-specific paths and remove
non-semantic trailing spaces:

- The accepted case directory becomes `<case-root>`.
- Its surrounding workspace becomes `<case-workspace>`.
- The repository checkout becomes `<repository>`.
- The local user home becomes `<user-home>`.

Metrics, model settings, module status, verification results, run IDs, and
delivery-acceptance results are not changed. The Skill inventory snapshot was
captured during publication preparation on the same host after the accepted
run; it is identified as a publication-time snapshot rather than a
runtime-emitted artifact.

The public reproduction wrapper rebuilds the accepted deliverable directory
shape under `reproduce/generated/`; the four computational Python scripts, the
dependency lock, raster figures, slide montage, and PPTX remain byte-identical
accepted copies. The SVG copies differ only by removed trailing spaces. Links
inside the public report point to this directory's copied figures.
`case-manifest.json` remains the accepted run snapshot, so its file hashes
describe the original case package.
