======================================================================
CONSOLIDATION REPORT - PROJECT_elements
======================================================================
Generated from: 422 enriched files
Model: llama3.1-8b

======================================================================
1. DUPLICATE FILENAMES (same file in multiple locations)
======================================================================

app.py (5 copies):
  - particle/tests/fixtures/toy_proof_import_invariance_no_import/app.py
    Purpose: A simple test file demonstrating a basic Python application ...
  - particle/tests/fixtures/toy_entry_fastapi/app.py
    Purpose: Provides a FastAPI entrypoint fixture for testing purposes....
  - particle/tests/fixtures/toy_entry_flask/app.py
    Purpose: Provides a simple Flask application with multiple routes for...
  - particle/tests/fixtures/toy_proof_import_invariance_with_import/app.py
    Purpose: A test fixture demonstrating the import invariance property ...
  - particle/tests/fixtures/toy_entry_typer/app.py
    Purpose: Provides a Typer CLI entrypoint fixture for testing purposes...

cli.py (3 copies):
  - particle/cli.py
    Purpose: Provides a unified command-line interface for the Standard M...
  - particle/tests/fixtures/toy_entry_click/cli.py
    Purpose: Provides a Click CLI entrypoint fixture for testing purposes...
  - wave/tools/docling_processor/cli.py
    Purpose: Provides a command-line interface for batch PDF processing u...

a.py (3 copies):
  - particle/tests/fixtures/toy_import_file_node/pkg/a.py
    Purpose: Provides a test fixture for importing a module from a packag...
  - particle/tests/fixtures/toy_import_internal/pkg/a.py
    Purpose: Provides a simple test fixture for demonstrating internal im...
  - particle/tests/fixtures/toy_import_ambiguous/pkg/a.py
    Purpose: This file demonstrates an ambiguous import statement for the...

topology_reasoning.py (2 copies):
  - particle/src/core/topology_reasoning.py
    Purpose: Provides topological reasoning and code health analysis for ...
  - particle/src/core/pipeline/stages/topology_reasoning.py
    Purpose: This file implements a stage in a data processing pipeline t...

purpose_intelligence.py (2 copies):
  - particle/src/core/purpose_intelligence.py
    Purpose: Computes quality scores measuring how well code serves the h...
  - particle/src/core/pipeline/stages/purpose_intelligence.py
    Purpose: Calculates quality scores and purpose clarity metrics for a ...

purpose_field.py (2 copies):
  - particle/src/core/purpose_field.py
    Purpose: This file provides a data model for detecting the hierarchic...
  - particle/src/core/pipeline/stages/purpose_field.py
    Purpose: Assigns architectural purpose to each node in the codebase b...

semantic_cortex.py (2 copies):
  - particle/src/core/semantic_cortex.py
    Purpose: Extracts high-level business concepts from code identifiers ...
  - particle/src/core/pipeline/stages/semantic_cortex.py
    Purpose: This file implements a stage in a pipeline that extracts sem...

graph_analytics.py (2 copies):
  - particle/src/core/pipeline/stages/graph_analytics.py
    Purpose: This file implements a stage in a pipeline that computes gra...
  - wave/tools/graphrag/graph_analytics.py
    Purpose: Provides a class for analyzing a Neo4j graph database, speci...

repo_mapper.py (2 copies):
  - wave/tools/repo_mapper.py
    Purpose: Repository mapper tool for analyzing and processing file met...
  - .agent/intelligence/repo_mapper.py
    Purpose: This file generates various CSV and JSON files for repositor...

config.py (2 copies):
  - wave/tools/docling_processor/config.py
    Purpose: Provides configuration management for Docling batch processo...
  - wave/tools/ai/analyze/config.py
    Purpose: Provides configuration settings for the analyze module, load...

output.py (2 copies):
  - wave/tools/docling_processor/output.py
    Purpose: Defines dataclasses for output data of a Docling processor, ...
  - wave/tools/ai/analyze/output.py
    Purpose: Provides a dataclass-based output module for AI analysis res...

collider_to_neo4j.py (2 copies):
  - wave/tools/graphrag/collider_to_neo4j.py
    Purpose: This file imports Collider output data into a Neo4j graph da...
  - .agent/tools/collider_to_neo4j.py
    Purpose: Imports Collider's unified_analysis.json into Neo4j database...

gemini_status.py (2 copies):
  - wave/tools/ai/gemini_status.py
    Purpose: Provides a tool for real-time observability and diagnostics ...
  - wave/tools/maintenance/gemini_status.py
    Purpose: Provides a tool for real-time observability and diagnostics ...

