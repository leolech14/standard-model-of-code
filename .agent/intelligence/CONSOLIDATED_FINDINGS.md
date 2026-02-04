# Consolidated Findings - GraphRAG Implementation
**Session:** 2026-01-27
**Research:** 120+ academic sources (3 Perplexity deep dives)
**Status:** Ready for repository-aligned implementation

---

## I. WHAT WE VALIDATED

### Research Finding 1: GraphRAG Accuracy
**Source:** Perplexity (60+ sources, empirical data)
- Vector-only RAG: 16.7% accuracy
- GraphRAG: 56.2% accuracy
- **Gain:** 3.4× improvement
- Medical domain: 94.2% (Cedars-Sinai) vs 49.9% baseline

### Research Finding 2: Multi-Hop Reasoning
**Source:** Perplexity advanced patterns
- Optimal depth: 2-4 hops (bidirectional sampling)
- Neighbor limiting: 50-100 per node prevents explosion
- Shortest-path pruning: Reduces 10K nodes → 200-500
- Performance: <2s for complex queries

### Research Finding 3: Hybrid Retrieval
**Source:** Production case studies
- Best: Vector + Graph + BM25 combined
- Vector: Semantic matching
- Graph: Relationship reasoning
- BM25: Keyword precision

### Research Finding 4: Community Detection
**Source:** Algorithmic analysis
- Leiden > Louvain (better connected communities)
- Hierarchical: 2-3 levels optimal
- Microsoft GraphRAG: Uses Leiden with hierarchical summaries
- Modularity >0.4 = good separation

### Research Finding 5: Context Management
**Source:** Token optimization research
- Query-driven subgraph: Extract only relevant 2-4 hop neighborhood
- Token reduction: 77% via dynamic community selection
- Context window: 10K-50K tokens typical (not full graph!)
- Hierarchical summaries: Enable global reasoning

---

## II. O QUE CONSTRUÍMOS

### Implementation 1: Neo4j Graph
**Status:** OPERATIONAL ✅
- 5,284 nodes (2,539 code + 2,657 chunks + 18 papers + concepts)
- 11,766 edges (code deps + chunk links + validations)
- Clean: Duplicates removed
- Query: Basic Cypher working

### Implementation 2: Import Scripts
- `collider_to_neo4j.py` - Imports code graph (2,540 nodes)
- `import_academic_foundations.py` - Imports theory papers (9 analyzed)
- Both: TESTED and WORKING ✅

### Implementation 3: Query Interface
- `graphrag_query.py` - Pattern-based query routing
- Patterns: Validation, Implementation, Research, Relationships
- Status: Basic version working, needs enhancement

### Implementation 4: Graph Data
**From Collider:** 2,540 code entities with Purpose Field π
**From Refinery:** 2,673 chunks with embeddings (not in Neo4j yet)
**From Academic Library:** 9 papers with concept mappings

---

## III. WHAT'S READY TO IMPLEMENT (From Research)

### Code Pattern 1: Vector Index
**Complete Cypher + Python provided:**
- Create index: 384-dim cosine similarity
- Store embeddings: Batch update chunks
- Hybrid query: Vector + graph combined
- Performance: <100ms on 5K nodes

### Code Pattern 2: Leiden Detection
**Complete Python provided:**
- Library: leidenalg + igraph
- Hierarchical: 2-3 levels
- Parameters: resolution=1.0, seed=42
- Integration: Store communities in Neo4j

### Code Pattern 3: Subgraph Extraction
**Complete algorithm provided:**
- Query-driven: Start from vector search seeds
- Expand: 2-4 hops with neighbor limits
- Prune: Shortest-path only
- Convert: To LLM-readable format

### Code Pattern 4: ACI Router
**Complete router provided:**
- Intent classification
- Tier selection (INSTANT/RAG/LONG_CONTEXT/PERPLEXITY/GRAPHRAG)
- Fallback chain
- Performance monitoring

### Code Pattern 5: Incremental Updates
**Complete pipeline provided:**
- Delta detection from file hashes
- Extract only changed documents
- Update graph incrementally
- Recompute affected communities

---

## IV. INTEGRATION POINTS (Repository Truth)

