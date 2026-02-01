# Archive Manifest

> **Generated:** 2026-01-19
> **Purpose:** Identify which docs are superseded by the new bibles

---

## New Canonical Sources

| Bible | Purpose | Supersedes |
|-------|---------|------------|
| `docs/THEORY.md` | Standard Model theory | Multiple theory docs |
| `docs/TOOL.md` | Collider implementation | Multiple tool docs |

---

## Documents Now Redundant

These documents contain information that is fully consolidated in the bibles:

### Superseded by THEORY.md

| File | Reason | Recommendation |
|------|--------|----------------|
| `docs/FORMAL_PROOF.md` | V1 constants, proofs | Keep for reference (historical) |
| `docs/THEORY_MAP.md` | Pipeline deps, 4-tier stack | Archive |
| `docs/ATOMS_REFERENCE.md` | V1 atom list (167) | Archive - outdated |
| `docs/PURPOSE_FIELD.md` | Purpose field theory | Archive - in THEORY.md |
| `docs/GLOSSARY.md` | Definitions | Review - some may be outdated |

### Superseded by TOOL.md

| File | Reason | Recommendation |
|------|--------|----------------|
| `docs/ARCHITECTURE.md` | Architecture details | Keep for detail, reference TOOL.md |
| `docs/COMMANDS.md` | Command reference | Archive - in TOOL.md |
| `docs/QUICKSTART.md` | Getting started | Archive - in TOOL.md |

### Historical / Registry

| File | Recommendation |
|------|----------------|
| `docs/THE_PIVOT.md` | Keep - historical value |
| `docs/DISCOVERY_PROCESS.md` | Keep - historical value |
| `docs/registry/HISTORY.md` | Keep - canonical history |
| `docs/registry/GEMINI_EXTRACTION_*.md` | Keep - fact source |

### Reports (Keep All)

| Directory | Purpose |
|-----------|---------|
| `docs/reports/` | All reports are point-in-time snapshots, keep |

---

## Recommended Archive Structure

```
docs/
├── THEORY.md              # NEW: Theory bible
├── TOOL.md                # NEW: Tool bible
├── ARCHITECTURE.md        # Keep - detailed reference
├── FORMAL_PROOF.md        # Keep - mathematical proofs
├── registry/              # Keep all - tracking data
│   ├── HISTORY.md
│   ├── GEMINI_EXTRACTION_*.md
│   └── ...
├── reports/               # Keep all - snapshots
│   └── ...
└── archive/               # NEW: Create this
    ├── THEORY_MAP.md      # Move here
    ├── ATOMS_REFERENCE.md # Move here
    ├── PURPOSE_FIELD.md   # Move here
    ├── COMMANDS.md        # Move here
    ├── QUICKSTART.md      # Move here
    └── GLOSSARY.md        # Move here (after review)
```

---

## Decision Points

### Keep vs Archive

1. **FORMAL_PROOF.md** - Has mathematical proofs with Lean references
   - Decision: Keep (proofs have value even if constants are V1)

2. **ARCHITECTURE.md** - Has detailed diagrams
   - Decision: Keep, but update to reference TOOL.md

3. **GLOSSARY.md** - Has term definitions
   - Decision: Review for accuracy, then decide

### Files to Update (Not Archive)

| File | Update Needed |
|------|---------------|
| `CLAUDE.md` | Add references to THEORY.md and TOOL.md |
| `README.md` | Point to new bibles |

---

## Action Items

1. Create `docs/archive/` directory
2. Move superseded files to archive
3. Update `CLAUDE.md` to reference bibles
4. Update any cross-references in remaining docs