boundary_analyzer.py (2 copies):
  - wave/tools/ai/boundary_analyzer.py
    Purpose: Validates declared boundaries (CODOME/CONTEXTOME/CONCORDANCE...
  - wave/tools/maintenance/boundary_analyzer.py
    Purpose: Validates declared boundaries (CODOME/CONTEXTOME/DOMAINS) ag...

play_card.py (2 copies):
  - wave/tools/ai/deck/play_card.py
    Purpose: This file provides a tool to execute a certified move from t...
  - .agent/tools/play_card.py
    Purpose: This file provides a tool to play a Decision Deck card, logg...

======================================================================
2. FILES WITH SIMILAR PURPOSE (potential merge candidates)
======================================================================

'GENERATE' tools (33 files):
  .agent/: 3 files
  wave/: 8 files
  particle/: 18 files
  tools/: 4 files

'EXTRACT' tools (26 files):
  .tools_venv/: 1 files
  particle/: 24 files
  tools/: 1 files

'ANALYZE' tools (22 files):
  .agent/: 2 files
  wave/: 7 files
  particle/: 13 files

'VALIDATE' tools (15 files):
  .agent/: 4 files
  wave/: 3 files
  particle/: 8 files

'SCAN' tools (5 files):
  .agent/: 2 files
  particle/: 1 files
  tools/: 2 files

'PARSE' tools (4 files):
  wave/: 2 files
  particle/: 2 files

======================================================================
3. SCATTERED FUNCTIONALITY (same semantic tags, different locations)
======================================================================

'code-analysis' (59 files across 4 directories):
  particle/: 47
  wave/: 9
  .agent/: 2
  tools/: 1

'data-validation' (49 files across 5 directories):
  particle/: 27
  wave/: 15
  tools/: 3
  .agent/: 3
  scripts/: 1

'api-endpoint' (38 files across 3 directories):
  wave/: 22
  particle/: 13
  scripts/: 3

'data-processing' (30 files across 4 directories):
  particle/: 19
  wave/: 7
  .agent/: 3
  scripts/: 1

'data-analysis' (22 files across 3 directories):
  particle/: 15
  wave/: 5
  .agent/: 2

'configuration' (14 files across 3 directories):
  wave/: 8
  particle/: 4
  tools/: 2

'automation' (14 files across 3 directories):
  .agent/: 7
  wave/: 4
  particle/: 3

'validation' (12 files across 3 directories):
  particle/: 8
  wave/: 3
  .agent/: 1

'pipeline' (11 files across 4 directories):
  particle/: 7
  .agent/: 2
  tools/: 1
  wave/: 1

'code-quality' (11 files across 3 directories):
  particle/: 9
  tools/: 1
  wave/: 1

======================================================================
4. CONSOLIDATION RECOMMENDATIONS
======================================================================

[HIGH] MERGE #1
  Reason: Identical purpose: "Provides a tool for real-time observability and di..."
  Files:
    - wave/tools/ai/gemini_status.py
    - wave/tools/maintenance/gemini_status.py

[MEDIUM] CONSOLIDATE #2
  Reason: 77 validation tools scattered across repo
  Files:
    - tools/verify_counts.py
    - tools/verify_placeholders.py
    - tools/score_reference_images.py
    - tools/verify_links.py
    - particle/tools/validate_ui.py
    ... and 72 more

======================================================================
5. DIRECTORY HEALTH ANALYSIS
======================================================================

Top directories and their dominant tags:
  particle/src: 721 files → code-analysis(43), pipeline-stage(20), data-processing(17)
  wave/tools: 565 files → api-endpoint(21), wave(19), data-validation(14)
  particle/tests: 248 files → testing(47), python(10), fixtures(10)
  .agent/tools: 235 files → automation(7), yaml(6), task-management(5)
  particle/tools: 135 files → data-validation(4), batch-processing(4), automation(3)
  particle/scripts: 45 files → data-analysis(3), data-validation(2), visualization(2)
  wave/services: 25 files → neo4j(3), data-retrieval(2), wave(2)
  wave/docs: 10 files → configuration-validation(1), path-diagnosis(1), yaml-parsing(1)
  .tools_venv/bin: 10 files → command-line-tool(1), json-data(1), jmespath-expression(1)
  .agent/intelligence: 10 files → data-analysis(1), documentation(1), repository-mapping(1)
  tools/generate_reader_config.py: 5 files → configuration(1), project-structure(1), quarto(1)
  tools/file_scanner.py: 5 files → directory-scanning(1), metadata-extraction(1), 3d-visualization(1)
  tools/verify_counts.py: 5 files → data-validation(1), pipeline(1), code-analysis(1)
  tools/verify_placeholders.py: 5 files → placeholder-detection(1), markdown(1), directory-scanning(1)
  tools/score_reference_images.py: 5 files → image-analysis(1), quality-assessment(1), data-validation(1)

======================================================================
END OF REPORT
======================================================================
