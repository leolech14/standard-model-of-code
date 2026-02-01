# Research: Claude Code CLI MCP server configuration: What is the exact precedence and relationship between thes...

> **Date:** 2026-01-27 04:54:22
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:3252f49e11bb19e0806f5e8a7d699fe10573dd9f9f4808a6a212d4a814558b29`
> **Raw JSON:** `raw/20260127_045422_claude_code_cli_mcp_server_configuration__what_is.json`

---

## Query

Claude Code CLI MCP server configuration: What is the exact precedence and relationship between these three config files?

1. ~/.claude/settings.json (has mcpServers key)
2. ~/.claude.json (has mcpServers at root level AND nested under projects.{path}.mcpServers)
3. ~/.config/claude/mcp.json (has mcpServers key)

Specifically:
- Which file does `claude mcp add --scope user` write to?
- Which file does `claude mcp add --scope project` write to?
- Does Claude Code read from all three? What's the merge order?
- Is ~/.config/claude/mcp.json for Claude Desktop only, or does Claude Code CLI also read it?
- If the same server name exists in multiple files, which one wins?
- Are the mcpServers in settings.json redundant with ~/.claude.json?

I need to know which file is canonical for Claude Code CLI specifically (not Claude Desktop).

---

## Response

**Claude Code CLI uses a hierarchical MCP server configuration system with `~/.claude.json` as the canonical user-global file (highest priority for global settings), `.claude/mcp.json` or `.mcp.json` for project scope, and `~/.claude/settings.json` primarily for other settings (not the main MCP store). Precedence prioritizes local/project scopes over user/global, with merges adding or overriding from least to most specific.[1][3][4][5]**

### CLI Write Locations
- **`claude mcp add --scope user`**: Writes to `~/.claude.json` at the root level under `mcpServers` (user-global scope); this is the primary user CLI-managed file, though some versions store internally without creating files (inconsistent behavior noted).[1][3]
- **`claude mcp add --scope project`**: Writes to `.claude/mcp.json` or `.mcp.json` in the project root (project-local scope).[1][3]

### Reading and Merge Order
Claude Code CLI reads from all relevant files in this **precedence order** (most specific/highest priority first, overriding conflicts):
1. **Project-local**: `.mcp.json` or `.claude/mcp.json` (or `.claude.json` nested under `projects.{path}.mcpServers` for multi-project).[1][3][4]
2. **User-global**: `~/.claude.json` (`mcpServers` at root).[3][4]
3. **Fallback/other**: `~/.claude/settings.json` (`mcpServers` key, lowest for MCP).[1][4]

- **Merge behavior**: Settings merge with more specific scopes overriding broader ones; same server name in multiple files uses the highest-precedence (e.g., project beats user).[4][5]
- **All three read?** Yes, CLI reads all applicable ones per the hierarchy (not just Desktop-specific).[1][3][4]

### Specific Files
- **`~/.config/claude/mcp.json`**: Not standard for CLI; appears Desktop-specific or non-canonical (no CLI mentions; CLI uses `~/.claude.json` or `~/.claude/`).[1][3] CLI does not read it as primary.
- **`mcpServers` in `~/.claude/settings.json`**: Somewhat redundant/legacy for MCP (CLI favors `~/.claude.json` for MCP); treated as lower-priority global fallback.[1][4]
- **`~/.claude.json` project nesting**: Supports per-project overrides (`projects.{path}.mcpServers`), but project-local `.mcp.json` takes precedence.[1][3]

**Canonical for CLI**: `~/.claude.json` (user) and `.mcp.json`/`.claude/mcp.json` (project); edit directly for transparency, as CLI `add` may not always create files.[1][6]

| Scope | Primary File | CLI `mcp add` Target | Precedence Rank |
|-------|--------------|----------------------|-----------------|
| **User-global** | `~/.claude.json` (`mcpServers`) | `--scope user` | 2 |
| **Project-local** | `.mcp.json` or `.claude/mcp.json` | `--scope project` | 1 (highest) |
| **Settings fallback** | `~/.claude/settings.json` (`mcpServers`) | N/A | 3 (lowest) |[1][3][4]

---

## Citations

1. https://github.com/anthropics/claude-code/issues/3098
2. https://www.claudelog.com/faqs/where-are-claude-code-global-settings/
3. https://inventivehq.com/knowledge-base/claude/where-configuration-files-are-stored
4. https://code.claude.com/docs/en/settings
5. https://code.claude.com/docs/en/mcp
6. https://scottspence.com/posts/configuring-mcp-tools-in-claude-code
7. https://shipyard.build/blog/claude-code-cheat-sheet/
8. https://www.anthropic.com/engineering/claude-code-best-practices

---

## Usage Stats

- Prompt tokens: 202
- Completion tokens: 748
- Total tokens: 950