### Integration 1: With Collider
**Collider provides:**
- unified_analysis.json (2,540 nodes ready-to-import)
- Purpose Field π (already computed)
- Graph structure (nodes + edges)

**GraphRAG enhances:**
- Validates purpose against academic theory
- Enriches Brain Download with theoretical grounding
- Generates research tasks for gaps

### Integration 2: With Refinery
**Refinery provides:**
- 2,673 semantic chunks
- Embeddings (all-MiniLM-L6-v2, 384-dim)
- Query interface (text search)

**GraphRAG extends:**
- Stores embeddings in Neo4j vector index
- Enables semantic + graph hybrid queries
- Replaces text search with graph traversal

### Integration 3: With ACI (analyze.py)
**ACI provides:**
- 4 existing tiers (INSTANT, RAG, LONG_CONTEXT, PERPLEXITY)
- Tier routing logic
- Gemini integration

**GraphRAG adds:**
- Tier 5: Graph-structured reasoning
- Intent classification for routing
- Fallback to RAG if graph empty

### Integration 4: With Communication Fabric
**Fabric provides:**
- Health metrics (F, MI, N, SNR, R, ΔH)
- Stability margin tracking
- Time-series history

**GraphRAG uses:**
- Queries health trends from graph
- Correlates code changes with stability
- Generates health insights

### Integration 5: With Automation (Wire)
**Wire provides:**
- 9-stage pipeline
- Delta detection
- Convergence checking

**GraphRAG hooks:**
- After REFINERY stages: Extract entities from changed chunks
- Update Neo4j incrementally
- Recompute communities if significant changes

---

## V. REPOSITORY ALIGNMENT QUESTIONS FOR GEMINI

1. **Where does GraphRAG fit in subsystem hierarchy?**
   - Is it S3 (AI Consumer) extension?
   - New S14 (Knowledge Graph)?
   - Part of Refinery (S??)?

2. **Integration with existing butlers?**
   - GraphRAG as 27th butler?
   - Or enhancement to existing butlers?

3. **Git truth principle:**
   - Graph state in git (export to JSON)?
   - Or graph is ephemeral (rebuild from sources)?

4. **Conventional commits:**
   - feat(graphrag): ... when adding features?
   - Where to commit graph schema definitions?

5. **analyze.py integration:**
   - Add --graph-query flag?
   - New tier in ACI routing?
   - How to combine with existing --set options?

6. **Performance vs accuracy trade-offs:**
   - When to use GraphRAG (complex) vs text search (fast)?
   - SLO for GraphRAG queries (<2s)?

7. **Maintenance:**
   - Who owns graph health?
   - Graph backup strategy?
   - Schema evolution process?

---

## VI. IMPLEMENTATION SEQUENCE (Aligned)

### Phase 1: Foundation (Complete ✅)
1. Neo4j installed
2. Basic graph imported
3. Query interface working
4. Research complete

### Phase 2: Enhanced GraphRAG (Next - 8h)
1. Add vector index to Neo4j (1h)
2. Implement Leiden detection (2h)
3. Create ACI Tier 5 router (2h)
4. Implement subgraph extraction (2h)
5. Test hybrid retrieval (1h)

### Phase 3: Integration (After - 6h)
1. Hook into wire.py (incremental updates) (2h)
2. Enhance Collider brain_download.py (2h)
3. Add to dashboard API (1h)
4. Documentation (1h)

### Phase 4: Validation (After - 4h)
1. Accuracy tests (50 queries) (2h)
2. Performance benchmarks (1h)
3. Integration tests (1h)

**Total remaining:** 18 hours

---

## VII. READY FOR GEMINI QUERY

**Question to ask:**
"How to implement GraphRAG (Neo4j + vector index + Leiden + hybrid retrieval) aligned with PROJECT_elements architecture, subsystem hierarchy, Git truth principle, and existing butler/ACI/wire infrastructure?"

**Context needed:**
- SUBSYSTEM_INTEGRATION.md (subsystem map)
- AGENT_KERNEL.md (principles)
- analyze.py structure (ACI tiers)
- wire.py pipeline (integration point)

**Goal:**
- Repository-aligned implementation plan
- Proper subsystem placement
- Git/commit strategy
- Butler integration pattern

---

**READY TO QUERY GEMINI WITH PROPER CONTEXT?**
