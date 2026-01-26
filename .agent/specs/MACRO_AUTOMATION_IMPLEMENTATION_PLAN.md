# Macro Automation Implementation Plan

> **Status:** APPROVED | **Version:** 1.0.0 | **Date:** 2026-01-25
> **Source:** Gemini 3 Pro (architect mode) + analyze.py validation
> **Query Manifest:** `research/gemini/sessions/20260125_223125_*.json`

---

## Executive Summary

Build a closed loop: **Code Change → Trigger → Macro Execution → Opportunity Creation**

| Metric | Value |
|--------|-------|
| **New Files** | 3 |
| **Modified Files** | 2 |
| **Total LOC** | ~400 |
| **Phases** | 4 |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MACRO AUTOMATION PIPELINE                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Git Commit ──► Post-Commit Hook                                   │
│                       │                                             │
│                       ▼                                             │
│               ┌───────────────┐                                     │
│               │ TRIGGER ENGINE│  (NEW: trigger_engine.py)           │
│               │               │                                     │
│               │ • Get changes │                                     │
│               │ • Load macros │                                     │
│               │ • Match rules │                                     │
│               └───────┬───────┘                                     │
│                       │                                             │
│                       ▼                                             │
│               ┌───────────────┐                                     │
│               │ BARE EXECUTOR │  (NEW: bare/macro_executor.py)      │
│               │               │                                     │
│               │ • Parse YAML  │                                     │
│               │ • Run steps   │                                     │
│               │ • Check crit. │                                     │
│               └───────┬───────┘                                     │
│                       │                                             │
│                       ▼                                             │
│               ┌───────────────┐                                     │
│               │ OPP GENERATOR │  (NEW: bare/opp_generator.py)       │
│               │               │                                     │
│               │ • Create OPP  │                                     │
│               │ • Set confid. │                                     │
│               └───────┬───────┘                                     │
│                       │                                             │
│                       ▼                                             │
│               .agent/registry/inbox/OPP-XXX.yaml                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: BARE Macro Executor

**File:** `.agent/tools/bare/macro_executor.py`
**LOC:** ~150-200
**Complexity:** Medium

### Responsibilities

1. **Schema Parser:** Validate `MACRO-XXX.yaml` against `macro.schema.yaml`
2. **Step Interpreter:** Execute steps sequentially
   - Shell commands → `subprocess.run`
   - Internal tools → Python function mapping
3. **Condition Checker:** Evaluate `success_criteria`
4. **Artifact Manager:** Capture stdout/stderr/files

### Interface

```python
class MacroExecutor:
    def __init__(self, macro_id: str):
        self.macro = self.load_macro(macro_id)

    def load_macro(self, macro_id: str) -> dict:
        """Load and validate macro YAML."""

    def execute(self, context: dict = None) -> ExecutionResult:
        """Run all steps, return results."""

    def execute_step(self, step: dict) -> StepResult:
        """Execute single step based on type."""

    def verify_criteria(self, results: list) -> bool:
        """Check if success_criteria met."""
```

### Test Command

```bash
python .agent/tools/bare/cli.py run-macro MACRO-001
```

---

## Phase 2: OPP Generator

**File:** `.agent/tools/bare/opp_generator.py`
**LOC:** ~80-100
**Complexity:** Low

### Responsibilities

1. **Template Engine:** Convert finding → OPP YAML
2. **Confidence Calculator:** Set 4D scores based on evidence
3. **File Writer:** Save to `.agent/registry/inbox/`

### Interface

```python
class OppGenerator:
    def create_from_finding(
        self,
        title: str,
        description: str,
        source_macro: str,
        evidence: list,
        category: str = "QUALITY"
    ) -> str:
        """Create OPP and return ID."""

    def calculate_confidence(self, evidence: list) -> dict:
        """Return 4D confidence scores."""
```

---

## Phase 3: Trigger Engine

**File:** `.agent/tools/trigger_engine.py`
**LOC:** ~120
**Complexity:** Low/Medium

### Responsibilities

1. **Context Detection:** Get changed files from git
2. **Registry Scan:** Load all macros from library
3. **Match Logic:** Evaluate trigger conditions
4. **Dispatch:** Invoke BARE for matching macros

### Trigger Types

