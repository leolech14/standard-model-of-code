# Research: Context7 MCP documentation intelligence tool provider docs

> **Date:** 2026-01-29 16:33:29
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:d77980399a06369be57c01181b4d8610254ce85c2896bfc4fb264688e68dd73b`
> **Raw JSON:** `raw/20260129_163329_context7_mcp_documentation_intelligence_tool_provi.json`

---

## Query

Context7 MCP documentation intelligence tool provider docs

---

## Response

**Context7 MCP** is a documentation intelligence tool developed by Upstash that integrates with AI coding assistants (like Cursor, Claude, VS Code, and others) via Anthropic's **Model Context Protocol (MCP)** to fetch and inject the latest, version-specific library documentation and code examples directly into prompts.[1][2][4]

### How It Works
When you include phrases like **"use context7"** in a prompt (e.g., "Create a FastAPI CRUD API. use context7"), the MCP server:
- Detects the referenced library or framework (e.g., FastAPI, Next.js).[1][2]
- Retrieves the most recent official docs, filtering by topic if specified (e.g., "routing").[1][4]
- Injects relevant content into the AI's context for accurate, up-to-date responses, avoiding reliance on outdated training data.[1][2]

Example prompts:[2]
- "Write a MongoDB aggregation pipeline. use context7"
- "implement basic authentication with supabase. use library /supabase/supabase"

You can skip detection by using exact **Context7-compatible library IDs** (e.g., `/vercel/next.js`, `/mongodb/docs`).[4][5]

### Installation and Setup
Context7 runs as an MCP server, installable locally (via npx/Docker) or remotely (HTTP with API key).[3][4][5]
- **Cursor (local)**: Add to `mcpServers` config: `{ "command": "npx", "args": ["-y", "@upstash/context7-mcp", "--api-key", "YOUR_API_KEY"] }`[5]
- **OpenAI Codex CLI**: `codex mcp add context7 -- npx -y @upstash/context7-mcp`[3]
- **VS Code**: Use `npx -y @upstash/context7-mcp` via MCP server settings; restart VS Code after adding.[6]
- **Remote HTTP**: `"url": "https://mcp.context7.com/mcp"`, with `CONTEXT7_API_KEY` header (OAuth option available).[4][5]
- Supports Windsurf, Augment Code, Trae, Copilot Coding Agent, and more.[4][5][6]

Key tools include `query-docs` (fetches docs by library ID and query) and `resolve-library-id`.[4]

### Automation Tips
Add rules to auto-invoke without "use context7":[4]
- **Cursor**: In Settings > Rules: "Always use Context7 MCP when I need library/API documentation..."
- **Claude**: In CLAUDE.md file.

Free tier available; npm package: `@upstash/context7-mcp`.[4][5][8] For full GitHub repo and library IDs, see Upstash's documentation.[4]

---

## Citations

1. https://upstash.com/blog/context7-mcp
2. https://apidog.com/blog/context7-mcp-server/
3. https://developers.openai.com/codex/mcp/
4. https://github.com/upstash/context7
5. https://www.npmjs.com/package/@upstash/context7-mcp
6. https://www.youtube.com/watch?v=-ls0D-rtET4
7. https://habr.com/ru/articles/933678/
8. https://www.pulsemcp.com/servers/upstash-context7
9. https://vc.ru/ai/2012617-context7-mcp-ai-pomoshchnik-po-kodu

---

## Usage Stats

- Prompt tokens: 8
- Completion tokens: 588
- Total tokens: 596
