# Canonical Data Directory

> **Single source of truth** for all Standard Model data.

## Structure

```
canonical/
├── fixed/      # 🔒 IMMUTABLE - Theory axioms
└── learned/    # 📈 MUTABLE - Edit here when learning
```

## Rules

### fixed/ - NEVER EDIT
These files define the theory's coordinate system. Changing them breaks existing classifications.

| File | Contains | Count |
|------|----------|-------|
| `atoms.json` | 167 atom taxonomy | Fixed |
| `dimensions.json` | 8 semantic dimensions | Fixed |
| `roles.json` | 27 canonical roles | Fixed |

### learned/ - EDIT HERE
These files grow with learning. This is the ONLY place to add new patterns.

| File | Contains | Dynamic |
|------|----------|---------|
| `patterns.json` | Prefix/suffix/path patterns | Yes |
| `ledger.md` | Changelog of what was added | Yes |

## How to Add a New Pattern

1. Edit `canonical/learned/patterns.json`
2. Add entry to `canonical/learned/ledger.md`
3. Run tests to verify

## Loading

Code loads from these files:
- `core/registry/pattern_repository.py` → `learned/patterns.json`
- `core/atom_classifier.py` → `fixed/atoms.json`
