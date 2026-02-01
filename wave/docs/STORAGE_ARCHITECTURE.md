# 🗄️ STORAGE ARCHITECTURE
**How Collider Outputs Are Stored Across Three Layers**
**Generated**: 2025-12-27

---

## 🎯 EXECUTIVE SUMMARY

The Collider's output architecture operates across **three distinct but interconnected layers**:

1. **Physical Layer** - Files on disk (JSON, CSV, databases)
2. **Virtual Layer** - In-memory data structures (graphs, indices, caches)
3. **Semantic Layer** - Meaning and relationships (8D + 8L queryable space)

Each layer serves different purposes and enables different use cases.

---

## 📊 LAYER 1: PHYSICAL STORAGE

### Primary Output Format: JSON

**Location**: `collider_output/unified_analysis.json`

**Schema**: v3.0.0

**Structure**:
```json
{
  "metadata": {
    "version": "3.0.0",
    "timestamp": "2025-12-27T...",
    "target": "src/core",
    "analysis_time_ms": 1923,
    "node_count": 571,
    "edge_count": 3218
  },
  "nodes": [...],
  "edges": [...],
  "statistics": {...}
}
```

### Node Storage Structure

**Each node contains ~100+ fields across 8 dimensions + 8 lenses:**

```json
{
  "id": "file.py:function_name",
  "name": "function_name",
  "kind": "function",
  "file_path": "src/core/file.py",
  "start_line": 42,
  "end_line": 58,

  // Role Classification
  "role": "Query",
  "role_confidence": 0.82,

  // 8 Dimensions (D1-D8)
  "dimensions": {
    "D1_WHAT": "QueryFunction",
    "D2_LAYER": "Domain",
    "D3_ROLE": "Query",
    "D4_BOUNDARY": "Internal",
    "D5_STATE": "Stateless",
    "D6_EFFECT": "Pure",
    "D7_LIFECYCLE": "Use",
    "D8_TRUST": 82
  },

  // 8 Lenses (R1-R8)
  "lenses": {
    "R1_IDENTITY": {
      "name": "function_name",
      "qualified_name": "file:42:function_name",
      "semantic_id": "file.py:function_name",
      "unique_reference": "file.py:42"
    },
    "R2_ONTOLOGY": {
      "entity_type": "function",
      "parameter_count": 2,
      "lines_of_code": 16,
      "complexity": 5
    },
    "R3_CLASSIFICATION": {
      "role": "Query",
      "atom_type": "QueryFunction",
      "confidence": 82,
      "quality": "good"
    },
    "R4_COMPOSITION": {
      "parent": "ParentClass",
      "children": [],
      "nesting_depth": 1
    },
    "R5_RELATIONSHIPS": {
      "in_degree": 3,
      "out_degree": 2,
      "calls": ["helper_a", "helper_b"],
      "called_by": ["controller_x", "service_y"]
    },
    "R6_TRANSFORMATION": {
      "input_types": ["User", "int"],
      "output_type": "QueryResult",
      "is_pure": true,
      "effect_type": "Pure"
    },
    "R7_SEMANTICS": {
      "purpose": "Retrieves user data by ID",
      "intent": "data_retrieval",
      "business_domain": "user_management"
    },
    "R8_EPISTEMOLOGY": {
      "confidence": 82,
      "evidence": {
        "has_docstring": true,
        "has_type_hints": true,
        "evidence_strength": "strong"
      },
      "uncertainties": [],
      "requires_review": false
    }
  }
}
```

### Edge Storage Structure

**Each edge represents a relationship:**

```json
{
  "id": "edge_12345",
  "source": "file1.py:ClassA",
  "target": "file1.py:method_b",
  "type": "contains",
  "metadata": {
    "line_number": 42,
    "explicit": true
  }
}
```

**Edge Types**:
- `contains` - Class → method relationships
- `calls` - Function → function calls
- `imports` - Module → module imports
- `inherits` - Class → base class inheritance
- `implements` - Class → interface implementation

### File Size Metrics

**Scaling Characteristics**:

