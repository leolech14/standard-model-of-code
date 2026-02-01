# Research: Claude Code CLI: How do project-scoped MCP servers work in ~/.claude.json?

I see this structure:
``...

> **Date:** 2026-01-27 04:54:33
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:7bc612b797d4063de66a335b0b3cf6b95beb0746f0bfaddd31151d84a7355251`
> **Raw JSON:** `raw/20260127_045433_claude_code_cli__how_do_project_scoped_mcp_servers.json`

---

## Query

Claude Code CLI: How do project-scoped MCP servers work in ~/.claude.json?

I see this structure:
```json
{
  "mcpServers": { ... global servers ... },
  "projects": {
    "/Users/me/my-project": {
      "mcpServers": { ... project-specific servers ... }
    }
  }
}
```

Questions:
1. When I run `claude mcp add --scope project myserver -- command args`, does it write to ~/.claude.json under projects.{cwd} or to .mcp.json in the project root?
2. What is the difference between 'local' scope and 'project' scope for MCP?
3. If I have a server in both global mcpServers and projects.{path}.mcpServers, which takes precedence?
4. How do I properly clean up old project-scoped servers for projects that no longer exist?
5. Is there a `claude mcp remove` command and does it handle project scope correctly?

---

## Response

Based on the search results, I can answer some of your questions, though the results don't contain complete information about all aspects of ~/.claude.json's internal structure.

## Project-Scoped MCP Server Storage

**When you run `claude mcp add --scope project`, it writes to `.mcp.json` in the project root, not to ~/.claude.json.**[1] Project-scoped servers are stored in a `.mcp.json` file designed to be checked into version control, ensuring all team members have access to the same MCP tools.[1] This is fundamentally different from local-scoped servers, which are stored in `~/.claude.json` in your home directory.[1]

## Local vs. Project Scope

The key differences are:

- **Local scope** (default): Stores configurations in `~/.claude.json` and is personal to you in the current project.[6] Use this for personal servers, experimental configurations, or sensitive credentials specific to one project.[1]

- **Project scope**: Stores configurations in `.mcp.json` at your project root and is shared with your team via version control.[1] Use this for team-shared servers, project-specific tools, or services required for collaboration.[1]

Additionally, there is a **user scope** available via `--scope user`, which stores configurations globally in `~/.claude.json` and makes servers available across all your projects.[1][4]

## Precedence for Duplicate Servers

If you have a server configured at multiple scopes with the same name, **local-scoped servers take precedence first, followed by project-scoped servers, and finally user-scoped servers.**[1] This design ensures that personal configurations can override shared ones when needed.

## Cleanup and Removal Commands

The search results do not contain information about removing project-scoped servers, how to clean up configurations for defunct projects, or whether a `claude mcp remove` command exists. You may need to consult the official Claude Code documentation or community resources for guidance on these administrative tasks.

## Important Note on Project-Scoped Servers

For security, Claude Code will **prompt for approval before using project-scoped servers** from `.mcp.json` files, ensuring you maintain control over which MCP servers can access your project.[5]

---

## Citations

1. https://code.claude.com/docs/en/mcp
2. https://developer.sailpoint.com/docs/extensibility/mcp/integrations/claude-code/
3. https://github.com/anthropics/claude-code/issues/5963
4. https://www.youtube.com/watch?v=DfWHX7kszQI
5. https://docs.endor.dev/cli/mcp/claude-code/
6. https://liblab.com/docs/mcp/howto-connect-mcp-to-claude
7. https://scottspence.com/posts/configuring-mcp-tools-in-claude-code
8. https://docs.trunk.io/ci-autopilot/overview/use-mcp-server/configuration/claude-code-cli

---

## Usage Stats

- Prompt tokens: 205
- Completion tokens: 468
- Total tokens: 673
