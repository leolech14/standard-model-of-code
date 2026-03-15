# Refinery Platform -- Claude Code Context

@../.ecoroot/common_knowledge.md

## Claude-Specific Deltas

### Workspace Context

This project lives inside PROJECT_elements but has its own design system, component library, and agent context. When working here, this file + common_knowledge.md are your primary context. The parent Elements CLAUDE.md covers the broader ecosystem (Collider, AI tools) which is irrelevant to dashboard frontend work.

Parent: `@../../CLAUDE.md` (only reference when you need Collider/Wave context)

### Path-Scoped Awareness

All component code in this project uses the Algebra-UI soft-token system. When writing or modifying any `.tsx` file:
- Reference `var(--color-*)`, `var(--radius-*)`, `var(--shadow-*)` tokens
- Use Tailwind classes mapped to tokens (`bg-surface`, `text-accent`, `border-danger`)
- Never introduce hex/rgb/hsl -- OKLCH only, through the parametric engine
- Check `app/globals.css` for available tokens before inventing new ones

### Session Continuity

Master plan: `~/.claude/plans/keen-wondering-puddle.md` (474 lines)
Check phase status in common_knowledge.md before starting work. Complete phases sequentially.

### Build Verification

After any code change: `npm run build` must pass before reporting completion.
Deploy path: rsync to VPS, verify at `dashboard.centralmcp.ai/{route}`.

### Agent Coordination

This project has parallel agent context for all three platforms:
- **Claude:** `.claude/CLAUDE.md` (this file) -- uses `@import`, path-scoped rules
- **Gemini:** `GEMINI.md` (project root) -- uses `@import`, persistent memory in `~/.gemini/antigravity/brain/`
- **Codex:** `AGENTS.md` (project root) -- uses CWD-level reading, flat structure

All three import `.ecoroot/common_knowledge.md`. When updating shared knowledge (design tokens, API surface, component inventory, rules), update common_knowledge.md -- it ripples to all agents. Agent-specific deltas stay in the respective wrapper file.

### Contextome Ripple Protocol

When a change occurs that affects agent context:

| What Changed | Update Where | Why |
|-------------|-------------|-----|
| Design token (seed/coefficient) | `app/globals.css` only | CSS calc() auto-propagates; common_knowledge.md describes the system, not the values |
| New component added | `common_knowledge.md` (component inventory) | All agents need to know available components |
| New API endpoint used | `common_knowledge.md` (API surface table) | All agents need to know available endpoints |
| New page/route created | `common_knowledge.md` (navigation + phase status) | All agents need current nav architecture |
| Claude-specific workflow change | This file only | Doesn't affect Gemini/Codex |
| Rule change | `common_knowledge.md` (rules section) | Rules are universal |

The "always-been" principle: after updating docs, write them as if the current state was always the state. No "we changed X to Y" -- just "X is Y." History lives in git, not in documentation.
