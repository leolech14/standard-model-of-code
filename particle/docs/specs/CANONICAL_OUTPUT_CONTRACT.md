# Canonical Output Contract

**Version:** 1.0.0
**Created:** 2026-02-01
**Status:** AUTHORITATIVE

---

## Command

```bash
./collider full <target_path> --output <output_dir>
```

**Example (self-analysis):**
```bash
./collider full . --output .collider
```

---

## Canonical Directory

| Context | Path |
|---------|------|
| Self-analysis | `.collider/` |
| Batch per-repo | `<repo>/.collider/` |
| Batch GCS | `gs://<bucket>/full_scans/<run_id>/<repo>/` |

**Cloud Upload Guardrail:** GCS upload is disabled by default. Set `UPLOAD_FULL_SCANS_TO_GCS=1` to enable.

---

## Guaranteed Files

| File | Format | Size (typical) | Purpose |
|------|--------|----------------|---------|
| `unified_analysis.json` | JSON | 5-50 MB | LLM-oriented graph data |
| `collider_report.html` | HTML | 50-100 KB | Human-readable visualization |

**Legacy aliases (same content):**
- `output_llm-oriented_*.json` → same as `unified_analysis.json`
- `output_human-readable_*.html` → same as `collider_report.html`

---

## unified_analysis.json Schema

```json
{
  "nodes": [
    {
      "id": "string",
      "file_path": "string",
      "start_line": "number",
      "end_line": "number",
      "kind": "string",
      "semantic_role": "string",
      "purpose": "string",
      "has_docstring": "boolean",
      "betweenness_centrality": "number"
    }
  ],
  "edges": [
    {
      "source": "string (node id)",
      "target": "string (node id)",
      "edge_type": "string",
      "family": "string",
      "resolution": "string"
    }
  ],
  "metadata": {
    "timestamp": "ISO8601",
    "collider_version": "string",
    "target_path": "string"
  }
}
```

---

## Validation

### Quick check (file exists + has nodes):

```bash
# Verify output exists
test -f .collider/unified_analysis.json && echo "OK" || echo "MISSING"

# Verify has content
python3 -c "import json; d=json.load(open('.collider/unified_analysis.json')); print(f'Nodes: {len(d.get(\"nodes\", []))}, Edges: {len(d.get(\"edges\", []))}')"
```

### Full validation script:

```bash
python3 particle/tools/batch_grade/validate_output.py .collider/unified_analysis.json
```

---

## Consumers

| Consumer | Location | Reads |
|----------|----------|-------|
| Neo4j Bridge | `.agent/tools/collider_to_neo4j.py` | `unified_analysis.json` |
| Batch Analyzer | `particle/tools/batch_grade/analyze_results.py` | grade summaries |
| HTML Viewer | Browser | `collider_report.html` |

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-02-01 | Initial contract (ARCHIVIST) |

---

## Breaking Changes Policy

1. `unified_analysis.json` schema changes require version bump
2. Consumers must handle missing optional fields gracefully
3. Deprecation warning before removing any field (minimum 30 days)
