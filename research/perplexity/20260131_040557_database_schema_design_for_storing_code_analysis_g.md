# Perplexity Research: Database schema design for storing code analysis graphs. Best SQLite schema for nodes (functions/cla...

> **Date:** 2026-01-31 04:05:57
> **Model:** sonar-pro
> **Query Length:** 194 chars

---

## Query

Database schema design for storing code analysis graphs. Best SQLite schema for nodes (functions/classes), edges (calls/imports), and file metadata. How to store AST node properties efficiently?

---

## Response

```sql
-- Core graph tables for code analysis (nodes and edges)
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,  -- 'function', 'class', 'method', 'variable', etc.
    name TEXT NOT NULL,
    file_id INTEGER NOT NULL,
    line_start INTEGER,
    line_end INTEGER,
    properties JSON,  -- AST properties, e.g. {"params": [...], "return_type": "void"}
    FOREIGN KEY (file_id) REFERENCES files(id)
);

CREATE TABLE edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_node_id INTEGER NOT NULL,
    to_node_id INTEGER NOT NULL,
    type TEXT NOT NULL,  -- 'calls', 'imports', 'inherits', 'references', etc.
    properties JSON,  -- Edge-specific data, e.g. {"call_site_line": 42}
    UNIQUE(from_node_id, to_node_id, type),  -- Prevent duplicate edge types
    FOREIGN KEY (from_node_id) REFERENCES nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (to_node_id) REFERENCES nodes(id) ON DELETE CASCADE
);

-- File metadata table
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT UNIQUE NOT NULL,
    hash TEXT,  -- Content hash for change detection
    language TEXT,  -- 'python', 'javascript', etc.
    modified_at INTEGER,  -- Unix timestamp
    content_size INTEGER,
    metadata JSON  -- Arbitrary file metadata
);

-- Indexes for efficient graph queries
CREATE INDEX idx_nodes_file ON nodes(file_id);
CREATE INDEX idx_nodes_type ON nodes(type);
CREATE INDEX idx_nodes_name ON nodes(name);
CREATE INDEX idx_edges_from ON edges(from_node_id);
CREATE INDEX idx_edges_to ON edges(to_node_id);
CREATE INDEX idx_edges_type ON edges(type);
```

## Key Design Decisions

**Simple two-table graph core** modeled after the `simple-graph` SQLite approach[1]:
- **Nodes** store functions/classes as JSON `properties` for flexible AST data
- **Edges** capture relationships (calls, imports, inheritance) with directionality
- Typed nodes/edges enable code-specific queries (e.g., `WHERE type = 'function'`)

**Efficient AST storage**:
- **JSON column** for `properties` holds structured AST data without schema proliferation
```json
{
  "params": [{"name": "x", "type": "int"}],
  "return_type": "str",
  "is_async": true,
  "docstring": "..."
}
```
- Line numbers (`line_start`, `line_end`) for precise location mapping
- Flat structure scales to millions of nodes/edges in SQLite[5]

**File metadata normalization**:
- Separate `files` table prevents data duplication
- `hash` enables incremental analysis (skip unchanged files)
- Foreign key ensures nodes always reference valid files

## Common Queries

**Find all functions called by a class**:
```sql
SELECT n2.* FROM nodes n1
JOIN edges e ON e.from_node_id = n1.id
JOIN nodes n2 ON e.to_node_id = n2.id
WHERE n1.type = 'class' AND n1.name = ? AND e.type = 'calls';
```

**Call graph traversal (using CTEs)**[5]:
```sql
WITH RECURSIVE call_graph AS (
  SELECT *, 0 as depth FROM nodes WHERE name = ?
  UNION
  SELECT n.*, cg.depth + 1
  FROM nodes n JOIN edges e ON n.id = e.from_node_id
  JOIN call_graph cg ON e.to_node_id = cg.id
  WHERE cg.depth < 10  -- Limit recursion depth
)
SELECT * FROM call_graph ORDER BY depth;
```

**Import dependencies per file**:
```sql
SELECT f.path, n2.name as imported_module
FROM files f JOIN nodes n1 ON n1.file_id = f.id
JOIN edges e ON e.from_node_id = n1.id
JOIN nodes n2 ON e.to_node_id = n2.id
WHERE e.type = 'imports';
```

This schema balances **SQLite performance**, **query flexibility**, and **code analysis requirements** while remaining simple enough for single-file deployment[1][5].

---

## Citations

1. https://github.com/dpapathanasiou/simple-graph
2. https://pkg.go.dev/github.com/paulsmith/sqlite-schema-viz
3. https://github.com/ncruces/sqlite-schema-diagram
4. https://news.ycombinator.com/item?id=23744449
5. https://news.ycombinator.com/item?id=24844534
6. https://crates.io/crates/graphlite

---

## Usage Stats

- Input tokens: 36
- Output tokens: 880
