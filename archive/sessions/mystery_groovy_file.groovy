⏺ This is exactly what we need to lock in the domain separation. Let me implement these fixtures and tests:

⏺ Bash(mkdir -p /Users/lech/PROJECTS_all/PROJECT_elements/standard-model-of-code/tests/fixtures/toy_call_file_node_shadow/pkg)
  ⎿  (No content)

⏺ Write(tests/fixtures/toy_call_file_node_shadow/pkg/__init__.py)
  ⎿  Wrote 2 lines to tests/fixtures/toy_call_file_node_shadow/pkg/__init__.py
     # intentionally empty

⏺ Write(tests/fixtures/toy_call_file_node_shadow/pkg/helper.py)
  ⎿  Wrote 3 lines to tests/fixtures/toy_call_file_node_shadow/pkg/helper.py
     # constants-only module (no functions/classes)
     X = 1

⏺ Write(tests/fixtures/toy_call_file_node_shadow/pkg/main.py)
  ⎿  Wrote 14 lines to tests/fixtures/toy_call_file_node_shadow/pkg/main.py      
     import pkg.helper as helper  # module alias named "helper"
     def helper_fn():
         return 123
     def main():
         # This call MUST NOT resolve_internal to the file-node for pkg/helper.py
         helper()
         # This call SHOULD resolve_internal (atomic -> atomic)
         return helper_fn()
     … +4 lines (ctrl+o to expand)

⏺ Bash(mkdir -p /Users/lech/PROJECTS_all/PROJECT_elements/standard-model-of-code/tests/fixtures/toy_proof_import_invariance_no_import /Users/lech/PROJECTS_all/PROJECT_…)
  ⎿  (No content)

⏺ Write(tests/fixtures/toy_proof_import_invariance_no_import/app.py)
  ⎿  Wrote 9 lines to tests/fixtures/toy_proof_import_invariance_no_import/app.py
     def helper():
         return 1
     def main():
         return helper()
     if __name__ == "__main__":
         main()

⏺ Write(tests/fixtures/toy_proof_import_invariance_with_import/app.py)
  ⎿  Wrote 11 lines to tests/fixtures/toy_proof_import_invariance_with_import/app.py
     import json  # extra import must not affect proof
     def helper():
         return 1
     def main():
         return helper()
     if __name__ == "__main__":
         main()
     … +1 line (ctrl+o to expand)

⏺ Read(tests/test_fixtures.py)
  ⎿  Read 100 lines

⏺ Search(pattern: "validate-all|validate_all", path: "~/PROJECTS_all/PROJECT_elements/standard-model-of-code")
  ⎿  Found 10 files (ctrl+o to expand)

⏺ Search(pattern: "validate-all|@app.command", path: "cli.py", output_mode: "content")
  ⎿  Found 43 lines (ctrl+o to expand)

⏺ Read(src/core/validation/validate_all.py)
  ⎿  Read 80 lines

