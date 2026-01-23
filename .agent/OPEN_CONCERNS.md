# Open Concerns & Sprint System Design

> Consolidated from Grok ideation session + Gemini/Perplexity validation
> Created: 2026-01-23

---

## Part 1: Open Concerns

### A. Discovery & Consolidation Gap

**Problem:** During research sessions, valuable insights emerge but get lost in the flow.

| Symptom | Root Cause | Proposed Fix |
|---------|------------|--------------|
| Too many directions at once | No capture mechanism | Discovery Inbox |
| Insights not actionable | No promotion workflow | `promote_opportunity.sh` |
| Research outputs scattered | No extraction pipeline | Research Refinery |

**Status:** Discovery Inbox validated by Gemini + Perplexity. Not yet built.

---

### B. Fragmented Context Loading

**Problem:** Agents don't automatically see what files exist or their relationships.

| Symptom | Root Cause | Proposed Fix |
|---------|------------|--------------|
| Agents miss obvious files | No manifest injection | KERNEL.md (exists) |
| Re-derive existing theory | No forced grounding | Bootstrap protocol (exists) |
| Context too large to load | No clustering | Regional RAG system |

**Status:** KERNEL.md + manifest.yaml exist. Regional clustering NOT built.

---

### C. No Sprint Discipline

**Problem:** Work drifts without clear version targets and relaxation points.

| Symptom | Root Cause | Proposed Fix |
|---------|------------|--------------|
| Never "done" | No version definition | Sprint Registry |
| Constant context switching | No commitment phase | Design → Execute → Relax cycle |
| No celebration/reset | Always in motion | Explicit relaxation hotspots |

**Status:** Not built. Critical for sustainable development.

---

### D. Roadmap Not Institutionalized

**Problem:** Strategic plans exist in scattered docs, not enforced.

| Symptom | Root Cause | Proposed Fix |
|---------|------------|--------------|
| Plans forgotten | No central registry | `ROADMAP_REGISTRY.yaml` |
| No validation against roadmap | No alignment scoring | Roadmap Alignment dimension |
| Priorities unclear | No ranking mechanism | Confidence + Urgency matrix |

**Status:** Partial (TASK_CONFIDENCE_REGISTRY exists). Needs formalization.

---

### E. Research History Untapped

**Problem:** 50+ Perplexity queries saved but not systematically mined.

| Symptom | Root Cause | Proposed Fix |
|---------|------------|--------------|
| Duplicate queries | No deduplication | Research Index |
| Insights buried | No extraction | Insight Extractor |
| No cross-reference | No linking | Semantic clustering |

**Status:** Auto-save works. Extraction pipeline NOT built.

---

## Part 2: Comprehensive Sprint System

### Vision

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SPRINT-BASED DEVELOPMENT FLOW                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│   │  DESIGN  │───►│ EXECUTE  │───►│ VALIDATE │───►│  RELAX   │     │
│   │  SPRINT  │    │  SPRINT  │    │  SPRINT  │    │  (reset) │     │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘     │
│        │                                                 │          │
│        └─────────────────────────────────────────────────┘          │
│                         (next version)                              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Core Concepts

#### 1. Regional RAG Clustering

**IMPORTANT:** Regional RAG does NOT replace `analysis_sets.yaml`. It CONSUMES it as the foundational region definitions. The existing 20+ curated sets (pipeline, viz_core, architecture_review, etc.) become the canonical regions.

```yaml
# Regional RAG extends analysis_sets.yaml with:
# - purity_check: validation rules per region
# - processing_logic: how to analyze this region
# - coherence_rules: cross-region consistency checks

# Example extension (NOT replacement):
regional_extensions:
  pipeline:  # Existing set from analysis_sets.yaml
    purity_check: "no_side_effects"
    processing_logic: "structural_analysis"

  research_history:  # New region (add to analysis_sets.yaml)
    paths: ["docs/research/perplexity/**"]
    processing_logic: "insight_extraction"
    purity_check: "has_citations"

# The cluster_analyzer.py tool will:
# 1. Load analysis_sets.yaml as base regions
# 2. Apply regional_extensions for validation
# 3. Report purity violations per region
```

**Integration Point:** `context-management/config/analysis_sets.yaml`

#### 2. Timestamp Coherence Analysis

Use file modification times to understand work patterns:

```python
def cluster_by_activity(files):
    """Group files modified together (likely related changes)."""
    # Files modified within same commit/session = cohesive unit
    # Files not touched in 30+ days = potential staleness
    # Recent burst of changes = active development area
```

#### 3. Sprint Registry

