# Governance Index

> **Purpose:** Project standards, decisions, and operational guides
> Updated: 2026-01-31

## Core Documents

| Document | Purpose |
|----------|---------|
| `ROADMAP.md` | Strategic direction and milestones |
| `ROADMAP_ENGINE.md` | Roadmap execution methodology |
| `DECISIONS.md` | Architectural decision records |
| `DEFINITION_OF_DONE.md` | Completion criteria |
| `QUALITY_GATES.md` | G1-G10 quality checkpoints |

## Operational Guides

| Document | Purpose |
|----------|---------|
| `QUICK_START.md` | Getting started guide |
| `BEST_PRACTICES.md` | Development standards |
| `CONTRIBUTING.md` | Contribution guidelines |
| `CHANGELOG.md` | Release history |

## Architecture

| Document | Purpose |
|----------|---------|
| `ARCHITECTURE_AUDIT_2026.md` | Current architecture assessment |
| `REPO_STRUCTURE.md` | Directory organization |
| `TOPOLOGY_MAP.md` | System topology |
| `PIPELINES.md` | Data pipeline documentation |
| `THE_MISSING_MANUAL.md` | Undocumented conventions |

## Technical

| Document | Purpose |
|----------|---------|
| `TECH_DEBT.md` | Technical debt registry (TD-001 to TD-004) |
| `ARCHIVE_INDEX.md` | Archive locations and status |

## Visual Documentation (Quarto)

| Document | Purpose |
|----------|---------|
| `VISUAL_GUIDE.qmd` | Visual documentation guide |
| `MERMAID_MASTERCLASS.qmd` | Mermaid diagram tutorial |
| `_quarto.yml` | Quarto configuration |
| `theme.scss`, `style.css` | Styling |

## Staging Area

| Directory | Contents |
|-----------|----------|
| `staging/audits/` | In-progress audits |
| `staging/specs/` | Draft specifications |
| `staging/reports/` | Pending reports |

## Document Lifecycle

```
Draft → staging/[type]/
Review → governance/[name].md
Archive → governance/staging/archive/ (if deprecated)
```

## See Also

- `.agent/` - Agent configuration
- `docs/` - User-facing documentation
- `wave/docs/` - Wave realm docs
