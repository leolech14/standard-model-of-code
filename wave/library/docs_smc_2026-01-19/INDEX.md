# Documentation Index

> **Reading Order Matters.** Follow the hierarchy.

---

## The Hierarchy (Top → Bottom)

```
                    CLAUDE.md
                   (Entry Point)
                        │
            ┌───────────┴───────────┐
            │                       │
        THEORY.md               TOOL.md
       (The Model)            (The Engine)
            │                       │
     ┌──────┼──────┐         ┌──────┼──────┐
     │      │      │         │      │      │
   FORMAL  ATOMS  HISTORY  ARCH   COMMANDS  ERRORS
   PROOF   REF              ITECT
```

---

## Layer 0: Entry Point

| File | Purpose | Read When |
|------|---------|-----------|
| `CLAUDE.md` | Agent instructions | Always first |

---

## Layer 1: Bibles (Canonical Sources)

| File | Purpose | Contains |
|------|---------|----------|
| `docs/THEORY.md` | Standard Model | Axioms, constants, theorems |
| `docs/TOOL.md` | Collider | Commands, pipeline, files |

**Rule:** If it's not in a bible, check if it should be.

---

## Layer 2: Deep Reference

| File | Purpose | Parent |
|------|---------|--------|
| `docs/FORMAL_PROOF.md` | Mathematical proofs | THEORY.md |
| `docs/ARCHITECTURE.md` | Detailed architecture | TOOL.md |
| `docs/ATOMS_REFERENCE.md` | Full atom list (V1) | THEORY.md |
| `docs/MECHANIZED_PROOFS.md` | Lean 4 verification | FORMAL_PROOF.md |

---

## Layer 3: Registry (Tracking)

| File | Purpose |
|------|---------|
| `docs/registry/HISTORY.md` | Project timeline |
| `docs/registry/GEMINI_EXTRACTION_*.md` | Verified facts |
| `docs/registry/DOC_NODES.md` | Document fragmentation |
| `docs/registry/ARCHIVE_MANIFEST.md` | Superseded docs |

---

## Layer 4: Reports (Snapshots)

| File | Purpose |
|------|---------|
| `docs/reports/*.md` | Point-in-time analyses |

---

## Navigation Rules

1. **Start at CLAUDE.md** - Always
2. **Go to bibles for answers** - THEORY.md or TOOL.md
3. **Go deeper only if needed** - Layer 2 for proofs/details
4. **Check registry for facts** - Layer 3 for tracking
5. **Reports are historical** - Don't use for current state

---

## Cross-Reference Convention

Every doc should have at the top:

```markdown
> **Parent:** [THEORY.md](THEORY.md) | **Layer:** 2
```

---

## File → Question Mapping

| Question | File |
|----------|------|
| "What are atoms?" | THEORY.md |
| "How many roles?" | THEORY.md |
| "How to run Collider?" | TOOL.md |
| "What flags exist?" | TOOL.md |
| "Prove completeness" | FORMAL_PROOF.md |
| "When was X added?" | registry/HISTORY.md |
| "What did Gemini find?" | registry/GEMINI_EXTRACTION_*.md |

---

## Update Protocol

When modifying docs:

1. **Check hierarchy** - Am I in the right layer?
2. **Update parent** - Does the bible need updating?
3. **Add cross-ref** - Link to related docs
4. **Timestamp** - Add date if significant change