| Nodes | Edges | JSON Size | Parse Time |
|-------|-------|-----------|------------|
| 5 | 3 | ~10 KB | 416 ms |
| 571 | 3,218 | ~2.8 MB | 1,923 ms |
| ~10,000 | ~50,000 | ~50 MB | ~15 sec |
| ~100,000 | ~500,000 | ~500 MB | ~3 min |

**Compression**: JSON can be gzipped to ~20% of original size

### Alternative Physical Formats

#### CSV Export (for analysis tools)
```bash
# Export nodes to CSV
cat unified_analysis.json | jq -r '
  .nodes[] |
  [.name, .role, .dimensions.D5_STATE, .dimensions.D6_EFFECT] |
  @csv
' > nodes.csv
```

#### SQLite Database (for complex queries)
```sql
-- Schema
CREATE TABLE nodes (
  id TEXT PRIMARY KEY,
  name TEXT,
  kind TEXT,
  role TEXT,
  d5_state TEXT,
  d6_effect TEXT,
  confidence REAL,
  lenses_json TEXT  -- Store full lenses as JSON blob
);

CREATE TABLE edges (
  id TEXT PRIMARY KEY,
  source TEXT,
  target TEXT,
  type TEXT,
  FOREIGN KEY (source) REFERENCES nodes(id),
  FOREIGN KEY (target) REFERENCES nodes(id)
);

CREATE INDEX idx_role ON nodes(role);
CREATE INDEX idx_state_effect ON nodes(d5_state, d6_effect);
CREATE INDEX idx_edge_type ON edges(type);
```

#### PostgreSQL (for production scale)
```sql
-- Full-text search support
CREATE TABLE nodes (
  id TEXT PRIMARY KEY,
  name TEXT,
  kind TEXT,
  role TEXT,
  dimensions JSONB,  -- Supports indexing
  lenses JSONB,
  search_vector tsvector
);

CREATE INDEX idx_dimensions_gin ON nodes USING gin(dimensions);
CREATE INDEX idx_lenses_gin ON nodes USING gin(lenses);
CREATE INDEX idx_search ON nodes USING gin(search_vector);
```

---

## 💾 LAYER 2: VIRTUAL STORAGE (In-Memory)

### Python Data Structures

**When Collider Runs**:

```python
# In unified_analysis.py
particles = []  # List[Dict] - All nodes
edges = []      # List[Dict] - All relationships

# Each particle is a dictionary
particle = {
    'id': 'unique_id',
    'name': 'function_name',
    'dimensions': {},  # Dict with D1-D8
    'lenses': {},      # Dict with R1-R8
    # ... ~100 other fields
}
```

### Graph Representation (NetworkX)

**In graph_analyzer.py**:

```python
import networkx as nx

# Build graph from edges
G = nx.DiGraph()

# Add nodes with all attributes
for node in particles:
    G.add_node(
        node['id'],
        **node  # All dimensions + lenses become node attributes
    )

# Add edges
for edge in edges:
    G.add_edge(
        edge['source'],
        edge['target'],
        type=edge['type']
    )

# Now you can query:
# - PageRank: nx.pagerank(G)
# - Betweenness: nx.betweenness_centrality(G)
# - Communities: nx.community.louvain_communities(G)
# - Shortest paths: nx.shortest_path(G, source, target)
```

### Index Structures (for fast lookup)

**Built during analysis**:

```python
# Role index
role_index = defaultdict(list)
for node in particles:
    role_index[node['role']].append(node['id'])

# Dimension index
state_effect_index = defaultdict(list)
for node in particles:
    key = (node['dimensions'].get('D5_STATE'),
           node['dimensions'].get('D6_EFFECT'))
    state_effect_index[key].append(node)

# File index
file_index = defaultdict(list)
for node in particles:
    file_index[node['file_path']].append(node)
```

**Usage**:
```python
# Find all pure, stateless functions (O(1) lookup)
cacheable = state_effect_index[('Stateless', 'Pure')]
# Result: 88 functions

# Find all DTOs (O(1) lookup)
dtos = role_index['DTO']
# Result: 100 nodes
```

### Caching Layer

**Memoization for expensive operations**:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_node_by_id(node_id: str) -> Dict:
    """Cache node lookups"""
    return node_lookup[node_id]

