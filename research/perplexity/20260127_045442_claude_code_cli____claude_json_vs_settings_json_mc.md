# Research: Claude Code CLI ~/.claude.json vs settings.json mcpServers configuration difference 2025 2026

> **Date:** 2026-01-27 04:54:42
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:25c4381d7a4f9749990b2c992911517b3dafef82ca859e3c5e9e4f2700670c5c`
> **Raw JSON:** `raw/20260127_045442_claude_code_cli____claude_json_vs_settings_json_mc.json`

---

## Query

Claude Code CLI ~/.claude.json vs settings.json mcpServers configuration difference 2025 2026

---

## Response

**The `~/.claude.json` file stores runtime state, OAuth tokens, and MCP server connections, while `settings.json` (in `~/.claude/`, `.claude/`, or `.claude/settings.local.json`) configures Claude Code CLI behaviors like permissions, models, and tools.**[2][4]

### Key Differences
| File | Location Options | Primary Purpose | MCP Servers Role | Scope & Overrides |
|------|------------------|-----------------|------------------|-------------------|
| **`~/.claude.json`** | User home (`~/.claude.json`) | Runtime state (e.g., OAuth tokens, active sessions, MCP connections) | Stores configured MCP server details (added via `claude mcp add` or manual edits); acts as persistent state for integrations like external tools/databases[1][2] | Global user state; not overridden by project files (N/A in hierarchy)[2] |
| **`settings.json`** | User: `~/.claude/settings.json`<br>Project: `.claude/settings.json` (team/shared, git-tracked)<br>Local: `.claude/settings.local.json` (personal, gitignored) | Technical settings (e.g., permissions via "allow"/"deny", model selection, output style, hooks, excluded commands)[1][2][4] | References or enables MCP via permissions/tools; does not store server state—use for allowlisting MCP actions (e.g., "mcpServers" for trusted plugins)[1][2] | Hierarchical: Project/local overrides user; CLI flags override all[2][4] |

**Configuration hierarchy (2026 updates):** Enterprise > User (`~/.claude/settings.json`) > Project (`.claude/settings.json`) > Local (`.claude/settings.local.json`) > CLI flags; `~/.claude.json` is separate for state[MCP integrations expanded to 3,000+ services].[2][4]

### MCP Servers Configuration
- **In `~/.claude.json`**: Holds runtime MCP data (e.g., server URLs, auth); managed via CLI like `claude mcp add` for plugins connecting to databases/project tools. Essential for persistence across sessions.[1][2]
- **In `settings.json`**: Defines permissions for MCP use (e.g., `"allow": ["mcp:database-read"]`); no direct server storage—focuses on safe execution modes like "default" (prompts) or "acceptEdits".[1][2][3]
- **Example settings.json snippet** (project `.claude/settings.json`):[2]
  ```
  {
    "permissions": {
      "allow": ["mcp:*", "edit", "bash:git"],
      "deny": ["docker"]
    },
    "mcpServers": { /* Optional refs/allowlist */ }
  }
  ```
- **Best practice**: Use `~/.claude.json` for MCP state, `settings.json` for team permissions; add `.claude/settings.local.json` to `.gitignore` for personal MCP tweaks.[2][4]

**Note**: No 2025-2026 changes alter this core split; v2.1+ adds MCP auto-search but retains file roles.[2] For full MCP setup, run `claude mcp` or `/mcp` in-session.[4]

---

## Citations

1. https://www.eesel.ai/blog/claude-code-configuration
2. https://blakecrosley.com/guide/claude-code
3. https://www.anthropic.com/engineering/claude-code-best-practices
4. https://www.jitendrazaa.com/blog/ai/claude-code-complete-guide-2026-from-basics-to-advanced-mcp-2/
5. https://codewithmukesh.com/blog/claude-code-for-beginners/
6. https://github.com/Cranot/claude-code-guide
7. https://www.whytryai.com/p/claude-code-beginner-guide

---

## Usage Stats

- Prompt tokens: 22
- Completion tokens: 703
- Total tokens: 725
