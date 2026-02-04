# REPOSITORY STRUCTURE (CANONICAL)

This document defines the definitive directory tree. Derived from `SUBSYSTEMS.yaml`.

**Last Updated:** 2026-02-01 (Post-consolidation sprint)

---

## ROOT

Primary entry points and master registries.

| File | Type | Purpose |
|------|------|---------|
| `CLAUDE.md` | MD | AI agent orientation & rules |
| `SUBSYSTEMS.yaml` | YAML | **Canonical** subsystem registry |
| `DOMAINS.yaml` | YAML | Code-Context symmetry map |
| `pe` | Exec | Primary CLI tool |

---

## `/governance/` (OBSERVER - Strategy)

Central command layer. Decisions, roadmaps, quality gates.

| File | Purpose |
|------|---------|
| `ROADMAP.md` | Strategic milestones |
| `DECISIONS.md` | Technical ADRs |
| `QUALITY_GATES.md` | Release criteria |
| `REPO_STRUCTURE.md` | This file (derived from SUBSYSTEMS) |

---

## `/particle/` (PARTICLE - Body)

Collider engine and Standard Model theory.

| Path | Purpose | Key Files |
|------|---------|-----------|
| `src/core/` | Collider Pipeline | `full_analysis.py`, `pipeline/stages/` |
| `docs/theory/` | The Canon | `THEORY_AXIOMS.md`, `THEORY_COMPLETE_ALL.md` |
| `schema/` | SM Schema | `antimatter_patterns.yaml`, `particle.schema.json` |
| `cli.py` | Entry point | Main CLI |

---

## `/wave/` (WAVE - Brain)

AI context intelligence and tools.

| Path | Purpose | Key Files |
|------|---------|-----------|
| `tools/ai/` | AI integration | `analyze.py` (Gemini), `aci/refinery.py` |
| `tools/couriers/` | Active processors | `dispatch.py` |
| `intelligence/` | Refined context | `chunks/`, integration point |
| `docs/` | Wave documentation | `PROJECTOME.md`, `CONTEXTOME.md` |

---

## `/.agent/` (OBSERVER - Automation)

Agent orchestration and task management.

| Path | Purpose | Key Files |
|------|---------|-----------|
| `registry/` | Task registry | `active/`, `archive/`, `batches/` |
| `intelligence/` | Canonical intel | `autopilot_logs/`, `chunks/` |
| `tools/` | Agent tools | `autopilot.py`, `wire.py` |
| `META_REGISTRY.yaml` | Master pointers | Points to all registries |

---

## `/research/` (RESEARCH - AI Outputs)

**Consolidated 2026-02-01** from `particle/docs/research/`

| Path | Purpose | Files |
|------|---------|-------|
| `gemini/` | Gemini 2.5 Flash research | 348 .md files |
| `perplexity/` | Perplexity web research | 293 .md files |
| `claude/` | Claude analysis | (future) |
| `INDEX.md` | Navigation | - |

---

## `/reports/` (REPORTS - Analysis Outputs)

**Consolidated 2026-02-01** from 6 scattered locations.

| Path | Purpose | Content |
|------|---------|---------|
| `refinery/` | Refinery audits | `docs_audit_*.json/md` |
| `audits/` | Strategic audits | Socratic, architecture |
| `archives/` | Historical | Legacy reports |
| `INDEX.md` | Navigation | - |

---

## `/tools/` (TOOLS - Utilities)

**Committed 2026-02-01** - previously untracked Python tools.

| File | Purpose |
|------|---------|
| `file_explorer.py` | 314KB GUI file browser |
| `file_scanner.py` | Directory metadata extraction |
| `image_browser.py` | Reference image navigator |
| `experiments/` | Experimental scripts |

---

## `/archive/` (ARCHIVE - Historical)

**Consolidated 2026-02-01** - gitignored, local only.

| Path | Content |
|------|---------|
| `smc/` | From particle |
| `cm/` | From wave |
| `tools/` | Archived tools |

---

## `/docs/` (Documentation)

Top-level documentation and visual assets.

| File | Purpose |
|------|---------|
| `AI_MODELS_REFERENCE.md` | AI model comparison |
| `AI_ECOSYSTEM_MAP.md` | Provider landscape |
| `*.png` | Architecture diagrams |

---

## MAINTENANCE RULES

1. **No Root Pollution**: New docs go to `/governance/` or subsystem
2. **Registry Sync**: Directory changes MUST update `SUBSYSTEMS.yaml`
3. **Single Locus**: Each registry type has ONE canonical location
4. **Derived Docs**: REPO_STRUCTURE.md is derived from SUBSYSTEMS.yaml

---

## SUBSYSTEM SUMMARY

| Subsystem | Role | Root |
|-----------|------|------|
| PARTICLE | Body (Collider) | `particle/` |
| WAVE | Brain (AI/Context) | `wave/` |
| OBSERVER | Governance | `.agent/`, `governance/` |
| RESEARCH | AI Outputs | `research/` |
| REPORTS | Analysis | `reports/` |
| TOOLS | Utilities | `tools/` |
| ARCHIVE | Historical | `archive/` (gitignored) |

---

*Derived from SUBSYSTEMS.yaml v2.0.0*
