# Standards Vocabulary Priority Matrix for SMC

> **Purpose:** Learning roadmap for building SMC on proper foundations
> **Date:** 2026-01-31
> **Status:** ACTIVE

---

## The Hierarchy

```
┌─────────────────────────────────────────────────────────────────────┐
│                           SMC THEORY                                │
│               (49 extensions, 20 truly novel concepts)              │
├─────────────────────────────────────────────────────────────────────┤
│                     P1: SYSTEMS ENGINEERING                         │
│                   INCOSE (21 core) + SEBoK (435)                    │
├─────────────────────────────────────────────────────────────────────┤
│                     P0: IEEE SEVOCAB (5,401)                        │
│                    THE CANONICAL FOUNDATION                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Priority Matrix

| Priority | Standard | Terms | SMC Relevance | Status | Action |
|----------|----------|-------|---------------|--------|--------|
| **P0** | IEEE SEVOCAB | 5,401 | FOUNDATION - every term check starts here | **ACQUIRED** | Master it |
| **P1** | INCOSE SE Definitions | 21 | Systems thinking, emergence, holons | **ACQUIRED** | Integrate |
| **P1** | SEBoK Glossary | 435 | Systems engineering complete vocab | **ACQUIRED** (names) | Fetch definitions |
| **P1** | ITIL | ~300 | **Operational Observer (Axiom G1)** | **ACQUIRED** | Study for ops |
| **P2** | OMG (UML/OCL) | ~500 | Formal roles, patterns, constraints | NOT STARTED | Selective study |
| **P2** | SEI CMMI | ~200 | Process maturity (maps to Ring Ω) | NOT STARTED | Cross-reference |
| **P3** | W3C (OWL/RDF) | ~200 | Only if SMC becomes formal ontology | DEFER | Optional |

---

## P0: IEEE SEVOCAB (CRITICAL)

**Status:** ACQUIRED - `SEVOCAB.db`

### Why Critical
- THE authoritative source (5,401 terms)
- Joint ISO/IEC/IEEE standard
- Absorbs PMI, references INCOSE
- Required by DoD, NASA, government

### Key Terms for SMC
| IEEE Term | SMC Connection |
|-----------|----------------|
| module | Maps to SMC Atom concept |
| component | Maps to SMC Element |
| architecture | Foundation for LOCUS |
| validation | Source for Validator role |
| verification | Source for Asserter role |
| layer | Extended to Ring (Ω) |
| level | Extended to Level (λ) |
| traceability | Foundation for Symmetry states |
| repository | IEEE-aligned role |
| service | IEEE-aligned role |
| factory | IEEE-aligned role |

### Usage
```bash
python3 lookup.py "validation"
python3 lookup.py --search "require"
python3 lookup.py --exists "LOCUS"  # Returns: NOT in IEEE (SMC extension)
```

---

## P1: INCOSE (HIGH)

**Status:** ACQUIRED - `INCOSE.json` + `INCOSE_SE_Definitions.pdf`

### Why Important
- Systems thinking vocabulary
- Emergence concept (critical for SMC)
- Transdisciplinary approach
- Physical vs Conceptual systems

### Key Terms for SMC
| INCOSE Term | SMC Connection |
|-------------|----------------|
| **system** | Core definition - parts exhibiting emergent behavior |
| **emergence** | Directly feeds SMC's holon/wave concepts |
| **engineered system** | Maps to PROJECTOME scope |
| **physical system** | Maps to CODOME (executable) |
| **conceptual system** | Maps to CONTEXTOME (knowledge) |
| **complex system** | Informs SMC complexity handling |
| **viable system** | Model for self-sustaining code |
| **anticipatory system** | AI-native systems concept |
| **transdisciplinary** | Justifies SMC's physics metaphor |
| **integrative approach** | Foundation for SMC methodology |

### Critical Insight
INCOSE defines **conceptual system** as "knowledge structure with meaning" - this directly validates SMC's CONTEXTOME partition.

---

## P1: SEBoK (HIGH)

**Status:** ACQUIRED (names only) - `SEBOK_terms.txt`

### Why Important
- 435 systems engineering terms
- Community-curated wiki
- Maintained by INCOSE + IEEE + Stevens
- Updated 2025 (v2.13)

### Terms to Fetch Definitions For
High priority for SMC alignment:
- Abstraction
- Architecture
- Behavior
- Boundary
- Capability
- Complexity
- Component
- Emergence
- Encapsulation
- Enterprise
- Function
- Interface
- Layer
- Lifecycle
- Module
- Pattern
- Property
- Requirement
- Service
- Stakeholder
- System

### Source
https://sebokwiki.org/wiki/Category:Glossary_of_Terms

---

## P2: OMG (MEDIUM)

**Status:** NOT STARTED

### Why Useful
- UML metamodel defines ROLES formally
- OCL provides constraint language
- SBVR formalizes business rules

### Terms to Study
| OMG Term | SMC Connection |
|----------|----------------|
| stereotype | Maps to SMC Role concept |
| constraint | Informs RPBL metrics |
| pattern | Validates role classification |
| classifier | Informs Atom taxonomy |

### Action
Selective extraction when formalizing SMC roles.

---

## P2: SEI CMMI (MEDIUM)

**Status:** NOT STARTED

### Why Useful
- Process maturity levels
- Capability assessment
- Maps to Ring (Ω) concept

### Key Concepts
| CMMI Concept | SMC Connection |
|--------------|----------------|
| Maturity Level 1-5 | Informs Ring dependency depth |
| Process Area | Maps to SMC responsibility dimension |
| Capability Level | Informs lifecycle assessment |

### Action
Cross-reference when refining Ring (Ω) definitions.

---

## P3: W3C (LOW)

**Status:** DEFER

### Why Potentially Useful
- OWL provides formal ontology language
- RDF enables machine-readable vocabulary
- Could formalize SMC as ontology

### When to Use
Only if SMC needs to become a formal, machine-readable ontology for AI consumption.

---

## P1: ITIL (CRITICAL FOR AXIOM G1)

**Status:** ACQUIRED - `ITIL4_glossary.pdf`

### Why Critical
SMC Axiom G1 (Observability Completeness) requires THREE observers:
1. Structural observer (what EXISTS) - Collider
2. **Operational observer (what HAPPENS)** - NEEDS ITIL VOCABULARY
3. Generative observer (what is CREATED) - .agent/

Without ITIL vocabulary, SMC cannot fully implement Axiom G1.

### Key Terms for SMC
| ITIL Term | SMC Connection |
|-----------|----------------|
| **incident** | Runtime failure detection |
| **problem** | Root cause analysis |
| **change** | Change flow (Axiom E2) |
| **release** | Deployment state |
| **service** | IEEE-aligned role |
| **configuration item** | Atom tracking |
| **event** | Operational observer input |
| **monitoring** | Health metrics |

### SMC Theory References
- **Axiom E2:** Four flow substances including CHANGE flow
- **Axiom G1:** Three observers including OPERATIONAL observer
- **Axiom D7:** Dynamic purpose evolution (deployment changes state)

### Why This Was Previously Marked "SKIP"
The implementation (Collider) is currently static-analysis focused. But the THEORY explicitly requires operational understanding. ITIL provides the vocabulary gap.

---

## SMC × Standards Cross-Reference

| SMC Concept | IEEE | INCOSE | SEBoK | OMG | Status |
|-------------|------|--------|-------|-----|--------|
| **LOCUS** | - | - | - | - | NOVEL |
| **CODOME** | source code⚡ | physical system⚡ | - | - | NOVEL (extends) |
| **CONTEXTOME** | documentation⚡ | conceptual system⚡ | - | - | NOVEL (extends) |
| **PROJECTOME** | project⚡ | - | - | - | NOVEL (extends) |
| **Ring (Ω)** | layer⚡ | - | Layer⚡ | - | EXTENDS |
| **Tier (τ)** | tier | - | Abstraction⚡ | - | EXTENDS |
| **Level (λ)** | level⚡ | - | - | - | EXTENDS |
| **RPBL** | - | - | - | - | NOVEL |
| **Holon** | - | - | - | - | NOVEL |
| **PARTICLE** | implementation⚡ | physical system⚡ | - | - | NOVEL (metaphor) |
| **WAVE** | - | conceptual system⚡ | - | - | NOVEL (metaphor) |
| **OBSERVER** | stakeholder⚡ | - | Stakeholder⚡ | - | NOVEL (metaphor) |
| **Purpose Field** | requirement⚡ | - | Requirement⚡ | - | NOVEL |
| **Emergence** | emergence✓ | emergence✓ | Emergence✓ | - | IEEE-ALIGNED |
| **Validator** | validation⚡ | - | - | stereotype⚡ | ROLE FROM NOUN |
| **Repository** | repository✓ | - | - | - | IEEE-ALIGNED |
| **Service** | service✓ | service✓ | Service✓ | - | IEEE-ALIGNED |

✓ = Same concept (use IEEE term)
⚡ = Related concept (SMC extends it)
- = No equivalent (SMC novel)

---

## Unified Lookup Tool

```bash
# Compare across all standards
python3 unified_lookup.py --compare "system"