@lru_cache(maxsize=64)
def get_callees(node_id: str) -> List[str]:
    """Cache relationship queries"""
    return [e['target'] for e in edges if e['source'] == node_id]
```

---

## 🧠 LAYER 3: SEMANTIC STORAGE

### Multi-Dimensional Semantic Space

**The 8 dimensions create an 8D coordinate system**:

Every node exists at a point in 8D space:

```
Node "get_user_by_id" =
  (D1: QueryFunction,
   D2: Domain,
   D3: Query,
   D4: Internal,
   D5: Stateless,
   D6: Pure,
   D7: Use,
   D8: 82%)
```

### Queryable Semantic Patterns

**Pattern 1: Pure Query Functions**
```python
# Find all nodes matching this semantic pattern
pattern = {
    'D3_ROLE': 'Query',
    'D5_STATE': 'Stateless',
    'D6_EFFECT': 'Pure',
    'D4_BOUNDARY': 'Internal'
}

matches = [n for n in particles if all(
    n['dimensions'].get(k) == v
    for k, v in pattern.items()
)]
# Result: 12 perfect cache candidates
```

**Pattern 2: Security-Critical I/O**
```python
pattern = {
    'D4_BOUNDARY': ['Output', 'I-O'],
    'D6_EFFECT': ['Write', 'ReadModify']
}

risky = [n for n in particles if
    n['dimensions'].get('D4_BOUNDARY') in pattern['D4_BOUNDARY'] and
    n['dimensions'].get('D6_EFFECT') in pattern['D6_EFFECT']
]
# Result: 9 functions needing security review
```

### Epistemic Quality Space (R8 Lens)

**Confidence-based filtering**:

```python
# High-quality, well-understood code
high_confidence = [n for n in particles
    if n['lenses']['R8_EPISTEMOLOGY']['confidence'] > 70]

# Code needing review
needs_review = [n for n in particles
    if n['lenses']['R8_EPISTEMOLOGY']['requires_review']]

# Strong evidence
strong_evidence = [n for n in particles if
    n['lenses']['R8_EPISTEMOLOGY']['evidence']['evidence_strength'] == 'strong']
```

### Relationship Topology Space (R5 Lens)

**Graph-based semantic queries**:

```python
# Find hubs (many outgoing calls)
hubs = [n for n in particles
    if n['lenses']['R5_RELATIONSHIPS']['is_hub']]

# Find authorities (many incoming calls)
authorities = [n for n in particles
    if n['lenses']['R5_RELATIONSHIPS']['is_authority']]

# Find isolated nodes (no connections)
isolated = [n for n in particles
    if n['lenses']['R5_RELATIONSHIPS']['is_isolated']]
```

### Semantic Search Examples

**Use Case 1: Find All Cacheable Functions**
```bash
cat unified_analysis.json | jq '
  .nodes | map(select(
    .dimensions.D5_STATE == "Stateless" and
    .dimensions.D6_EFFECT == "Pure"
  )) | map({
    name: .name,
    file: .file_path,
    confidence: .lenses.R8_EPISTEMOLOGY.confidence
  })
'
```

**Use Case 2: Security Audit**
```bash
cat unified_analysis.json | jq '
  .nodes | map(select(
    (.dimensions.D4_BOUNDARY == "Output" or
     .dimensions.D4_BOUNDARY == "I-O") and
    .dimensions.D6_EFFECT == "Write"
  )) | map({
    name: .name,
    file: .file_path,
    line: .start_line,
    purpose: .lenses.R7_SEMANTICS.purpose
  })
'
```

**Use Case 3: Code Quality Dashboard**
```bash
cat unified_analysis.json | jq '{
  total_nodes: (.nodes | length),
  high_quality: (.nodes | map(select(
    .lenses.R8_EPISTEMOLOGY.confidence > 70
  )) | length),
  needs_review: (.nodes | map(select(
    .lenses.R8_EPISTEMOLOGY.requires_review
  )) | length),
  pure_functions: (.nodes | map(select(
    .dimensions.D6_EFFECT == "Pure"
  )) | length),
  stateless: (.nodes | map(select(
    .dimensions.D5_STATE == "Stateless"
  )) | length)
}'
```

---

## 🔄 LAYER INTERACTIONS

### Physical → Virtual

**Loading from disk into memory**:

```python
# Read JSON (Physical)
with open('collider_output/unified_analysis.json') as f:
    data = json.load(f)

