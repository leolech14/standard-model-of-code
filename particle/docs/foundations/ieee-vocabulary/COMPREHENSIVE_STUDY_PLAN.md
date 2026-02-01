# Comprehensive Standards Study Plan

> **Goal:** Achieve TOTALITY - complete understanding of prior work in software/systems engineering
> **Corpus:** 6,000+ terms across IEEE, INCOSE, SEBoK
> **Duration:** Systematic study over weeks/months
> **Outcome:** SMC built on complete foundation, not partial knowledge

---

## The Magnitude

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      50 YEARS OF HUMAN KNOWLEDGE                        │
│                   IN SOFTWARE & SYSTEMS ENGINEERING                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   IEEE SEVOCAB: 5,401 terms                                            │
│   ├── 105 requirements terms                                           │
│   ├── 100+ testing terms                                               │
│   ├── 50+ architecture/design terms                                    │
│   ├── 44 system terms                                                  │
│   ├── 60+ process terms                                                │
│   ├── 27 component/module terms                                        │
│   ├── 26 verification/validation terms                                 │
│   └── 5,000+ more specialized terms                                    │
│                                                                         │
│   INCOSE: 21 core definitions                                          │
│   └── Systems thinking foundations                                     │
│                                                                         │
│   SEBoK: 435 terms                                                     │
│   └── Community-curated SE vocabulary                                  │
│                                                                         │
│   Source Standards: 45+                                                │
│   └── ISO, IEEE, PMI, INCOSE consolidated                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Study Strategy

### Phase 1: SMC-Critical Terms (Week 1-2)

Focus on terms that DIRECTLY map to SMC concepts.

#### 1.1 Structural Terms (SMC Atoms)
```bash
sqlite3 SEVOCAB.db "SELECT term FROM terms WHERE
  term_lower LIKE '%module%' OR
  term_lower LIKE '%component%' OR
  term_lower LIKE '%service%' OR
  term_lower LIKE '%class%' OR
  term_lower LIKE '%function%'
ORDER BY term"
```

SMC Mapping:
- module → Atom
- component → Element
- service → Role:Service
- function → Role:Query/Command

#### 1.2 Architectural Terms (SMC LOCUS)
```bash
sqlite3 SEVOCAB.db "SELECT term FROM terms WHERE
  term_lower LIKE '%layer%' OR
  term_lower LIKE '%level%' OR
  term_lower LIKE '%tier%' OR
  term_lower LIKE '%architecture%'
ORDER BY term"
```

SMC Mapping:
- layer → Ring (Ω)
- level → Level (λ)
- tier → Tier (τ)
- architecture → LOCUS framework

#### 1.3 Lifecycle Terms (SMC Lifecycle dimension)
```bash
sqlite3 SEVOCAB.db "SELECT term FROM terms WHERE
  term_lower LIKE '%lifecycle%' OR
  term_lower LIKE '%life cycle%' OR
  term_lower LIKE '%phase%'
ORDER BY term"
```

#### 1.4 Role Terms (SMC 33 Roles)
```bash
sqlite3 SEVOCAB.db "SELECT term FROM terms WHERE
  term_lower LIKE '%factory%' OR
  term_lower LIKE '%repository%' OR
  term_lower LIKE '%handler%' OR
  term_lower LIKE '%controller%' OR
  term_lower LIKE '%validator%' OR
  term_lower LIKE '%service%'
ORDER BY term"
```

---

### Phase 2: Systems Thinking Foundation (Week 3)

INCOSE deep dive - this is where SMC gets theoretical grounding.

#### 2.1 Core Systems Concepts
| INCOSE Term | Study Priority | SMC Connection |
|-------------|----------------|----------------|
| system | CRITICAL | Foundation for everything |
| emergence | CRITICAL | Holon concept |
| physical system | HIGH | CODOME |
| conceptual system | HIGH | CONTEXTOME |
| engineered system | HIGH | PROJECTOME |
| complex system | HIGH | Complexity handling |
| viable system | MEDIUM | Self-sustaining code |
| anticipatory system | MEDIUM | AI-native systems |

#### 2.2 Read Full Documents
- [ ] INCOSE_SE_Definitions.pdf (17 pages)
- [ ] INCOSE SE Handbook Chapter on Definitions
- [ ] SEBoK Part 1: SE Overview

---

### Phase 3: Domain Deep Dives (Week 4-6)

Systematic exploration of each major domain.

#### 3.1 Requirements Domain (105 terms)
Why: SMC Purpose Field maps to requirements
```bash
sqlite3 SEVOCAB.db "SELECT term, definition FROM terms t
  JOIN definitions d ON t.id = d.term_id
  WHERE term_lower LIKE '%require%'
  ORDER BY term" > requirements_study.txt
```

