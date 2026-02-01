# Research: Claude Code CLI settings.json CLAUDE.md rules agents hidden features undocumented

> **Date:** 2026-01-27 03:38:53
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:2357b3e9f990141fbfa8841a30c70a689e3413687a697328d9443f646c484afb`
> **Raw JSON:** `raw/20260127_033853_claude_code_cli_settings_json_claude_md_rules_agen.json`

---

## Query

Claude Code CLI settings.json CLAUDE.md rules agents hidden features undocumented

---

## Response

Claude Code CLI uses a hierarchical **settings.json** configuration system across multiple files for customizing models, permissions, hooks, environment variables, and tools, with precedence from local project overrides down to global user settings.

### Settings Hierarchy and Locations
Settings merge with higher-precedence files overriding lower ones[2][3][5]:
- **Managed settings** (`managed-settings.json`): Highest precedence, IT/DevOps-enforced, non-overridable (e.g., blocked sources)[5].
- **Command-line arguments**: Temporary session overrides[5].
- **Local project** (`.claude/settings.local.json`): Personal, git-ignored overrides[2][3][5].
- **Shared project** (`.claude/settings.json`): Team-shared, git-committed[2][3][5].
- **User/global** (`~/.claude/settings.json`): Applies to all projects[1][2][5].

Legacy or separate configs like `~/.claude/claude.json` or `~/.claude.json` exist but are buggy or deprecated; use `settings.json` primarily[4][5].

**Example user/project settings.json** structure[1][2][5]:
```
{
  "model": "claude-sonnet-4-20250514",
  "maxTokens": 4096,
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "your_key",
    "ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthropic",
    "API_TIMEOUT_MS": "3000000"
  },
  "permissions": {
    "allowedTools": ["Read", "Write", "Bash(git *)"],
    "deny": ["Read(./.env)", "Read(./.env.*)"]
  },
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write(*.py)",
      "hooks": [{
        "type": "command",
        "command": "python -m black $file"
      }]
    }],
    "SessionStart": [{
      "matcher": "startup",
      "hooks": [{
        "type": "command",
        "command": "echo 'conda activate myenv' >> \"$CLAUDE_ENV_FILE\""
      }]
    }]
  },
  "enabledPlugins": {
    "code-formatter@team-tools": true
  }
}
```

### CLAUDE.md Rules
**CLAUDE.md** files provide memory/context loaded at startup, with hierarchy[5]:
- Global: `~/.claude/CLAUDE.md`
- Project: `CLAUDE.md` or `.claude/CLAUDE.md`
- Local: `CLAUDE.local.md`

Used for instructions, rules, or custom prompts (e.g., vibe coding workflows)[6].

### Agents (Subagents)
Custom subagents stored hierarchically[5][6]:
- User: `~/.claude/agents/`
- Project: `.claude/agents/`

Curated examples available for development workflows[6].

### Hidden/Undocumented Features
- **Hooks**: Trigger commands on events (e.g., PostToolUse for auto-formatting, SessionStart for env setup); project-specific via `$CLAUDE_ENV_FILE`[2][5][7].
- **Permissions granularity**: Allow/deny specific tools like `Bash(npm run:*)`; deny rules sometimes ignored (security risk)[2][3][5].
- **MCP servers**: Extend tools/integrations; configured via `~/.claude.json`, `.mcp.json`, or CLI (`claude mcp add`); per-project overrides[5][8].
- **Skills**: Custom prompts invoked via `/skill-name` or auto-loaded[5].
- **CLI flags**: `--output-format json`, `--input-format stream-json`, `--verbose` for logging[2].
- **Custom tools**: Bash scripts for file search (e.g., repo indexing via JSON stdin/stdout)[5].
- **Marketplaces**: Define plugin sources in managed settings (exact matching, non-overridable)[5].

### Troubleshooting and Best Practices
- Validate JSON format; restart CLI (`claude`) after edits; delete/recreate if needed[1].
- Review changes before accepting; deny access to `.env`; use local files for secrets[2].
- Permissions project settings override user ones[5].
- Environment vars settable in settings.json or hooks for team rollout[5].

For full examples, see curated GitHub repos[6]. Deny rules unreliability noted as a common issue[3].

---

## Citations

1. https://docs.z.ai/scenario-example/develop-tools/claude
2. https://shipyard.build/blog/claude-code-cheat-sheet/
3. https://www.eesel.ai/blog/settings-json-claude-code
4. https://tessl.io/blog/configuring-claude-code
5. https://code.claude.com/docs/en/settings
6. https://github.com/feiskyer/claude-code-settings
7. https://www.builder.io/blog/claude-code
8. https://scottspence.com/posts/configuring-mcp-tools-in-claude-code

---

## Usage Stats

- Prompt tokens: 15
- Completion tokens: 954
- Total tokens: 969
