# READY TO EXECUTE - GraphRAG Phase 1
**Status:** Neo4j installed, scripts ready, waiting for password
**Time to first query:** 10 minutes after password set

---

## SCRIPTS PRONTOS

### 1. Academic Foundations Import ✅
**File:** `.agent/tools/import_academic_foundations.py`
**Input:** 9 analyzed papers (REF-001, REF-040, KOESTLER, etc.)
**Output:** 9 papers + 45 concepts + 45 validations
**Command:**
```bash
.tools_venv/bin/python .agent/tools/import_academic_foundations.py \
  --neo4j-password elements2026 --test
```

### 2. Collider Graph Import ✅
**File:** `.agent/tools/collider_to_neo4j.py`
**Input:** unified_analysis.json (2,540 nodes, 7,346 edges)
**Output:** Complete code graph in Neo4j
**Command:**
```bash
.tools_venv/bin/python .agent/tools/collider_to_neo4j.py \
  .collider-full/output_llm-oriented_particle_20260126_050447.json
```

### 3. Simple Query Test ✅
**Cypher query in browser:**
```cypher
// What validates Purpose Field?
MATCH (c:SmocConcept {name: 'purpose_field_dynamics'})
MATCH (pc)-[:VALIDATES]->(c)
MATCH (p)-[:DEFINES]->(pc)
RETURN p.title, p.author
```

---

## DATA INTEGRATION MAP

```
NEO4J DATABASE
│
├─ AcademicPaper (9 nodes)
│   ├─ REF-001 (Lawvere) ────┐
│   ├─ REF-040 (Friston) ────┤
│   └─ KOESTLER (Holons) ────┤
│                             ↓
├─ PaperConcept (45 nodes) ──┤
│   ├─ "Free Energy Min" ────┤
│   ├─ "Cartesian Closed" ───┤
│   └─ "Holarchy" ────────────┤
│                             ↓
├─ SmocConcept (45 nodes) ───┤
│   ├─ purpose_field_dynamics ← VALIDATES
│   ├─ codome_contextome ─────← VALIDATES
│   └─ scales_16_level ───────← VALIDATES
│
├─ CodeEntity (2,540 nodes from Collider)
│   ├─ fabric.py::compute_state
│   ├─ autopilot.py::run
│   └─ [2,538 more...]
│       ↓
├─ Chunk (2,673 nodes from Refinery)
│   └─ Linked via HAS_CHUNK edges
│
└─ Relationships (~10,000)
    ├─ DEFINES (paper → concept)
    ├─ VALIDATES (paper concept → SMoC concept)
    ├─ HAS_CHUNK (code → chunk)
    ├─ CALLS (code → code)
    ├─ IMPORTS (code → code)
    └─ SIMILAR_TO (chunk → chunk)
```

---

## EXPECTED QUERIES (After Import)

### Q1: Theory Validation
```cypher
// What papers validate CODOME ⊔ CONTEXTOME partition?
MATCH (c:SmocConcept {name: 'codome_contextome_partition'})
MATCH (pc)-[:VALIDATES]->(c)
MATCH (p)-[:DEFINES]->(pc)
RETURN p.title, p.author
```
**Expected:** Lawvere's Fixed Point Theorem

### Q2: Code → Theory Traceability
```cypher
// What theory explains fabric.py?
MATCH (code:CodeEntity)
WHERE code.file_path CONTAINS 'fabric.py'
MATCH (code)-[:IMPLEMENTS]->(concept:SmocConcept)
MATCH (pc)-[:VALIDATES]->(concept)
MATCH (p)-[:DEFINES]->(pc)
RETURN code.id, concept.name, p.title
```
**Expected:** fabric.py implements concepts validated by Friston (FEP)

### Q3: Research Gaps
```cypher
// SMoC concepts WITHOUT academic validation
MATCH (c:SmocConcept)
WHERE NOT (c)<-[:VALIDATES]-()
RETURN c.name
```
**Expected:** Concepts needing research (E(S|Φ), Peri-Purpose Resonance, etc.)

---

## INTEGRATION WITH EXISTING SYSTEMS

### Update collider_to_neo4j.py (Line 21):
```python
NEO4J_PASSWORD = "elements2026"  # Changed from "neo4j"
```

### Add to ./pe script:
```bash
graphrag)
    shift
    case "${1:-help}" in
        query)
            shift
            .tools_venv/bin/python .agent/tools/graphrag_query.py "$@"
            ;;
        status)
            cypher-shell -u neo4j -p elements2026 \
              "MATCH (n) RETURN labels(n)[0] as type, count(n) as count;"
            ;;
        *)
            echo "./pe graphrag query 'question'"
            echo "./pe graphrag status"
            ;;
    esac
    ;;
```

---

## AFTER SUCCESSFUL IMPORT

**You'll have:**
- 5,222 nodes total
- ~10,000 relationships
- 3 data modalities integrated (papers, code, chunks)
- Working GraphRAG queries

**Test command:**
```bash
./pe graphrag query "What validates Purpose Field?"
```

**Expected response:**
```
Friston (2010): The free-energy principle
→ Provides mathematical foundation for dπ/dt = -∇Incoherence
```

---

🚀 **SCRIPTS READY - EXECUTE APÓS PASSWORD SETUP!**

**Browser:** http://localhost:7474 (login: neo4j/neo4j, set new password)
**Then:** Run import scripts
**Result:** First GraphRAG queries em 10 minutos!
