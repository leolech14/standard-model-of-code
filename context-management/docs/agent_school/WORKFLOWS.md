# Workflows

## The Micro-Loop (Your Heartbeat)

Every task follows this pattern. No exceptions.

```
┌─────────────────────────────────────────────────────┐
│  1. SCAN                                            │
│     git status, git diff --stat, locate files      │
├─────────────────────────────────────────────────────┤
│  2. PLAN                                            │
│     3-7 bullet points of what you'll do            │
├─────────────────────────────────────────────────────┤
│  3. EXECUTE                                         │
│     Make a small, logical chunk of changes         │
├─────────────────────────────────────────────────────┤
│  4. VALIDATE                                        │
│     Run tests/lint relevant to the chunk           │
├─────────────────────────────────────────────────────┤
│  5. COMMIT                                          │
│     Commit with clear message                      │
├─────────────────────────────────────────────────────┤
│  6. REPEAT                                          │
│     Until task complete                            │
└─────────────────────────────────────────────────────┘
```

---

## Commit Discipline

### The Contract

1. **Commit after each logical change-set** — not after 40 unrelated edits
2. **Never end a task with uncommitted work** — this is a hard rule
3. **If tests fail**: commit with `WIP:` prefix + explain in message + add TODO

### Commit Message Format

```
<type>: <short description>

<optional body explaining why>

<optional: Co-Authored-By if pair programming>
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `wip`

### What If You Cannot Commit?

If you genuinely cannot commit (merge conflict, CI blocking, etc.):

1. Stash changes: `git stash -m "WIP: description"`
2. Explain why in your summary
3. List exact steps for human to resolve

**"I forgot" is not a valid reason.**

---

## Before Claiming "Done"

Run this checklist EVERY time:

```bash
# 1. Check working tree
git status

# 2. Run tests
<test_command>

# 3. Run lint (if configured)
<lint_command>

# 4. Verify no uncommitted changes
git diff --stat
```

If any of these fail, you are NOT done.

---

## The End-of-Task Seal

Your final message for any task MUST include:

```markdown
## Summary

### What Changed
- [file1]: description of change
- [file2]: description of change

### Why
Brief rationale for the approach taken.

### How to Verify
1. Step to verify change 1
2. Step to verify change 2

### Repo State
- Branch: <branch_name>
- Status: clean | dirty (with explanation)
- Tests: pass | fail (with details)
- Commits: <commit_hash> "<message>"
```

---

## Git Workflow

### Starting Work

```bash
git status                    # Verify clean state
git pull origin main          # Get latest (if applicable)
git checkout -b feature/name  # New branch for features
```

### During Work

```bash
git add <specific_files>      # Stage only what you changed
git commit -m "type: msg"     # Commit logical chunks
```

### Finishing Work

```bash
git status                    # Must be clean
git log --oneline -5          # Verify your commits
```

---

## Code Review Workflow

When reviewing code:

1. Read the PR description
2. Check files changed
3. Run tests locally
4. Provide specific, actionable feedback
5. Approve only when all concerns addressed

---

## Handling Errors

When something fails:

1. **Read the error** — don't just retry blindly
2. **Identify root cause** — not just symptoms
3. **Fix the cause** — not a workaround
4. **Verify the fix** — run tests again
5. **Document** — explain what went wrong and how you fixed it

---

## Workflow Evidence Requirements

For audit/compliance, preserve evidence:

| Step | Required Evidence |
|------|-------------------|
| SCAN | `git status` output |
| VALIDATE | Test command + output |
| COMMIT | Commit hash + message |
| DONE | Final `git status` showing clean |
