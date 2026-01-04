# THEORY IMPLEMENTATION MAP

This map ties THEORY invariants to enforcement points and tests.
Scope: resolution_contract, proof_metrics, shim_policy, validate_all_workflow.

## Invariant Map

1) Resolution is tri-state on disk.
- Rule: Emit only resolved_internal | external | unresolved to artifacts.
- Code: `src/core/output_factory.py` `UnifiedOutputBuilder._normalize_edge`
- Tests: `tests/test_resolution_semantics.py::test_output_normalizes_resolution_to_tristate`

2) Resolution semantics are target-only.
- Rule: resolved_internal means target resolves to a node in N.
- Code: `src/core/edge_extractor.py` `resolve_edges`
- Tests: `tests/test_resolution_semantics.py::test_resolve_edges_assigns_resolution`

3) Graph-internal edges require both endpoints in N.
- Rule: internal edges are source ∈ N AND target ∈ N, even if resolution is resolved_internal.
- Code: `src/core/graph_metrics.py` `_filter_internal`
- Tests: `tests/test_graph_internal_semantics.py::test_graph_internal_requires_both_endpoints`

4) Proof graph filter is strict.
- Rule: proof edges are only calls + resolved_internal.
- Code: `src/core/validation/self_proof.py` `_build_real_call_graph`
- Tests: `tests/test_fixtures.py::TestLinearFixture::test_all_resolved_internal`

5) Entrypoint policy is rule-based only.
- Rule: entrypoints are detected by rules; indegree fallback is forbidden.
- Code: `src/core/validation/self_proof.py` `_is_entry_point`, `_calculate_reachability`
- Tests: `tests/test_fixtures.py::TestEntryMainFixture::test_main_is_entry`,
  `tests/test_fixtures.py::TestEntryClickFixture::test_cli_is_entry`,
  `tests/test_fixtures.py::TestEntryFastAPIFixture::test_handlers_are_entries`,
  `tests/test_fixtures.py::TestEntryPytestFixture::test_test_functions_are_entries`

6) Shim policy prevents phantom init files when excluded.
- Rule: when include_init=False, __init__.py is treated as shim and filtered from phantom checks.
- Code: `src/core/validation/self_proof.py` `_apply_shim_policy`
- Tests: `tests/test_shim_policy.py::test_self_proof_exclude_init_shim_policy`

7) Metadata alignment is enforced by the canonical workflow.
- Rule: validate-all produces aligned run_id/target_path and validators fail fast on mismatch.
- Code: `src/core/validation/validate_all.py` `run_validate_all`,
  `src/core/validation/file_validator.py` `_assert_metadata_consistency`,
  `src/core/validation/self_proof.py` `_validate_metadata_alignment`
- Tests: `tests/test_metadata_alignment.py::test_file_validator_metadata_mismatch_raises`,
  `tests/test_metadata_alignment.py::test_self_proof_metadata_mismatch_raises`

8) Structural vs proof separation is explicit in bundle outputs.
- Rule: bundle manifest must only expose structural_* keys, never metrics/entrypoints.
- Code: `src/core/app_bundle.py` `export_app_bundle`
- Tests: `tests/test_bundle_contract.py::test_bundle_completeness`

9) Import resolution is structural only (module → file → node).
- Rule: import edges may resolve internal modules to node ids without changing proof rules.
- Code: `src/core/edge_extractor.py` `resolve_import_target_to_file`, `resolve_edges`;
  `src/core/unified_analysis.py` stats fields `import_resolution`, `top_unresolved_import_roots`
- Tests: `tests/test_import_resolution.py::test_import_internal_resolves`,
  `tests/test_import_resolution.py::test_import_ambiguous_remains_unresolved`,
  `tests/test_import_resolution.py::test_import_resolves_to_file_node`

10) File nodes exist for every scanned Python file.
- Rule: emit a file-level node per `.py` file; use file-node ids for import targets.
- Code: `src/core/unified_analysis.py` `_emit_file_nodes`;
  `src/core/edge_extractor.py` `file_node_id`, `_collect_file_node_ids`
- Tests: `tests/test_import_resolution.py::test_import_resolves_to_file_node`

## Mismatches / Open Holes

- Import resolution does not handle relative imports or aliasing; unresolved is expected.

## Theory-Derived Roadmap (Next 2–3 Steps)

1) Resolve relative imports and aliasing without guessing.
2) Improve call graph qualification for attribute/alias targets (still strict).
3) Add entrypoint allowlist config with fixture gates.
