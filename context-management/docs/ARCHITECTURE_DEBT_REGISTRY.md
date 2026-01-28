# Architecture Debt Registry
> "The map is not the territory... but we fix the map."

| Status | Discrepancy | Location found | Correction needed | Severity | AI Verdict | FS Verified |
| --- | --- | --- | --- | --- | --- | --- |
| [x] | `Context DOM` terminology | `ARCHITECTURE_INVENTORY.md` | Rename to Contextome | Low | REJECT | N/A |
| [ ] | Broken `pipeline.py` refs | 3 docs in `research/gemini/` | Fix paths | High | PASS | ✓ 3 files |
| [x] | `GraphEngine` vs `GraphRAGService` | `analyze.py` | Fixed | High | N/A | N/A |
| [ ] | Neo4j Schema Fragility | `graph_rag_service.py:201` | Robust queries | Medium | PASS | ✓ 5 refs |
| [ ] | Hardcoded Panel IDs | `panel-system.js` | Extract to config | Medium | PASS | ✓ 7 refs |
| [ ] | Implicit Globals | `panel-system.js` | Inject deps | Low | PASS | ✓ 9 refs |
| [ ] | Root MD Clutter | `PROJECT_elements/` | Move to `docs/` | Low | PASS | ✓ 13 files |
| [ ] | Large Artifact | `unified_analysis.json` | Move or ignore | Low | PASS | ✓ 28MB |
| [ ] | Loose Scripts | `change_neo4j_password.py` | Move to `tools/ops/` | Low | PASS | ✓ 2 files |
| [ ] | Orphaned Directories | `experiments/`, etc. | Archive | Medium | PASS | ✓ 4 dirs |
| [ ] | Legacy Report Dirs | `*_report/` | Move to `reports/` | Low | PASS | ✓ 3 dirs |
| [ ] | Redundant Map | `PROJECT_MAP.md` | Delete | Low | PASS | ✓ exists |
| [ ] | Dead-Letter Attention | `semantic_finder.py` | Integrate into `Refinery` | High | PASS | ✓ Logic found |

