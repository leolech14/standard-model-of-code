# Context Management Services

**Shared infrastructure services consumed by multiple tools.**

---

## Architecture Principle

```
wave/
├── tools/       ← Things you RUN (executables, scripts)
│   ├── ai/      (analyze.py, etc.)
│   └── refinery/ (scanner, chunker, etc.)
├── services/    ← Things you QUERY (infrastructure, microservices)
│   ├── graph_rag/ (S14 - semantic graph queries)
│   └── [future services]
└── config/
```

**Distinction:**
- `tools/` = Command-line executables, batch processors
- `services/` = Shared infrastructure, always-available APIs

---

## Current Services

### S14: GraphRAG (`graph_rag/`)
**Purpose:** Semantic graph query service over code + documentation + research

**Backend:** Neo4j (localhost:7687)

**Consumers:**
- `tools/ai/analyze.py` (research queries)
- Refinery (knowledge consolidation)
- Dashboard (visualization)
- Future agents (context retrieval)

**Usage:**
```python
from context_management.services.graph_rag import GraphRAGService

service = GraphRAGService()
result = service.query("What validates Purpose Field?")
print(result['answer'])
```

**Data:**
- 5,284 nodes (code + chunks + academic papers)
- Semantic edges (similarity + references)
- Community detection ready (Leiden/Louvain)

**Config:** `graph_rag/schema.yaml`

---

## Future Services (Planned)

### Vector Search
**Purpose:** FAISS/Chroma vector similarity search over embeddings

**Use case:** Fast k-NN retrieval for RAG

---

### Embedding Service
**Purpose:** Shared embedding generation (Gemini, OpenAI, local models)

**Use case:** Consistent embeddings across all tools

---

### Cache Service
**Purpose:** Redis/memory cache for expensive operations

**Use case:** Avoid re-computing embeddings, API calls

---

## Design Principles

1. **Services are stateless** (except Neo4j/Redis backends)
2. **Services expose Python APIs** (not REST, for local dev)
3. **Services handle their own errors** (circuit breakers, retries)
4. **Services are independently testable**
5. **Services document their schemas** (inputs/outputs)

---

## When to Create a Service (vs Tool)

**Create a SERVICE if:**
- ✅ Multiple tools need to query it
- ✅ It manages shared state (database, cache)
- ✅ It's infrastructure (not a one-off script)
- ✅ It has a clear API contract

**Create a TOOL if:**
- ✅ It's a CLI executable
- ✅ It's run on-demand (not always-on)
- ✅ It's specific to one workflow
- ✅ It's a batch processor

---

## Adding a New Service

1. Create `services/your_service/`
2. Add `__init__.py` exposing main API
3. Document schema in `schema.yaml`
4. Update `services/__init__.py`
5. Update this README
6. Add tests in `tests/services/`

---

**Architecture follows purpose.**
**Shape emerges from need.**
