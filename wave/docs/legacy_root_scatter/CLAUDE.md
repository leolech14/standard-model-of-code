# PROJECT_elements

## Start Here
```bash
./pe boot              # Run boot sequence (shows available moves)
./pe deck deal         # Show certified moves you can execute now
./pe status            # System health check
```

## Decision Deck (AI Governance)

**Before improvising, check available certified moves:**
```bash
./pe deck deal              # Moves whose preconditions are satisfied
./pe deck route "intent"    # Match your intent to a card
./pe deck play CARD-ANA-001 # Execute the card
./pe deck play CARD-ANA-001 --dry-run  # Preview first
```

Each card has: preconditions, steps, expected outcomes, rollback procedures.
**Prefer selecting a card over free-form action when one matches your intent.**

## Rules (Priority 0)
- Never leave uncommitted changes
- Run tests before claiming done
- Provide summary with rationale
- **Check `./pe deck deal` before complex actions**

## Commands (via ./pe)
| Task | Command |
|------|---------|
| **Deck** | `./pe deck [list|deal|route|show]` |
| **Health** | `./pe status` |
| **Analyze** | `./pe collider full <path> --output <dir>` |
| **Test** | `./pe test` |
| **AI Query** | `./pe ask "query"` |
| **Research** | `./pe research "topic"` |
| **Verify** | `./pe verify` (HSL audit) |
| **Sync** | `./pe sync` (cloud mirror) |
| **Viz** | `./pe viz` (3D graph) |

See `wave/docs/agent_school/CLI_GRAMMAR.md` for full CLI reference.

## Projectome (Navigation Topology)

```
P = C ⊔ X    (disjoint union - MECE partition)
```

| Universe | Definition | Doc |
|----------|------------|-----|
| **CODOME** | All executable code | `wave/docs/CODOME.md` |
| **CONTEXTOME** | All non-executable content | `wave/docs/CONTEXTOME.md` |
| **PROJECTOME** | Complete project contents | `wave/docs/PROJECTOME.md` |
| **CONCORDANCES** | Semantic groupings with alignment scores | `wave/docs/CONCORDANCES.md` |
| **GLOSSARY** | All terminology | `wave/docs/GLOSSARY.md` |

## Essential Docs
| Doc | Purpose |
|-----|---------|
| `wave/docs/operations/AGENT_KERNEL.md` | Core rules, micro-loop |
| `wave/docs/agent_school/DOD.md` | Definition of Done |
| `wave/docs/agent_school/CLI_GRAMMAR.md` | ./pe CLI reference for AI agents |
| `wave/docs/agent_school/WORKFLOWS.md` | Git, commit, PR workflows |

## Concordance Entry Points
| Concordance | File |
|-------------|------|
| Collider (analysis engine) | `particle/CLAUDE.md` |
| Context (AI tools) | `wave/docs/deep/AI_USER_GUIDE.md` |

## Deep Docs
Theory, architecture, research: `wave/docs/deep/`

| Doc | Purpose |
|-----|---------|
| `wave/docs/deep/THEORY_AMENDMENT_2026-01.md` | A1:Tools, A2:Dark Matter, A3:Confidence extensions |
