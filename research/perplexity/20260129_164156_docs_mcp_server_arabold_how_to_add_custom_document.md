# Research: docs-mcp-server arabold how to add custom documentation sources index website github

> **Date:** 2026-01-29 16:41:56
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:3c036a8531fb60b4031934fe7e86fcde8cc1a752271e455e9d076621e98a2a05`
> **Raw JSON:** `raw/20260129_164156_docs_mcp_server_arabold_how_to_add_custom_document.json`

---

## Query

docs-mcp-server arabold how to add custom documentation sources index website github

---

## Response

The **Docs MCP Server** by arabold allows you to add custom documentation sources through a web interface or programmatically using MCP tools[3].

## Adding Documentation via Web Interface

1. Start the server and open the Web UI at `http://localhost:6280`[3]
2. Use the "Queue New Scrape Job" form to add documentation[3]
3. Enter the documentation URL, library name, and optionally the version[3]
4. Click "Queue Job" and monitor progress in the Job Queue[3]

## Adding Documentation via MCP Tools

Your AI assistant can index new documentation directly using the built-in `scrape_docs` tool[3]. For example:

```
Please scrape the React documentation from https://react.dev/reference/react for library "react" version "18.x"
```

## Supported Documentation Sources

The server indexes documentation from multiple sources[3]:

- **Websites** — Direct documentation URLs
- **GitHub repositories** — Project documentation hosted on GitHub
- **Package managers** — npm and PyPI documentation
- **Local files and folders** — Using `file://` URLs (e.g., `file:///Users/me/docs/my-library`)[3]

## Configuration

To use the server with your AI client (VS Code, Claude Desktop, etc.), add this to your MCP settings[3]:

```json
{
  "mcpServers": {
    "docs-mcp-server": {
      "command": "npx",
      "args": ["@arabold/docs-mcp-server@latest"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

Once configured, the server provides **version-aware search** and generates embeddings for semantic understanding, allowing your AI assistant to access the latest documentation and reduce hallucinations[3].

---

## Citations

1. https://lobehub.com/mcp/arabold-docs-mcp-server
2. https://gitbook.com/docs/publishing-documentation/mcp-servers-for-published-docs
3. https://github.com/arabold/docs-mcp-server
4. https://www.mintlify.com/blog/how-to-use-mcp-servers-to-generate-docs
5. https://developers.openai.com/resources/docs-mcp/
6. https://langfuse.com/docs/docs-mcp
7. https://code.visualstudio.com/docs/copilot/customization/mcp-servers
8. https://docs.customgpt.ai/reference/mcp
9. https://modelcontextprotocol.io/docs/develop/build-server

---

## Usage Stats

- Prompt tokens: 15
- Completion tokens: 372
- Total tokens: 387
