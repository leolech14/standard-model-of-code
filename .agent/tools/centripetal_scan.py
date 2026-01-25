#!/usr/bin/env python3
"""
Centripetal Scan - 12-Round Progressive Resolution Analysis
============================================================

TWO SOURCES OF KNOWLEDGE (IN/OUT Axis):
  INTERNAL - Codebase context (Gemini + local files) - Bit → Module
  EXTERNAL - World knowledge (Perplexity research) - Project → Universe

The scan moves CENTRIPETALLY from EXTERNAL → INTERNAL:
  Round 1-3:   EXTERNAL/MACRO - World context, ecosystem, standards
  Round 4-6:   BOUNDARY/MESO - Where code meets world (APIs, configs)
  Round 7-9:   INTERNAL/MICRO - Code structure, algorithms
  Round 10-12: CORE/NANO - Encoding, invariants, the code itself

Each round queries BOTH sources and synthesizes:
  1. EXTERNAL query (what does the world say?) via Perplexity
  2. INTERNAL query (what does the code say?) via Gemini
  3. SYNTHESIS (reconcile external vs internal at this scale)

Physics analogy: RG flow from UV (external) to IR (internal)

Each round's output feeds the next round's context.
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
ANALYZE_PY = PROJECT_ROOT / "context-management/tools/ai/analyze.py"
OUTPUT_DIR = PROJECT_ROOT / ".agent/intelligence/centripetal_scans"

# 12 rounds of progressive queries - INTERNAL + EXTERNAL
ROUNDS = [
    # MACRO (1-3): Directory-level understanding
    {
        "id": 1,
        "level": "MACRO",
        "internal": {
            "query": """List ALL top-level directories in this repository. For each:
- Name, purpose (1 sentence), importance (CRITICAL/HIGH/MEDIUM/LOW)
Output as a table.""",
            "set": "theory",
        },
        "external": {
            "query": "What is the Standard Model of Code? What is a 'Collider' in the context of code analysis tools?",
        },
        "synthesis": "Reconcile: Does the directory structure match the Standard Model of Code theory?",
    },
    {
        "id": 2,
        "level": "MACRO",
        "internal": {
            "query": """Identify the REALMS (major subsystems):
- What are the 3-5 main realms/hemispheres?
- What is the boundary between them?
- Which realm owns which directories?""",
            "set": "architecture_review",
        },
        "external": {
            "query": "What is particle-wave duality in software architecture? How do 'realms' or 'hemispheres' work in monorepo organization?",
        },
        "synthesis": "Does our particle/wave architecture follow established patterns?",
    },
    {
        "id": 3,
        "level": "MACRO",
        "internal": {
            "query": """Map the ENTRY POINTS:
- CLI entry points (executables)
- Configuration entry points
- Documentation entry points
List paths explicitly.""",
            "set": "pipeline",
        },
        "external": {
            "query": "Best practices for CLI tool entry points in Python. What makes a good developer tool interface?",
        },
        "synthesis": "Do our entry points follow CLI best practices?",
    },

    # MESO (4-6): Module-level understanding
    {
        "id": 4,
        "level": "MESO",
        "internal": {
            "query": """For each REALM, list the MODULES:
- Module name and path
- Primary responsibility
- Key dependencies
- Public interface""",
            "set": "pipeline",
        },
        "external": {
            "query": "What are 'atoms' in code classification? How do AST-based code analyzers typically structure their modules?",
        },
        "synthesis": "Does our module structure match AST analyzer best practices?",
    },
    {
        "id": 5,
        "level": "MESO",
        "internal": {
            "query": """Map the DATA FLOW:
- What data structures flow between modules?
- Canonical data format (JSON, YAML)?
- Where does state accumulate?
- Transformation stages?""",
            "set": "pipeline",
        },
        "external": {
            "query": "What is unified_analysis.json in code analysis pipelines? How do code analysis tools structure their output data?",
        },
        "synthesis": "Does our data flow match industry code analysis patterns?",
    },
    {
        "id": 6,
        "level": "MESO",
        "internal": {
            "query": """Identify INTEGRATION POINTS:
- Where do realms connect?
- Shared schemas or protocols?
- Contracts between subsystems?
- Seams (easy to modify)?""",
            "set": "architecture_review",
        },
        "external": {
            "query": "How do AI-assisted code analysis tools integrate with LLMs? What is RAG for code repositories?",
        },
        "synthesis": "Are our AI integration points following RAG best practices?",
    },

    # MICRO (7-9): File-level understanding
    {
        "id": 7,
        "level": "MICRO",
        "internal": {
            "query": """For the 10 most important files:
- File path, line count
- Main class/function names
- Key algorithms or patterns
- Technical debt indicators""",
            "set": "pipeline",
        },
        "external": {
            "query": "What algorithms are used in code graph analysis? How do dependency graph analyzers work?",
        },
        "synthesis": "Are we using established graph analysis algorithms?",
    },
    {
        "id": 8,
        "level": "MICRO",
        "internal": {
            "query": """Map the CONFIGURATION landscape:
- All YAML/JSON config files
- What each controls
- Environment variables
- Secrets management""",
            "set": "brain",
        },
        "external": {
            "query": "Best practices for configuration management in AI tools. How should API keys be managed in developer tools?",
        },
        "synthesis": "Does our config management follow security best practices?",
    },
    {
        "id": 9,
        "level": "MICRO",
        "internal": {
            "query": """Identify PATTERNS across the codebase:
