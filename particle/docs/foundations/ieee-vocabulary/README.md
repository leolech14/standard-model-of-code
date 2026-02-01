# IEEE SEVOCAB - Industry Terminology Foundation

> **Status:** FOUNDATIONAL
> **Source:** IEEE Computer Society SEVOCAB (https://pascal.computer.org/sev_display/)
> **Terms:** 5,401
> **Last Updated:** 2026-01-31

---

## Why This Exists

**SMC builds ON TOP of IEEE vocabulary, not beside it.**

```
┌─────────────────────────────────────────┐
│           SMC EXTENSIONS                │  ← What we ADD
│   (LOCUS, Purpose Field, Atoms, etc.)   │
├─────────────────────────────────────────┤
│         IEEE SEVOCAB (5,401 terms)      │  ← FOUNDATION
│   (Industry standard terminology)       │
└─────────────────────────────────────────┘
```

Before inventing a term, **check if IEEE already defines it**.
If IEEE has it → USE IT.
If IEEE lacks it → EXTEND with clear justification.

---

## Files

| File | Description |
|------|-------------|
| `SEVOCAB.db` | SQLite database (queryable) |
| `SEVOCAB_canonical.json` | JSON (one definition per term) |
| `lookup.py` | CLI tool for lookups |
| `SMC_EXTENSIONS.md` | What SMC adds beyond IEEE |

---

## Usage

### Quick Lookup
```bash
python3 lookup.py "validation"
python3 lookup.py "repository"
python3 lookup.py "architecture"
```

### Search
```bash
python3 lookup.py --search "test"
python3 lookup.py --search "require"
```

### Check if term exists
```bash
python3 lookup.py --exists "validator"  # False - SMC extension
python3 lookup.py --exists "validation" # True - IEEE term
```

### Programmatic
```python
from lookup import ieee_lookup, ieee_exists

defn = ieee_lookup("module")
print(defn)  # "program unit that is discrete and identifiable..."

if not ieee_exists("LOCUS"):
    print("LOCUS is an SMC extension, not IEEE standard")
```

---

## The Rule

### When writing SMC documentation:

1. **Use IEEE term if it exists**
   - "validation" not "Validator" for the concept
   - "module" not "MODULE"
   - "repository" as-is

2. **Capitalize only SMC extensions**
   - `LOCUS` - SMC coordinate system (not in IEEE)
   - `RPBL` - SMC metrics (not in IEEE)
   - `CODOME` - SMC partition (not in IEEE)

3. **Document the extension**
   - Add to `SMC_EXTENSIONS.md`
   - Explain why IEEE term doesn't suffice

---

## Database Schema

```sql
-- terms table
CREATE TABLE terms (
    id INTEGER PRIMARY KEY,
    term TEXT NOT NULL,
    term_lower TEXT NOT NULL  -- for case-insensitive lookup
);

-- definitions table
CREATE TABLE definitions (
    id INTEGER PRIMARY KEY,
    term_id INTEGER,
    def_num INTEGER,          -- 1, 2, 3... (usually same meaning, different sources)
    definition TEXT,
    source TEXT,              -- e.g., "ISO/IEC/IEEE 12207:2026"
    FOREIGN KEY (term_id) REFERENCES terms(id)
);

-- Index for fast lookup
CREATE INDEX idx_term_lower ON terms(term_lower);
```

---

## Statistics

| Metric | Value |
|--------|-------|
| Total terms | 5,401 |
| Unique meanings | 5,401 |
| Source standards | ~45 |
| Coverage | Software + Systems Engineering |

### Source Standards Include:
- ISO/IEC/IEEE 12207 (Software lifecycle)
- ISO/IEC/IEEE 15288 (System lifecycle)
- ISO/IEC/IEEE 24765 (Vocabulary)
- ISO/IEC/IEEE 29119 (Testing)
- IEEE 828 (Configuration Management)
- IEEE 1012 (V&V)
- PMI PMBOK (Project Management)
- INCOSE Handbook (Systems Engineering)

---

## Maintenance

### Updating SEVOCAB

The SEVOCAB database is updated periodically by IEEE. To refresh:

```bash
# Download latest from IEEE
curl -sL "https://pascal.computer.org/sev_display/printCatalog.action" -o SEVOCAB_latest.pdf

# Extract and parse (requires pdftotext)
pdftotext -layout SEVOCAB_latest.pdf SEVOCAB_latest.txt

# Run parser (in wave/tools/)
python3 parse_sevocab.py SEVOCAB_latest.txt
```

---

## See Also

- `SMC_EXTENSIONS.md` - Terms SMC adds beyond IEEE
- `../theory/L1_DEFINITIONS.md` - SMC formal definitions
- `../theory/CODE_ZOO.md` - SMC taxonomy (builds on IEEE)

---

*This is Layer 0 of SMC theory. Everything else builds on these 5,401 industry-standard terms.*
