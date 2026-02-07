# 03 - Decision Deck System

> **Scope:** `wave/tools/ai/deck/` -- Constrained action space for AI agents
> **Files analyzed:** 4 Python modules, 26 YAML cards, 1 external consumer
> **Date:** 2026-02-07

---

## 1. System Purpose

The Decision Deck is a governance layer that constrains AI agent actions to a curated library of **certified moves** (cards). Instead of free-form improvisation, agents choose from validated cards with explicit preconditions, steps, expected outcomes, meter effects, and rollback procedures. The spec cites 40-60% improvement in task success rates from constrained action spaces.

Key metaphor: A card game. The system has a Dealer (filters available cards), a Router (maps natural language to cards), a Player (executes cards), and Meters (track cumulative state).

---

## 2. File Map

```
wave/tools/ai/deck/
  deck_router.py        # Game Master: loads cards, routes intents, deals hands
  play_card.py          # Execution engine: runs card steps with checkpoints
  deck_context.py       # ACI integration: generates context for AI query injection
  fabric_bridge.py      # Communication Fabric bridge: system health for decisions
  CARD-ANA-001.yaml     # Handcrafted card: Run Collider Analysis
  CARD-AUD-001.yaml     # Handcrafted card: Skeptical Audit
  CARD-DOC-001.yaml     # Handcrafted card: Write Specification
  CARD-GIT-001.yaml     # Handcrafted card: Commit Checkpoint
  CARD-RES-001.yaml     # Handcrafted card: Research with Perplexity
  CARD-RES-002.yaml     # Handcrafted card: Research with Gemini
  CARD-SES-001.yaml     # Handcrafted card: Start Session
  CARD-SYS-001.yaml     # Handcrafted card: System Config Audit & Cleanup
  CARD-WLD-000.yaml     # Handcrafted card: Wildcard (escape hatch)
  CARD-OPP-059..084     # Auto-generated from OPP registry (15 cards)

.agent/tools/deal_cards.py    # Alternative dealer (reads from .agent/deck/)
.agent/deck/DEPRECATED.md     # Old location pointer
.agent/specs/DECISION_DECK_LAYER.md  # Formal specification
```

---

## 3. Python Module Analysis

### 3.1 deck_router.py (13.2 KB, 395 lines)

**Purpose:** The "Game Master" layer. Loads all CARD-*.yaml files into memory, routes natural language intents to cards via regex pattern matching, evaluates preconditions, and deals available hands. Primary entry point for the deck subsystem.

**Key classes/functions:**

| Name | Type | Description |
|------|------|-------------|
| `Card` | dataclass | Certified move. Fields: id, title, description, phase_gate, preconditions, steps, outcomes, rollback, context_injection, cost, tags |
| `Card.from_yaml(path)` | classmethod | Loads a card from YAML file |
| `Card.check_preconditions(state)` | method | Evaluates preconditions including fabric checks. Returns (ok, failures) |
| `Card.to_prompt()` | method | Generates markdown representation for chat display |
| `DeckRouter` | class | Main router. Loads cards, routes intents, filters by preconditions |
| `DeckRouter._load_cards()` | method | Globs CARD-*.yaml in deck_dir |
| `DeckRouter.route_intent(intent)` | method | Pattern-matches intent string to card ID |
| `DeckRouter.get_available_cards(state)` | method | Returns cards with satisfied preconditions |
| `DeckRouter.deal(state, include_fabric)` | method | Builds formatted "hand" string including fabric health |
| `INTENT_PATTERNS` | dict | Maps card IDs to regex lists for intent routing |

**Internal imports:**
- `fabric_bridge.get_bridge`, `check_fabric_precondition`, `ActionRisk` (optional, try/except)

**External dependencies:** `re`, `yaml`, `pathlib`, `typing`, `dataclasses`

**Intent routing patterns:**

