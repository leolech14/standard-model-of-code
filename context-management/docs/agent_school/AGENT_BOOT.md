# AGENT_BOOT.md - Single Source for Agent Initiation

> **One file. One script. One output. You're ready.**

---

## Quick Start

```bash
# Run this first
bash context-management/tools/maintenance/boot.sh --json
```

This outputs your `INITIATION_REPORT` JSON. If it runs, you're initialized.

---

## Non-Negotiables

1. **Never leave repo dirty** - Commit changes or explain why you cannot
2. **Verify before "done"** - Run `git status`, tests, lint
3. **No silent refactors** - State file moves/renames explicitly
4. **No duplicates** - Search before creating new modules
5. **Rationale required** - Every change needs a written "why"

---

## Commands (PROJECT_elements)

| Task | Command |
|------|---------|
| **Test** | `cd standard-model-of-code && pytest tests/ -q` |
| **Lint** | `cd standard-model-of-code && ruff check src/` |
| **Format** | `cd standard-model-of-code && black src/ --check` |
| **Build** | `cd standard-model-of-code && pip install -e .` |
| **Run** | `./collider full <path> --output <dir>` |

---

## The Micro-Loop

Every task follows this pattern:

```
SCAN → PLAN → EXECUTE → VALIDATE → COMMIT → REPEAT
```

| Step | Action |
|------|--------|
| **SCAN** | `git status`, `git diff --stat`, locate files |
| **PLAN** | 3-7 bullet points of what you'll do |
| **EXECUTE** | Make a small, logical chunk of changes |
| **VALIDATE** | Run tests/lint relevant to the chunk |
| **COMMIT** | Commit with clear message |
| **REPEAT** | Until task complete |

---

## Definition of Done

A task is **DONE** when ALL of these are true:

```
[x] git status → clean (or explained)
[x] tests → pass (or documented)
[x] changes → committed
[x] summary → provided
```

### Summary Format

```markdown
## Summary

### What Changed
- [file]: description

### Why
Brief rationale.

### How to Verify
1. Step to verify

### Repo State
- Branch: <name>
- Status: clean | dirty (explanation)
- Tests: pass | fail (details)
- Commit: <hash> "message"
```

---

## INITIATION_REPORT

After boot, you have this JSON:

```json
{
  "initiated": true,
  "timestamp": "ISO-8601",
  "repo_root": "/path/to/repo",
  "branch": "main",
  "status": "clean|dirty",
  "commands": {
    "test": "...",
    "lint": "...",
    "format": "...",
    "build": "...",
    "run": "..."
  },
  "policies_acknowledged": {
    "commit_discipline": true,
    "no_dirty_end": true,
    "test_before_done": true,
    "summary_required": true
  }
}
```

---

## Architecture (Brain/Body)

```
PROJECT_elements/
├── standard-model-of-code/   ← BODY (Collider engine)
│   ├── src/core/             ← Pipeline, classifiers
│   ├── schema/               ← Atoms, roles, constants
│   └── docs/                 ← MODEL.md, COLLIDER.md
│
└── context-management/       ← BRAIN (AI tools)
    ├── tools/ai/             ← analyze.py
    ├── config/               ← analysis_sets.yaml
    └── docs/agent_school/    ← This file
```

**Rule:** Know which hemisphere you're in before making changes.

---

## Key Files

| Need | File |
|------|------|
| Theory | `standard-model-of-code/docs/MODEL.md` |
| Tool docs | `standard-model-of-code/docs/COLLIDER.md` |
| Constants SSoT | `standard-model-of-code/schema/constants.yaml` |
| AI analysis | `context-management/tools/ai/analyze.py` |
| Analysis sets | `context-management/config/analysis_sets.yaml` |

---

## Deep Docs (Optional Reading)

| Doc | Purpose |
|-----|---------|
| `WORKFLOWS.md` | Full git/commit procedures |
| `DOD.md` | Complete definition of done |
| `REPO_FACTS.md` | Environment, dependencies |
| `../AI_USER_GUIDE.md` | The Triad (Librarian, Surgeon, Architect) |

---

## Emergency

- Primary: leonardo.lech@gmail.com
- Infra docs: `~/gcp-infrastructure/CLAUDE.md`

---

*"SCAN → PLAN → EXECUTE → VALIDATE → COMMIT → REPEAT"*
