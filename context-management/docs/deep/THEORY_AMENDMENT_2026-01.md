# Standard Model of Code: Theory Amendment (January 2026)

**Status:** PROPOSED
**Date:** 2026-01-26
**Scope:** Three complementary extensions to core theory

---

## Executive Summary

The Standard Model of Code currently treats code as a static structural object. Three empirically-validated gaps require theoretical amendment:

| Amendment | Core Insight | Evidence |
|-----------|--------------|----------|
| **A1: Tools as Objects** | CODOME = f(CODE, TOOLS) | Research: 22.5% lower smells with TypeScript |
| **A2: Dark Matter** | Invisible dependencies are real | Data: 14.7% of edges have no visible source |
| **A3: Confidence Dimension** | Uncertainty is information | Data: 36.8% of nodes classified with low confidence |

These are **NOT alternatives**. They are complementary extensions that together complete the model.

---

## Amendment 1: Tools as Objects (TOOLOME)

### The Problem

Current model assumes code structure is determined solely by developer intent. But:
- A function's shape changes when Black enforces 88-char lines
- Import graphs differ based on bundler choice
- Test organization varies by framework

**The tool is not a passive observer. It is an active participant in code formation.**

### Theoretical Extension

```
CODOME_observed = f(CODE_intended, TOOLCHAIN)

Where TOOLCHAIN = {
    formatters,      # Black, Prettier, gofmt
    linters,         # ESLint, Ruff, Pylint
    type_systems,    # TypeScript, MyPy, Flow
    build_tools,     # webpack, vite, cargo
    test_frameworks, # pytest, jest, vitest
    language_servers # LSP implementations
}
```

### Empirical Evidence

| Finding | Source | Implication |
|---------|--------|-------------|
| TypeScript projects have 22.5% lower code smells than JavaScript | Academic study | Type tools shape cleanliness |
| TypeScript shows 20% lower cognitive complexity | Academic study | Tools affect comprehensibility |
| Linters catch 16-76% of defects surviving code review | Industry research | Tools are structural gatekeepers |
| Black/Prettier force structural refactoring at line limits | Observable behavior | Formatters change AST patterns |
| Monorepo tools (Nx, Turborepo) create different module boundaries | Industry patterns | Build tools shape architecture |

### Proposed Implementation

**Stage 0.5: Toolchain Discovery** (before Survey)

Detects and records:
- `package.json` scripts and devDependencies
- Config files: `.eslintrc`, `pyproject.toml`, `tsconfig.json`
- Lock files: presence indicates toolchain stability
- CI configs: reveal enforced tooling

Output: `toolchain_profile` in CodebaseState metadata

### Tool Ontology (T-Classification)

```
TOOL_UNIVERSE (Complete Taxonomy)
│
├── TOOLOME (Development Tools) - Shape the CODOME
│   │
│   ├── T-ATOMS (Structural Types)
│   │   ├── T-Formatter    # Black, Prettier, gofmt
│   │   ├── T-Linter       # ESLint, Ruff, Pylint
│   │   ├── T-TypeChecker  # TypeScript, MyPy, Flow
│   │   ├── T-Bundler      # webpack, vite, esbuild
│   │   ├── T-TestRunner   # pytest, jest, vitest
│   │   ├── T-Builder      # make, cargo, gradle
│   │   └── T-LanguageServer # LSP implementations
│   │
│   ├── T-ROLES (Functional Purpose)
│   │   ├── T-Enforcer     # Blocks non-conforming code
│   │   ├── T-Suggester    # Recommends but doesn't block
│   │   ├── T-Transformer  # Rewrites code (formatters)
│   │   ├── T-Analyzer     # Reports without changing
│   │   └── T-Generator    # Creates code/artifacts
│   │
│   └── Stone Tool Test: PASS (human-usable)
│
└── STONE_TOOLS (Analysis Tools) - Observe the CODOME
    │
    ├── S-ATOMS (Output Types)
    │   ├── S-StructuredData  # unified_analysis.json, POM YAML
    │   ├── S-Graph           # Node/edge exports, GraphRAG
    │   ├── S-Metrics         # Health scores, coverage data
    │   └── S-Visualization   # 3D graphs, force-directed layouts
    │
    ├── S-ROLES (Consumer Target)
    │   ├── S-AIConsumer      # Designed for AI parsing
    │   ├── S-HumanMediated   # Human sees via AI interpretation
    │   └── S-HybridConsumer  # Both (markdown reports)
    │
    └── Stone Tool Test: FAIL (AI-native, requires mediation)
```

### The Stone Tool Test

> "Can a human use this tool directly, without AI mediation?"

