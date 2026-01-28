# DECISIONS - Locked Canonical Choices

**📍 Governance:** [ROADMAP](./ROADMAP.md) | [Quality Gates](./QUALITY_GATES.md) | [Definition of Done](./DEFINITION_OF_DONE.md)
**📊 Architecture:** [SUBSYSTEMS.yaml](./SUBSYSTEMS.yaml) | [DOMAINS.yaml](./DOMAINS.yaml) | [PIPELINES.md](./PIPELINES.md)

**Purpose:** Prevent drift by documenting immutable architectural decisions
**Updated:** 2026-01-28
**Authority:** Based on ChatGPT 5.2 Pro audit + repository analysis

---

## D1: Registry-First Architecture ✅

**Decision:** Canonical truth lives in machine-readable registries (YAML/JSON), never in markdown.

**Rationale:** Markdown drifts, registries validate. Counts/indexes/summaries MUST be generated from registries.

**Registries:**
- `SUBSYSTEMS.yaml` - 4 subsystems (PARTICLE, WAVE, OBSERVER, ARCHIVE)
- `DOMAINS.yaml` - 5 domains with symmetry tracking
- `standard-model-of-code/src/patterns/*.yaml` - Atom taxonomy
- `context-management/config/analysis_sets.yaml` - AI query sets
- `.agent/registry/` - Task/opportunity registry

**Enforced by:** All index generators MUST read from registries, never scrape docs.

---

## D2: Single Canonical Source Per Concept ✅

**Decision:** If two files disagree, one is canonical and the other is derived/reference.

**Canonical Sources (locked):**

| Concept | Canonical Source | Derived/Reference |
|---------|------------------|-------------------|
| **Atoms** | `src/patterns/ATOMS_T*.yaml` | `docs/MODEL.md` (summary), `ATOMS_UNIVERSAL_INDEX.yaml` (generated) |
| **Pipeline Stages** | `src/core/pipeline/stages/__init__.py` (code) | `docs/specs/PIPELINE_STAGES.md` (generated), `REGISTRY_OF_REGISTRIES.md` (generated summary) |
| **Subsystems** | `SUBSYSTEMS.yaml` | Any "subsystem list" in docs |
| **Domains** | `DOMAINS.yaml` | Any "domain map" in docs |
| **Theory Axioms** | `docs/theory/THEORY_AXIOMS.md` | `docs/MODEL.md` (summary) |
| **UI Controls** | `docs/specs/UI_CONTROLS_SCHEMA.md` | Circuit breaker tests (runtime validation) |

**Enforced by:** Verification scripts fail if derived docs don't match canonical source.

---

## D3: Active vs Archive is Structural ✅

**Decision:** Active docs MUST pass quality gates. Archive can be messy.

**Active directories:**
- `standard-model-of-code/docs/` (excluding `docs/archive/`)
- `context-management/docs/` (excluding `docs/archive/`)
- `.agent/intelligence/` (excluding logs older than 30 days)
- `.agent/deck/`

**Archive directories:**
- `archive/` (top-level cold storage)
- `standard-model-of-code/docs/archive/`
- `context-management/docs/archive/`
- `.agent/intelligence/autopilot_logs/` (>30 days)
- `.agent/macros/logs/` (>30 days)

**Quality gates for Active:**
- No broken internal links
- No unresolved placeholders (`{...}`, `TODO`, `FIXME` without issue)
- No "validated_*" files that are actually failures
- All claims (counts, canonical status) must be true

**Archive is exempt:** Broken links, drift, placeholders allowed.

**Enforced by:** `./pe verify --active-only` must pass before any release.

---

## D4: v1 Scope is Defined ✅

**Decision:** v1 is NOT "the entire repo." v1 is the minimal viable canonical core.

**v1 Core Contents:**

