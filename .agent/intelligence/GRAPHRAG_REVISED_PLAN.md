# GraphRAG Revised Plan - Critical Optimization
**Date:** 2026-01-27
**Discovery:** Collider output is ALREADY graph format!
**Impact:** Reduces effort from 24h → 12h

---

## ORIGINAL ESTIMATE (WRONG)

**Assumed:**
- Need to extract entities from code (2,673 chunks)
- ~10-20M tokens
- Cost: $1,150
- Time: 24 hours

**Reality:**
- Collider ALREADY has 2,540 nodes + 7,346 edges
- Import directly (0 tokens!)
- Cost: $0 for code
- Time: 30 minutes import

---

## REVISED TOKEN ESTIMATE

### What Actually Needs Extraction:

**1. Semantic Chunks (Enhance, not extract structure):**
- 2,673 chunks
- Extract: Concepts, patterns, algorithms FROM CONTENT
- NOT structure (Collider has that)
- Tokens: 2,673 × 200 = ~534K tokens

**2. Research Files:**
- 1,068 files
- Extract: Key findings, theories mentioned, citations
- Tokens: 1,068 × 500 = ~534K tokens

**3. Theory Documents:**
- 281 theories
- Extract: Axioms, formulas, relationships
- Tokens: 281 × 300 = ~84K tokens

**TOTAL ACTUAL:** 1.15M tokens (NOT 10-20M!)

**Cost:** ~$115 via Batch API (was $1,150!)
**Savings:** 90% reduction!

---

## REVISED TASK BREAKDOWN

### PHASE 1: Import Existing Structure (2 hours)

**Task A: Import Collider Graph**
```python
# collider_to_neo4j.py
import json
from neo4j import GraphDatabase

# Load Collider output
with open('.collider-full/output_llm*.json') as f:
    data = json.load(f)

# Create nodes
for node in data['nodes']:
    neo4j.create_node(
        labels=['CodeEntity'],
        properties={
            'id': node['id'],
            'file': node['file_path'],
            'line': node['start_line'],
            'role': node.get('semantic_role'),
            'purpose': node.get('purpose')  # Purpose Field!
        }
    )

# Create edges
for edge in data['edges']:
    neo4j.create_edge(
        source=edge['source'],
        target=edge['target'],
        type=edge['edge_type']
    )
```
**Time:** 30 minutes
**Result:** 2,540 nodes + 7,346 edges in Neo4j

---

**Task B: Import Chunks Metadata**
```python
# Link chunks to code nodes
for chunk in chunks:
    # Find corresponding code node
    code_node = find_node_by_location(chunk['source_file'], chunk['start_line'])

    # Create chunk node
    chunk_node = create_chunk_node(chunk)

    # Link: CodeEntity -[HAS_CHUNK]-> Chunk
    neo4j.create_edge(code_node, chunk_node, 'HAS_CHUNK')
```
**Time:** 30 minutes
**Result:** 2,673 chunk nodes linked to code

---

**Task C: Import LOL Entities**
```python
# Import 2,469 entities from LOL
import pandas as pd

lol = pd.read_csv('.agent/intelligence/LOL_UNIFIED.csv')

for entity in lol.itertuples():
    neo4j.create_node(
        labels=['Entity'],
        properties={
            'path': entity.path,
            'domain': entity.domain,
            'category': entity.category,
            'role': entity.role
        }
    )
```
**Time:** 30 minutes
**Result:** 2,469 entity nodes

---

**Task D: Compute Similarity Edges**
```python
# For chunks: compute cosine similarity
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode([c['content'] for c in chunks])

# Create edges where similarity >0.75
for i, j in pairs:
    sim = cosine_similarity(embeddings[i], embeddings[j])
    if sim > 0.75:
        neo4j.create_edge(chunks[i], chunks[j], 'SIMILAR_TO', weight=sim)
```
**Time:** 30 minutes
**Result:** Similarity edges added

**PHASE 1 TOTAL:** 2 hours (not 4!)

---

### PHASE 2: Entity Extraction (Batch API) - 26 hours

