"""
🚀 COLLIDER UNIFIED CLI
Refactored entry point for all standard model tools.
"""
import sys
import os
import argparse
import re
import tempfile
from datetime import datetime
from pathlib import Path

# Add root to path to ensure modules are found
root_dir = Path(__file__).resolve().parent
sys.path.append(str(root_dir))


def main():
    parser = argparse.ArgumentParser(
        prog="collider",
        description="🔬 Collider - Standard Model of Code - Analyze any codebase structure"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # ==========================================
    # MUTATE Command
    # ==========================================
    mutate_parser = subparsers.add_parser(
        "mutate",
        help="Apply JSON mutations to a source file rewriting the AST.",
        description="Applies a series of JSON-defined mutations to a source file, rewriting its Abstract Syntax Tree (AST)."
    )
    mutate_parser.add_argument(
        "path",
        help="Path to the source file to mutate"
    )
    mutate_parser.add_argument(
        "mutations",
        help="JSON string or path to a JSON file containing the mutations array"
    )
    mutate_parser.add_argument(
        "--inplace",
        action="store_true",
        help="Overwrite the original file instead of printing to stdout"
    )

    # ==========================================
    # ANALYZE Command
    # ==========================================
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze a repository and emit the canonical output bundle",
        description="Runs the canonical full analysis and produces both LLM-oriented JSON and human-readable HTML."
    )

    # Positional path argument
    analyze_parser.add_argument(
        "path",
        nargs="?",
        help="Path to the repository or directory to analyze"
    )

    # Flags
    analyze_parser.add_argument(
        "--output",
        default=None,
        help="Output directory for results (defaults to <repo>/.collider)",
    )
    analyze_open = analyze_parser.add_mutually_exclusive_group()
    analyze_open.add_argument(
        "--open",
        dest="open_latest",
        action="store_true",
        help="Open newest HTML output after analysis",
    )
    analyze_open.add_argument(
        "--no-open",
        dest="open_latest",
        action="store_false",
        help="Do not open HTML output after analysis",
    )
    analyze_parser.set_defaults(open_latest=None)

    analyze_parser.add_argument(
        "--html",
        action="store_true",
        help="Generate human-readable HTML report (Collider reports are AI-only telemetry by default)"
    )
    analyze_parser.add_argument(
        "--language",
        default=None,
        help="Force specific language analysis"
    )
    analyze_parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of worker processes"
    )
    analyze_parser.add_argument(
        "--no-learn",
        action="store_true",
        help="Disable auto-learning of unknown patterns"
    )
    analyze_parser.add_argument(
        "--llm",
        action="store_true",
        help="Enable LLM classification (requires Ollama)"
    )
    analyze_parser.add_argument(
        "--llm-model",
        default="qwen2.5:7b-instruct",
        help="Ollama model to use"
    )

    # ==========================================
    # DOCTOR Command - Contract Validation
    # ==========================================
    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Run pipeline + output contract validation",
        description="Runs analysis, normalizes outputs, and validates canonical output contract."
    )
    doctor_parser.add_argument(
        "path",
        help="Path to the repository or directory to analyze"
    )
    doctor_parser.add_argument(
        "--output",
        default=None,
        help="Optional output directory for doctor artifacts"
    )

    # ==========================================
    # HEALTH Command
    # ==========================================
    health_parser = subparsers.add_parser(
        "health",
        help="Run comprehensive system health checks (Newman Layer)",
        description="Validates integrity of static analysis, graph generation, and LLM connectivity."
    )

    # ==========================================
    # GRADE Command - Codebase Health Score
    # ==========================================
    grade_parser = subparsers.add_parser(
        "grade",
        help="Get codebase health grade (A-F) based on topology and complexity",
        description="Analyzes codebase structure and returns a health score (0-10) with letter grade."
    )
    grade_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the repository to analyze (default: current directory)"
    )
    grade_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show component scores breakdown"
    )
    grade_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    # ==========================================
    # AUDIT Command
    # ==========================================
    audit_parser = subparsers.add_parser(
        "audit",
        help="Run a combined health check and minimal analysis to validate the toolchain",
        description="Performs a full audit: Newman suite + minimal repo scan to prove the pipeline works."
    )
    audit_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Target repository (defaults to current directory)"
    )

    audit_parser.add_argument(
        "--output",
        default="output/audit",
        help="Output directory for audit artifacts"
    )

    # ==========================================
    # FULL Command - Complete Analysis
    # ==========================================
    full_parser = subparsers.add_parser(
        "full",
        help="Run complete deterministic analysis with all theoretical frameworks",
        description="Single command for Markov chains, knot detection, data flow, and complete Standard Model."
    )
    full_parser.add_argument(
        "path",
        help="Path to the repository to analyze"
    )
    full_parser.add_argument(
        "--output",
        default=None,
        help="Output directory for results (defaults to <repo>/.collider)"
    )
    full_open = full_parser.add_mutually_exclusive_group()
    full_open.add_argument(
        "--open",
        dest="open_latest",
        action="store_true",
        help="Open newest HTML output after analysis",
    )
    full_open.add_argument(
        "--no-open",
        dest="open_latest",
        action="store_false",
        help="Do not open HTML output after analysis",
    )
    full_parser.set_defaults(open_latest=None)

    full_parser.add_argument(
        "--html",
        action="store_true",
        help="Generate human-readable HTML report (Collider reports are AI-only telemetry by default)"
    )
    full_parser.add_argument(
        "--roadmap",
        default=None,
        help="Architectural roadmap to evaluate against (e.g. 'internal_tool')"
    )
    full_parser.add_argument(
        "--ai-insights",
        action="store_true",
        help="Generate AI insights using Vertex AI Gemini (requires gcloud auth)"
    )
    full_parser.add_argument(
        "--ai-insights-model",
        default="gemini-2.0-flash-001",
        help="Gemini model for insights generation (default: gemini-2.0-flash-001)"
    )
    full_parser.add_argument(
        "--timing",
        action="store_true",
        help="Enable pipeline timing metrics (summary at end)"
    )
    full_parser.add_argument(
        "--verbose-timing",
        action="store_true",
        help="Print per-stage timing during execution (implies --timing)"
    )
    full_parser.add_argument(
        "--validate-ui",
        action="store_true",
        help="Run circuit breaker UI tests on generated HTML (requires playwright)"
    )
    full_parser.add_argument(
        "--no-survey",
        action="store_true",
        help="Skip pre-analysis survey (exclude detection for vendor/minified code)"
    )
    full_parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Additional paths to exclude from analysis (can be repeated)"
    )

    # Database options (Phase 30)
    full_parser.add_argument(
        "--db",
        default=None,
        metavar="PATH",
        help="Database path (enables persistence, default: .collider/collider.db)"
    )
    full_parser.add_argument(
        "--no-db",
        action="store_true",
        help="Disable database persistence (JSON output only)"
    )
    full_parser.add_argument(
        "--db-backend",
        choices=["sqlite", "postgres", "duckdb"],
        default="sqlite",
        help="Database backend (default: sqlite)"
    )
    full_parser.add_argument(
        "--incremental",
        action="store_true",
        default=True,
        help="Enable incremental analysis - skip unchanged files (default: on)"
    )
    full_parser.add_argument(
        "--no-incremental",
        action="store_true",
        help="Disable incremental analysis - re-analyze all files"
    )
    full_parser.add_argument(
        "--search",
        action="store_true",
        help="Enable Tantivy full-text search indexing (beta)"
    )
    full_parser.add_argument(
        "--analytics",
        action="store_true",
        help="Enable DuckDB analytics export (beta)"
    )
    full_parser.add_argument(
        "--list-features",
        action="store_true",
        help="List all database features and exit"
    )

    # ==========================================
    # QUERY Command - Database Search
    # ==========================================
    query_parser = subparsers.add_parser(
        "query",
        help="Search analysis history and compare runs",
        description="Query the Collider database for nodes, runs, and comparisons."
    )
    query_parser.add_argument(
        "search",
        nargs="?",
        default=None,
        help="Search term to find nodes (name, file path, or role)"
    )
    query_parser.add_argument(
        "--history",
        action="store_true",
        help="Show analysis run history"
    )
    query_parser.add_argument(
        "--compare",
        nargs=2,
        metavar=("RUN1", "RUN2"),
        help="Compare two analysis runs"
    )
    query_parser.add_argument(
        "--run",
        default=None,
        help="Specific run ID to query (default: latest)"
    )
    query_parser.add_argument(
        "--project",
        default=".",
        help="Project path to query (default: current directory)"
    )
    query_parser.add_argument(
        "--db",
        default=None,
        help="Database path (default: .collider/collider.db)"
    )
    query_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Max results to return (default: 20)"
    )
    query_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    query_parser.add_argument(
        "--export",
        choices=["json", "csv"],
        help="Export results to file"
    )

    # ==========================================
    # GRAPH Command
    # ==========================================
    graph_parser = subparsers.add_parser(
        "graph",
        help="Analyze a code graph for patterns, bottlenecks, and optimization opportunities",
        description="Run network analysis on a graph.json file produced by the analyze command."
    )
    graph_parser.add_argument(
        "graph_path",
        nargs="?",
        help="Path to graph.json file"
    )
    graph_parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output path for the markdown report"
    )
    graph_parser.add_argument(
        "--top", "-n",
        type=int,
        default=20,
        help="Number of top results to show (default: 20)"
    )
    graph_parser.add_argument(
        "--shortest-path",
        default=None,
        help="Find shortest path between two functions (format: 'source:target')"
    )
    graph_parser.add_argument(
        "--bottlenecks",
        action="store_true",
        help="Show only bottleneck analysis"
    )

    # ==========================================
    # VIZ Command
    # ==========================================
    viz_parser = subparsers.add_parser(
        "viz",
        help="Generate interactive HTML visualization",
        description="Creates a robust, interactive HTML visualization from a graph.json file."
    )
    viz_parser.add_argument(
        "graph_path",
        help="Path to graph.json file"
    )
    viz_parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output path for the HTML file"
    )
    viz_parser.add_argument(
        "--3d",
        dest="use_3d",
        action="store_true",
        help="Use new 3D visualization (MermaidFlow)"
    )

    # ==========================================
    # FIX Command (Consolidated from FixGenerator)
    # ==========================================
    fix_parser = subparsers.add_parser(
        "fix",
        help="Generate fix code for optimization schemas",
        description="Generates scaffolding code for architectural patterns (Repositories, Services, etc.)."
    )
    fix_parser.add_argument(
        "--schema", "-s",
        required=True,
        choices=["REPOSITORY_PATTERN", "TEST_COVERAGE", "SERVICE_EXTRACTION", "CQRS_SEPARATION", "GOD_CLASS_DECOMPOSITION"],
        help="Optimization schema to generate code for"
    )
    fix_parser.add_argument(
        "--entity", "-e",
        default="Entity",
        help="Name of the entity/component (e.g. 'User')"
    )
    fix_parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file path (prints to stdout if not specified)"
    )

    # ==========================================
    # DISCOVER Command - Self-Learning Taxonomy
    # ==========================================
    discover_parser = subparsers.add_parser(
        "discover",
        help="Run discovery engine to find unknown patterns (T3)",
        description="Analyze a codebase using T0/T1/T2 cascade, document unknown patterns as T3 discoveries."
    )
    discover_parser.add_argument(
        "path",
        help="Path to the repository to analyze"
    )
    discover_parser.add_argument(
        "--language",
        default=None,
        help="Analyze only specific language (python, go, typescript, etc.)"
    )
    discover_parser.add_argument(
        "--output", "-o",
        default="output/discoveries.json",
        help="Output path for discovered patterns JSON"
    )
    discover_parser.add_argument(
        "--load",
        default=None,
        help="Load previous discoveries to merge with new ones"
    )

    # ==========================================
    # EVAL Command - Comprehensive Evaluation
    # ==========================================
    eval_parser = subparsers.add_parser(
        "eval",
        help="Run comprehensive evaluation of the analysis pipeline",
        description="Test Python, Go, JS extraction and classification with clear PASS/FAIL metrics."
    )
    eval_parser.add_argument(
        "--full",
        action="store_true",
        help="Run full benchmark (200 files per language)"
    )
    eval_parser.add_argument(
        "--save",
        metavar="NAME",
        help="Save results with given name (e.g., 'baseline')"
    )
    eval_parser.add_argument(
        "--compare",
        metavar="NAME",
        help="Compare current results to saved baseline"
    )

    # ==========================================
    # PROVE Command - Self-Proving Validation (Phase 4)
    # ==========================================
    prove_parser = subparsers.add_parser(
        "prove",
        help="Run self-proof validation (pass/fail + diagnostics)",
        description="Single command that validates codebase graph integrity and returns pass/fail status."
    )
    prove_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the repository to validate (default: current directory)"
    )
    prove_parser.add_argument(
        "--threshold",
        type=float,
        default=0.80,
        help="Minimum proof_score to pass (default: 0.80 = 80%%)"
    )
    prove_parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include test functions as entrypoints"
    )
    prove_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    prove_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed diagnostics including witness paths"
    )

    # ==========================================
    # CHARTS Command - Scientific Data Visualization
    # ==========================================
    charts_parser = subparsers.add_parser(
        "charts",
        help="Generate scientific charts from analysis data",
        description="Publication-quality data visualization for code metrics."
    )
    charts_parser.add_argument(
        "analysis_path",
        nargs="?",
        default=None,
        help="Path to unified_analysis.json (default: .collider/unified_analysis.json)"
    )
    charts_parser.add_argument(
        "--output", "-o",
        default="charts",
        help="Output directory for charts (default: charts/)"
    )
    charts_parser.add_argument(
        "--style", "-s",
        choices=["publication", "dark", "minimal", "poster"],
        default="publication",
        help="Chart style (default: publication)"
    )
    charts_parser.add_argument(
        "--format", "-f",
        action="append",
        dest="formats",
        choices=["png", "pdf", "svg"],
        help="Output format (can repeat, default: png pdf)"
    )
    charts_parser.add_argument(
        "--html",
        action="store_true",
        help="Generate interactive HTML viewer"
    )
    charts_parser.add_argument(
        "--open",
        action="store_true",
        help="Open HTML viewer in browser after generation"
    )

    # ==========================================
    # SYMMETRY Command - Wave-Particle Symmetry Analysis
    # ==========================================
    symmetry_parser = subparsers.add_parser(
        "symmetry",
        help="Analyze Wave-Particle symmetry between docs and code",
        description="Compare documentation (Wave) with implementation (Particle) to measure symmetry."
    )
    symmetry_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the repository to analyze (default: current directory)"
    )
    symmetry_parser.add_argument(
        "--docs",
        default=".",
        help="Path to documentation directory (default: same as path)"
    )
    symmetry_parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file path for the report"
    )
    symmetry_parser.add_argument(
        "--format", "-f",
        choices=["brief", "json", "markdown"],
        default="brief",
        help="Output format (default: brief)"
    )
    symmetry_parser.add_argument(
        "--threshold",
        type=float,
        default=0.75,
        help="Minimum confidence threshold for matching (default: 0.75)"
    )

    # Parse
    args = parser.parse_args()

    if args.command == "discover":
        from src.core.discovery_engine import DiscoveryEngine
        # Path already imported globally at top of file

        print(f"🔬 Discovery Engine — Hybrid T0/T1/T2 + T3 Discovery")
        print("=" * 60)

        engine = DiscoveryEngine()

        # Load previous discoveries if specified
        if args.load and Path(args.load).exists():
            print(f"   Loading previous discoveries from: {args.load}")
            engine.load_discoveries(args.load)
            print(f"   Loaded {len(engine.discovered_registry)} existing patterns")

        print(f"\n   Analyzing: {args.path}")
        if args.language:
            print(f"   Language: {args.language}")

        report = engine.analyze_repo(args.path, language=args.language)
        print(engine.generate_report())

        # Export discoveries
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        engine.export_discoveries(str(output_path))
        print(f"\n   Discoveries exported to: {output_path}")

        # Show taxonomy candidates
        candidates = engine.get_taxonomy_candidates(min_occurrences=10, min_confidence=0.5)
        if candidates:
            print(f"\n   {len(candidates)} patterns ready for taxonomy promotion")

        sys.exit(0)

    elif args.command == "eval":
        from scripts.evaluate import run_evaluation, save_result, compare_results
        result = run_evaluation(full=args.full)
        if args.save:
            save_result(result, args.save)
        if args.compare:
            compare_results(result, args.compare)
        sys.exit(0 if result.overall_status == "PASS" else 1)

    elif args.command == "prove":
        from src.core.validation.self_proof import SelfProofValidator
        import json

        target_path = Path(args.path).resolve()
        if not target_path.exists():
            print(f"Error: Path not found: {target_path}")
            sys.exit(1)

        print(f"Self-Proof Validation")
        print(f"   Target: {target_path}")
        print(f"   Threshold: {args.threshold:.0%}")
        if args.include_tests:
            print(f"   Including tests: Yes")
        print()

        validator = SelfProofValidator(
            target_path,
            include_tests=getattr(args, 'include_tests', False)
        )
        result = validator.prove(threshold=args.threshold)

        if getattr(args, 'json', False):
            # JSON output
            output = {
                "passed": result.passed,
                "proof_score": result.proof_score,
                "registry_accuracy": result.registry_accuracy,
                "connection_coverage": result.connection_coverage,
                "edge_accuracy": result.edge_accuracy,
                "reachability": result.reachability,
                "phantoms": result.phantoms,
                "determinism_hash": result.determinism_hash,
                "failure_reasons": result.failure_reasons,
                "filesystem_components": result.filesystem_components,
                "registry_components": result.registry_components,
                "entrypoints_count": len(result.entrypoints),
                "unreachable_count": len(result.unreachable),
            }
            if args.verbose:
                output["entrypoints"] = result.entrypoints[:20]
                output["unreachable"] = result.unreachable[:20]
                output["witness_paths_sample"] = dict(list(result.witness_paths.items())[:5])
            print(json.dumps(output, indent=2))
        else:
            # Human-readable output
            status_icon = "PASS" if result.passed else "FAIL"
            print(f"   Result: {status_icon}")
            print()
            print(f"   Metrics:")
            print(f"      proof_score:        {result.proof_score:.1%}")
            print(f"      registry_accuracy:  {result.registry_accuracy:.1%}")
            print(f"      connection_coverage:{result.connection_coverage:.1%}")
            print(f"      edge_accuracy:      {result.edge_accuracy:.1%}")
            print(f"      reachability:       {result.reachability:.1%}")
            print()
            print(f"   Counts:")
            print(f"      atomic nodes:       {result.registry_components}")
            print(f"      entrypoints:        {len(result.entrypoints)}")
            print(f"      unreachable:        {len(result.unreachable)}")
            print(f"      phantoms:           {result.phantoms}")
            print()
            print(f"   Determinism hash: {result.determinism_hash}")

            if result.failure_reasons:
                print()
                print(f"   Failure reasons:")
                for reason in result.failure_reasons:
                    print(f"      - {reason}")

            if args.verbose:
                print()
                print(f"   Entrypoints (first 10):")
                for ep in sorted(result.entrypoints)[:10]:
                    print(f"      - {ep}")

                if result.unreachable:
                    print()
                    print(f"   Unreachable (first 10):")
                    for ur in sorted(result.unreachable)[:10]:
                        print(f"      - {ur}")

                if result.witness_paths:
                    print()
                    print(f"   Witness paths (sample):")
                    for node_id, path in list(result.witness_paths.items())[:3]:
                        print(f"      {node_id}:")
                        print(f"         via: {' -> '.join(path[:5])}")
                        if len(path) > 5:
                            print(f"         ... ({len(path)} total hops)")

        sys.exit(0 if result.passed else 1)

    elif args.command == "charts":
        from src.core.scientific_charts import generate_charts

        # Find analysis file
        analysis_path = args.analysis_path
        if not analysis_path:
            # Try common locations
            for candidate in ['.collider/unified_analysis.json', 'unified_analysis.json',
                              'output/unified_analysis.json']:
                if Path(candidate).exists():
                    analysis_path = candidate
                    break

        if not analysis_path or not Path(analysis_path).exists():
            print(f"Error: Analysis file not found. Run 'collider full' first or specify path.")
            print("Usage: collider charts <analysis.json> --output charts/")
            sys.exit(1)

        formats = args.formats or ['png', 'pdf']
        output_dir = args.output

        try:
            generated = generate_charts(
                analysis_path=analysis_path,
                output_dir=output_dir,
                style=args.style,
                formats=formats
            )
            print(f"\nGenerated {len(generated)} chart files in {output_dir}/")

            # Generate HTML viewer if requested
            if getattr(args, 'html', False) or getattr(args, 'open', False):
                from src.core.chart_viewer import generate_chart_viewer
                html_path = str(Path(output_dir) / 'charts_report.html')
                generate_chart_viewer([output_dir], html_path)
                print(f"Generated HTML viewer: {html_path}")

                if getattr(args, 'open', False):
                    import subprocess
                    subprocess.run(['open', html_path], check=False)
                    print("Opened in browser")

            sys.exit(0)
        except Exception as e:
            print(f"Error generating charts: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    elif args.command == "health":
        from src.core.newman_runner import run_health_check
        sys.exit(run_health_check(exit_on_fail=True))

    elif args.command == "grade":
        from src.core.full_analysis import run_full_analysis
        from src.core.topology_reasoning import (
            LandscapeProfile,
            LandscapeHealthIndex,
            TopologyClassifier,
            ElevationModel,
            compute_gradient
        )
        import json as json_module
        import io

        target_path = Path(args.path).resolve()
        if not target_path.exists():
            print(f"Error: Path not found: {target_path}")
            sys.exit(1)

        # Run analysis - suppress stdout when --json to avoid polluting JSON output
        temp_output = tempfile.mkdtemp(prefix="collider_grade_")
        json_mode = getattr(args, 'json', False)
        old_stdout = sys.stdout  # Always capture for cleanup
        try:
            if json_mode:
                # Redirect stdout to suppress analysis progress messages
                sys.stdout = io.StringIO()
            try:
                result = run_full_analysis(str(target_path), temp_output, options={"open_latest": False})
            finally:
                if json_mode:
                    sys.stdout = old_stdout
        except Exception as e:
            sys.stdout = old_stdout
            print(f"Error: Analysis failed: {e}")
            sys.exit(1)

        # Extract nodes and edges from result
        nodes = result.get("nodes", [])
        edges = result.get("edges", [])

        if not nodes:
            print("Error: No nodes found in analysis")
            sys.exit(1)

        # Compute topology (Betti numbers)
        classifier = TopologyClassifier()
        betti = classifier.compute_betti_numbers(nodes, edges)

        # Compute elevations
        elevation_model = ElevationModel()
        elevation_map = elevation_model.compute_elevation_map(nodes, edges)
        elevations = {nid: er.elevation for nid, er in elevation_map.items()}

        # Compute gradients
        gradients = []
        for edge in edges:
            src = edge.get('source', '')
            tgt = edge.get('target', '')
            if src in elevations and tgt in elevations:
                gradients.append(compute_gradient(elevations[src], elevations[tgt]))

        # Extract alignment data (Q_purity from D6_pure_score, weighted by confidence + pagerank)
        alignment_data = {}
        for node in nodes:
            node_id = node.get('id', '')
            if not node_id:
                continue

            # Use D6_pure_score as Q_purity (already [0,1])
            purity = node.get('D6_pure_score')
            if purity is None:
                continue  # Skip nodes without purity data

            alignment_data[node_id] = {
                'purity': purity,
                'confidence': node.get('confidence', 0.5),
                'pagerank': node.get('pagerank', 0.0)
            }

        # Build profile and compute health
        profile = LandscapeProfile(
            b0=betti.b0,
            b1=betti.b1,
            elevations=elevations,
            gradients=gradients
        )

        lhi = LandscapeHealthIndex()
        health = lhi.compute(profile)

        # Output
        if getattr(args, 'json', False):
            output = {
                "path": str(target_path),
                "nodes": len(nodes),
                "edges": len(edges),
                "nodes_with_alignment": len(alignment_data),
                "health_index": health['index'],
                "grade": health['grade'],
                "formula": "H = 0.25*T + 0.25*E + 0.25*Gd + 0.25*A",
                "betti": {"b0": betti.b0, "b1": betti.b1},
                "component_scores": health['component_scores']
            }
            print(json_module.dumps(output, indent=2))
        else:
            print(f"Health: {health['index']:.1f}/10 ({health['grade']})")
            if getattr(args, 'verbose', False):
                print(f"\n   Path: {target_path}")
                print(f"   Nodes: {len(nodes)}, Edges: {len(edges)}")
                print(f"   Nodes with alignment data: {len(alignment_data)}")
                print(f"   Topology: b0={betti.b0} (components), b1={betti.b1} (cycles)")
                print(f"\n   Component Scores (H = T + E + Gd + A):")
                for component, score in health['component_scores'].items():
                    print(f"      {component}: {score:.1f}/10")

        sys.exit(0)


    elif args.command == "full":
        # Handle --list-features first
        if getattr(args, 'list_features', False):
            from src.core.database import list_features
            list_features()
            sys.exit(0)

        from src.core.full_analysis import run_full_analysis
        try:
            options = {"roadmap": args.roadmap} if args.roadmap else {}
            if args.open_latest is not None:
                options["open_latest"] = args.open_latest
            if getattr(args, 'ai_insights', False):
                options["ai_insights"] = True
                options["ai_insights_model"] = getattr(args, 'ai_insights_model', 'gemini-2.0-flash-001')
            # Timing options
            if getattr(args, 'verbose_timing', False):
                options["verbose_timing"] = True
                options["timing"] = True  # verbose implies timing
            elif getattr(args, 'timing', False):
                options["timing"] = True
            # Survey options (Phase 10)
            if getattr(args, 'no_survey', False):
                options["no_survey"] = True
            # Additional exclusions (--exclude flag)
            exclude_list = getattr(args, 'exclude', [])
            if exclude_list:
                options["extra_excludes"] = exclude_list

            # Database options (Phase 30)
            if getattr(args, 'no_db', False):
                options["no_db"] = True
            else:
                if getattr(args, 'db', None):
                    options["db"] = args.db
                options["db_backend"] = getattr(args, 'db_backend', 'sqlite')
                options["incremental"] = not getattr(args, 'no_incremental', False)
                if getattr(args, 'search', False):
                    options["search"] = True
                if getattr(args, 'analytics', False):
                    options["analytics"] = True

            options["skip_html"] = not getattr(args, 'html', False)

            run_full_analysis(args.path, args.output, options=options)

            # UI Validation (optional)
            if getattr(args, 'validate_ui', False):
                import glob
                output_dir = args.output or os.path.join(args.path, '.collider')
                html_files = glob.glob(os.path.join(output_dir, 'output_human-readable_*.html'))
                if html_files:
                    newest_html = max(html_files, key=os.path.getmtime)
                    print(f"\n🧪 Running UI validation on: {os.path.basename(newest_html)}")
                    try:
                        # Dynamic import of validate_ui from tools directory
                        import importlib.util
                        script_dir = os.path.dirname(os.path.abspath(__file__))
                        validate_ui_path = os.path.join(script_dir, 'tools', 'validate_ui.py')
                        spec = importlib.util.spec_from_file_location("validate_ui", validate_ui_path)
                        validate_ui_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(validate_ui_module)

                        result = validate_ui_module.validate_ui(newest_html, verbose=True)
                        validate_ui_module.print_report(result, verbose=True)
                        if result['failed'] > 0:
                            print("\n⚠️  UI validation found failures. See above for details.")
                    except ImportError as e:
                        if 'playwright' in str(e).lower():
                            print("⚠️  UI validation requires playwright. Install with: pip install playwright && playwright install chromium")
                        else:
                            print(f"⚠️  UI validation import error: {e}")
                else:
                    print("⚠️  No HTML output found for UI validation")
        except Exception as e:
            print(f"❌ Full analysis failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    elif args.command == "analyze":
        if not args.path:
            print("❌ Error: path argument is required for analyze command")
            print("Usage: collider analyze <path_to_code>")
            sys.exit(1)

        print(f"🚀 Launching Collider Analysis on: {args.path}")
        try:
            from src.core.full_analysis import run_full_analysis

            options = {}
            if args.open_latest is not None:
                options["open_latest"] = args.open_latest
            if args.llm:
                options["llm"] = True
                options["llm_model"] = args.llm_model
            if args.language:
                options["language"] = args.language
            if args.no_learn:
                options["no_learn"] = True
            if args.workers:
                options["workers"] = args.workers

            options["skip_html"] = not getattr(args, 'html', False)

            if args.no_learn or args.workers:
                print("⚠️  Note: --no-learn/--workers are accepted but not used by the full pipeline yet.")

            run_full_analysis(args.path, args.output, options=options)
            print("\n✅ Analysis complete. Consolidated outputs generated.")
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            sys.exit(1)

    elif args.command == "doctor":
        from src.core.full_analysis import run_full_analysis
        from src.core.normalize_output import normalize_output, validate_contract
        from collections import Counter

        output_dir = args.output or tempfile.mkdtemp(prefix="collider_doctor_")
        print(f"🩺 Doctor running on: {args.path}")
        print(f"   Output: {output_dir}")

        try:
            result = run_full_analysis(args.path, output_dir, options={})
        except Exception as e:
            print(f"❌ Doctor failed during analysis: {e}")
            sys.exit(1)

        normalized = normalize_output(result)
        errors, warnings = validate_contract(normalized)

        if warnings:
            print("⚠️  Warnings:")
            for msg in warnings:
                print(f"   - {msg}")

        if errors:
            print("❌ Contract validation failed:")
            for msg in errors:
                print(f"   - {msg}")
            sys.exit(1)

        print("✅ Doctor PASS: output contract verified.")
        nodes = normalized.get("nodes", []) if isinstance(normalized, dict) else []
        atom_family_counts = Counter()
        tier_counts = Counter()
        for node in nodes:
            if not isinstance(node, dict):
                continue
            atom_family = node.get("atom_family") or "unknown"
            tier = node.get("tier") or "unknown"
            atom_family_counts[str(atom_family)] += 1
            tier_counts[str(tier)] += 1
        if nodes:
            print("   atom_family counts:", dict(atom_family_counts))
            print("   tier counts:", dict(tier_counts))

    elif args.command == "graph":
        from src.core.graph_analyzer import analyze_full, generate_report, load_graph, shortest_path

        if not args.graph_path:
            print("❌ Error: graph.json path required")
            sys.exit(1)

        graph_path = Path(args.graph_path)
        if not graph_path.exists():
            print(f"❌ Error: Graph file not found: {args.graph_path}")
            sys.exit(1)

        print(f"🔬 Analyzing graph: {args.graph_path}")

        if args.shortest_path:
            # Handle shortest path query
            parts = args.shortest_path.split(":")
            if len(parts) != 2:
                print("❌ Error: shortest-path format should be 'source:target'")
                sys.exit(1)
            G = load_graph(graph_path)
            path = shortest_path(G, parts[0], parts[1])
            if path:
                print(f"📍 Shortest path ({len(path)} hops):")
                for i, node in enumerate(path):
                    name = node.split("|")[-2] if "|" in node else node[:50]
                    print(f"   {i+1}. {name}")
            else:
                print("❌ No path found between those nodes")
        else:
            # Full analysis
            result = analyze_full(graph_path, top_n=args.top)
            output_path = args.output or str(graph_path.parent / "GRAPH_ANALYSIS.md")
            generate_report(result, output_path)
            print(f"\n✅ Report saved to: {output_path}")

    elif args.command == "viz":
        graph_path = Path(args.graph_path)
        if args.output:
            output_path = Path(args.output)
        else:
            stem = re.sub(r"[^A-Za-z0-9]+", "-", graph_path.stem.lower()).strip("-") or "graph"
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = graph_path.parent / f"output_human-readable_{stem}_{ts}.html"

        try:
            if args.use_3d:
                from src.core.viz_generator import VisualizationGenerator
                generator = VisualizationGenerator()
                saved_path = generator.generate(graph_path, output_path, mode="3d")
            else:
                from src.core.output_generator import write_html_report
                saved_path = write_html_report(graph_path, output_path.parent, filename=output_path.name)
            print(f"✅ Visualization generated: {saved_path}")
        except Exception as e:
            print(f"❌ Error generating visualization: {e}")
            sys.exit(1)

    elif args.command == "fix":
        from src.core.fix_generator import FixGenerator

        generator = FixGenerator("python") # Default to python for now

        # Context building
        context = {
            "entity": args.entity.lower(),
            "Entity": args.entity.capitalize(),
            "component": args.entity,
            "Component": args.entity.capitalize(),
            "class": args.entity,
            "Class": args.entity.capitalize()
        }

        template = generator.generate_fix(args.schema, context)

        if template:
            if args.output:
                out_path = Path(args.output)
                with open(out_path, 'w') as f:
                    f.write(template.code)
                print(f"✅ Generated {args.schema} implementation at {out_path}")
            else:
                print(f"# {template.filename}")
                print(template.code)
        else:
            print(f"❌ Could not generate fix for schema: {args.schema}")
            sys.exit(1)

    elif args.command == "symmetry":
        from src.core.symmetry_reporter import run_symmetry_analysis

        repo_path = Path(args.path).resolve()
        docs_path = Path(args.docs).resolve() if args.docs != "." else repo_path

        if not repo_path.exists():
            print(f"❌ Error: Repository path not found: {repo_path}")
            sys.exit(1)

        print(f"🔬 Wave-Particle Symmetry Analysis")
        print(f"   Repository: {repo_path}")
        print(f"   Documentation: {docs_path}")
        print()

        try:
            result = run_symmetry_analysis(
                repo_path=str(repo_path),
                docs_path=str(docs_path),
                output_format=args.format,
                threshold=args.threshold
            )

            if args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(result)
                print(f"✅ Report saved to: {output_path}")
            else:
                print(result)

        except Exception as e:
            print(f"❌ Symmetry analysis failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    elif args.command == "query":
        import json as json_module

        project_path = str(Path(getattr(args, 'project', '.')).resolve())

        # Initialize database
        try:
            from src.core.database import create_database_manager, DatabaseConfig

            db_path = getattr(args, 'db', None)
            if db_path is None:
                db_path = str(Path(project_path) / '.collider' / 'collider.db')

            if not Path(db_path).exists():
                print(f"No database found at {db_path}")
                print("Run 'collider full <path>' first to create the database.")
                sys.exit(1)

            config = DatabaseConfig()
            config.sqlite_path = db_path
            db = create_database_manager(config, project_path)

            if db is None:
                print("Database is disabled.")
                sys.exit(1)

            db.connect()
            db.initialize_schema()

        except ImportError as e:
            print(f"Database module not available: {e}")
            sys.exit(1)

        limit = getattr(args, 'limit', 20)
        json_output = getattr(args, 'json', False)

        # History mode
        if getattr(args, 'history', False):
            runs = db.get_runs(project_path=project_path, limit=limit)

            if json_output:
                output = [{
                    "id": r.id,
                    "project_name": r.project_name,
                    "started_at": r.started_at.isoformat() if r.started_at else None,
                    "status": r.status,
                    "node_count": r.node_count,
                    "edge_count": r.edge_count,
                } for r in runs]
                print(json_module.dumps(output, indent=2))
            else:
                print(f"Analysis History for {project_path}")
                print("=" * 60)
                for r in runs:
                    started = r.started_at.strftime("%Y-%m-%d %H:%M") if r.started_at else "?"
                    print(f"  {r.id}  {started}  {r.status:<10}  {r.node_count:>5} nodes  {r.edge_count:>5} edges")

        # Compare mode
        elif getattr(args, 'compare', None):
            run1_id, run2_id = args.compare
            comparison = db.compare_runs(run1_id, run2_id)

            if json_output:
                print(json_module.dumps(comparison, indent=2))
            else:
                print(f"Comparison: {run1_id} vs {run2_id}")
                print("=" * 60)
                print(f"  Added:   {comparison.get('added', 0)} nodes")
                print(f"  Removed: {comparison.get('removed', 0)} nodes")
                print(f"  Common:  {comparison.get('common', 0)} nodes")
                if comparison.get('added_ids'):
                    print(f"\n  Sample added nodes:")
                    for nid in comparison['added_ids'][:5]:
                        print(f"    + {nid}")
                if comparison.get('removed_ids'):
                    print(f"\n  Sample removed nodes:")
                    for nid in comparison['removed_ids'][:5]:
                        print(f"    - {nid}")

        # Search mode
        elif getattr(args, 'search', None):
            search_term = args.search
            run_id = getattr(args, 'run', None)

            nodes = db.search_nodes(search_term, run_id=run_id, limit=limit)

            if json_output:
                print(json_module.dumps(nodes, indent=2))
            else:
                print(f"Search results for '{search_term}'")
                print("=" * 60)
                for n in nodes:
                    role = n.get('role', '?')[:15]
                    name = n.get('name', '?')[:40]
                    file_path = n.get('file_path', '?')
                    line = n.get('start_line', '?')
                    print(f"  [{role:<15}] {name:<40} {file_path}:{line}")

                if not nodes:
                    print("  No results found.")

        # Export mode
        elif getattr(args, 'export', None):
            export_format = args.export
            run_id = getattr(args, 'run', None)

            if run_id is None:
                latest = db.get_latest_run(project_path)
                if latest:
                    run_id = latest.id
                else:
                    print("No runs found for this project.")
                    sys.exit(1)

            nodes = db.get_nodes(run_id)
            edges = db.get_edges(run_id)

            if export_format == "json":
                output = {"run_id": run_id, "nodes": nodes, "edges": edges}
                print(json_module.dumps(output, indent=2))
            elif export_format == "csv":
                import csv
                import io
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=["id", "name", "role", "kind", "file_path"])
                writer.writeheader()
                for n in nodes:
                    writer.writerow({k: n.get(k, '') for k in ["id", "name", "role", "kind", "file_path"]})
                print(output.getvalue())

        else:
            print("Usage: collider query <search_term>")
            print("       collider query --history")
            print("       collider query --compare RUN1 RUN2")
            sys.exit(1)

        db.disconnect()
        sys.exit(0)

    elif args.command == "mutate":
        from src.core.synthesis.compiler import ColliderCompiler
        import json as json_module
        from pathlib import Path

        target_path = Path(args.path)
        if not target_path.exists():
            print(f"Error: Target file not found: {args.path}")
            sys.exit(1)

        # Load mutations from file or string
        mutations_str = args.mutations
        if mutations_str.endswith(".json") and Path(mutations_str).exists():
            with open(mutations_str, "r") as f:
                mutations_data = json_module.load(f)
        else:
            try:
                mutations_data = json_module.loads(mutations_str)
            except json_module.JSONDecodeError as e:
                print(f"Error: Invalid JSON mutations provided: {e}")
                sys.exit(1)

        # Construct the full request expected by the compiler
        request_data = {
            "target_file": str(target_path),
            "mutations": mutations_data if isinstance(mutations_data, list) else mutations_data.get("mutations", [])
        }

        with open(target_path, "r") as f:
            source_code = f.read()

        try:
            modified_code = ColliderCompiler.apply_mutations(source_code, request_data)
        except Exception as e:
            print(f"Error: Synthesis failed. {e}")
            sys.exit(1)

        if getattr(args, "inplace", False):
            with open(target_path, "w") as f:
                f.write(modified_code)
            print(f"Successfully mutated and overwrote {target_path}")
        else:
            print(modified_code)

        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