| Tool | Usable? | Category |
|------|---------|----------|
| Black (formatter) | Yes | TOOLOME |
| ESLint (linter) | Yes | TOOLOME |
| unified_analysis.json | **No** | STONE_TOOL |
| POM YAML output | **No** | STONE_TOOL |
| collider_report.html | Partial | Hybrid |

**See:** `context-management/docs/specs/AI_CONSUMER_CLASS.md` (Axiom H4)

### Tool Dimensions (Shared by TOOLOME and STONE_TOOLS)

```
T-DIMENSIONS (8 axes, applicable to all tools)
├── D1:KIND        # What type of tool
├── D2:LAYER       # Where it operates (source/build/runtime)
├── D3:ROLE        # Its functional purpose
├── D4:LIFECYCLE   # When it runs (edit/commit/CI)
├── D5:STATE       # Stateless (formatter) vs stateful (cache)
├── D6:EFFECT      # Read-only vs mutating
├── D7:BOUNDARY    # Local vs networked
└── D8:CONFIDENCE  # How certain is detection
```

---

## Amendment 2: Dark Matter (Codome Boundaries)

### The Problem

Current edge extraction finds ~85% of call relationships. The remaining ~15% are "dark" - they exist but have no visible source in code:

```python
# This edge exists but has no caller in our codebase
def main():  # Called by: __codome__::pytest
    pass

# This edge crosses language boundaries
def api_handler():  # Called by: __codome__::javascript_frontend
    pass
```

### Theoretical Extension

Dark Matter edges are **real dependencies** that cross the codome boundary. They should be:
1. Explicitly modeled (not ignored)
2. Classified by source
3. Used to infer external system shape

```
CODOME_complete = CODOME_visible ∪ CODOME_dark

Where CODOME_dark includes:
- Test framework invocations (pytest, jest)
- Entry points (main, CLI handlers)
- Framework callbacks (Flask routes, React hooks)
- Cross-language calls (FFI, HTTP APIs)
- Dynamic dispatch (eval, getattr)
```

### Empirical Evidence

From analysis of this codebase (2,530 nodes, 7,330 edges):

| Dark Edge Source | Count | Percentage |
|------------------|-------|------------|
| test_entry | 528 | 49.1% |
| external_boundary | 252 | 23.4% |
| cross_language | 134 | 12.5% |
| framework_managed | 115 | 10.7% |
| entry_point | 45 | 4.2% |
| dynamic_target | 2 | 0.2% |
| **Total Dark** | **1,076** | **14.7%** |

### Dark Matter Signature

The distribution of dark edge types creates a **signature** that characterizes the codebase:

```
This codebase signature:
- 49% test_entry → Heavy test coverage, test-driven
- 23% external_boundary → Significant external integrations
- 12% cross_language → Multi-language ecosystem
```

Different projects have different signatures:
- Pure library: low test_entry, high external_boundary
- Microservice: high cross_language, high framework_managed
- CLI tool: high entry_point, low framework_managed

### Proposed Implementation

**Stage 6.9: Dark Matter Analysis** (after Codome Boundary)

1. Identify all nodes with `is_codome_boundary = True`
2. Classify each by dark edge source
3. Compute dark matter signature
4. Generate predictions about external system shape

Output: `dark_matter` section in analysis results

---

## Amendment 3: Confidence as Meta-Dimension

### The Problem

Current classifications are binary: a node IS a Factory or it ISN'T. But classification confidence varies:

```python
class UserFactory:      # HIGH confidence - name contains "Factory"
    def create(): ...

class DataProcessor:    # MEDIUM confidence - "Processor" suggests Transformer
    def process(): ...

class Helper:           # LOW confidence - generic name, unclear role
    def do_thing(): ...
```

Hiding uncertainty produces false precision. A graph where 37% of nodes have uncertain classification is **less trustworthy** than one that admits uncertainty.

### Theoretical Extension

Every classification carries a confidence score:

```
Classification = (Value, Confidence)

Where Confidence ∈ {high, medium, low} or [0.0, 1.0]

Examples:
- D3_ROLE: (Factory, high)      # Strong signal
- D3_ROLE: (Transformer, medium) # Moderate signal
- D3_ROLE: (Internal, low)       # Fallback/default
```

### Empirical Evidence

From analysis of this codebase:

| Confidence Level | Node Count | Percentage |
|------------------|------------|------------|
| High | 1,237 | 48.9% |
| Medium | 363 | 14.3% |
| Low | 930 | 36.8% |
| **Overall Score** | - | **64.9%** |

**Interpretation:** Only 49% of classifications are high-confidence. The model is honest about its 37% uncertainty.

### Confidence Sources

Different dimensions have different confidence characteristics:

