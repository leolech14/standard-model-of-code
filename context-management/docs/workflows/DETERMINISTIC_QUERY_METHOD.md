# Deterministic Implementation Workflow
# Research workflow for converting requirements → executable tasks

workflow_id: deterministic_implementation
version: 1.0.0
created: 2026-01-27

# Purpose
description: >
  Converts vague requirements into deterministically executable tasks
  via iterative research queries with exact specifications.

# Method
method: >
  1. Identify requirement (e.g., "implement GraphRAG")
  2. Formulate deterministic query with:
     - Exact context (numbers, current state)
     - Specific questions (numbered, measurable)
     - Format demands (copy-paste, no theory)
     - Output specification (commands, code, costs)
  3. Query Perplexity (or equivalent research engine)
  4. Extract: Code, parameters, costs, timeline
  5. Validate with Gemini (repository alignment)
  6. Iterate until confidence ≥95%
  7. Generate task with step-by-step instructions

# Input Requirements
inputs:
  - requirement: Vague goal or feature request
  - context: Current state with exact numbers
  - constraints: Budget, timeline, technology stack
  - target_confidence: Minimum acceptable (default: 95%)

# Query Structure Template
query_template: |
  CONTEXT: [Exact current state with numbers]
  - System: [Specific metrics]
  - Data: [Specific volumes]
  - Goal: [Specific targets]

  QUESTIONS: [Numbered, specific]
  1. Exact [Tool] commands for [Context]?
  2. Parameters: [Metric] for [Target]?
  3. Cost: Precise USD for [Volume]?

  CONSTRAINTS:
  - No theory
  - Only ACTIONABLE
  - Copy-paste ready
  - Exact (not approximate)

  Provide: [Exact deliverables list]

# Output Format
outputs:
  task_yaml:
    structure: >
      - Step-by-step instructions
      - Copy-paste commands
      - Exact parameters (no ranges)
      - Precise costs
      - Measurable validation criteria
      - 4D confidence scores

  code_artifacts:
    - Python scripts (working code)
    - Cypher queries (exact commands)
    - Config files (specific values)
    - Deployment files (Docker, etc.)

# Validation Criteria
validation:
  confidence_threshold: 95%
  dimensions:
    - factual: Can we execute this? (code works)
    - alignment: Does this serve goal?
    - current: Fits existing architecture?
    - onwards: Foundation for future?

  success_criteria:
    - All 4 dimensions ≥95%
    - Code is copy-paste ready
    - Costs calculated to cents
    - Timeline in hours (not estimates)

# Example Application (This Session)
example:
  requirement: "Implement GraphRAG for knowledge graph"

  deterministic_query: >
    "Complete GraphRAG implementation for production:
     CURRENT: Neo4j 5,284 nodes
     TARGET: 15-30 communities via Leiden
     COST: Calculate for 5.3M tokens
     Provide: EXACT commands, parameters, code (no theory)"

  result:
    - 58 academic sources
    - Complete production guide
    - Exact Cypher commands
    - Exact costs: $483 + $220/month
    - Timeline: 21.5 hours
    - Confidence: 93%+

  tasks_generated:
    - Task #4: Leiden (exact parameters)
    - Task #6: Cytoscape.js (working code)
    - Task #7: Batch API (precise cost)
    - Task #8: Validation (50 queries)

# When to Use
use_cases:
  - Converting vague feature requests → implementations
  - Research validation → executable plans
  - Architecture decisions → specific configurations
  - Cost estimation → precise budgets
  - Any "how do we build X?" → "here's exact code for X"

# Integration Points
integrations:
  - ACI analyze.py: Add as research mode
  - Task registry: Auto-enrich tasks with this workflow
  - BARE: Use for opportunity → task conversion
  - Refinery: Research results become implementation guides

# Comparison to Other Workflows
vs_theoretical_discussion:
  difference: "Theory explores concepts; Deterministic demands executables"
  when_to_use_deterministic: "When you need to BUILD, not understand"

vs_validation_trio:
  difference: "Validation confirms correctness; Deterministic generates code"
  when_to_use_deterministic: "When you need WHAT to build, not IF it's correct"

# Success Metrics
metrics:
  - Query → Answer time: <5 minutes (Perplexity research)
  - Answer → Task conversion: <30 minutes (extraction)
  - Task → Execution readiness: 100% (copy-paste level)
  - Confidence achieved: ≥95% after 2-3 iterations

# Limitations
limitations:
  - Requires clear constraints (if vague input → vague output)
  - Works for well-documented domains (GraphRAG has 100s of sources)
  - May fail for novel/unpublished techniques
  - Cost: Research queries consume API quota

# Storage Location
storage:
  workflow_definition: context-management/config/workflows/deterministic_implementation.yaml
  examples: .agent/intelligence/examples/deterministic_queries/
  research_archive: standard-model-of-code/docs/research/workflows/

# Maintenance
maintenance:
  - Update query_template when discovering better patterns
  - Track success rate (% tasks reaching 95% confidence)
  - Refine constraints based on output quality
  - Version workflow when method evolves

---

**STATUS:** Active workflow
**CREATOR:** Claude Sonnet 4.5 + Leonardo Lech (Session 2026-01-27)
**VALIDATION:** Achieved 93%+ confidence on GraphRAG tasks
**RECOMMENDED:** Use for all major implementation planning
