# Archive Index

> **Purpose:** Central index of all archive/legacy directories in PROJECT_elements.
> Updated: 2026-01-31

## Active Archives (11 locations)

### Agent Archives
| Directory | Purpose | Status |
|-----------|---------|--------|
| `.agent/registry/archive/` | Completed/rejected tasks | Active rotation |
| `.agent/specs/archive/` | Old specification documents | Reference only |
| `.agent/sprints/archive/` | Completed sprint records | Historical |

### Context Management Archives
| Directory | Purpose | Status |
|-----------|---------|--------|
| `wave/docs/archive/` | Old documentation | Reference only |
| `wave/docs/theory/archive/` | Superseded theory docs | Reference only |
| `wave/library/legacy/` | Old library code | Dead code |
| `wave/library/intelligence/legacy/` | Old intelligence tools | Dead code |
| `wave/tools/archive/` | Deprecated tools | Reference only |

### Standard Model Archives
| Directory | Purpose | Status |
|-----------|---------|--------|
| `particle/.archive/` | Hidden archive (docs, old code) | Dead code |
| `particle/archive/` | Legacy experiments, audit logs | Mixed |
| `particle/docs/archive/` | Old documentation | Reference only |
| `particle/src/core/viz/assets/archive/` | Old visualization assets | Dead assets |

## Status Legend
- **Active rotation**: Regularly receives new items
- **Reference only**: Keep for historical reference, don't modify
- **Dead code**: Safe to delete if space needed
- **Mixed**: Contains both active and dead items

## Archival Policy
1. **Before archiving**: Check if file is referenced elsewhere
2. **Naming**: Move to nearest `archive/` directory
3. **Don't delete**: Archive first, delete only after 90 days
4. **Document**: Add reason for archival in commit message

## Cleanup Candidates
Files archived > 6 months with no references:
- `wave/library/legacy/` - Full cleanup recommended
- `wave/library/intelligence/legacy/` - Full cleanup recommended
- `particle/.archive/` - Review and cleanup

## See Also
- `governance/DECISIONS.md` - Archival decisions
- `.gitignore` - What's excluded from git
