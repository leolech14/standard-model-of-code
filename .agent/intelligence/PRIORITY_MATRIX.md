# Priority Matrix: Wave/Particle Balance Actions

> Generated: 2026-01-23 | Source: Collider Self-Analysis

---

## Matrix View (Impact vs Effort)

```
                            EFFORT
              LOW                           HIGH
         ┌─────────────────────────────────────────┐
    HIGH │  [P1] ✅ DONE          [P2] Split       │
         │                             analyze.py  │
 IMPACT  │                                         │
         │  [P3] Document         [P4] Refactor    │
    LOW  │       Observer API          Dead Code   │
         └─────────────────────────────────────────┘
```

**Quadrant Priority:**
- **Top-Left (Quick Wins):** Do immediately
- **Top-Right (Strategic):** Plan and schedule
- **Bottom-Left (Fill-ins):** Do when convenient
- **Bottom-Right (Reconsider):** Evaluate ROI before starting

---

## Ranked Action Items

| Priority | Action | Impact | Effort | Metric | Risk |
|:--------:|--------|:------:|:------:|:------:|:----:|
| **P0** | Achieve Gold Symmetry (90+) | STRATEGIC | ONGOING | +17 pts | LOW |
| **P1** | ~~Archive stale Wave tools~~ | ✅ DONE | N/A | Files already removed | N/A |
| **P2** | Split analyze.py into modules | HIGH | MEDIUM | restructure | MEDIUM |
| **P3** | Document Observer external API | MEDIUM | LOW | +docs | LOW |
| **P4** | Audit/remove dead code in Wave | MEDIUM | HIGH | -2,000 lines | MEDIUM |

> **P0 (Symmetry)** is the overarching goal. P1-P4 contribute to it.

---

## Detailed Breakdown

### P0: Wave-Particle Symmetry [STRATEGIC GOAL]

**Target:** Achieve Gold Tier (90+ points)

**Current State:** 🥈 Silver (81/100) | **Validated:** 2026-01-23

```
Category      Current  Target  Gap    Evidence
──────────────────────────────────────────────────────────
Structural     24/25    25     +1    96% class, 77% func docs
Behavioral     20/25    25     +5    CLI works, partial config
Examples       12/20    18     +6    4 blocks, not tested
References     13/15    15     +2    0 broken links
Freshness      12/15    15     +3    86 active TODOs
──────────────────────────────────────────────────────────
TOTAL          81/100   95     +9    Gap to Gold
```

**Spec:** [WAVE_PARTICLE_SYMMETRY.md](../specs/WAVE_PARTICLE_SYMMETRY.md)

**Why Strategic:**
- Documentation IS the product for AI-native repos
- Perfect symmetry = zero drift between code and docs
- Enables AI agents to trust documentation completely

**How P1-P4 Contribute:**
| Action | Symmetry Impact |
|--------|-----------------|
| P1 (Archive tools) | +2 Structural (fewer undocumented) |
| P2 (Split analyze) | +3 Structural (clearer modules) |
| P3 (Document API) | +5 Behavioral (complete API docs) |
| P4 (Dead code) | +2 Freshness (no orphans) |

---

### P1: Archive Stale Wave Tools [COMPLETED - FILES ALREADY REMOVED]

**Status:** ✅ INVALIDATED (2026-01-25)

**Original Target:** `wave/tools/`
```
repo_archaeologist.py  ~600 lines  ❌ FILE NOT FOUND
present_architect.py   ~600 lines  ❌ FILE NOT FOUND
future_visionary.py    ~600 lines  ❌ FILE NOT FOUND
```

**Validation:** These files were removed in a previous cleanup. No action needed.

**Note:** The ~1,800 line reduction claim was stale. These tools were already archived or deleted.

---

### P2: Split analyze.py [STRATEGIC]

**Target:** `wave/tools/ai/analyze.py` (3,143 lines)

**Current State:** Monolith handling 4 tiers + 6 modes + interactive

**Proposed Structure:**
```
wave/tools/ai/
├── analyze.py           # CLI entry (200 lines)
├── tiers/
│   ├── instant.py       # INSTANT tier
│   ├── rag.py           # RAG/FileSearch tier
│   ├── long_context.py  # LONG_CONTEXT tier
│   └── perplexity.py    # PERPLEXITY tier
├── modes/
│   ├── forensic.py      # --mode forensic
│   ├── architect.py     # --mode architect
│   └── insights.py      # --mode insights
└── socratic/
    └── validator.py     # SocraticValidator class
```

**Why High Impact:**
- Maintainability (single-responsibility)
- Testability (isolated components)
- Extensibility (add new tiers/modes easily)

**Why Medium Effort:**
- Requires careful import management
- Need to preserve CLI interface
- Test coverage must be maintained

**Validation:** All existing commands must work identically post-refactor

---

### P3: Document Observer External API [FILL-IN]

**Target:** `.agent/` (205 nodes, 315 edges to other realms)

**Concern:** Observer couples to both Particle and Wave. Need clarity on:
- Which exports are intentional APIs?
- Which are internal implementation?

**Action:** Create `.agent/docs/EXTERNAL_API.md`:
```markdown
# .agent External API

## Intentional Exports (use these)
- task_store.py: TaskStore class
- sprint.py: Sprint CLI

## Internal (do not depend on)
- intelligence/*: Generated artifacts
- hooks/*: Git integration only
```

**Why Medium Impact:** Prevents accidental coupling growth

---

### P4: Audit Dead Code in Wave [RECONSIDER]

**Target:** 47 orphan nodes identified in Wave realm

**Current Evidence:**
```
Orphans by type:
- Unused imports: 23
- Dead functions: 12
- Unreachable code: 8
- Config artifacts: 4
```

**Why High Effort:**
- Each orphan needs manual verification
- Some may be "intentionally unused" (future features)
- Risk of breaking runtime behavior

**Recommendation:** Defer until P1-P3 complete. Re-run Collider analysis after cleanup to get fresh orphan count.

---

## Implementation Schedule

```
Week 1: P1 (Archive stale tools)      ██████████  ✅ DONE (files already removed)
Week 2: P3 (Document Observer API)    ████████░░  80% confidence
Week 3-4: P2 (Split analyze.py)       ██████░░░░  60% confidence
Week 5+: P4 (Dead code audit)         ████░░░░░░  40% confidence
```

---

## Success Metrics

| Metric | Before | Target After |
|--------|--------|--------------|
| Wave file count | 50 | 47 (-3 archived) |
| analyze.py lines | 3,143 | <300 (entry) |
| Observer docs | 0 | 1 (API doc) |
| Orphan nodes | 47 | <30 |

---

## Regenerating This Matrix

After completing actions, re-run analysis:

```bash
# 1. Run Collider self-analysis
python .agent/tools/wave_particle_balance.py --run-collider

# 2. Extract fresh metrics
python .agent/tools/wave_particle_balance.py --json > /tmp/balance.json

# 3. Compare against this document
```

---

*This matrix should be updated after each major cleanup iteration.*
