# Research: julianoczkowski anthropic-docs-mcp-ts install npm github

> **Date:** 2026-01-29 16:37:17
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:f7679933e9021fbbd854dea2d6a8b168686b9269115c24746f9c48bd464ff9fd`
> **Raw JSON:** `raw/20260129_163717_julianoczkowski_anthropic_docs_mcp_ts_install_npm.json`

---

## Query

julianoczkowski anthropic-docs-mcp-ts install npm github

---

## Response

To install the **julianoczkowski/anthropic-docs-mcp-ts** MCP server (a Model Context Protocol tool for searching and retrieving Claude/Anthropic documentation), use NPM globally and configure it in your IDE.[1][4]

### Installation via NPM
Run one of these commands in your terminal (requires Node.js >= v18.0.0):
```
npm install -g @julianoczkowski/anthropic-docs-mcp-ts
```
or with sudo on Unix-like systems:
```
sudo npm install -g @julianoczkowski/anthropic-docs-mcp-ts
```
[1]

Verify installation:
```
anthropic-docs-mcp --help
```
[1]

### GitHub Repository
Source code and details: **https://github.com/julianoczkowski/anthropic-docs-mcp-ts** (MIT licensed).[4]

### IDE Configuration
#### Cursor (~/.cursor/mcp.json)
Add this to your config:
```json
{
  "mcpServers": {
    "anthropic-docs": {
      "command": "anthropic-docs-mcp",
      "args": ["--transport", "stdio"]
    }
  }
}
```
[1]

#### VS Code (with MCP extension)
Add to your MCP config:
```json
{
  "servers": {
    "anthropic-docs": {
      "type": "stdio",
      "command": "anthropic-docs-mcp",
      "args": ["--transport", "stdio"]
    }
  }
}
```
[1]

### Tools Provided
Once set up, use these in your LLM conversations:
- **`search_anthropic_docs`**: Search docs by query (e.g., `{"query": "MCP server development", "max_results": 3}`).[1]
- **`fetch_doc`**: Fetch/clean a doc page (e.g., `{"url": "https://docs.claude.com/en/docs/agents-and-tools/mcp-connector", "max_chars": 2000}`).[1]

For issues (e.g., tools not appearing), re-run the global install and test the command.[1] The repo is listed in MCP server collections.[3]

---

## Citations

1. https://lobehub.com/de/mcp/julianoczkowski-anthropic-docs-mcp-ts
2. https://www.youtube.com/watch?v=ebgdlgAEi28
3. https://github.com/madhukarkumar/anthropic-mcp-servers
4. https://github.com/julianoczkowski/anthropic-docs-mcp-ts
5. https://lobehub.com/mcp/julianoczkowski-anthropic-docs-mcp-ts?activeTab=deployment
6. https://github.com/modelcontextprotocol/typescript-sdk
7. https://lobechat.com/discover/mcp/julianoczkowski-anthropic-docs-mcp-ts?hl=bg-BG
8. https://github.com/anthropics/anthropic-sdk-typescript
9. https://github.com/modelcontextprotocol
10. https://github.com/anthropics/anthropic-sdk-typescript/issues/714

---

## Usage Stats

- Prompt tokens: 16
- Completion tokens: 472
- Total tokens: 488