| Card | Triggers |
|------|----------|
| CARD-ANA-001 | "analyze code", "run collider", "scan project" |
| CARD-RES-001 | "research", "investigate", "deep dive", "validate claim" |
| CARD-RES-002 | "perplexity", "external research", "grounding" |
| CARD-GIT-001 | "commit", "save changes", "checkpoint" |
| CARD-DOC-001 | "document", "update docs", "write spec" |
| CARD-SES-001 | "start session", "initialize", "boot" |
| CARD-AUD-001 | "audit", "verify", "check drift", "hsl", "socratic" |
| CARD-SYS-001 | "clean config", "remove duplicate config", "mcp cleanup" |
| CARD-WLD-000 | "wildcard", "custom", "other", "unknown" |

**Fabric-aware dealing:** When the Communication Fabric bridge is available, `deal()` includes system health tier, risk level, warnings, and recommendations. If system is BLOCKED, only LOW risk cards are dealt. If RISKY, a warning is shown.

**CLI commands:**
- `deck_router.py list` -- List all cards grouped by tag
- `deck_router.py deal` -- Show available cards (precondition-filtered hand)
- `deck_router.py route <intent>` -- Route NL intent to card
- `deck_router.py show <card-id>` -- Display card details
- `deck_router.py fabric` / `health` -- Show fabric context and precondition checks

---

### 3.2 play_card.py (11.5 KB, 340 lines)

**Purpose:** Execution engine. Loads a card by ID, verifies preconditions, runs steps sequentially with optional checkpoints (user confirmation), applies success/failure outcomes to meters, logs plays to history, and handles rollback.

**Key classes/functions:**

| Name | Type | Description |
|------|------|-------------|
| `CardPlayer` | class | Core executor. Constructed with card_id, dry_run, auto flags |
| `CardPlayer.load_card()` | method | Reads CARD-{id}.yaml from deck directory |
| `CardPlayer.check_preconditions()` | method | File existence checks and state checks |
| `CardPlayer.execute_step(step, num)` | method | Dispatches step by action prefix |
| `CardPlayer.apply_outcome(type)` | method | Updates meters and logs play |
| `CardPlayer.rollback()` | method | Executes rollback steps if available |
| `CardPlayer.play()` | method | Full pipeline: load, preconditions, steps, outcome |
| `load_meters()` | function | Reads .agent/state/meters.yaml |
| `save_meters(meters)` | function | Writes .agent/state/meters.yaml |
| `log_play(card_id, outcome, details)` | function | Appends to .agent/state/play_log.yaml (last 100) |
| `update_meters(meters, changes)` | function | Applies delta changes to meter values |

**Internal imports:** None (standalone)

**External dependencies:** `sys`, `yaml`, `subprocess`, `pathlib`, `datetime`, `typing`

**Step action dispatching (by prefix):**

| Prefix | Behavior |
|--------|----------|
| `./`, `python`, `cd` | Shell command via `subprocess.run` (5-min timeout) |
| `Load`, `Read`, `Review` | Context loading -- acknowledges, checks file existence |
| `Check`, `Scan` | Directory scanning -- counts glob matches |
| `Initialize`, `Create` | Creates YAML file with timestamp and card reference |
| `Display` | Reads and confirms file availability |
| (other) | Manual action -- prompts user for confirmation |

**State files:**
- `PROJECT_ROOT/.agent/state/meters.yaml` -- Persistent meter values
- `PROJECT_ROOT/.agent/state/play_log.yaml` -- Play history (capped at 100 entries)

**Modes:** `--dry-run` (no execution), `--auto` (no prompts)

---

### 3.3 deck_context.py (5.5 KB, 187 lines)

**Purpose:** Dynamic state generator for ACI (Adaptive Context Intelligence) integration. Produces markdown context strings about deck state -- meters, recent plays, available cards -- for injection into AI queries. This is how the AI agent "sees" the deck.

**Key functions:**

| Name | Returns | Description |
|------|---------|-------------|
| `get_meters()` | Dict[str, int] | Current meter values (focus, reliability, discovery, debt, readiness) |
| `get_recent_plays(limit)` | List[Dict] | Last N plays from play_log.yaml |
| `get_available_cards()` | List[Dict] | All cards with basic info (id, title, phase_gate, tags) |
| `get_deck_summary()` | Dict | Complete state: meters + play stats + card list |
| `get_deck_context(verbose)` | str | Markdown-formatted context string for AI injection |
| `get_meter_health()` | str | One-line health: HEALTHY, DEGRADED, or CRITICAL |

