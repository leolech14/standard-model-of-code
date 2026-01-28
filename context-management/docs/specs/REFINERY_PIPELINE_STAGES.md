# REFINERY PIPELINE - Contextome Atomization Stages

**Pipeline:** Refinery (Contextome processing)
**Location:** `context-management/tools/ai/aci/refinery.py`
**Purpose:** Break documentation/config into AI-consumable semantic chunks
**Stages:** 8 (documented 2026-01-27)

---

## OVERVIEW

The Refinery Pipeline transforms large context files (docs, code, config) into atomic chunks with metadata, enabling efficient AI context building and semantic search.

```
Input (large files)
  ↓
[Stage 1-2] Load & Route
  ↓
[Stage 3-4] Chunk & Identify
  ↓
[Stage 5-6] Enrich & Embed
  ↓
[Stage 7-8] Validate & Export
  ↓
Output (semantic chunks)
```

---

## STAGE DEFINITIONS

### Stage 1: Load File
**Class:** `FileChunker._load()`
**Input:** File path
**Output:** Raw file content (UTF-8)
**Error handling:** Replace invalid chars, log failures

---

### Stage 2: Route to Chunker
**Class:** `Refinery._get_chunker()`
**Input:** File path
**Logic:**
```python
if suffix == '.py':     return PythonChunker
elif suffix == '.md':   return MarkdownChunker
elif suffix == '.yaml': return YamlChunker
else:                   return GenericChunker
```
**Output:** Appropriate chunker instance

---

### Stage 3: Semantic Chunking
**Class:** `FileChunker.chunk()` (polymorphic)
**Strategies by file type:**

| Type | Chunker | Units |
|------|---------|-------|
| Python | PythonChunker | functions, classes, imports, constants |
| Markdown | MarkdownChunker | sections (by headers H1-H6) |
| YAML | YamlChunker | top-level keys |
| Generic | GenericChunker | blocks (separated by blank lines) |

**Output:** List of (content, chunk_type, start_line, end_line)

**Examples:**
- Python: `('def foo():\n    ...', 'function', 45, 67)`
- Markdown: `('## Atoms\nAtoms are...', 'h2', 12, 25)`
- YAML: `('subsystems:\n  - name: PARTICLE', 'yaml_key:subsystems', 1, 10)`

---

### Stage 4: Generate Chunk ID
**Class:** `Refinery._generate_chunk_id()`
**Input:** File path + content
**Algorithm:** `SHA256(file_path + content)[:16]`
**Output:** Unique 16-char hex ID
**Purpose:** Stable identifier for caching

---

### Stage 5: Score Relevance
**Class:** `Refinery._score_relevance()`
**Input:** Content + chunk type
**Algorithm:** Heuristic scoring (0.0-1.0)

**Scoring rules:**
```python
Base score = 0.5
+ Has docstring: +0.2
+ Long content (>500 chars): +0.1
+ Type is 'function' or 'class': +0.1
+ Type is 'h1' or 'h2': +0.15
+ Contains keywords (TODO, CRITICAL, etc.): +0.05
```

**Output:** Relevance score (float)

---

### Stage 6: Generate Embeddings (Optional)
**Class:** `EmbeddingEngine.embed()`
**Model:** `sentence-transformers/all-MiniLM-L6-v2`
**Dimensions:** 384
**Cost:** ~15ms per 1K tokens
**Output:** Vector embedding (list of 384 floats)

**When enabled:**
```python
refinery = Refinery(enable_embeddings=True)
```

**Purpose:** Semantic search, similarity scoring

---

### Stage 7: Validate Chunks
**Class:** `Refinery._validate_chunks()`
**Checks:**
- All chunks have non-empty content
- All chunks have valid types
- Line numbers are sequential
- No duplicate chunk IDs

**Output:** Validation errors (list)

---

### Stage 8: Export to Registry
**Class:** `Refinery.export_to_json()`
**Format:**
```json
{
  "metadata": {
    "source_file": "...",
    "generated_at": "2026-01-27T...",
    "total_chunks": 42,
    "total_tokens": 12000
  },
  "chunks": [
    {
      "chunk_id": "a1b2c3d4...",
      "content": "...",
      "chunk_type": "function",
      "relevance_score": 0.85,
      "start_line": 45,
      "end_line": 67,
      "token_estimate": 150,
      "embedding": [0.1, 0.2, ...] // if enabled
    }
  ]
}
```

**Output locations:**
- `.agent/intelligence/chunks/agent_chunks.json`
- `.agent/intelligence/chunks/core_chunks.json`
- `.agent/intelligence/chunks/aci_chunks.json`

---

## CHUNKER SPECIFICATIONS

### PythonChunker
**Patterns detected:**
- `class ClassName:` → type: 'class'
- `def function_name():` → type: 'function'
- `async def ...` → type: 'function'
- `CONSTANT = value` → type: 'constant'
- `variable = value` → type: 'variable'
- `import ...` / `from ...` → type: 'imports'

**Logic:** Detects definitions at column 0, captures until next definition

---

### MarkdownChunker
**Patterns detected:**
- `# Header` → type: 'h1'
- `## Header` → type: 'h2'
- ... up to `######` → type: 'h6'

**Logic:** Split on headers, include content until next header

---

### YamlChunker
**Patterns detected:**
- `top_key:` → type: 'yaml_key:top_key'

**Logic:** Split on top-level keys (no indent)

---

### GenericChunker
**Patterns:** None (fallback)
**Logic:** Split on blank lines (2+ consecutive newlines)
**Type:** 'paragraph'

---

## INTEGRATION WITH WIRE.PY

The Refinery is triggered by the Wire pipeline:

```
File change detected
  ↓
Filesystem Watcher (5 min quiet period)
  ↓
wire.py orchestrates:
  1. Detect changed files
  2. Call refinery.process_file() for each
  3. Merge into master chunks.json
  4. Update state
  5. Log metrics
```

---

## PERFORMANCE

**Benchmarks (without embeddings):**
- Python file (500 LOC): ~50ms
- Markdown file (200 lines): ~20ms
- YAML file (100 keys): ~15ms

**With embeddings (MiniLM):**
- +15ms per chunk
- For 100 chunks: +1.5 seconds total

---

## COMPARISON TO COLLIDER PIPELINE

| Aspect | Collider Pipeline | Refinery Pipeline |
|--------|-------------------|-------------------|
| **Stages** | 28 | 8 |
| **Input** | Code (.py, .js, etc.) | Docs/config (.md, .yaml, .py) |
| **Output** | Graph (unified_analysis.json) | Chunks (chunks.json) |
| **Purpose** | Structural analysis | Context atomization |
| **Scope** | Codome (executable) | Contextome (non-executable) |
| **Runtime** | Minutes (full repo) | Seconds (single file) |
| **Trigger** | Manual (`./collider`) | Auto (filesystem watcher) |
| **Consumers** | Visualization, metrics | AI queries (analyze.py, ACI) |

---

## CANONICAL SOURCE

**Code:** `context-management/tools/ai/aci/refinery.py`
**Documentation:** This file (REFINERY_PIPELINE_STAGES.md)
**Registry:** TBD - should create `REFINERY_STAGES.yaml`

---

**Last verified:** 2026-01-27
**Stage count:** 8 stages
**Status:** Production (used by wire.py, analyze.py)