# Check if SMC term is novel
python3 unified_lookup.py --smc-check "LOCUS"

# Get statistics
python3 unified_lookup.py --stats

# Quick IEEE lookup
python3 unified_lookup.py "validation"
```

---

## Learning Roadmap

### Week 1: Master IEEE SEVOCAB
- [ ] Run `python3 lookup.py --stats` - understand scale
- [ ] Look up all 16 IEEE-aligned SMC roles
- [ ] Verify each SMC "extends" term has IEEE foundation
- [ ] Create IEEE citation for each extended term

### Week 2: Integrate INCOSE
- [ ] Read INCOSE_SE_Definitions.pdf fully
- [ ] Map INCOSE emergence → SMC emergence signals
- [ ] Map INCOSE physical/conceptual → CODOME/CONTEXTOME
- [ ] Add INCOSE citations where applicable

### Week 3: SEBoK Deep Dive
- [ ] Fetch definitions for 21 priority terms
- [ ] Cross-reference with IEEE definitions
- [ ] Identify any SMC gaps

### Week 4: Selective OMG/CMMI
- [ ] Extract UML stereotype definitions
- [ ] Map CMMI maturity to Ring concept
- [ ] Document formal justifications

---

## Files in This Directory

| File | Description |
|------|-------------|
| `SEVOCAB.db` | IEEE vocabulary database (5,401 terms) |
| `SEVOCAB_canonical.json` | One definition per term |
| `INCOSE.json` | INCOSE core definitions (21) |
| `INCOSE_SE_Definitions.pdf` | Full INCOSE document |
| `SEBOK_terms.txt` | SEBoK term names (435) |
| `lookup.py` | IEEE-only lookup tool |
| `unified_lookup.py` | Multi-standard lookup tool |
| `SMC_AUDIT.md` | SMC terms audit against IEEE |
| `SMC_EXTENSIONS.md` | SMC extensions catalog |
| `README.md` | Directory overview |

---

## The Rule

> **Before creating ANY SMC term:**
> 1. Check IEEE SEVOCAB first
> 2. Check INCOSE second
> 3. Check SEBoK third
> 4. If found: USE the standard term
> 5. If not found: Document as SMC extension with justification

---

*SMC builds ON TOP of standards, not beside them.*
