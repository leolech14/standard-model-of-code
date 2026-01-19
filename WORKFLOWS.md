# PROJECT_elements Workflows

> **Seamless Enforcement**: Easy guarantees that prevent mistakes before they happen.

---

## Core Principle: The Dichotomy

```
PROJECT_elements/
├── standard-model-of-code/    ← THE PROJECT (Theory + Collider)
└── everything else            ← Support, experiments, archives
```

**Rule**: Only `standard-model-of-code/` is the canonical source. Everything else is auxiliary.

---

## Workflow 1: Evaluation Lifecycle

When evaluating new tools, libraries, or approaches:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   IDEATION   │ ──▶ │   DOWNLOAD   │ ──▶ │   EVALUATE   │ ──▶ │   CLEANUP    │
│              │     │              │     │              │     │              │
│ Log in       │     │ Place in     │     │ Test, doc    │     │ Delete or    │
│ EVAL_LOG.md  │     │ .eval/       │     │ findings     │     │ archive      │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

**Location**: `.eval/active/` (gitignored)
**Tracking**: `EVAL_LOG.md` (tracked)

---

## Workflow 2: Conversation Artifacts

AI conversations produce valuable artifacts. Handle them properly:

```
During Session:          After Session:
┌────────────────┐       ┌────────────────┐
│ AI generates   │  ──▶  │ Review value   │
│ large .md file │       │                │
└────────────────┘       └───────┬────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
            ┌──────────────┐          ┌──────────────┐
            │ VALUABLE     │          │ ROUTINE      │
            │ → archive/   │          │ → Delete     │
            │   sessions/  │          │              │
            └──────────────┘          └──────────────┘
```

**Never leave large AI artifacts at root level.**

---

## Workflow 3: Backup Before Risky Changes

**DON'T**: Create `.zip` files
**DO**: Use Git branches

```bash
# Before risky change
git checkout -b backup/before-migration

# Do the work on another branch
git checkout pr/migration
# ... make changes ...

# If it works, delete backup
git branch -d backup/before-migration

# If it fails, restore
git checkout backup/before-migration
```

---

## Workflow 4: Virtual Environments

**Rule**: One venv per project, always named `.venv/`

```bash
# Create
python -m venv .venv

# Activate
source .venv/bin/activate

# Recreate (if corrupted)
rm -rf .venv && python -m venv .venv && pip install -r requirements.txt
```

**Never**: `venv_experiment/`, `venv_treesitter/`, etc.

---

## Workflow 5: Cleanup Checklist

Run periodically (monthly):

```bash
# Find orphaned files at root
ls -la | grep -v standard-model-of-code | grep -v README | grep -v WORKFLOWS

# Find large files
find . -maxdepth 2 -size +10M -type f

# Find old venvs
find . -name "venv*" -type d -o -name ".venv" -type d

# Find Python caches
find . -name "__pycache__" -type d

# Find evaluation downloads
find . -name "*Evaluation*" -type d
```

---

## Seamless Enforcement

| Guarantee | Mechanism |
|-----------|-----------|
| No cruft committed | `.gitignore` |
| No accidental large files | `.gitattributes` + pre-commit |
| Evaluations tracked | `EVAL_LOG.md` |
| Artifacts archived | `archive/sessions/` |

---

## Quick Reference

| I want to... | Do this |
|--------------|---------|
| Evaluate a new library | Create `.eval/active/library-name/`, log in `EVAL_LOG.md` |
| Sync to Cloud | `python context-management/tools/archive/archive.py mirror` |
| Save AI conversation | Move to `archive/sessions/YYYY-MM-topic.md` |
| Make risky change | Create `backup/before-X` branch |
| Clean up | Run checklist above |
| Create venv | `python -m venv .venv` (always this name) |