| Dimension | High Confidence When | Low Confidence When |
|-----------|---------------------|---------------------|
| D1:KIND | AST node type is unambiguous | Dynamic constructs |
| D2:LAYER | Clear architectural markers | Generic utilities |
| D3:ROLE | Name contains role keyword | Generic names |
| D4:LIFECYCLE | Explicit init/destroy | Ambiguous lifetime |
| D5:STATE | Pure functions or explicit state | Mixed patterns |
| D6:EFFECT | Clear I/O operations | Side effects hidden |
| D7:BOUNDARY | Explicit API markers | Internal ambiguity |
| D8:CONFIDENCE | (Meta) | (Meta) |

### Proposed Implementation

**Stage 8.7: Confidence Aggregation** (after Purpose Intelligence)

1. Collect confidence from all prior classifications
2. Compute per-node aggregate confidence
3. Compute per-dimension confidence distribution
4. Flag low-confidence hotspots for review

Output: `confidence` section in analysis results with:
- Overall score
- Distribution by level
- Recommendations for improvement

---

## Implementation Status

### Completed

| Component | Status | Location |
|-----------|--------|----------|
| ManifestWriterStage | ✅ Done | `src/core/pipeline/stages/manifest_writer.py` |
| OverallUnderstandingQuery | ✅ Done | `src/core/queries/overall_understanding.py` |
| Pipeline Registration | ✅ Done | 28 stages (was 27) |
| Dark Matter Analysis | ✅ Done | In OverallUnderstandingQuery |
| Confidence Analysis | ✅ Done | In OverallUnderstandingQuery |

### Pending

| Component | Priority | Dependency |
|-----------|----------|------------|
| Stage 0.5: Toolchain Discovery | HIGH | None |
| Stage 6.9: Dark Matter Stage | MEDIUM | Codome Boundary |
| Stage 8.7: Confidence Aggregation | MEDIUM | Purpose Intelligence |
| Tool Ontology Registry | LOW | Toolchain Discovery |
| Artifact Layout (.colliderruns/) | LOW | Manifest Writer |

---

## Validation Results

Query run on 2026-01-26 against this codebase:

```
=== Overall Understanding: PASSED ===

Nodes: 2,530
Edges: 7,330

Dark Matter: 14.7% (1,076 edges)
  - Prediction: Moderate dark matter, boundaries should be theorized
  - Signature: Test framework dominates (49%)

Confidence: 64.9% overall
  - High: 48.9%
  - Medium: 14.3%
  - Low: 36.8%
  - Recommendation: Review edge cases

Quality Gates: PASSED (0 errors, 0 warnings)

Recommendations:
1. [HIGH] Formalize Dark Matter - Implement Proposal 2
2. [HIGH] Model Uncertainty - Implement Proposal 3
```

---

## Theoretical Implications

### The Complete Model

With all three amendments, the Standard Model becomes:

```
MEASURED_CODOME = {
    structure: f(CODE, TOOLS),           # Amendment 1
    dependencies: VISIBLE ∪ DARK,        # Amendment 2
    classifications: [(value, conf), ...] # Amendment 3
    provenance: {git, pipeline, env},    # Manifest
    integrity: {checksums, merkle_root}  # Manifest
}
```

### What This Enables

1. **Reproducibility**: Same code + same tools = same analysis
2. **Drift Detection**: Changed tool → expected structural change
3. **Honest Uncertainty**: Low confidence = request human review
4. **External System Inference**: Dark matter signature → system architecture
5. **Scientific Measurement**: Analysis is falsifiable, comparable, versioned

---

## References

### Internal Documents
- `context-management/docs/deep/STANDARD_MODEL.md` - Core theory
- `context-management/docs/CODOME.md` - Codome definition
- `src/core/pipeline/stages/manifest_writer.py` - Provenance implementation
- `src/core/queries/overall_understanding.py` - Meta-analysis query

### External Research
- TypeScript code quality studies (22.5% smell reduction)
- Linter effectiveness research (16-76% defect detection)
- Formatter impact on code structure (Black, Prettier)

---

## Appendix: Query Output Samples

### JSON Output (abbreviated)
```json
{
  "dark_matter": {
    "dark_ratio": 0.1468,
    "total_dark_edges": 1076,
    "signature": [
      {"source": "test_entry", "count": 528, "percent": 49.1},
      {"source": "external_boundary", "count": 252, "percent": 23.4}
    ]
  },
  "confidence": {
    "overall_score": 0.649,
    "distribution": {
      "high": {"count": 1237, "percent": 48.9},
      "low": {"count": 930, "percent": 36.8}
    }
  }
}
```

### Markdown Report (abbreviated)
```markdown
## Dark Matter Analysis
- Dark edges: 1076
- Dark ratio: **14.7%**

### Signature
- test_entry: 528 (49.1%)
- external_boundary: 252 (23.4%)

## Confidence Analysis
- Overall score: **64.9%**
- high: 1237 (48.9%)
- low: 930 (36.8%)
```
