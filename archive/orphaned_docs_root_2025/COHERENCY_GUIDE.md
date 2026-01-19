# Coherency Guide for Standard Model of Code

This guide documents the current conflicts across code and docs, explains why they matter, and gives a concrete, ordered path to a coherent system. Treat this as the working instructions for alignment. It is intentionally explicit and opinionated.

## Objectives

1. Establish a single source of truth for schema, taxonomy, and outputs.
2. Normalize confidence scoring and layer semantics across all components.
3. Align CLI behavior, outputs, and docs so they are mutually consistent.
4. Preserve backward compatibility with a clear deprecation timeline.

## System Truth Hierarchy (Must Be Chosen and Enforced)

Pick one and enforce it everywhere (code, docs, JSON schemas, CLI, examples):

1. Canonical schema document (preferred: docs/CANONICAL_SCHEMA.md).
2. Machine-readable JSON schema (STANDARD_MODEL_SCHEMA.json).
3. Runtime output schema (core/unified_analysis.py + tools/prove.py).
4. Naming and terminology guide (docs/NAMING_SCHEMA.md).

If any other source conflicts with these, it must either be updated or marked legacy.

## Conflict Map (What Is Incoherent Right Now)

Each item includes impact, symptoms, and where the conflict is observed. These are the most urgent sources of incoherency.

### 1) Taxonomy Mismatch: 33 vs 167 vs 22

Impact:
- Classifiers, docs, and schemas disagree about what "particle" means.
- Output consumers cannot rely on stable types.

Symptoms:
- STANDARD_MODEL_SCHEMA.json defines 33 particle types.
- docs/ATOMS_REFERENCE.md and patterns/atoms.json define 167 atoms.
- patterns/particle_defs.json defines only 22 particle types for RPBL scoring.

Resolution:
- Decide primary taxonomy (33 or 167).
- If 167 is primary, mark 33 as a derived/summary schema and update the JSON schema accordingly.
- If 33 is primary, document how 167 folds into 33 and ensure classifier output is normalized.

### 2) Missing Node IDs (Schema vs Runtime)

Impact:
- Graph integrity cannot be guaranteed.
- CodebaseState drops nodes without IDs, leading to invisible data loss.

Symptoms:
- Canonical schema requires node IDs.
- Tree-sitter extraction does not set `id`.
- Unified output uses empty IDs, and CodebaseState drops them.

Resolution:
- Generate deterministic IDs during extraction (e.g., file_path:name:line).
- Validate ID uniqueness and fail early if missing.

### 3) Confidence Scale Conflict (0-1 vs 0-100)

Impact:
- Misclassification metrics and filters are off by 100x.
- "High/medium/low" buckets are unreliable.

Symptoms:
- Canonical schema requires 0-1.
- Tree-sitter uses 0-100.
- Unified analysis buckets use 80/50 thresholds.

Resolution:
- Normalize confidence at the extraction boundary.
- Document and enforce a single scale (prefer 0-1 to match schema).

Timestamp requirement:
- Any scoring conflict resolution must include a timestamp in the decision log.
- Use ISO 8601 with timezone (example: 2025-01-14T09:32:11Z).

### 4) Layer Semantics and Allowed Flow

Impact:
- "Layer violations" are judged differently across modules.
- Purpose flow rules can contradict README statements.

Symptoms:
- Purpose field layer order treats Presentation -> Application -> Domain -> Infrastructure as the "downward" flow.
- README states Domain must not depend on Infrastructure.
- Different layer sets exist (TESTING, CROSS_CUTTING, Unknown-only).

Resolution:
- Define the allowed dependency direction explicitly in one place.
- Normalize layer enum values and casing across all code and docs.
- Document testing and cross-cutting behavior explicitly.

### 5) Output Naming and CLI Contract Drift

Impact:
- Users do not know which output file is authoritative.
- `collider viz` expects a graph JSON but README points to proof_output.json.

Symptoms:
- README advertises proof_output.json as the main output.
- Naming schema says collider_output.json should exist.
- Unified analysis writes spectrometer_output/unified_analysis.json.
- viz command expects a graph JSON, not proof_output.json.

Resolution:
- Choose a single primary output filename and format.
- Update CLI help, README, and docs to match.
- Provide a compatibility adapter if older outputs are supported.

### 6) Pipeline Stages vs Proof Metadata

Impact:
- Report metadata does not reflect actual pipeline.
- Automated validation or research claims can be undermined.

Symptoms:
- proof_output.json metadata says 9 stages.
- run_proof clearly runs stage 10 (visualization).

Resolution:
- Align pipeline stage count with actual steps.
- If visualization is optional, clarify in metadata.

## Coherency Urgency (Why This Matters Now)

1. External users will treat docs as authoritative; mismatches erode trust.
2. Output schema drift prevents reliable tooling and automation.
3. ML-assisted or LLM-assisted classifiers rely on stable IDs and scales.
4. Research claims (coverage, accuracy) can be invalidated by mismatched metrics.

## Decision Log Requirements (Mandatory)

Every change that resolves a conflict must add a decision entry with:

- Timestamp (ISO 8601 with timezone)
- Conflict ID (from this guide)
- Decision summary
- Affected files
- Migration impact

Example entry template:

Timestamp: 2025-01-14T09:32:11Z
Conflict: C3 confidence-scale
Decision: normalize all confidence values to 0-1 at extraction
Files: core/tree_sitter_engine.py, core/unified_analysis.py, docs/CANONICAL_SCHEMA.md
Impact: downstream consumers must assume 0-1; update thresholds

## Ordered Resolution Plan (Recommended Sequence)

1) Define canonical taxonomy and schema
- Decide 33 vs 167 and document the mapping if both exist.
- Update STANDARD_MODEL_SCHEMA.json and docs/CANONICAL_SCHEMA.md to match.

2) Normalize IDs
- Add deterministic ID generation at extraction time.
- Ensure all downstream modules use IDs (edges, purpose field, performance).

3) Normalize confidence
- Enforce a single scale at the boundary.
- Update thresholds and docs accordingly.
- Log the decision with timestamp.

4) Align layer semantics
- Decide on allowed dependency direction.
- Normalize enum values (Domain/Application/Infrastructure/Presentation/Testing/CrossCutting).
- Update purpose field and docs to the same definition.

5) Align output contracts and CLI
- Choose a single output artifact as "primary."
- Update CLI, README, and naming schema docs.
- Provide adapters for any legacy outputs.

6) Verify pipeline metadata
- Ensure proof metadata matches actual stages.
- Document any optional stages as optional, not missing.

## Validation Checklist (Use This Before Release)

1. All outputs match canonical schema (fields, types, casing).
2. Every node has a stable, non-empty ID.
3. Confidence values are within the documented scale.
4. Layer enums match the authoritative list.
5. CLI help matches README instructions.
6. Visualization accepts the documented output file without manual conversion.
7. Decision log entries exist for every resolved conflict.

## Conflict IDs (for Decision Logs)

- C1 taxonomy-mismatch
- C2 missing-node-ids
- C3 confidence-scale
- C4 layer-semantics
- C5 output-contract
- C6 pipeline-stage-metadata

## Owner Guidance

If you must choose between backward compatibility and coherence, prefer coherence but document the migration and provide a short-term compatibility adapter.

