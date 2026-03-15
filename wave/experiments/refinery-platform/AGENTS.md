# Refinery Platform -- Codex Context

Read `.ecoroot/common_knowledge.md` for full architecture, design system, API surface, component library, and rules.

## Codex-Specific Deltas

### Execution Contract

- Build verification: `npm run build` must pass after every change
- Never commit from VPS -- local Mac only
- Minimal changes: one concern per commit
- Use existing components from `components/ui/` before creating new ones

### Stack

Next.js 15 / React 19 / Tailwind 4 / TypeScript. Port 3001.

### Algebra-UI Design System

All visual properties are parametric OKLCH (seeds + coefficients in `app/globals.css`). Never hardcode hex/rgb/hsl. Reference `var(--color-*)` tokens. Theme switching = seed overrides only.

### Key Commands

```bash
npm run dev          # localhost:3001
npm run build        # verify before deploy
npm run lint         # ESLint
```

### Agent Coordination

Shared SSOT: `.ecoroot/common_knowledge.md` (Claude, Gemini, Codex all read it). Update there for shared knowledge. Codex-specific notes stay here.