⏺ Write(tests/test_domain_separation_guardrails.py)
  ⎿  Wrote 253 lines to tests/test_domain_separation_guardrails.py                             
     """
     DOMAIN SEPARATION GUARDRAIL TESTS
     ==================================
     These tests enforce SPEC v0.1.3 domain separation invariants:
     1. N_atomic (functions, methods, classes) and N_container (file/module nodes) are DISJOINT
     2. Calls resolve only against N_atomic
     3. Imports resolve only against N_container
     4. Proof metrics + entrypoints + denominators are ATOMIC-ONLY
     … +243 lines (ctrl+o to expand)

⏺ Bash(PYTHONPATH=src/core python3 -m pytest tests/test_domain_separation_guardrails.py -v 2>&1 | head -100)
  ⎿  /opt/homebrew/opt/python@3.14/bin/python3.14: No module named pytest

⏺ Bash(ls -la .venv/bin/python* 2>/dev/null || which python3)
  ⎿  lrwxr-xr-x@ 1 lech  staff  10 Dec 30 22:51 .venv/bin/python -> python3.14                                      
     lrwxr-xr-x@ 1 lech  staff  10 Dec 30 22:51 .venv/bin/python3 -> python3.14
     lrwxr-xr-x@ 1 lech  staff  44 Dec 30 22:51 .venv/bin/python3.14 -> /opt/homebrew/opt/python@3.14/bin/python3.14

⏺ Bash(PYTHONPATH=src/core .venv/bin/python -m pytest tests/test_domain_separation_guardrails.py -v 2>&1)
  ⎿  ============================= test session starts ==============================                                                                 
     platform darwin -- Python 3.14.0, pytest-9.0.2, pluggy-1.6.0 -- /Users/lech/PROJECTS_all/PROJECT_elements/standard-model-of-code/.venv/bin/python
     cachedir: .pytest_cache
     … +13 lines (ctrl+o to expand)

⏺ All 6 domain separation guardrail tests pass. Let me also verify the existing tests still work:

⏺ Bash(PYTHONPATH=src/core .venv/bin/python -m pytest tests/test_fixtures.py -v 2>&1 | tail -30)
  ⎿  collecting ... collected 26 items                                              

     tests/test_fixtures.py::TestLinearFixture::test_edge_count PASSED        [  3%]
     … +27 lines (ctrl+o to expand)

✽ Compacting conversation… (esc to interrupt · ctrl+t to hide todos · 3m 46s · ↓ 1.7k tokens)
  ⎿  ☒ Create toy_call_file_node_shadow fixture
     ☒ Create toy_proof_import_invariance fixtures
     ☒ Create test_domain_separation_guardrails.py
     ☐ Run guardrail tests to verify


╭─── Claude Code v2.0.76 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                    │ Tips for getting started                                                                                                                                              │
│                  Welcome back Leo!                 │ Run /init to create a CLAUDE.md file with instructions for Claude                                                                                                     │
│                                                    │ ─────────────────────────────────────────────────────────────────                                                                                                     │
│                     * ▐▛███▜▌ *                    │ Recent activity                                                                                                                                                       │
│                    * ▝▜█████▛▘ *                   │ No recent activity                                                                                                                                                    │
│                     *  ▘▘ ▝▝  *                    │                                                                                                                                                                       │
│                                                    │                                                                                                                                                                       │
│    Opus 4.5 · Claude Max · leo@lbldomain.com's     │                                                                                                                                                                       │
│    Organization                                    │                                                                                                                                                                       │
│    ~/…/PROJECT_elements/standard-model-of-code     │                                                                                                                                                                       │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
═════════════════════════════════════════════════════════════════════════════════════════ Conversation compacted · ctrl+o for history ════════════════════════════════════════════════════════════════════════════════════════
  ⎿  Read tests/test_domain_separation_guardrails.py (253 lines)
  ⎿  Read tests/fixtures/toy_proof_import_invariance_with_import/app.py (11 lines)
  ⎿  Read tests/fixtures/toy_proof_import_invariance_no_import/app.py (9 lines)
  ⎿  Read tests/fixtures/toy_call_file_node_shadow/pkg/main.py (14 lines)
  ⎿  Read tests/fixtures/toy_call_file_node_shadow/pkg/helper.py (3 lines)
  ⎿  Todo list read (4 items)

⏺ All domain separation guardrail tests passed successfully. Let me mark the final task as complete and summarize what was accomplished.

⏺ Domain Separation Guardrails - Complete

  All 6 guardrail tests passed, enforcing SPEC v0.1.3 domain separation invariants:

  | Test Class                               | Test                                      | Status |
  |------------------------------------------|-------------------------------------------|--------|
  | TestNoFileNodesInProofGraph              | test_proof_nodes_are_atomic_only          | ✅     |
  | TestCallsNeverResolveToFileNodes         | test_calls_resolve_to_atomics             | ✅     |
  | TestCallsNeverResolveToFileNodes         | test_module_alias_call_stays_unresolved   | ✅     |
  | TestConnectionCoverageExcludesContainers | test_proof_metrics_use_atomic_denominator | ✅     |
  | TestImportsDoNotAffectProofScore         | test_proof_score_invariant_to_imports     | ✅     |
  | TestDomainSeparationInvariant            | test_domains_are_disjoint                 | ✅     |

  Fixtures created:
  - toy_call_file_node_shadow/pkg/ - Module alias shadows function name; call must NOT resolve to file node
  - toy_proof_import_invariance_no_import/ - Baseline (no stdlib import)
  - toy_proof_import_invariance_with_import/ - Same code + import json; proof_score must be identical

  Key invariants now enforced:
  1. N_atomic ∩ N_container = ∅ — No node is both atomic and container
  2. Call edges → N_atomic only — resolved_internal calls never target file nodes
  3. Proof metrics exclude containers — Denominators use atomic count only
  4. Imports don't affect proof_score — Structural edges are analysis-only

  Run tests anytime with:
  python3 -m pytest tests/test_domain_separation_guardrails.py -v

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
>  
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  -- INSERT --