| Type | Condition | Example |
|------|-----------|---------|
| `manual` | Only explicit invocation | Default |
| `post_commit` | After any commit | MACRO-001 target |
| `schedule` | Cron expression | Daily health check |
| `file_change` | Glob pattern match | `**/*.py` changes |

### Interface

```python
class TriggerEngine:
    def __init__(self):
        self.macros = self.load_all_macros()

    def evaluate_event(self, event_type: str, context: dict) -> list:
        """Return list of macros to execute."""

    def get_git_changes(self) -> list:
        """Return files changed in last commit."""

    def dispatch(self, macro_ids: list, context: dict):
        """Execute macros via BARE."""
```

### CLI

```bash
python .agent/tools/trigger_engine.py --event post-commit
python .agent/tools/trigger_engine.py --event schedule --cron "0 6 * * *"
python .agent/tools/trigger_engine.py --macro MACRO-001  # Force run
```

---

## Phase 4: Hook Wiring

**File:** `.agent/hooks/post-commit` (modify)
**LOC:** ~10 added
**Complexity:** Low

### Changes

```bash
#!/bin/bash
# ... existing archive sync ...

# === MACRO AUTOMATION (Phase 4) ===
echo "[Trigger] Scanning for macros..."
python .agent/tools/trigger_engine.py --event post-commit

# Log execution
echo "$(date -Iseconds) post-commit trigger completed" >> .agent/logs/trigger.log
```

---

## Implementation Order

| Phase | Component | Files | LOC | Depends On |
|-------|-----------|-------|-----|------------|
| **1** | Macro Executor | `bare/macro_executor.py`, `bare/cli.py` | 180 | - |
| **2** | OPP Generator | `bare/opp_generator.py` | 100 | Phase 1 |
| **3** | Trigger Engine | `trigger_engine.py` | 120 | Phase 1 |
| **4** | Hook Wiring | `post-commit` | 10 | Phase 3 |

**Total:** 3 new files, 2 modified, ~410 LOC

---

## File Map

```
.agent/
├── tools/
│   ├── bare/
│   │   ├── cli.py                    # MODIFY: Add run-macro command
│   │   ├── macro_executor.py         # NEW: Phase 1
│   │   └── opp_generator.py          # NEW: Phase 2
│   └── trigger_engine.py             # NEW: Phase 3
├── hooks/
│   └── post-commit                   # MODIFY: Phase 4
├── macros/
│   ├── library/
│   │   └── MACRO-001-skeptical-audit.yaml
│   └── logs/
│       └── MACRO-001/
│           └── {timestamp}.log       # Execution logs
└── logs/
    └── trigger.log                   # Trigger engine log
```

---

## Success Criteria

### Phase 1 Complete When:
- [ ] `python .agent/tools/bare/cli.py run-macro MACRO-001` executes
- [ ] Steps are logged
- [ ] Success/failure determined

### Phase 2 Complete When:
- [ ] Failed macro creates OPP in inbox
- [ ] OPP has valid 4D confidence
- [ ] OPP references source macro

### Phase 3 Complete When:
- [ ] `trigger_engine.py --event post-commit` identifies matching macros
- [ ] Macros are dispatched to BARE

### Phase 4 Complete When:
- [ ] Post-commit hook invokes trigger engine
- [ ] End-to-end: commit → macro runs → OPP created (if issues found)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Hook slows commits | Macros run async (background) |
| Macro failure breaks hook | Try/except, always exit 0 |
| Infinite loop (macro creates commit) | Skip trigger if commit is from BARE |
| Token cost explosion | Rate limit macro executions per day |

---

## Connection to Existing Systems

| System | Integration Point |
|--------|-------------------|
| Task Registry | OPP Generator writes to inbox |
| BARE | Extended with MacroExecutor |
| Workflow Registry | Macros can invoke workflows |
| Decision Deck | CARD-AUD-001 can invoke manually |
| SOS_MAP | S13 (Macro Registry) documented |

---

## Immediate Next Step

**Create Phase 1: Macro Executor**

```bash
# Create the file structure
mkdir -p .agent/tools/bare
touch .agent/tools/bare/macro_executor.py
touch .agent/tools/bare/__init__.py
```

---

*Generated: 2026-01-25T22:31:25Z*
*Model: gemini-3-pro-preview (architect mode)*
*Tokens: 40,602 in / 1,510 out*
*Cost: $0.099*