**Task E: Extract from Chunks** (Batch)
- Submit: 2,673 chunks to Gemini Batch API
- Prompt: "Extract: theories, concepts, algorithms, patterns"
- Cost: $53.40 (534K tokens × $0.10/M × 0.5)
- Wait: 24 hours
- **Calendar:** 1h setup + 24h wait

**Task F: Extract from Research** (Batch)
- Submit: 1,068 research files
- Prompt: "Extract: key findings, theories, citations"
- Cost: $53.40 (534K tokens × $0.10/M × 0.5)
- Wait: 24 hours (parallel with Task E)
- **Calendar:** 1h setup + 24h wait (same batch)

**Task G: Extract from Theories** (Manual + Semi-Auto)
- Scan: Theory .md files
- Extract: Axioms, theorems, laws
- Cost: $8.40 (84K tokens × $0.10/M × 0.5)
- Wait: Included in same batch
- **Calendar:** Included in 24h

**PHASE 2 TOTAL:** 2h human + 24h wait = 26h calendar

---

### PHASE 3: Graph Enrichment (3 hours)

**Task H: Load Extracted Entities**
- Parse: Batch API outputs
- Create: Concept, Theory, Algorithm nodes
- Link: To source chunks/research/theories
- **Time:** 1 hour

**Task I: Create Cross-Modal Edges**
- Link: Code nodes → Concept nodes (IMPLEMENTS)
- Link: Theory nodes → Concept nodes (DESCRIBES)
- Link: Research nodes → Theory nodes (VALIDATES)
- **Time:** 1 hour

**Task J: Community Detection**
- Run: Louvain algorithm
- Identify: Theory clusters, research themes
- Label: Communities
- **Time:** 30 minutes

**Task K: Compute Metrics**
- Centrality: Betweenness, PageRank
- Clustering: Coefficient
- Path analysis: Shortest paths
- **Time:** 30 minutes

**PHASE 3 TOTAL:** 3 hours

---

### PHASE 4: Query Interface (3 hours)

**Task L: GraphRAG Python Integration**
```bash
pip install neo4j-graphrag
```
```python
from neo4j_graphrag import GraphRAG

graphrag = GraphRAG(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="<password>"
)

result = graphrag.query("What theories validate Communication Fabric?")
```
**Time:** 2 hours (setup + test)

**Task M: CLI Integration**
```bash
# Add to pe script:
graphrag)
    shift
    python3 "$TOOLS/graphrag_query.py" "$@"
    ;;
```
**Time:** 1 hour

**PHASE 4 TOTAL:** 3 hours

---

### PHASE 5: Validation (2 hours)

**Task N: Accuracy Testing**
- Test: 20 queries
- Baseline: ./pe refinery search
- GraphRAG: ./pe graphrag query
- Measure: Precision, recall, latency
- **Time:** 2 hours

**PHASE 5 TOTAL:** 2 hours

---

## NEW TOTAL EFFORT

**Original:** 27 hours
**Revised:** 10h human + 24h wait = **34h calendar, 10h active**

**Cost:**
- Original: $1,150
- Revised: $115 (90% savings!)

**Why:**
- Collider graph already exists (0 tokens)
- Only extract semantic layer (not structure)
- Batch API (50% discount)

---

## EXECUTION SEQUENCE (This Week)

**Monday (Today):**
- ✅ Task #1: Install Neo4j (DONE)
- ✅ Task #2: Validate data (DONE)
- Phase 1: Import existing (2h)

**Tuesday:**
- Phase 2: Submit batch extraction (2h active)
- Start: 24h wait

**Wednesday (Waiting):**
- Batch processing (background)
- Work on: Paper outline or Cloud R0

**Thursday:**
- Phase 3: Load entities + enrich (3h)
- Phase 4: Query interface (3h)

**Friday:**
- Phase 5: Validation (2h)
- Decision: Results good enough?

**TOTAL:** 5 days calendar, 12h active work

---

🎉 **OPTIMIZED: 90% cost reduction, 50% time reduction!**

**Continuing with Phase 1 now...**