**Internal imports:** None (reads YAML files directly)

**External dependencies:** `yaml`, `pathlib`, `typing`

**Health logic:** debt > 5 = CRITICAL, debt > 2 or reliability < 0 = DEGRADED, else HEALTHY.

**ACI connection:** `get_deck_context()` output is designed to be injected into AI prompts as a `## Decision Deck State` block, giving the AI awareness of current meters, recent history, and success rates.

---

### 3.4 fabric_bridge.py (16.1 KB, 447 lines)

**Purpose:** Bridges the Communication Fabric (system-level metrics at `.agent/intelligence/comms/fabric.py`) to the Decision Deck. Translates system metrics (stability, noise, mutual information, test coverage, change entropy) into agent-actionable signals: precondition checks, risk assessments, and filtered card hands.

**Key classes/functions:**

| Name | Type | Description |
|------|------|-------------|
| `ActionRisk` | Enum | SAFE, CAUTION, RISKY, BLOCKED |
| `FabricState` | dataclass | Simplified fabric state for agent consumption (17 fields) |
| `FabricBridge` | class | Main bridge. Cached state, precondition checks, risk assessment |
| `FabricBridge.get_state(force_refresh)` | method | Gets cached fabric state (60s TTL) |
| `FabricBridge.check_precondition(condition)` | method | Evaluates `fabric.*` conditions |
| `FabricBridge.assess_action_risk(action_type)` | method | Risk for refactor/analyze/commit/docs |
| `FabricBridge.get_fabric_context()` | method | Markdown context string for agents |
| `FabricBridge.filter_cards_by_risk(cards, max_risk)` | method | Removes cards above risk threshold |
| `get_bridge()` | function | Singleton accessor |

**Internal imports:** `fabric.py` via `importlib.util` dynamic import from `.agent/intelligence/comms/`

**External dependencies:** `sys`, `pathlib`, `typing`, `dataclasses`, `enum`, `importlib`

**Precondition checks:**

| Condition | What it checks |
|-----------|---------------|
| `fabric.stability_ok` | Stability margin > 0.1 |
| `fabric.stability_positive` | Stability margin > 0 |
| `fabric.noise_acceptable` | Noise < 0.7 |
| `fabric.noise_low` | Noise < 0.4 |
| `fabric.mi_adequate` | Mutual Information > 0.5 |
| `fabric.mi_good` | Mutual Information > 0.7 |
| `fabric.redundancy_ok` | R_auto (test coverage) > 0.5 |
| `fabric.system_stable` | Stability OK AND delta_H < 0.5 |
| `fabric.not_blocked` | Risk level != BLOCKED |
| `fabric.safe_for_refactor` | Stability OK AND redundancy OK |
| `fabric.safe_for_analysis` | Noise acceptable |

**Graceful degradation:** If fabric.py is not importable, returns safe defaults with one warning.

---

### 3.5 deal_cards.py (.agent/tools/, 287 lines)

**Purpose:** Alternative card dealer reading from `.agent/deck/` (deprecated location). Provides ASCII box display for chat rendering. Independent from `deck_router.py`.

**Note:** Reads from `.agent/deck/` which is deprecated. The canonical location is `wave/tools/ai/deck/`. Both directories currently contain the same YAML cards.

---

## 4. Card Catalog

### 4.1 Handcrafted Cards (9)

| ID | Title | Phase Gate | Risk | Unlocks |
|----|-------|-----------|------|---------|
| CARD-SES-001 | Start Session | ANY | LOW | RES-001, ANA-001, GIT-001, DOC-001, WLD-000 |
| CARD-ANA-001 | Run Collider Analysis | EXECUTING, VALIDATING | LOW | VIZ-001, DOC-002 |
| CARD-RES-001 | Research with Perplexity | DESIGNING, VALIDATING, ANY | LOW | DOC-001, REG-001 |
| CARD-RES-002 | Research with Gemini | DESIGNING, VALIDATING, ANY | LOW | DOC-001, REG-001 |
| CARD-DOC-001 | Write Specification | DESIGNING | LOW | REG-001, TST-001 |
| CARD-GIT-001 | Commit Checkpoint | ANY | LOW | GIT-002 |
| CARD-AUD-001 | Skeptical Audit | EXECUTING, VALIDATING | LOW | (none) |
| CARD-SYS-001 | System Config Audit & Cleanup | ANY | LOW | (none) |
| CARD-WLD-000 | Wildcard Action | ANY | MEDIUM | (none) |

