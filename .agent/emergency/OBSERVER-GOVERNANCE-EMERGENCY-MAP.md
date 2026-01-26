# OBSERVER GOVERNANCE - EMERGENCY MAP

> **Status:** PARTIALLY OPERATIONAL - Integration gaps
> **Created:** 2026-01-26
> **Author:** Claude Opus 4.5 (system crystallization)
> **Realm:** OBSERVER (Governance & Autonomous Refinement)

---

## EXECUTIVE SUMMARY

The Observer realm manages tasks, validation, and autonomous refinement. It's the **nervous system** that should respond to changes and coordinate action. Currently **fragmented** - components work in isolation but don't talk to each other.

```
SEVERITY: MEDIUM-HIGH
IMPACT:   No autonomous refinement, manual coordination required
ROOT:     S5 (Task Registry) → S6 (BARE) integration missing
CASCADE:  Changes happen → no auto-response → manual intervention always needed
```

---

## 1. OBSERVER SUBSYSTEMS

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        OBSERVER REALM                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   S5: TASK REGISTRY                     S6: BARE                       │
│   ┌─────────────────────┐               ┌─────────────────────┐        │
│   │ .agent/registry/    │               │ Background Auto-    │        │
│   │ ├── active/ (25)    │ ──── ? ────►  │ Refinement Engine   │        │
│   │ ├── inbox/ (60)     │   BLOCKED     │                     │        │
│   │ └── archive/        │               │ (can't read S5)     │        │
│   └─────────────────────┘               └─────────────────────┘        │
│           │                                       │                     │
│           │                                       │                     │
│   S8: HYGIENE                           S10: ENRICHMENT                │
│   ┌─────────────────────┐               ┌─────────────────────┐        │
│   │ Pre-commit hooks    │               │ Task promotion      │        │
│   │ ├── YAML validation │               │ inbox → active      │        │
│   │ ├── JSON check      │               │                     │        │
│   │ └── commitlint      │               │                     │        │
│   │ STATUS: WORKING     │               │ STATUS: WORKING     │        │
│   └─────────────────────┘               └─────────────────────┘        │
│                                                                         │
│   S13: MACRO REGISTRY                                                  │
│   ┌─────────────────────┐                                              │
│   │ .agent/macros/      │                                              │
│   │ Recorded patterns   │                                              │
│   │ STATUS: NEW (1 macro│                                              │
│   └─────────────────────┘                                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. THE S5 → S6 GAP (SG-004)

### What Should Happen

```
Developer commits code
        │
        ▼
┌─────────────────┐
│ S8: Pre-commit  │ ◄── Validates YAML, JSON, commit msg
│ hooks run       │
└────────┬────────┘
         │ (commit succeeds)
         ▼
┌─────────────────┐
│ S6: BARE        │ ◄── Reads task registry
│ Post-commit     │     Identifies relevant tasks
│ hook triggers   │     Auto-generates fixes/updates
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ S5: Task        │ ◄── Tasks updated automatically
│ Registry        │     Progress tracked
└─────────────────┘
```

### What Actually Happens

```
Developer commits code
        │
        ▼
┌─────────────────┐
│ S8: Pre-commit  │ ✓ WORKS
│ hooks run       │
└────────┬────────┘
         │ (commit succeeds)
         ▼
┌─────────────────┐
│ S6: BARE        │ ✗ CAN'T READ S5
│ Post-commit     │   (no structured YAML interface)
│ hook triggers   │
└────────┬────────┘
         │
         ▼
         ∅  (nothing happens)
```

### Gap Details

| Aspect | Status |
|--------|--------|
| **Gap ID** | SG-004 |
| **Source** | SOS_MAP_TRUTH.md |
| **Problem** | S6 (BARE) needs to poll S5 (Task Registry) for task facts |
| **Missing** | Structured YAML output from S5 that S6 can parse |
| **Impact** | No autonomous task-aware refinement |

---

## 3. TASK REGISTRY (S5) DEEP DIVE

### Structure

```
.agent/registry/
├── INDEX.md              # Human-readable summary
├── METRICS.md            # Statistics
├── active/               # 25 tasks in progress
│   ├── TASK-001.yaml
│   ├── TASK-002.yaml
│   └── ...
├── inbox/                # 60 opportunities (unprocessed)
│   ├── OPP-001.yaml
│   ├── OPP-002.yaml
│   └── ...
├── archive/              # Completed/abandoned
│   └── ...
└── batches/              # Grouped operations
    └── ...
```

### Task Schema

```yaml
# Example: TASK-065.yaml
id: TASK-065
title: "Implement Purpose Coherence Export"
status: in_progress
priority: P1
created: 2026-01-25
tags: [collider, purpose-field]
context:
  related_files:
    - standard-model-of-code/src/core/full_analysis.py
    - standard-model-of-code/src/core/purpose_field.py
acceptance_criteria:
  - coherence_score exported to unified_analysis.json
  - POM reads coherence_score
```

### What S5 Can Do

| Capability | Status |
|------------|--------|
| Store tasks as YAML | ✓ WORKING |
| Human-readable INDEX | ✓ WORKING |
| Query tasks by status | ✓ WORKING (manual) |
| Emit structured feed | ✗ MISSING |
| Push updates to S6 | ✗ MISSING |

---

## 4. BARE (S6) DEEP DIVE

### What BARE Is Designed For

```
BARE = Background Auto-Refinement Engine

Purpose:
  - Watch for code changes
  - Identify what tasks might be affected
  - Auto-generate fixes or updates
  - Keep the repo self-healing

Trigger:
  - Post-commit hook
  - File watcher (via launchd)
```

### What BARE Needs

```
To function, BARE needs:
  1. List of active tasks (from S5)
  2. Task context (related files, acceptance criteria)
  3. Recent changes (from git diff)
  4. Ability to match changes to tasks
  5. Ability to generate/suggest fixes
```

### What BARE Has

```
Currently BARE has:
  1. ✗ No structured interface to S5
  2. ✗ Can't programmatically read tasks
  3. ✓ Can read git diff
  4. ✗ No task matching logic
  5. ? Fix generation capability unclear
```

---

## 5. HYGIENE (S8) - WORKING

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml (excerpt)
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: check-yaml
      - id: check-json
      - id: check-toml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: local
    hooks:
      - id: commitlint
        name: commitlint
        entry: npx commitlint --edit
```

### Status

| Hook | Status |
|------|--------|
| check-yaml | ✓ WORKING |
| check-json | ✓ WORKING |
| check-toml | ✓ WORKING |
| end-of-file-fixer | ✓ WORKING |
| trailing-whitespace | ✓ WORKING |
| commitlint | ✓ WORKING |
| UI Control Registry | ✓ WORKING |

---

## 6. MACRO REGISTRY (S13) - NEW

### What Macros Are

```
MACRO = Recorded action pattern that can be replayed

Example:
  1. Human does: analyze → fix → test → commit
  2. Macro records the pattern
  3. Next time: macro replays automatically
```

### Current State

```
.agent/macros/
└── (1 macro recorded)

Tools:
  - macro_executor.py   # Runs macros
  - opp_generator.py    # Generates opportunities from patterns
  - trigger_engine.py   # Triggers macros on events
```

### Status

| Aspect | Status |
|--------|--------|
| Macro storage | ✓ WORKING |
| Macro recording | ? UNCLEAR |
| Macro replay | ? UNCLEAR |
| Auto-triggering | ✗ NOT CONNECTED |

---

## 7. THE AUTONOMOUS LOOP (DESIGN)

### What Should Exist

```
┌──────────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS REFINEMENT LOOP                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   SENSE                                                          │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ File watchers detect changes                             │   │
│   │ Git hooks trigger on commit                              │   │
│   │ Collider produces fresh analysis                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│   THINK                                                          │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ BARE matches changes to tasks                            │   │
│   │ Macro registry finds applicable patterns                 │   │
│   │ ACI provides reasoning                                   │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│   ACT                                                            │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ Auto-generate fixes                                      │   │
│   │ Update task status                                       │   │
│   │ Create new opportunities                                 │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│   LEARN                                                          │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ Record successful patterns as macros                     │   │
│   │ Update truths with new facts                             │   │
│   │ Adjust confidence scores                                 │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### What Actually Exists

```
┌──────────────────────────────────────────────────────────────────┐
│                    ACTUAL STATE                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   SENSE                                                          │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ File watchers: IDLE (daemons not running)                │   │
│   │ Git hooks: ✓ WORKING (pre-commit only)                   │   │
│   │ Collider: DEGRADED (tree-sitter broken)                  │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│   THINK                                                          │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ BARE: CAN'T READ TASKS (S5→S6 gap)                       │   │
│   │ Macro registry: EXISTS but not connected                 │   │
│   │ ACI: WORKING but fed stale data                          │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│   ACT                                                            │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ Auto-generate fixes: ✗ NOT HAPPENING                     │   │
│   │ Update task status: MANUAL ONLY                          │   │
│   │ Create opportunities: MANUAL ONLY                        │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│   LEARN                                                          │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ Macro recording: ? UNCLEAR                               │   │
│   │ Truth updates: MANUAL                                    │   │
│   │ Confidence adjustment: NOT IMPLEMENTED                   │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 8. FIXING THE S5 → S6 GAP

### Option A: Structured YAML Export from S5

```python
# tasks_exporter.py (NEW)
def export_active_tasks() -> dict:
    """Export active tasks in format BARE can consume."""
    tasks = []
    for yaml_file in Path(".agent/registry/active").glob("*.yaml"):
        task = yaml.safe_load(yaml_file.read_text())
        tasks.append({
            "id": task["id"],
            "title": task["title"],
            "related_files": task.get("context", {}).get("related_files", []),
            "acceptance_criteria": task.get("acceptance_criteria", []),
        })
    return {"tasks": tasks, "exported_at": datetime.now().isoformat()}
```

### Option B: BARE Reads YAML Directly

```python
# bare.py modification
def load_task_context():
    """BARE reads task registry directly."""
    tasks = {}
    for yaml_file in Path(".agent/registry/active").glob("*.yaml"):
        task = yaml.safe_load(yaml_file.read_text())
        for file in task.get("context", {}).get("related_files", []):
            if file not in tasks:
                tasks[file] = []
            tasks[file].append(task["id"])
    return tasks  # Map: file -> [task_ids]
```

### Option C: Event Bus

```
S5 emits events → Event bus → S6 subscribes

Event: TaskCreated, TaskUpdated, TaskCompleted
Payload: { task_id, related_files, ... }
```

---

## 9. RECOVERY PROCEDURE

### Step 1: Verify S5 Working

```bash
# Check task registry structure
ls -la .agent/registry/active/ | head -10

# Count tasks
echo "Active: $(ls .agent/registry/active/*.yaml 2>/dev/null | wc -l)"
echo "Inbox: $(ls .agent/registry/inbox/*.yaml 2>/dev/null | wc -l)"
```

### Step 2: Create S5 Export Interface

```bash
# Create tasks_exporter.py in .agent/tools/
# (implementation as shown in Option A above)
```

### Step 3: Modify BARE to Consume

```bash
# Update BARE to call tasks_exporter
# Map git diff files to affected tasks
```

### Step 4: Test Integration

```bash
# Make a change to a file mentioned in a task
# Verify BARE detects the relationship
# Verify task status could be updated
```

---

## 10. SUCCESS CRITERIA

| Metric | Current | Target |
|--------|---------|--------|
| S5 readable by S6 | NO | YES |
| Task-aware commits | NO | YES |
| Auto task updates | NO | YES |
| Macro triggering | NO | YES |
| Autonomous loop | BROKEN | OPERATIONAL |

---

## 11. RELATED EMERGENCY MAPS

| Map | Relationship |
|-----|--------------|
| `WAVE-AI-SUBSYSTEM-EMERGENCY-MAP.md` | ACI needs fresh data from Observer |
| `PARTICLE-COLLIDER-EMERGENCY-MAP.md` | Collider feeds Observer with analysis |

---

*The Observer should observe and act. Currently it only observes (barely).*
