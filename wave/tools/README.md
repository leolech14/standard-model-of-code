# Wave Tools Index

> **Realm:** WAVE (probabilistic, AI-powered)
> **Purpose:** Intelligence and semantic processing tools
> Updated: 2026-01-31

## Directory Structure

```
tools/
├── ai/                 # AI analysis tools (PRIMARY)
│   ├── analyze.py      # Main AI query tool
│   ├── cerebras_*.py   # Cerebras fast inference (5 tools)
│   ├── aci/            # Adaptive Context Intelligence
│   └── deck/           # Decision deck routing
│
├── refinery/           # Context refinement pipeline
│   ├── pipeline.py     # Main refinery pipeline
│   ├── chunker.py      # Document chunking
│   └── corpus_*.py     # Corpus management
│
├── docling_processor/  # PDF/document processing
│   ├── processor.py    # Docling integration
│   └── cli.py          # Batch processing CLI
│
├── docsintel/          # External documentation intelligence
│   └── install.sh      # MCP server installer
│
├── pom/                # Projectome Omniscience Module
│   └── projectome_omniscience.py
│
├── archive/            # Deprecated tools (reference only)
├── couriers/           # Data transport utilities
├── graphrag/           # Graph RAG experiments
├── maintenance/        # System maintenance scripts
├── mcp/                # MCP server tools
├── ops/                # Operational scripts
├── pipeline_booster/   # Pipeline optimization
└── utils/              # Shared utilities
```

## Primary Tools

### AI Analysis (`ai/`)
| Tool | ID | Purpose |
|------|-----|---------|
| `analyze.py` | T004 | Gemini-powered code analysis |
| `cerebras_spiral_intel.py` | T055 | Multi-pass codebase understanding |
| `cerebras_enricher.py` | T056 | Semantic enrichment at 3000 t/s |
| `cerebras_tagger.py` | T057 | Batch D1-D8 classification |

### Refinery (`refinery/`)
| Tool | ID | Purpose |
|------|-----|---------|
| `pipeline.py` | T007 | Context refinement pipeline |
| `corpus_inventory.py` | T008 | Corpus scanning |

### Document Processing (`docling_processor/`)
| Tool | ID | Purpose |
|------|-----|---------|
| `processor.py` | T054 | IBM Docling PDF processing |

## Tool Taxonomy

**By Processing Nature:**
- **Deterministic** (PARTICLE): `repo_mapper.py` phases 1-2
- **Probabilistic** (WAVE): All AI tools
- **Reactive** (OBSERVER): Maintenance scripts

**By Input:**
- **Files**: analyze.py, refinery, docling
- **Queries**: analyze.py, aci/
- **Codebase**: spiral_intel, pom

**By Output:**
- **JSON**: Most tools
- **Markdown**: analyze.py, docling
- **YAML**: Some configs

## Usage Patterns

```bash
# AI Analysis
doppler run -- python3 tools/ai/analyze.py "What does X do?"

# Spiral Intel
python3 tools/ai/cerebras_spiral_intel.py status
python3 tools/ai/cerebras_spiral_intel.py spiral --parallel -w 20

# Refinery
python3 tools/refinery/pipeline.py /path/to/source

# Docling
python3 -m context_management.tools.docling_processor process
```

## See Also
- `.agent/intelligence/TOOLS_REGISTRY.yaml` - Full tool definitions
- `.agent/registry/REGISTRY_OF_REGISTRIES.yaml` - Registry index
- `wave/config/README.md` - Configuration index
