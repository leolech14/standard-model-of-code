# Perplexity Research Archive

**Deterministic Auto-Save Pipeline**

All Perplexity research queries are automatically saved by the `perplexity-local` MCP server.

## Directory Structure

```
perplexity/
├── README.md          # This file
├── raw/               # Complete JSON API responses (ZERO information loss)
│   └── YYYYMMDD_HHMMSS_slug.json
└── docs/              # Human-readable markdown summaries
    └── YYYYMMDD_HHMMSS_slug.md
```

## Pipeline

1. Query received via MCP JSON-RPC
2. Perplexity API called
3. **Deterministic Save:**
   - Full API response → `raw/{timestamp}_{slug}.json`
   - Markdown summary → `docs/{timestamp}_{slug}.md`
4. Response returned with save confirmation

## Filename Convention

```
{YYYYMMDD}_{HHMMSS}_{slug}.{ext}

Example:
20260122_150830_mcp_factory_design.json
20260122_150830_mcp_factory_design.md
```

- Timestamp: UTC time of query
- Slug: First 50 chars of query, alphanumeric only

## Usage

The MCP server auto-saves. No manual action needed.

To query saved research:
```bash
# Find by topic
ls docs/ | grep -i "mcp"

# Read raw JSON
cat raw/20260122_150830_mcp_factory_design.json | jq .

# Get all queries from a date
ls docs/ | grep "^20260122"
```

## Configuration

MCP Server: `context-management/tools/mcp/perplexity_mcp_server.py`
Settings: `~/.claude/settings.json` → mcpServers.perplexity-local