### 4.2 Auto-Generated OPP Cards (15)

| ID | Title | Confidence | Tags |
|----|-------|------------|------|
| CARD-OPP-059 | Sprawl Consolidation Infrastructure | 90% | infrastructure |
| CARD-OPP-060 | Autonomous Enrichment Pipeline MVP | 80% | infrastructure |
| CARD-OPP-061 | Fix HSL Daemon Locally | 95% | infrastructure |
| CARD-OPP-062 | BARE Phase 2 - CrossValidator | 35% | intelligence |
| CARD-OPP-063 | Verify GCS Mirror Post-Triage | 70% | infrastructure |
| CARD-OPP-064 | Hierarchical Tree Layout for File View | 85% | visualization |
| CARD-OPP-065 | Always-Green Continuous Refinement | 85% | infrastructure |
| CARD-OPP-066 | Handle Gemini API Rate Limiting (429) | 95% | infrastructure |
| CARD-OPP-067 | Implement Health Model (H=T+E+Gd+A) | 70% | health_model |
| CARD-OPP-071 | Fix MISALIGNMENT reporting | 70% | general |
| CARD-OPP-076 | Implement collider mcafee CLI | 70% | cli |
| CARD-OPP-077 | Refine orphan detection patterns | 70% | general |
| CARD-OPP-082 | Create pathogen impact inventory | 70% | health_model |
| CARD-OPP-083 | Select golden repos for regression | 70% | testing |
| CARD-OPP-084 | Add Goodhart's Law protection | 70% | general |

---

## 5. Execution Flow

```
User Intent (NL or CLI)
         |
         v
  +--------------+
  | ./pe deck    |  CLI entry point (pe bash script)
  +--------------+
         |
         +--- "list"/"deal"/"route"/"show" ---> deck_router.py
         |                                          |
         |                          +---------------+---------------+
         |                          |               |               |
         |                   route_intent()   get_available()    deal()
         |                    (regex match)  (precond filter)  (full hand)
         |                          |               |               |
         |                          |       fabric_bridge.py -------+
         |                          |       (system health)
         |                          v
         +--- "play" ----------> play_card.py
         |                          |
         |                  1. load_card()
         |                     (read CARD-*.yaml)
         |                          |
         |                  2. check_preconditions()
         |                     (files, state, fabric)
         |                          |
         |                  3. execute_step() x N
         |                     (shell / context / scan / create / manual)
         |                     [checkpoints require user confirm]
         |                          |
         |                  4. apply_outcome()
         |                     +-- update meters.yaml
         |                     +-- append play_log.yaml
         |                          |
         |                  5. show unlocked cards
         |
         +--- "context" -------> deck_context.py
         |                          |
         |                  get_deck_context()
         |                     (meters + plays + cards -> markdown)
         |                     [injected into AI prompts via ACI]
         |
         +--- "health" --------> deck_context.py --health
                                    |
                                get_meter_health()
                                   (HEALTHY / DEGRADED / CRITICAL)
```

---

## 6. State Files

| File | Purpose | Written By | Read By |
|------|---------|-----------|---------|
| `.agent/state/meters.yaml` | 5 meters: focus, reliability, discovery, debt, readiness | play_card.py | play_card.py, deck_context.py, deal_cards.py |
| `.agent/state/play_log.yaml` | Last 100 card plays with timestamps and outcomes | play_card.py | deck_context.py |
| `.agent/state/session.yaml` | Active session state (created by CARD-SES-001) | play_card.py | play_card.py (precondition check) |
| `.agent/state/wildcard_log.yaml` | Wildcard usage patterns (referenced, not yet impl) | (planned) | (planned) |

---

## 7. Meters System

Five meters track cumulative agent performance:

