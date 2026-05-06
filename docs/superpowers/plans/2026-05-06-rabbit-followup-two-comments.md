# Rabbit Follow-Up Two Comments Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve the two currently unresolved CodeRabbit inline comments on PR 228 with minimal, verified edits.

**Architecture:** This is a narrow review-follow-up patch. One task updates a wording-only Markdown checklist line. One task removes an unreferenced PowerShell helper from the installer script without changing installer behavior.

**Tech Stack:** Markdown documentation, PowerShell installer script, pytest, ripgrep, GitHub CLI.

---

### Task 1: Fix Follow-Up Plan Checklist Wording

**Files:**
- Modify: `docs/superpowers/plans/2026-05-06-rabbit-review-followup.md:119`

- [ ] **Step 1: Confirm the current wording**

Run:

```powershell
$p = 'docs/superpowers/plans/2026-05-06-rabbit-review-followup.md'
$lines = Get-Content -LiteralPath $p
for ($i = 116; $i -le 120; $i++) {
  '{0,4}: {1}' -f $i, $lines[$i - 1]
}
```

Expected: line 119 contains `host approved additions`.

- [ ] **Step 2: Apply the wording fix**

Change:

```markdown
lock rehydration, and host approved additions.
```

to:

```markdown
lock rehydration, and host-approved additions.
```

- [ ] **Step 3: Verify the wording fix**

Run:

```powershell
rg -n "host approved additions|host-approved additions" docs/superpowers/plans/2026-05-06-rabbit-review-followup.md
```

Expected: only `host-approved additions` appears.

### Task 2: Remove Unused Installer Helper

**Files:**
- Modify: `scripts/install/Install-VgoAdapter.ps1:204-214`

- [ ] **Step 1: Confirm the helper is unreferenced**

Run:

```powershell
rg -n "Test-VgoSkillEntryPoint" scripts tests packages -S
```

Expected before the edit: only the definition in `scripts/install/Install-VgoAdapter.ps1` appears.

- [ ] **Step 2: Remove the unused function block**

Delete this block from `scripts/install/Install-VgoAdapter.ps1`:

```powershell
function Test-VgoSkillEntryPoint {
    param([string]$SkillRoot)

    if ([string]::IsNullOrWhiteSpace($SkillRoot)) {
        return $false
    }
    return (
        (Test-Path -LiteralPath (Join-Path $SkillRoot 'SKILL.md') -PathType Leaf) -or
        (Test-Path -LiteralPath (Join-Path $SkillRoot 'SKILL.runtime-mirror.md') -PathType Leaf)
    )
}
```

- [ ] **Step 3: Verify no stale helper references remain**

Run:

```powershell
rg -n "Test-VgoSkillEntryPoint" scripts tests packages -S
```

Expected after the edit: no code or test matches. The design and implementation
plan may still mention the removed helper by name.

### Task 3: Validate and Commit

**Files:**
- Check: `docs/superpowers/plans/2026-05-06-rabbit-review-followup.md`
- Check: `scripts/install/Install-VgoAdapter.ps1`
- Check: `docs/superpowers/specs/2026-05-06-rabbit-followup-two-comments-design.md`
- Check: `docs/superpowers/plans/2026-05-06-rabbit-followup-two-comments.md`

- [ ] **Step 1: Run targeted installer test**

Run:

```powershell
pytest tests/runtime_neutral/test_generated_nested_bundled.py::InstallTimeGeneratedNestedBundledTests::test_powershell_fallback_in_place_internal_corpus_prunes_and_sanitizes -q
```

Expected: the targeted pytest test passes.

- [ ] **Step 2: Run whitespace validation**

Run:

```powershell
git diff --check
```

Expected: no output and exit code `0`.

- [ ] **Step 3: Commit the implementation**

Run:

```powershell
git status --short
git add -- docs/superpowers/plans/2026-05-06-rabbit-review-followup.md scripts/install/Install-VgoAdapter.ps1 docs/superpowers/plans/2026-05-06-rabbit-followup-two-comments.md
git commit -m "fix: resolve rabbit follow-up inline comments"
```

Expected: a commit containing the wording fix, helper removal, and this implementation plan.

### Task 4: Update PR Branch and Verify GitHub State

**Files:**
- No direct file edits.

- [ ] **Step 1: Attempt normal push**

Run:

```powershell
git push origin HEAD:review/pr226-pr227-combined
```

Expected: branch updates successfully. If HTTPS push fails with the known connection reset or port 443 failure, use the GitHub Git Database API update path and verify tree equality.

- [ ] **Step 2: Verify unresolved review threads**

Run:

```powershell
$json = gh api graphql -f query='query($owner:String!, $repo:String!, $number:Int!) { repository(owner:$owner, name:$repo) { pullRequest(number:$number) { reviewThreads(first: 100) { nodes { isResolved isOutdated path line } } } } }' -f owner='foryourhealth111-pixel' -f repo='Vibe-Skills' -F number=228 | ConvertFrom-Json
$threads = @($json.data.repository.pullRequest.reviewThreads.nodes)
$unresolved = @($threads | Where-Object { -not $_.isResolved })
[pscustomobject]@{
  total_threads = $threads.Count
  unresolved_threads = $unresolved.Count
  unresolved_paths = (@($unresolved | ForEach-Object { $_.path }) -join ', ')
} | Format-List
```

Expected: unresolved thread count becomes `0` after CodeRabbit processes the update or the outdated threads are resolved.

- [ ] **Step 3: Verify PR checks**

Run:

```powershell
gh pr checks 228 --repo foryourhealth111-pixel/Vibe-Skills
```

Expected: CodeRabbit, gates, and python-validation are passing after the branch update.
