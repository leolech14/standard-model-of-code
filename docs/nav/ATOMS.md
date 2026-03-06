---
id: nav_atoms
title: "Atoms - The Classification Taxonomy"
category: nav
theory_refs: [MODEL.md §2, L1_DEFINITIONS.md §3]
tier_count: 3
atom_count: 3610
---

# ATOMS - The Classification Taxonomy

> What TYPE of code element is this? The atom is the answer.

<!-- T1:END -->

---

## What's an Atom?

An atom is the finest-grained **structural type** assigned to a code element. It answers the WHAT dimension: "What kind of thing is this?"

Every node in the dependency graph gets exactly one atom. This is a **total function**:
```
σ: Nodes → Atoms    (no node is unclassified)
```

---

## The 3 Tiers

| Tier | Count | Coverage | What It Captures |
|------|-------|----------|------------------|
| **Tier 0** (Core AST) | 42 | 100% of any codebase | Language-universal structures |
| **Tier 1** (Stdlib) | 21 | 20-40% of typical codebases | Language-specific patterns |
| **Tier 2** (Ecosystem) | 3,531 | Variable | Framework/library-specific types |

**Total taxonomy:** 3,610 atoms. **Implemented in Collider:** 94.

---

## Tier 0: The Universal 42

These exist in every programming language:

| Category | Examples |
|----------|----------|
| **Declarations** | Function, Class, Variable, Constant, Interface |
| **Expressions** | Call, Assignment, BinaryOp, UnaryOp |
| **Control Flow** | If, For, While, Switch, Try |
| **Structural** | Import, Export, Module, Block |
| **Data** | Parameter, Property, TypeAlias, Enum |

---

<!-- T2:END -->

## Tier 1: Language Patterns

Present in some but not all languages:

| Atom | Languages |
|------|-----------|
| Decorator | Python, TypeScript |
| Generator | Python, JavaScript |
| Comprehension | Python |
| Extension | Swift, Kotlin |
| Protocol | Swift, Elixir |
| Trait | Rust, PHP |

---

## Tier 2: Framework Atoms

Detected via decorators, inheritance, and naming:

| Atom | Framework | Detection Signal |
|------|-----------|-----------------|
| ReactComponent | React | `extends Component`, JSX return |
| DjangoView | Django | `@api_view`, inherits `View` |
| FastAPIRoute | FastAPI | `@app.get()`, `@router.post()` |
| ExpressMiddleware | Express | `(req, res, next)` signature |
| SQLAlchemyModel | SQLAlchemy | inherits `Base`, `__tablename__` |

---

## The Base 14 (atoms.json)

The irreducible base kinds that every atom maps back to:

```
Function, Class, Variable, Constant, Interface, Type,
Enum, Module, Import, Export, Statement, Expression,
Block, Decorator
```

Every Tier 0/1/2 atom is ultimately a specialization of one of these 14.

---

## Detection: No AI Required

Atom assignment uses three deterministic signals:

1. **AST node type** → Tree-sitter parse → Tier 0 atom
2. **Decorators/annotations** → Framework pattern match → Tier 2 atom
3. **Inheritance chain** → Base class lookup → Tier 2 atom

Zero unknowns across 91 tested repositories, 270,000+ nodes.

---

*Source: MODEL.md (§2), L1_DEFINITIONS.md (§3)*
*See also: [ROLES.md](ROLES.md) for the WHY dimension, [../essentials/CLASSIFICATION.md](../essentials/CLASSIFICATION.md) for full reference*