#### 3.2 Testing Domain (100+ terms)
Why: SMC symmetry states need validation concepts
```bash
sqlite3 SEVOCAB.db "SELECT term, definition FROM terms t
  JOIN definitions d ON t.id = d.term_id
  WHERE term_lower LIKE '%test%'
  ORDER BY term" > testing_study.txt
```

#### 3.3 Architecture Domain (50+ terms)
Why: SMC LOCUS is architectural
```bash
sqlite3 SEVOCAB.db "SELECT term, definition FROM terms t
  JOIN definitions d ON t.id = d.term_id
  WHERE term_lower LIKE '%architect%' OR term_lower LIKE '%design%'
  ORDER BY term" > architecture_study.txt
```

#### 3.4 Process Domain (60+ terms)
Why: SMC lifecycle dimension
```bash
sqlite3 SEVOCAB.db "SELECT term, definition FROM terms t
  JOIN definitions d ON t.id = d.term_id
  WHERE term_lower LIKE '%process%'
  ORDER BY term" > process_study.txt
```

---

### Phase 4: Gap Analysis (Week 7)

After studying standards, identify:

1. **SMC terms with NO IEEE equivalent** → Truly novel
2. **SMC terms with IEEE equivalent** → Use IEEE term
3. **SMC terms that EXTEND IEEE** → Document the extension
4. **IEEE terms SMC should add** → Gaps in SMC

#### Gap Analysis Queries
```bash
# What IEEE has that SMC doesn't mention
sqlite3 SEVOCAB.db "SELECT term FROM terms WHERE
  term_lower NOT IN (
    'module', 'component', 'service', 'repository',
    'validation', 'architecture', 'system', 'layer'
    -- add all SMC-referenced terms
  )
  ORDER BY term"

# Common patterns SMC might be missing
sqlite3 SEVOCAB.db "SELECT term FROM terms WHERE
  term_lower LIKE '%pattern%' ORDER BY term"
```

---

### Phase 5: SEBoK Definitions Fetch (Week 8)

Currently we have 435 term NAMES. Need to fetch definitions.

#### Priority Terms for SEBoK Deep Study
1. Abstraction
2. Architecture
3. Behavior
4. Boundary
5. Capability
6. Complexity
7. Component
8. Emergence
9. Encapsulation
10. Enterprise
11. Function
12. Interface
13. Layer
14. Lifecycle
15. Module
16. Pattern
17. Property
18. Requirement
19. Service
20. Stakeholder
21. System

#### Fetch Script
```python
# sebok_fetch.py - fetch definitions from SEBoK wiki
import requests
from bs4 import BeautifulSoup

SEBOK_BASE = "https://sebokwiki.org/wiki/"

def fetch_definition(term):
    url = f"{SEBOK_BASE}{term}_(glossary)"
    # ... parse and extract
```

---

## Study Artifacts to Create

### Per-Domain Study Notes
```
ieee-vocabulary/
├── study/
│   ├── requirements_terms.md      # 105 terms analyzed
│   ├── testing_terms.md           # 100+ terms analyzed
│   ├── architecture_terms.md      # 50+ terms analyzed
│   ├── process_terms.md           # 60+ terms analyzed
│   ├── system_terms.md            # 44 terms analyzed
│   └── component_terms.md         # 27 terms analyzed
```

### Cross-Reference Matrix
```
ieee-vocabulary/
├── SMC_IEEE_CROSSREF.md           # Every SMC term → IEEE mapping
├── IEEE_GAPS.md                   # IEEE terms SMC should consider
└── NOVEL_JUSTIFICATION.md         # Why each novel term is needed
```

---

## Success Criteria

After comprehensive study, you should be able to:

1. **For any SMC term:** Instantly know if IEEE has it
2. **For any IEEE term:** Know if SMC uses, extends, or ignores it
3. **For any concept:** Know the standard definition
4. **For any claim:** Cite the authoritative source

---

## The Payoff

> "SMC doesn't invent vocabulary. SMC extends IEEE vocabulary
> where IEEE lacks concepts for AI-native software engineering."

With comprehensive study:
- SMC gains **legitimacy** (built on standards)
- SMC gains **precision** (uses defined terms)
- SMC gains **adoption** (familiar vocabulary)
- SMC gains **completeness** (no blind spots)

---

## Quick Reference Queries

```bash
# How many terms contain X?
sqlite3 SEVOCAB.db "SELECT COUNT(*) FROM terms WHERE term_lower LIKE '%X%'"

# What does IEEE say about X?
python3 lookup.py "X"

# Compare X across all standards
python3 unified_lookup.py --compare "X"

# Is X novel to SMC?
python3 unified_lookup.py --smc-check "X"

# Export domain for study
sqlite3 SEVOCAB.db "SELECT term, definition FROM terms t
  JOIN definitions d ON t.id = d.term_id
  WHERE term_lower LIKE '%domain%'
  ORDER BY term" > domain_study.txt
```

---

*Comprehensive study transforms SMC from "a theory" to "THE theory that extends IEEE."*