```yaml
# .agent/sprints/SPRINT-001.yaml
id: SPRINT-001
name: "Agent System Foundation"
version_target: "0.2.0"
status: EXECUTING  # DESIGNING | EXECUTING | VALIDATING | COMPLETE

definition_of_done:
  - "Discovery Inbox operational"
  - "Individual agent todos implemented"
  - "BARE Phase 2 (CrossValidator) complete"
  - "All tasks at 85%+ confidence"

tasks:
  - TASK-000  # Bootstrap (90%)
  - TASK-001  # MCP template (80%)

started: "2026-01-23"
target_completion: "2026-01-30"

relaxation_reward: "Ship to production, update portfolio"
```

#### 4. Research Refinery Pipeline

```
docs/research/perplexity/raw/*.json
         │
         ▼
┌─────────────────────┐
│  INSIGHT EXTRACTOR  │  ← Extract key findings, recommendations
└─────────┬───────────┘
         │
         ▼
┌─────────────────────┐
│  DEDUPLICATOR       │  ← Remove redundant insights
└─────────┬───────────┘
         │
         ▼
┌─────────────────────┐
│  ROADMAP LINKER     │  ← Connect to strategic goals
└─────────┬───────────┘
         │
         ▼
.agent/intelligence/insights/INSIGHT-XXX.yaml
```

---

## Part 3: Proposed Architecture

### New Directory Structure

```
.agent/
├── KERNEL.md                    # Bootstrap (exists)
├── OPEN_CONCERNS.md             # This file
├── SUBSYSTEM_INTEGRATION.md     # Integration map (exists)
│
├── sprints/                     # NEW: Sprint definitions
│   ├── SPRINT-001.yaml          # Current sprint
│   └── archive/                 # Completed sprints
│
├── registry/
│   ├── inbox/                   # NEW: Discovery Inbox
│   ├── active/                  # Current tasks (exists)
│   ├── claimed/                 # Locked tasks (exists)
│   └── archive/                 # Completed (exists)
│
├── agents/                      # NEW: Individual workspaces
│   ├── claude/todo.yaml
│   ├── gemini/todo.yaml
│   └── grok/todo.yaml
│
├── intelligence/
│   ├── truths/                  # BARE output (exists)
│   ├── insights/                # NEW: Extracted insights
│   └── clusters/                # NEW: Regional analysis
│
├── roadmap/                     # NEW: Institutionalized roadmap
│   ├── ROADMAP_REGISTRY.yaml    # Strategic goals
│   └── alignment_scores.yaml    # Task-roadmap alignment
│
└── tools/
    ├── bare                     # BARE CLI (exists)
    ├── truth_validator.py       # Phase 1 (exists)
    ├── promote_opportunity.sh   # NEW: Inbox → Active
    ├── extract_insights.py      # NEW: Research refinery
    └── cluster_analyzer.py      # NEW: Regional RAG
```

### Implementation Phases

| Phase | Deliverable | Effort | Impact |
|-------|-------------|--------|--------|
| **1** | Discovery Inbox + promote script | LOW | HIGH |
| **2** | Sprint Registry + SPRINT-001.yaml | LOW | HIGH |
| **3** | Individual agent workspaces | MEDIUM | MEDIUM |
| **4** | Research Refinery (insight extraction) | MEDIUM | HIGH |
| **5** | Regional RAG clustering | HIGH | HIGH |
| **6** | Timestamp coherence analysis | MEDIUM | MEDIUM |

---

## Part 4: Immediate Actions

### Sprint-001 Definition of Done

To close this design phase and enter execution:

- [ ] Discovery Inbox created (`.agent/registry/inbox/`)
- [ ] `opportunity.schema.yaml` written
- [ ] `promote_opportunity.sh` working
- [ ] Sprint Registry created (`.agent/sprints/`)
- [ ] SPRINT-001.yaml defined with this scope
- [ ] All above committed and documented

### Success Criteria

When SPRINT-001 completes:
1. New discoveries automatically land in inbox
2. Promotion workflow is one command
3. Sprint progress is visible at a glance
4. System is ready for SPRINT-002 (Research Refinery)

---

## Part 5: Duality Reminder

From Grok session - the guiding philosophy:

```
KNOWLEDGE/WISDOM          ↔          ACTION/CARE
(Contemplative)                      (Mindful Doing)

DESIGN SPRINT             ↔          EXECUTE SPRINT
(Think deeply)                       (Build carefully)

TURBULENCE               ↔          LAMINAR FLOW
(Mix, review, reshape)              (Seamless execution)
```

The sprint system institutionalizes this rhythm:
- **Design phase** = Knowledge/Wisdom dominates (turbulence encouraged)
- **Execute phase** = Action/Care dominates (laminar flow required)
- **Relax phase** = Integration and reset

---

## Version

| Field | Value |
|-------|-------|
| Created | 2026-01-23 |
| Status | DRAFT |
| Next Review | After SPRINT-001 execution |