- Naming conventions
- Error handling patterns
- Logging and testing patterns
Give examples.""",
            "set": "pipeline",
        },
        "external": {
            "query": "Python naming conventions for code analysis tools. What patterns do static analysis tools use?",
        },
        "synthesis": "Do our patterns match Python static analysis conventions?",
    },

    # NANO (10-12): Line-level understanding
    {
        "id": 10,
        "level": "NANO",
        "internal": {
            "query": """Find INVARIANTS - things that must always be true:
- Type constraints, validation rules
- Assertions and preconditions
- Schema constraints
Quote actual code.""",
            "set": "pipeline",
        },
        "external": {
            "query": "What invariants should code analysis tools maintain? How do AST parsers ensure correctness?",
        },
        "synthesis": "Are our invariants sufficient for a code analysis tool?",
    },
    {
        "id": 11,
        "level": "NANO",
        "internal": {
            "query": """Identify EDGE CASES and DEFENSIVE CODE:
- Error handling blocks
- Fallback behaviors
- Timeout and null handling
What could go wrong?""",
            "set": "pipeline",
        },
        "external": {
            "query": "Common failure modes in code analysis tools. How do production AST tools handle malformed input?",
        },
        "synthesis": "Do we handle the same edge cases as production tools?",
    },
    {
        "id": 12,
        "level": "NANO",
        "internal": {
            "query": """FINAL SYNTHESIS:
1. ONE-SENTENCE summary
2. THREE key architectural decisions
3. FIVE most important files (paths)
4. TOP risk
5. TOP opportunity""",
            "set": "architecture_review",
        },
        "external": {
            "query": "What makes a successful code analysis tool? Key success factors for developer tools like linters and analyzers.",
        },
        "synthesis": "How does our tool compare to successful code analysis tools?",
    },
]


def run_gemini_query(query: str, context_set: str, round_num: int, previous_context: str = "") -> str:
    """Run a single Gemini query with optional previous context."""

    # Build the full prompt with previous context
    if previous_context:
        full_query = f"""PREVIOUS ANALYSIS CONTEXT (Rounds 1-{round_num-1}):
{previous_context[:50000]}

---

CURRENT ROUND {round_num} QUERY:
{query}"""
    else:
        full_query = query

    cmd = [
        sys.executable, str(ANALYZE_PY),
        "--set", context_set,
        "--tier", "flash_deep",  # Use 2M context
        "--force-oneshot",
        full_query
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"ERROR: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "ERROR: Query timed out"
    except Exception as e:
        return f"ERROR: {e}"


def run_centripetal_scan():
    """Execute all 12 rounds of progressive analysis."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("=" * 70)
    print("CENTRIPETAL SCAN - 12-Round Progressive Resolution Analysis")
    print("=" * 70)
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Output: {OUTPUT_DIR}")
    print()

    results = []
    accumulated_context = ""

    for round_info in ROUNDS:
        round_num = round_info["id"]
        level = round_info["level"]
        query = round_info["query"]
        context_set = round_info["set"]

        print(f"\n{'='*70}")
        print(f"ROUND {round_num}/12 [{level}]")
        print(f"{'='*70}")
        print(f"Query: {query[:100]}...")
        print(f"Set: {context_set}")
        print("Running...", flush=True)

        # Run the query with accumulated context from previous rounds
        response = run_gemini_query(query, context_set, round_num, accumulated_context)

        # Store result
        result = {
            "round": round_num,
            "level": level,
            "query": query,
            "set": context_set,
            "response": response,
            "timestamp": datetime.now().isoformat(),
        }
        results.append(result)

        # Accumulate context for next round (summarized)
        accumulated_context += f"\n\n=== ROUND {round_num} ({level}) ===\n{response[:10000]}"

        # Print summary
        print(f"\nResponse length: {len(response)} chars")
        print(f"Preview: {response[:500]}...")

        # Save intermediate result
        round_file = OUTPUT_DIR / f"{timestamp}_round_{round_num:02d}_{level.lower()}.md"
        with open(round_file, 'w') as f:
            f.write(f"# Centripetal Scan - Round {round_num} ({level})\n\n")
            f.write(f"**Query:** {query}\n\n")
            f.write(f"**Set:** {context_set}\n\n")
            f.write("---\n\n")
            f.write(response)

        print(f"Saved: {round_file.name}")

    # Save complete results
    complete_file = OUTPUT_DIR / f"{timestamp}_complete_scan.json"
    with open(complete_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Generate summary markdown
    summary_file = OUTPUT_DIR / f"{timestamp}_SUMMARY.md"
    with open(summary_file, 'w') as f:
        f.write("# Centripetal Scan Summary\n\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
        f.write("## Resolution Levels\n\n")
        f.write("| Round | Level | Query Summary |\n")
        f.write("|-------|-------|---------------|\n")
        for r in results:
            f.write(f"| {r['round']} | {r['level']} | {r['query'][:50]}... |\n")
        f.write("\n## Final Synthesis (Round 12)\n\n")
        f.write(results[-1]["response"] if results else "No results")

    print("\n" + "=" * 70)
    print("CENTRIPETAL SCAN COMPLETE")
    print("=" * 70)
    print(f"Results: {complete_file}")
    print(f"Summary: {summary_file}")

    return results


if __name__ == "__main__":
    run_centripetal_scan()
