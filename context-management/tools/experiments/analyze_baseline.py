#!/usr/bin/env python3
"""
Baseline Analyzer
Extracts metrics from Refinery output to establish "Before" state.
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

def analyze_baseline(input_json: str) -> dict:
    """Generate baseline metrics from Refinery output."""

    with open(input_json, 'r') as f:
        data = json.load(f)

    nodes = data.get('nodes', [])
    total_nodes = len(nodes)

    # Metrics
    documented = 0
    total_relevance = 0
    chunk_sizes = []
    file_coverage = defaultdict(int)

    for node in nodes:
        content = node.get('content', '')
        relevance = node.get('relevance_score', 0)
        source = node.get('source_file', 'unknown')

        # Documentation heuristic: has docstring markers or is markdown header
        has_doc = '"""' in content or "'''" in content or content.strip().startswith('#')
        if has_doc:
            documented += 1

        total_relevance += relevance
        chunk_sizes.append(len(content))
        file_coverage[Path(source).name] += 1

    avg_relevance = total_relevance / total_nodes if total_nodes > 0 else 0
    avg_chunk_size = sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0
    doc_coverage = (documented / total_nodes * 100) if total_nodes > 0 else 0

    # Top files by chunk count (complexity proxy)
    top_files = sorted(file_coverage.items(), key=lambda x: x[1], reverse=True)[:10]

    report = {
        "timestamp": data.get('exported_at'),
        "total_chunks": total_nodes,
        "total_tokens": data.get('total_tokens', 0),
        "metrics": {
            "documentation_coverage_pct": round(doc_coverage, 2),
            "avg_relevance_score": round(avg_relevance, 3),
            "avg_chunk_size_chars": round(avg_chunk_size, 0),
            "documented_chunks": documented,
            "undocumented_chunks": total_nodes - documented
        },
        "top_files_by_complexity": [
            {"file": f, "chunk_count": c} for f, c in top_files
        ],
        "recommendations": []
    }

    # Generate recommendations
    if doc_coverage < 80:
        report["recommendations"].append({
            "priority": "HIGH",
            "action": "Deploy courier_archivist",
            "reason": f"Documentation coverage at {doc_coverage:.1f}% (target: 80%)"
        })

    if avg_chunk_size > 500:
        report["recommendations"].append({
            "priority": "MEDIUM",
            "action": "Deploy courier_mechanic",
            "reason": f"Large average chunk size ({avg_chunk_size:.0f} chars) suggests complexity"
        })

    return report

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: analyze_baseline.py <logistics_demo.json>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = input_file.replace('logistics_demo.json', 'baseline_report.json')

    print(f"📊 Analyzing baseline metrics from {input_file}...")

    report = analyze_baseline(input_file)

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"✅ Baseline report saved to {output_file}")
    print(f"\n📈 BASELINE METRICS:")
    print(f"   Total Chunks: {report['total_chunks']}")
    print(f"   Documentation Coverage: {report['metrics']['documentation_coverage_pct']}%")
    print(f"   Avg Relevance Score: {report['metrics']['avg_relevance_score']}")
    print(f"   Avg Chunk Size: {report['metrics']['avg_chunk_size_chars']} chars")
    print(f"\n🎯 RECOMMENDATIONS:")
    for rec in report['recommendations']:
        print(f"   [{rec['priority']}] {rec['action']}: {rec['reason']}")
