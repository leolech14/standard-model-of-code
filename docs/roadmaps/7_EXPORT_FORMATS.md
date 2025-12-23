# Roadmap: Export Format Expansion

## Strategic Goal
Expand Collider's output capabilities by adding converters from the canonical JSON format to standard industry formats, enabling integration with external tools.

---

## Current State

**Canonical Format**: `unified_analysis.json`
- Contains all nodes, edges, and metadata
- Lossless and complete
- All other formats derive from this

---

## Future Export Formats

### Priority 1: CI/CD Integration
| Format | Use Case | Ecosystem |
|--------|----------|-----------|
| **SARIF** | GitHub Code Scanning, VS Code | Security/quality tools |

### Priority 2: Graph Analysis
| Format | Use Case | Ecosystem |
|--------|----------|-----------|
| **GraphML** | Gephi, yEd, Neo4j import | Graph analysis tools |
| **DOT (Graphviz)** | Static diagram generation | Graphviz ecosystem |

### Priority 3: Documentation
| Format | Use Case | Ecosystem |
|--------|----------|-----------|
| **Mermaid** | Markdown docs | GitHub, GitLab, wikis |
| **PlantUML** | UML diagrams | Architecture docs |
| **C4 DSL** | Structurizr | C4 model tooling |

### Priority 4: Data Exchange
| Format | Use Case | Ecosystem |
|--------|----------|-----------|
| **CSV** | Spreadsheet analysis | Excel, Google Sheets |
| **JSON-LD** | Semantic web | Knowledge graphs |

---

## Implementation Notes

Each converter is a simple script:
```
scripts/export/
├── to_sarif.py
├── to_graphml.py
├── to_dot.py
├── to_mermaid.py
└── to_csv.py
```

**Input**: `unified_analysis.json`
**Output**: Requested format

---

## Status
- [ ] SARIF converter
- [ ] GraphML converter
- [ ] DOT converter
- [x] Mermaid (partial, inline in reports)
- [ ] PlantUML converter
- [ ] CSV converter
