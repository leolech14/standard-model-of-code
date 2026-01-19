#!/usr/bin/env python3
"""
LLM Brain Download Generator

Generates a concise, LLM-optimized summary of a codebase analysis.
Designed for instant understanding and actionable insights.

Output: output.md - A structured document optimized for LLM consumption.
"""
import json
from pathlib import Path
from typing import Dict, List, Any
from collections import Counter


def generate_brain_download(full_analysis: Dict) -> str:
    """Generate LLM-optimized brain download from full analysis."""
    
    lines = []
    
    # =========================================================================
    # SECTION 1: IDENTITY (What is this?)
    # =========================================================================
    target = Path(full_analysis['meta']['target']).name
    counts = full_analysis['counts']
    coverage = full_analysis['coverage']
    
    lines.append("# COLLIDER REPORT")
    
    # Inject Metaphor Primer if available
    try:
        primer_path = Path(__file__).parent / "metaphor_primer.md"
        if primer_path.exists():
            lines.append(primer_path.read_text())
    except Exception:
        pass

    lines.append(f"**Target**: `{target}`")
    lines.append(f"**Generated**: {full_analysis['meta']['timestamp']}")
    lines.append("")
    lines.append("## IDENTITY")
    lines.append("")
    lines.append(f"This is a **{counts['nodes']} node** codebase with **{counts['edges']} edges**.")
    lines.append(f"- Files: {counts['files']}")
    lines.append(f"- Entry points: {counts['entry_points']}")
    lines.append(f"- Dead code: {coverage['dead_code_percent']:.1f}%")
    lines.append("")
    
    # =========================================================================
    # SECTION 2: CHARACTER (RPBL Profile)
    # =========================================================================
    rpbl = full_analysis['rpbl_profile']
    lines.append("## CHARACTER (RPBL)")
    lines.append("")
    lines.append("| Dimension | Score | Meaning |")
    lines.append("|-----------|-------|---------|")
    
    # Interpret RPBL
    r_meaning = "Focused" if rpbl['responsibility'] < 5 else "Broad responsibility"
    p_meaning = "Pure (safe)" if rpbl['purity'] > 6 else "Impure (side effects)"
    b_meaning = "Internal" if rpbl['boundary'] < 5 else "I/O heavy (risky)"
    l_meaning = "Stateless" if rpbl['lifecycle'] < 5 else "Stateful (complex)"
    
    lines.append(f"| Responsibility | {rpbl['responsibility']}/10 | {r_meaning} |")
    lines.append(f"| Purity | {rpbl['purity']}/10 | {p_meaning} |")
    lines.append(f"| Boundary | {rpbl['boundary']}/10 | {b_meaning} |")
    lines.append(f"| Lifecycle | {rpbl['lifecycle']}/10 | {l_meaning} |")
    lines.append("")
    
    # =========================================================================
    # SECTION 3: ARCHITECTURE (How is it organized?)
    # =========================================================================
    dist = full_analysis['distributions']
    lines.append("## ARCHITECTURE")
    lines.append("")
    
    # Top types
    lines.append("**Types**:")
    for t, c in list(dist['types'].items())[:8]:
        lines.append(f"- {t}: {c}")
    lines.append("")
    
    # Layers
    lines.append("**Layers**:")
    layers = dist.get('layers', {})
    if layers:
        for l, c in layers.items():
            pct = c / counts['nodes'] * 100 if counts.get('nodes') else 0
            lines.append(f"- {l}: {c} ({pct:.0f}%)")
    else:
        lines.append("- No layer data available")
    lines.append("")
    
    # =========================================================================
    # SECTION 4: HUBS (Key Components)
    # =========================================================================
    lines.append("## KEY COMPONENTS")
    lines.append("")
    lines.append("Most connected nodes (change these carefully):")
    lines.append("")
    for hub in full_analysis['top_hubs'][:5]:
        lines.append(f"- `{hub['name']}` ({hub['in_degree']} callers)")
    lines.append("")
    
    # =========================================================================
    # SECTION 5: HEALTH (What's the status?)
    # =========================================================================
    knots = full_analysis['knots']
    exec_flow = full_analysis['execution_flow']
    purpose = full_analysis['purpose_field']
    
    lines.append("## HEALTH STATUS")
    lines.append("")
    
    # Traffic light indicators
    health_items = []
    
    # Coverage
    if coverage['type_coverage'] == 100:
        health_items.append("✅ Type coverage: 100%")
    else:
        health_items.append(f"⚠️ Type coverage: {coverage['type_coverage']:.0f}%")
    
    # Dead code
    if coverage['dead_code_percent'] < 5:
        health_items.append(f"✅ Dead code: {coverage['dead_code_percent']:.1f}%")
    elif coverage['dead_code_percent'] < 15:
        health_items.append(f"⚠️ Dead code: {coverage['dead_code_percent']:.1f}%")
    else:
        health_items.append(f"❌ Dead code: {coverage['dead_code_percent']:.1f}%")
    
    # Knots
    if knots['knot_score'] < 3:
        health_items.append(f"✅ Knot score: {knots['knot_score']}/10")
    elif knots['knot_score'] < 7:
        health_items.append(f"⚠️ Knot score: {knots['knot_score']}/10")
    else:
        health_items.append(f"❌ Knot score: {knots['knot_score']}/10 (tangled)")
    
    # Violations
    violations = purpose.get('violations', 0)
    if violations < 50:
        health_items.append(f"✅ Purpose violations: {violations}")
    elif violations < 200:
        health_items.append(f"⚠️ Purpose violations: {violations}")
    else:
        health_items.append(f"❌ Purpose violations: {violations}")
    
    for item in health_items:
        lines.append(item)
    lines.append("")
    
    # =========================================================================
    # SECTION 6: ACTIONABLE IMPROVEMENTS (What to do?)
    # =========================================================================
    lines.append("## ACTIONABLE IMPROVEMENTS")
    lines.append("")
    lines.append("Prioritized list of improvements:")
    lines.append("")
    
    improvements = []
    
    # Priority 1: Critical issues
    if knots['knot_score'] >= 7:
        improvements.append({
            'priority': 'CRITICAL',
            'action': 'Untangle Dependency Cycles',
            'target': 'Modules',
            'why': f"Knot Score {knots['knot_score']}/10 ({knots['cycles_detected']} cycles)",
            'how': 'Apply Dependency Inversion Principle, Extract shared interfaces to a neutral package, Inject dependencies via constructor'
        })
    
    if coverage['dead_code_percent'] > 10:
        orphans = full_analysis.get('orphans_list', [])[:5]
        orphan_names = [o.split(':')[-1] if ':' in o else o.split('/')[-1] for o in orphans]
        improvements.append({
            'priority': 'HIGH',
            'action': 'Prune Dead Code',
            'target': ', '.join(orphan_names[:3]),
            'why': f"{coverage['dead_code_percent']:.0f}% of code is unreachable ({counts['orphans']} orphans)",
            'how': 'Verify no dynamic imports usage, Delete files listed in orphans report, Remove unused exports'
        })
    
    if violations > 100:
        improvements.append({
            'priority': 'MEDIUM',
            'action': 'Enforce Strict Layering',
            'target': 'Architecture',
            'why': f'{violations} illegal flows detected (lower layers calling higher layers)',
            'how': 'Refactor to unidirectional flow, Introduce Event Bus for upward communication, Use Dependency Injection'
        })
    
    # High entropy nodes
    markov = full_analysis.get('markov', {})
    high_entropy = markov.get('high_entropy_nodes', [])
    if high_entropy and high_entropy[0]['fanout'] > 15:
        improvements.append({
            'priority': 'MEDIUM',
            'action': 'Decouple God Node',
            'target': f"`{high_entropy[0]['node']}`",
            'why': f"High Entropic Coupling (Fan-out: {high_entropy[0]['fanout']})",
            'how': 'Apply Interface Segregation, Split into smaller specialized services, Use Decorator pattern for cross-cutting concerns'
        })
    
    # Hub dependencies
    if full_analysis['top_hubs'] and full_analysis['top_hubs'][0]['in_degree'] > 500:
        hub = full_analysis['top_hubs'][0]
        improvements.append({
            'priority': 'LOW',
            'action': 'Optimize Hotspot',
            'target': f"`{hub['name']}`",
            'why': f"Central Traffic Hub ({hub['in_degree']} callers)",
            'how': 'Implement caching/memoization, Ensure thread-safety if stateful, Monitor for bottleneck performance'
        })
    
    # Add default if no issues
    if not improvements:
        improvements.append({
            'priority': 'LOW',
            'action': 'Maintain current health',
            'why': 'Architecture is in good shape',
            'how': 'Focus on tests and documentation'
        })
    
    # Format improvements
    for i, imp in enumerate(improvements, 1):
        lines.append(f"### {i}. [{imp['priority']}] {imp['action']}")
        lines.append(f"**Target**: `{imp.get('target', 'Codebase')}`")
        lines.append(f"**Issue**: {imp['why']}")
        lines.append("**Prescription**:")
        
        # Split 'how' into steps if it contains commas
        steps = imp['how'].split(', ')
        for step in steps:
            lines.append(f"1. {step.strip()}")
            
        lines.append("")
    
    # =========================================================================
    # SECTION 7: STRATEGIC GAPS & ROADMAP (Intelligence)
    # =========================================================================
    if 'roadmap' in full_analysis and full_analysis['roadmap']:
        lines.append("## STRATEGIC INTELLIGENCE")
        lines.append("")
        rm = full_analysis['roadmap']
        lines.append(f"**Roadmap**: {rm.get('name', 'Unknown')}")
        lines.append(f"**Maturity**: {rm.get('stage', 'Unknown')}")
        lines.append(f"**Readiness**: {rm.get('readiness_score', 0)}%")
        lines.append("")
        
        if 'gaps' in rm and rm['gaps']:
            lines.append("### 🚫 Missing Capabilities (Gaps)")
            for gap in rm['gaps']:
                lines.append(f"- **{gap}**")
            lines.append("")

        if 'violations' in rm and rm['violations']:
            lines.append("### ⚠️ Architectural Violations")
            for violation in rm['violations']:
                lines.append(f"- **{violation['rule']}**: Found in {', '.join(violation['matches'][:5])}")
            lines.append("")
            
        if 'achieved' in rm and rm['achieved']:
            lines.append("### ✅ Achieved Capabilities")
            for ach in rm['achieved']:
                lines.append(f"- {ach}")
            lines.append("")
    else:
        lines.append("## STRATEGIC INTELLIGENCE")
        lines.append("")
        lines.append("### 💡 Potentials")
        lines.append("No explicit roadmap found. Consider defining key capabilities, maturity stages, and readiness goals to guide architectural evolution.")
        lines.append("")

    # =========================================================================
    # SECTION 8: VISUAL REASONING (See the Diagram)
    # =========================================================================
    if 'topology' in full_analysis:
        topo = full_analysis['topology']
        vm = topo.get('visual_metrics', {})
        lines.append("## VISUAL REASONING (The 'Shape')")
        lines.append("")
        lines.append(f"**Overall Shape**: `{topo['shape']}`")
        lines.append(f"{topo['description']}")
        lines.append("")
        lines.append("### Topological Metrics")
        lines.append(f"- **Centralization**: {vm.get('centralization_score', 0):.2f} (0=mesh, 1=star)")
        lines.append(f"- **Components**: {vm.get('components', 1)} (islands)")
        lines.append(f"- **Largest Cluster**: {vm.get('largest_cluster_percent', 0):.1f}% of nodes")
        lines.append(f"- **Density**: {vm.get('density_score', 0):.2f} avg connections")
        lines.append("")

    # =========================================================================
    # SECTION 9: DOMAIN CONTEXT (Business Logic)
    # =========================================================================
    if 'semantics' in full_analysis:
        sem = full_analysis['semantics']
        lines.append("## DOMAIN CONTEXT (Business Meaning)")
        lines.append("")
        lines.append(f"**Inferred Domain**: `{sem['domain_inference']}`")
        lines.append("")
        lines.append("### Top Business Concepts")
        top_concepts = [f"{t['term']} ({t['count']})" for t in sem['top_concepts'][:8]]
        lines.append(", ".join(top_concepts))
        lines.append("")

    # =========================================================================
    # SECTION 10: QUICK REFERENCE
    # =========================================================================
    lines.append("## QUICK REFERENCE")
    lines.append("")
    lines.append("```")
    lines.append(f"Nodes:      {counts['nodes']}")
    lines.append(f"Edges:      {counts['edges']}")
    lines.append(f"Files:      {counts['files']}")
    lines.append(f"Entry pts:  {counts['entry_points']}")
    lines.append(f"Orphans:    {counts['orphans']}")
    lines.append(f"Cycles:     {knots['cycles_detected']}")
    lines.append(f"RPBL:       R={rpbl['responsibility']} P={rpbl['purity']} B={rpbl['boundary']} L={rpbl['lifecycle']}")
    lines.append("```")
    lines.append("")
    
    return "\n".join(lines)


def generate_from_file(analysis_path: str, output_path: str = None):
    """Generate brain download from full_analysis.json file."""
    with open(analysis_path) as f:
        analysis = json.load(f)
    
    brain = generate_brain_download(analysis)
    
    if output_path:
        with open(output_path, 'w') as f:
            f.write(brain)
        print(f"✅ Brain download saved to: {output_path}")
    else:
        print(brain)
    
    return brain


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python brain_download.py <full_analysis.json> [output.md]")
        sys.exit(1)
    
    analysis_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    generate_from_file(analysis_path, output_path)
