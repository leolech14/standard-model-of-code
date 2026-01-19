# Agent School — Initiation

## Purpose

You are being initiated into this repository. This process ensures you can operate safely, predictably, and with full awareness of the rules.

**Failing to complete initiation = operating blind.**

---

## Required Reading (in order)

1. `REPO_FACTS.md` — commands, paths, environment
2. `WORKFLOWS.md` — git, test, commit procedures
3. `DOD.md` — definition of done (what "complete" means)

---

## Boot Checklist

Execute these steps NOW, before any other work:

### A) Identify Basics
- [ ] Confirm repo root path
- [ ] Identify current branch
- [ ] Run `git status` — is it clean or dirty?

### B) Find Commands
- [ ] Test command(s): `___________`
- [ ] Lint command(s): `___________`
- [ ] Format command(s): `___________`
- [ ] Build command(s): `___________`
- [ ] Run command(s): `___________`

### C) Acknowledge Policies
- [ ] I will commit each logical change-set
- [ ] I will never end a task with uncommitted work
- [ ] I will run tests before claiming "done"
- [ ] I will provide a summary with rationale

---

## Required Output: INITIATION_REPORT

After completing the checklist, you MUST output this JSON:

```json
{
  "initiated": true,
  "timestamp": "ISO-8601 timestamp",
  "repo_root": "/absolute/path/to/repo",
  "branch": "current-branch-name",
  "status": "clean|dirty",
  "commands": {
    "test": "npm test | pytest | go test | etc",
    "lint": "eslint . | ruff | etc",
    "format": "prettier | black | etc",
    "build": "npm run build | make | etc",
    "run": "npm start | python main.py | etc"
  },
  "policies_acknowledged": {
    "commit_discipline": true,
    "no_dirty_end": true,
    "test_before_done": true,
    "summary_required": true
  },
  "notes": ["optional observations about repo state"]
}
```

### Validation Rules

- `initiated` must be `true`
- `status` must reflect actual `git status` output
- All `policies_acknowledged` must be `true`
- Commands should be actual commands found in the repo (or "not_found")

---

## What Happens If You Skip Initiation

1. You operate without knowing critical commands
2. You may duplicate existing code/modules
3. You may violate commit policies unknowingly
4. Your "done" may not actually be done
5. The human will not trust your work

---

## After Initiation

Once you've output the INITIATION_REPORT, you may proceed with tasks.

Remember the micro-loop for all work:

```
SCAN → PLAN → EXECUTE → VALIDATE → COMMIT → REPEAT
```

See `WORKFLOWS.md` for details.
