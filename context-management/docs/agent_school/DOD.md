# Definition of Done (DOD)

## What "Done" Means

A task is **DONE** when ALL of the following are true:

---

## Hard Requirements (Non-Negotiable)

### 1. Working Tree is Clean
```bash
git status
# Must show: "nothing to commit, working tree clean"
```

**Exceptions allowed ONLY if:**
- Merge conflict requires human resolution (documented)
- CI/pre-commit hook blocks commit (documented)
- Changes are intentionally uncommitted (with explicit reason)

### 2. Tests Pass
```bash
<test_command>
# Must exit with code 0
```

**Exceptions allowed ONLY if:**
- Tests were already failing before your changes
- New tests are failing due to known limitation (documented as TODO)
- Test infrastructure is broken (documented)

### 3. Changes are Committed
```bash
git log --oneline -3
# Your changes should appear here
```

**No exceptions.** If you changed code, it must be committed.

### 4. Summary Provided

Your final message includes:
- What changed (files + description)
- Why it changed (rationale)
- How to verify (steps)
- Repo state (branch, status, test results)

---

## Soft Requirements (Should Do)

### Lint Passes
```bash
<lint_command>
# Should exit with code 0
```

### Format Applied
```bash
<format_command>
# Code should be formatted
```

### Documentation Updated
- If you added a feature, did you update relevant docs?
- If you changed an API, did you update examples?

### No Regressions
- Existing functionality still works
- No new warnings introduced

---

## The Checklist

Before saying "done", run through this:

```
[ ] git status → clean
[ ] tests → pass
[ ] changes → committed
[ ] summary → provided
[ ] lint → pass (if configured)
[ ] format → applied (if configured)
```

---

## Common "Done" Failures

| Failure | Why It's Not Done |
|---------|-------------------|
| "I made the changes" | Did you commit them? |
| "Tests pass" | Is working tree clean? |
| "Working tree clean" | Did you provide a summary? |
| "Here's what I did" | Did tests pass? |
| Uncommitted changes | Not done. Commit or explain. |
| Failing tests | Not done. Fix or document. |
| No summary | Not done. Explain your work. |

---

## Evidence Template

Copy this and fill it in for every task completion:

```markdown
## Task Complete

### Changes
- `path/to/file1.ext`: Brief description
- `path/to/file2.ext`: Brief description

### Rationale
Why this approach was chosen.

### Verification
1. Run `command` to verify X
2. Check `location` for Y

### State
- Branch: `branch-name`
- Status: clean
- Tests: pass
- Commit: `abc1234` "commit message"
```

---

## Not Done Until Proven Done

Saying "I'm done" is not proof.
Showing the evidence is proof.

```
"Done" without evidence = Not done
"Done" with evidence = Actually done
```
