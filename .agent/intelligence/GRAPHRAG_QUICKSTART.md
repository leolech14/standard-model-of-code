# GraphRAG QuickStart - Next 30 Minutes
**Status:** Neo4j running, password setup pending
**Goal:** Get first GraphRAG query working

---

## STEP 1: Set Neo4j Password (2 min)

**Browser opened at:** http://localhost:7474

**Actions:**
1. Login: `neo4j` / `neo4j`
2. Set new password: `elements2026` (or your choice)
3. Keep password - needed for scripts

---

## STEP 2: Import Academic Foundations (2 min)

```bash
# Replace <PASSWORD> with your password from Step 1
.tools_venv/bin/python .agent/tools/import_academic_foundations.py \
  --neo4j-password <PASSWORD> \
  --test
```

**Expected output:**
```
Found 9 analyzed papers

✓ Imported REF-001: Diagonal arguments and Cartesian closed...
✓ Imported REF-040: Free-energy principle...
✓ Imported KOESTLER: The Ghost in the Machine...
... (6 more)

IMPORT COMPLETE
Papers imported: 9
Concepts extracted: 45
Validations created: 45

Testing query: What validates Purpose Field?
  Free-energy principle validates via Free Energy Minimization
```

**Verify in browser:**
```cypher
// Query: Show all papers
MATCH (p:AcademicPaper) RETURN p LIMIT 10

// Query: Show concept network
MATCH (p:AcademicPaper)-[:DEFINES]->(pc:PaperConcept)-[:VALIDATES]->(sc:SmocConcept)
RETURN p, pc, sc LIMIT 25
```

---

## STEP 3: Import Collider Graph (2 min)

```bash
# Update password in script first
# Edit: .agent/tools/collider_to_neo4j.py line 21

.tools_venv/bin/python .agent/tools/collider_to_neo4j.py \
  .collider-full/output_llm-oriented_particle_20260126_050447.json
```

**Expected:**
```
Loading unified_analysis.json...
Loaded: 2540 nodes, 7346 edges

Importing 2540 nodes...
  Progress: 100/2540
  Progress: 200/2540
  ...
✓ Imported 2540 nodes

Importing 7346 edges...
✓ Imported 7346 edges

Linking 2673 chunks...
✓ Linked 2673 chunks

IMPORT COMPLETE
Nodes: 2540 code + 9 papers = 2549
Edges: 7346 code + 2673 chunks + 45 validations = 10064
```

---

## STEP 4: Test First GraphRAG Query (5 min)

**In Neo4j Browser:**

```cypher
// Q: What code implements concepts validated by Friston?
MATCH (p:AcademicPaper {id: 'REF-040'})
MATCH (p)-[:DEFINES]->(pc:PaperConcept)
MATCH (pc)-[:VALIDATES]->(sc:SmocConcept)
MATCH (code:CodeEntity)
WHERE code.purpose CONTAINS sc.name
RETURN code.id, sc.name, p.title
LIMIT 10
```

**Expected result:**
```
code.id                    | sc.name                  | p.title
fabric.py::compute_state   | free_energy_minimization | Free-energy principle
...
```

**This proves:** Code ↔ Theory ↔ Academic Paper linkage works!

---

## STEP 5: Create Simple Query Interface (10 min)

```python
# .agent/tools/graphrag_query.py
from neo4j import GraphDatabase

def query_graphrag(question, password):
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", password))

    # Simple pattern matching for now
    if "validate" in question.lower() and "purpose" in question.lower():
        with driver.session() as session:
            result = session.run("""
                MATCH (c:SmocConcept {name: 'purpose_field_dynamics'})
                MATCH (pc:PaperConcept)-[:VALIDATES]->(c)
                MATCH (p:AcademicPaper)-[:DEFINES]->(pc)
                RETURN p.title, p.author, p.year
            """)

            for record in result:
                print(f"  {record['author']} ({record['year']}): {record['title']}")

    driver.close()

if __name__ == "__main__":
    import sys
    query_graphrag(sys.argv[1], sys.argv[2])
```

**Test:**
```bash
.tools_venv/bin/python .agent/tools/graphrag_query.py \
  "What validates purpose field?" \
  <your-password>
```

---

## STEP 6: Verify Integration (5 min)

**Check all 3 data sources integrated:**

```cypher
// 1. Academic papers (9)
MATCH (p:AcademicPaper) RETURN count(p)

// 2. Code entities (2,540)
MATCH (c:CodeEntity) RETURN count(c)

// 3. Chunks (2,673)
MATCH (ch:Chunk) RETURN count(ch)

// Total nodes
MATCH (n) RETURN count(n)
// Expected: ~5,222 (9 + 2540 + 2673)

// Total relationships
MATCH ()-[r]->() RETURN count(r)
// Expected: ~10,000+ (code deps + chunks + validations)
```

---

## STEP 7: Community Detection (5 min)

```bash
.tools_venv/bin/pip install networkx --quiet

# Run community detection
.tools_venv/bin/python << 'PYEOF'
from neo4j import GraphDatabase
import networkx as nx

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "<PASSWORD>"))

with driver.session() as session:
    # Export graph to NetworkX
    result = session.run("MATCH (n)-[r]->(m) RETURN id(n), id(m)")

    G = nx.DiGraph()
    for record in result:
        G.add_edge(record['id(n)'], record['id(m)'])

    # Louvain community detection
    from networkx.algorithms import community
    communities = community.louvain_communities(G.to_undirected())

    print(f"Found {len(communities)} communities")
    for i, comm in enumerate(communities[:5], 1):
        print(f"  Community {i}: {len(comm)} nodes")

driver.close()
PYEOF
```

---

## SUCCESS CRITERIA (30 min total)

After these 7 steps, you should have:

✅ Neo4j running with data
✅ 9 academic papers imported
✅ 2,540 code entities imported
✅ 2,673 chunks linked
✅ ~10,000 relationships
✅ First GraphRAG query working
✅ Communities detected

**This proves:** GraphRAG foundation is solid!

**Then:** Scale to full implementation (research files, full query engine, dashboard integration)

---

## TROUBLESHOOTING

### "Authentication failed"
- Check: Password set correctly in browser
- Update: Scripts with actual password

### "No data returned"
- Check: Import actually ran
- Verify: `MATCH (n) RETURN count(n)` shows >0

### "Module not found"
- Install: `.tools_venv/bin/pip install neo4j networkx`

---

**READY TO EXECUTE - Waiting for password setup!**

Once password is set:
1. Run import_academic_foundations.py
2. Run collider_to_neo4j.py
3. Test queries
4. Celebrate first GraphRAG success! 🎉