| Meter | Meaning | Increased By | Decreased By |
|-------|---------|-------------|--------------|
| **focus** | On-task adherence | Session start, commits, config cleanup | (indirectly by drift) |
| **reliability** | System trustworthiness | Commits (+2), audits (+2), analysis (+1), cleanup (+3) | Failed plays (-1 to -2) |
| **discovery** | New knowledge gained | Research (+1 to +2), analysis (+1), audits (+1) | Failed research (-1) |
| **debt** | Technical debt level | Failed plays (+1) | Audits (-1), specs (-1), cleanup (-2) |
| **readiness** | Operational readiness | Session start (+1) | Failed session (-1) |

Health thresholds: debt > 5 = CRITICAL, debt > 2 or reliability < 0 = DEGRADED, else HEALTHY.

---

## 8. Connection Points

### To ACI (Adaptive Context Intelligence)
- `deck_context.py` generates markdown context for injection into AI queries
- `get_deck_context()` produces the `## Decision Deck State` block
- Card definitions include `context_injection` paths pointing to relevant docs

### To Communication Fabric
- `fabric_bridge.py` imports `compute_state_vector()` from `.agent/intelligence/comms/fabric.py`
- Fabric metrics (stability, noise, MI, R_auto, delta_H) gate card availability
- BLOCKED systems get only LOW risk cards during `deal()`

### To Registry System
- Auto-generated OPP cards bridge the registry inbox to the deck
- Cards reference `registry.OPP-NNN.exists` as preconditions
- CARD-SES-001 scans `.agent/registry/inbox/` and `.agent/registry/active/`

### To Refinery / Cerebras
- No direct connection. Refinery operates at a higher platform level.
- Cerebras (fast inference) is not referenced by deck modules.

### To pe CLI
- `./pe deck [list|deal|route|show|play|context|health]` dispatches to deck modules
- `./pe` also attempts intent routing on unrecognized commands via `deck_router.py route`

---

## 9. Card Schema

```yaml
id: CARD-XXX-NNN
title: "Human-readable title"
description: "What this card does"
phase_gate: [DESIGNING, EXECUTING, VALIDATING, ANY]

preconditions:
  - check: "condition_name"
    description: "Human explanation"
    files_must_exist: ["path/to/file"]   # optional
    hard_fail: true                       # optional, for fabric checks

steps:
  - action: "Shell command or action description"
    description: "What this step does"
    checkpoint: true/false     # true = requires user confirmation
    context_file: "path"       # optional, for Load/Read actions
    scan_directory: "path"     # optional, for Check/Scan actions
    creates_file: "path"       # optional, for Initialize/Create actions

outcomes:
  success:
    state_changes: ["description of what changed"]
    unlocks: [CARD-XXX-NNN]   # cards that become available
    meters: {focus: 1, reliability: 2, debt: -1}
  failure:
    state_changes: ["description of failure state"]
    meters: {reliability: -1, debt: 1}

rollback:
  possible: true/false
  steps: ["shell command or description"]
  warning: "Caveats about rollback"

context_injection:
  - path: "file to inject"
    sections: ["relevant sections"]

cost:
  tokens_estimate: 500
  risk_level: LOW/MEDIUM/HIGH

tags: [category, feature, domain]
```

---

## 10. Architecture Observations

1. **Two parallel implementations.** `deck_router.py` (canonical, wave/tools/ai/deck/) and `deal_cards.py` (legacy, .agent/tools/) both load and display cards. Different meter formats, different source directories. The deprecated .agent/deck/ still holds card copies.

2. **OPP cards are structurally thin.** Auto-generated cards lack detailed steps, rollback, and context injection. They function as task pointers, not executable playbooks.

3. **Fabric bridge degrades gracefully.** All fabric imports use try/except with safe defaults. The deck operates fully without the Communication Fabric.

4. **Phantom unlocked cards.** Several cards unlock non-existent cards: VIZ-001, DOC-002, REG-001, REG-002, TST-001, GIT-002. The unlock mechanism tracks intent but has no enforcement.

5. **Intent routing is regex-only.** No embedding or LLM classification. Pattern matching keeps latency under 10ms but limits coverage. Unmatched intents fall through to CARD-WLD-000.

6. **26 cards total.** 9 handcrafted governance/workflow cards + 15 auto-generated OPP cards + 2 unused card slots referenced by unlocks.
