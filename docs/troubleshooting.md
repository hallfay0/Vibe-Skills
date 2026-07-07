# Troubleshooting

## Missing skill after install
- Run `check.ps1`
- Confirm target path is `~/.agents/skills`
- Re-run `install.ps1 -Profile full -StrictOffline`
- Run `scripts/verify/vibe-offline-skills-gate.ps1` and fix lock mismatch if any

## Host plugin or online enhancement unavailable
- Check environment variables and local binaries
- Re-run `check.ps1 -HostId <host> -Deep`
- Treat host plugins and online enhancement as host-managed surfaces

## Upstream update broke behavior
- Do not hot-replace bundled content from upstream
- Use manual merge workflow and update `config/upstream-lock.json`

## Plugin install failures
- Installer is best-effort by design
- See `config/plugins-manifest.codex.json` and install manually
