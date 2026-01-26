# Macro Registry - Dashboard

> **Purpose:** Recorded action patterns that can be auto-executed on triggers.
> **Principle:** If you do it twice manually, record it as a macro.
> **Status:** INITIALIZED | **Version:** 1.0.0 | **Date:** 2026-01-25

---

## Quick Stats

```
Total Macros:    1
DRAFT:           0
TESTED:          1
PRODUCTION:      0
DEPRECATED:      0
```

---

## The Concept

```
┌─────────────────────────────────────────────────────────────────┐
│                    MACRO LIFECYCLE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. MANUAL EXECUTION                                           │
│      Human or agent performs action sequence                    │
│      "I did X, then Y, then Z, and it worked"                  │
│                                                                 │
│   2. RECORD AS MACRO                                            │
│      Document trigger + steps + success criteria                │
│      Status: DRAFT                                              │
│                                                                 │
│   3. TEST THE MACRO                                             │
│      Execute via manual trigger, verify output                  │
│      Status: TESTED                                             │
│                                                                 │
│   4. AUTOMATE                                                   │
│      Set real trigger (schedule, event, file_change)            │
│      Status: PRODUCTION                                         │
│                                                                 │
│   5. EVOLVE                                                     │
│      Refine based on execution history                          │
│      Version bump for significant changes                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Macro Library

| ID | Name | Status | Trigger | Last Run | Success Rate |
|----|------|--------|---------|----------|--------------|
| MACRO-001 | Skeptical Audit | TESTED | manual | 2026-01-25 | 100% (1/1) |

---

## MACRO-001: Skeptical Audit

**Purpose:** Systematic self-criticism after sessions creating new code.

**Trigger:** Manual (future: post-commit for feat(*))

**Steps:**
1. Inventory session artifacts
2. Check for dead code
3. Check for integration failures
4. Analyze validation theater
5. Check for schema bloat
6. Generate report

**Output:** `.agent/intelligence/SKEPTICAL_AUDIT_{date}.md`

**Automation Path:**
```
TESTED ──► post_commit trigger ──► PRODUCTION
           (needs trigger engine)
```

---

## Directory Structure

```
.agent/macros/
├── INDEX.md                          # This file
├── schema/
│   └── macro.schema.yaml             # Macro definition schema
├── library/
│   └── MACRO-001-skeptical-audit.yaml
└── logs/
    └── MACRO-001/
        └── (execution logs)
```

---

## Integration Points

| System | Connection | Status |
|--------|------------|--------|
| Task Registry | Macros can create OPPs | PLANNED |
| Workflow Registry | Macros can invoke workflows | PLANNED |
| Research Schemas | Macros can execute research | PLANNED |
| BARE | BARE can run production macros | PLANNED |
| Post-commit hooks | Trigger macros after commits | PLANNED |

---

## Trigger Engine (NOT YET IMPLEMENTED)

The trigger engine will:
1. Watch for trigger conditions (file change, schedule, event)
2. Check preconditions
3. Execute macro steps
4. Log execution
5. Update manifest

**Current State:** Macros are manually invoked by agents.
**Target State:** Automatic execution via trigger engine.

---

## Planned Macros

| ID | Name | Purpose | Priority |
|----|------|---------|----------|
| MACRO-002 | Integration Test | Verify all imports work | HIGH |
| MACRO-003 | Manifest Generator | Auto-save query manifests | HIGH |
| MACRO-004 | Dead Code Scan | Weekly orphan detection | MEDIUM |
| MACRO-005 | Schema Drift Detector | Check docs match code | MEDIUM |
| MACRO-006 | Research Archiver | Save Perplexity/Gemini outputs | LOW |

---

## How to Create a New Macro

1. **Do the task manually** and document each step
2. **Create YAML** in `library/MACRO-XXX-name.yaml` using `schema/macro.schema.yaml`
3. **Set status to DRAFT**
4. **Test manually** by following the steps
5. **Update status to TESTED** and add execution to history
6. **Define real trigger** when ready for automation
7. **Update status to PRODUCTION** when trigger engine supports it

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-25 | Initial creation with MACRO-001 |

---

*Created: 2026-01-25*
*Author: Claude Code + Leonardo Lech*
