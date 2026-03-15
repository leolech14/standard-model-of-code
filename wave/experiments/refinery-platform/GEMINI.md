# Refinery Platform -- Gemini Context

@.ecoroot/common_knowledge.md

## Gemini-Specific Deltas

### Role

Exploration, research, design system analysis. When working on the Refinery Platform:
- Reference common_knowledge.md for full architecture, component library, API surface
- The Algebra-UI design system (soft tokens via OKLCH seeds + coefficients) is in `app/globals.css`
- All visual properties are parametric -- understand the genotype/phenotype model before suggesting changes

### Preferred Output

- Diffs over narrative when proposing code changes
- Visual thinking for layout and component architecture
- Bullet points over paragraphs for status reports

### Persistent Memory

If you've stored context about this project in `~/.gemini/antigravity/brain/`, reference it. The design system, component library, and API surface are documented in common_knowledge.md and should be the canonical source.

### Parent Context

This project lives inside PROJECT_elements (Wave hemisphere). For broader context:
@../../.gemini/context/brain.md

### Agent Coordination

All three agents (Claude, Gemini, Codex) share `.ecoroot/common_knowledge.md` as SSOT. When updating shared knowledge, update that file. Gemini-specific observations stay here.

### Key Constraint

Never suggest hex/rgb/hsl colors. This project is OKLCH-only, parametric. Propose changes as seed or coefficient adjustments, not raw values.