```
v1_core/
├── registries/
│   ├── SUBSYSTEMS.yaml
│   ├── DOMAINS.yaml
│   └── atoms/
│       ├── ATOMS_T0.yaml
│       ├── ATOMS_T1.yaml
│       └── ATOMS_T2_*.yaml
├── verification/
│   ├── verify_atoms.py (check uniqueness)
│   ├── verify_links.py (active docs only)
│   ├── verify_counts.py (registry vs index)
│   └── verify_symmetry.py (code↔context)
├── generated/
│   ├── ATOM_INDEX.md (from YAML)
│   ├── PIPELINE_STAGES.md (from code)
│   └── SUBSYSTEM_MAP.md (from SUBSYSTEMS.yaml)
├── docs/
│   ├── GETTING_STARTED.md
│   ├── EXTENSION_GUIDE.md
│   └── theory/
│       ├── THEORY_AXIOMS.md
│       └── MODEL.md
└── README.md
```

**Everything else:** v2+ or archive.

**Enforced by:** `./pe verify v1` must pass. No new features until v1 ships.

---

## D5: No New Scope Until Gates Pass ✅

**Decision:** Anti-stall rule. Cannot add features while canonical has drift.

**The Rule:**
```
IF any P0 gate fails:
  THEN new scope is blocked
  ONLY allowed: fix gates OR archive the blocker
```

**P0 Gates (must pass):**
1. Atom ID uniqueness ✅ (FIXED 2026-01-27)
2. Registry count consistency ❌ (atoms index drift)
3. Pipeline stage consistency ❌ (28 vs 18 drift)
4. Active doc link integrity ❌ (14 broken links)
5. No misleading artifacts ❌ (validated_* failures)

**Current Status:** 1/5 gates pass. **New scope BLOCKED until 5/5.**

**Enforced by:** Pre-commit hook rejects commits adding new subsystems/domains if gates fail.

---

## D6: Generated Outputs Are Stamped ✅

**Decision:** Every generated file MUST have a header declaring its source.

**Header format:**
```markdown
<!--
GENERATED FILE - DO NOT EDIT BY HAND
Source: SUBSYSTEMS.yaml
Generator: tools/generate_subsystem_map.py v1.2.0
Generated: 2026-01-27T12:00:00Z
Git SHA: a1b2c3d
-->
```

**Applies to:**
- Atom indexes
- Count tables
- Subsystem maps
- Pipeline summaries
- Any doc with counts/lists from registries

**Enforced by:** Verification fails if generated file lacks header OR is out of sync with source.

---

## D7: Archive is a Feature, Not Failure ✅

**Decision:** Moving something to archive is PROGRESS, not guilt.

**Archive criteria:**
- No longer actively maintained
- May contain drift/errors
- Kept for historical reference only
- Does NOT block v1 shipment

**Process:**
```bash
git mv path/to/old_thing archive/YYYY-MM-DD_old_thing/
git commit -m "archive: Move old_thing (reason)"
```

**Philosophy:** Archive early, archive often. Clarity > completeness.

---

## D8: Every Session Must Ship Something ✅

**Decision:** No research-only sessions. Every session ends with one of:

- ✅ A decision logged (this file)
- ✅ A gap resolved (duplicate atoms fixed)
- ✅ Verification improved (SUBSYSTEMS.yaml created)
- ✅ v1 package improved

**WIP Limit:** Max 3 active P0/P1 gaps. Everything else goes to backlog.

**Enforced by:** Session handoff document (`WHEN_YOU_RETURN.md`) must list concrete progress.

---

## DECISION LOG (Chronological)

| Date | Decision | Status |
|------|----------|--------|
| 2026-01-27 | Registry-first architecture | ✅ Locked |
| 2026-01-27 | SUBSYSTEMS.yaml is canonical | ✅ Created |
| 2026-01-27 | DOMAINS.yaml tracks symmetry | ✅ Created |
| 2026-01-27 | Fix 16 duplicate atom IDs | ✅ Fixed |
| 2026-01-27 | v1 scope defined | ✅ Locked |
| 2026-01-27 | Active vs Archive structural | ✅ Locked |
| 2026-01-27 | Generated outputs stamped | ✅ Locked |
| 2026-01-27 | No new scope until gates pass | ✅ Locked |

---

**This file is append-only. Decisions are immutable once locked.**