# Build graph (Virtual)
G = nx.DiGraph()
for node in data['nodes']:
    G.add_node(node['id'], **node)
for edge in data['edges']:
    G.add_edge(edge['source'], edge['target'], **edge)

# Build indices (Virtual)
role_index = build_role_index(data['nodes'])
dim_index = build_dimension_index(data['nodes'])
```

### Virtual → Semantic

**Querying in-memory structures with semantic meaning**:

```python
# Virtual: Get all nodes with role='Query'
query_nodes = role_index['Query']

# Semantic: Filter by dimensional properties
pure_queries = [
    n for n in query_nodes
    if n['dimensions']['D5_STATE'] == 'Stateless' and
       n['dimensions']['D6_EFFECT'] == 'Pure'
]

# Semantic interpretation: These are cacheable!
cacheable_queries = pure_queries
```

### Semantic → Physical

**Saving insights back to disk**:

```python
# Semantic: Discover pattern
cacheable = find_cacheable_functions(particles)

# Virtual: Format for output
report = {
    'pattern': 'Cacheable Functions',
    'criteria': {'D5_STATE': 'Stateless', 'D6_EFFECT': 'Pure'},
    'count': len(cacheable),
    'functions': [{'name': n['name'], 'file': n['file_path']}
                  for n in cacheable]
}

# Physical: Write to disk
with open('insights/cacheable_functions.json', 'w') as f:
    json.dump(report, f, indent=2)
```

---

## 📦 STORAGE BEST PRACTICES

### 1. Physical Layer

**✓ DO**:
- Use JSON for portability
- Compress large outputs (gzip)
- Version your schema
- Include metadata (timestamp, version, target)

**✗ DON'T**:
- Store raw code in output (use references)
- Duplicate data across files
- Hardcode file paths

### 2. Virtual Layer

**✓ DO**:
- Build indices for common queries
- Use NetworkX for graph operations
- Cache expensive computations
- Lazy-load large datasets

**✗ DON'T**:
- Load entire dataset if you only need subset
- Rebuild indices on every query
- Keep duplicate copies in memory

### 3. Semantic Layer

**✓ DO**:
- Use dimensional patterns for queries
- Combine lenses for richer insights
- Track evidence strength (R8)
- Document query patterns

**✗ DON'T**:
- Ignore confidence scores
- Mix physical IDs with semantic patterns
- Hard-code dimension values

---

## 🎯 USE CASE EXAMPLES

### Use Case 1: Automated Code Review

**Goal**: Find all functions needing review

**Physical**: Load `unified_analysis.json`

**Virtual**: Build index by R8 confidence

**Semantic**: Query for `requires_review == true`

**Output**: List of 144 functions with reasons

```python
needs_review = [
    n for n in particles
    if n['lenses']['R8_EPISTEMOLOGY']['requires_review']
]

for node in needs_review:
    print(f"Review: {node['name']} ({node['file_path']}:{node['start_line']})")
    print(f"  Reason: {node['lenses']['R8_EPISTEMOLOGY']['uncertainties']}")
```

### Use Case 2: Performance Optimization

**Goal**: Find functions to memoize

**Physical**: Load JSON

**Virtual**: Build state+effect index

**Semantic**: Query for Pure + Stateless

**Output**: 88 cacheable functions

```python
cacheable = [
    n for n in particles
    if n['dimensions']['D5_STATE'] == 'Stateless' and
       n['dimensions']['D6_EFFECT'] == 'Pure'
]

# Generate code
for func in cacheable:
    print(f"@lru_cache(maxsize=128)")
    print(f"def {func['name']}(...):")
```

### Use Case 3: Security Audit

**Goal**: Find I/O write operations

**Physical**: Load JSON

**Virtual**: Build boundary+effect index

**Semantic**: Query for Output + Write

**Output**: 9 security-critical functions

```python
write_ops = [
    n for n in particles
    if n['dimensions']['D4_BOUNDARY'] in ['Output', 'I-O'] and
       n['dimensions']['D6_EFFECT'] in ['Write', 'ReadModify']
]

for op in write_ops:
    print(f"REVIEW: {op['name']} writes to external system")
    print(f"  Purpose: {op['lenses']['R7_SEMANTICS']['purpose']}")
    print(f"  Confidence: {op['lenses']['R8_EPISTEMOLOGY']['confidence']}%")
```

---

## 🚀 ADVANCED STORAGE PATTERNS

### Pattern 1: Incremental Storage

**Problem**: Analyzing 100K+ nodes takes time

**Solution**: Store intermediate results

```python
# Save after each file
for file in files:
    result = analyze_file(file)
    save_partial(f"cache/{file}.json", result)

# Merge at the end
final = merge_partial_results("cache/*.json")
```

### Pattern 2: Differential Storage

**Problem**: Only a few files changed

**Solution**: Store diffs, not full snapshots

```python
# Previous analysis
old = load_analysis("2025-12-26.json")

# Current analysis
new = analyze_codebase()

# Store only changes
diff = {
    'added': [n for n in new['nodes'] if n['id'] not in old_ids],
    'removed': [n for n in old['nodes'] if n['id'] not in new_ids],
    'modified': [n for n in new['nodes'] if changed(n, old)]
}

save_diff("2025-12-27.diff.json", diff)
```

### Pattern 3: Multi-Format Storage

**Problem**: Different tools need different formats

**Solution**: Generate all formats from canonical JSON

```python
# Canonical: JSON
canonical = load_analysis("unified_analysis.json")

# Export to CSV (for Excel)
to_csv(canonical, "nodes.csv")

# Export to SQLite (for queries)
to_sqlite(canonical, "analysis.db")

# Export to Neo4j (for graph viz)
to_neo4j(canonical, "bolt://localhost:7687")

# Export to GraphML (for Gephi)
to_graphml(canonical, "graph.graphml")
```

---

## 📊 STORAGE METRICS

### Current State (src/core analysis)

| Metric | Value |
|--------|-------|
| Nodes stored | 571 |
| Edges stored | 3,218 |
| JSON size | 2.8 MB |
| Fields per node | ~100 |
| Lenses per node | 8 |
| Dimensions per node | 8 |
| Parse time | 1.9 sec |
| Query time (jq) | ~200 ms |

### Scalability Projections

| Scale | Nodes | Edges | JSON | RAM | Parse | Query |
|-------|-------|-------|------|-----|-------|-------|
| Small | 100 | 300 | 500 KB | 10 MB | 0.5s | 50ms |
| Medium | 1K | 5K | 5 MB | 50 MB | 3s | 200ms |
| Large | 10K | 50K | 50 MB | 500 MB | 30s | 2s |
| X-Large | 100K | 500K | 500 MB | 5 GB | 5min | 20s |
| Enterprise | 1M | 5M | 5 GB | 50 GB | 1hr | 3min |

**Note**: Enterprise scale requires database backend (PostgreSQL, Neo4j)

---

## 🎉 CONCLUSION

### The Three Layers Work Together

1. **Physical Layer** - Durable storage on disk
   - JSON for portability
   - SQLite/PostgreSQL for queries
   - CSV for analysis tools

2. **Virtual Layer** - Fast in-memory access
   - Python dictionaries and lists
   - NetworkX graphs
   - Indices and caches

3. **Semantic Layer** - Meaningful queries
   - 8D dimensional space
   - 8L epistemic lenses
   - Pattern-based discovery

### Key Insights

- **Physical** = "Where is it?"
- **Virtual** = "How do I access it?"
- **Semantic** = "What does it mean?"

All three layers are necessary:
- Physical for persistence
- Virtual for performance
- Semantic for intelligence

The **8D + 8L system creates a queryable semantic space** that enables insights impossible with traditional static analysis.

---

**Generated by**: Collider v3.0.0
**Schema**: v3.0.0
**Theory**: Standard Code Model v2
**Date**: 2025-12-27
