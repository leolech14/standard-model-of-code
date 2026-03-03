#!/usr/bin/env python3
"""
Generate a sample dev payload for the Vite dev server.

Usage:
    cd particle && .venv/bin/python3 scripts/gen-dev-payload.py

This creates build/src/core/viz/build/dev-payload.txt containing a small
gzipped+base64 graph payload for local development without running the
full Collider pipeline.
"""

import json
import gzip
import base64
from pathlib import Path

def generate_dev_payload():
    """Generate a minimal but realistic graph payload for development."""

    nodes = [
        {"id": f"node_{i}", "name": f"Module{i}", "atom": atom, "val": 1.0,
         "color": color, "layer": "Core", "ring": ring, "role": "Unknown",
         "file": f"src/module_{i}.py", "fileIdx": i % 5,
         "boundary": "internal", "state": "stateless", "lifecycle": "use",
         "in_degree": i % 4, "out_degree": (i + 1) % 5, "fan_in": i % 4,
         "fan_out": (i + 1) % 5, "complexity": i * 3, "loc": 50 + i * 20,
         "trust": 0.9, "responsibility": 5, "purity": 5,
         "lifecycle_score": 5, "boundary_score": 5,
         "centrality": 0.1 * i, "rank": 0.05 * i, "depth": i % 3,
         "churn": i, "age": 30 - i, "body": ""}
        for i, (atom, color, ring) in enumerate([
            ("Function", "#5a9a70", "DOMAIN"),
            ("Class", "#7090a0", "APPLICATION"),
            ("Method", "#b07070", "DOMAIN"),
            ("Variable", "#a09060", "INFRASTRUCTURE"),
            ("Import", "#667788", "DOMAIN"),
            ("Module", "#5a9a70", "APPLICATION"),
            ("Constant", "#7090a0", "TESTING"),
            ("Interface", "#b07070", "PRESENTATION"),
            ("Function", "#5a9a70", "DOMAIN"),
            ("Class", "#a09060", "APPLICATION"),
        ])
    ]

    edges = [
        {"source": f"node_{i}", "target": f"node_{(i+1) % 10}",
         "color": "#333333", "opacity": 0.2, "edge_type": "calls",
         "weight": 1.0, "markov_weight": 0.1, "confidence": 0.9,
         "resolution": "resolved"}
        for i in range(10)
    ]

    graph_data = {
        "nodes": nodes,
        "links": edges,
        "file_boundaries": [
            {"file": f"src/module_{i}.py", "file_name": f"module_{i}.py",
             "atom_count": 2, "line_range": [1, 100], "cohesion": 0.8,
             "purpose": "General module", "classes": [], "functions": []}
            for i in range(5)
        ],
        "kpis": {
            "edge_resolution_percent": 85.0,
            "call_ratio_percent": 60.0,
            "orphan_count": 1,
            "top_hub_count": 2,
            "topology_shape": "LAYERED"
        },
        "meta": {
            "version": "dev",
            "target": "/dev/sample",
            "timestamp": "2026-02-28T00:00:00"
        },
        "physics": {"forces": {"charge": {"strength": -120}}},
        "appearance": {},
        "controls": {"filters": {"rings": ["DOMAIN", "APPLICATION"], "families": []}},
        "counts": {"nodes": 10, "edges": 10},
        "stats": {},
        "theme_config": {}
    }

    # Compress
    json_bytes = json.dumps(graph_data).encode('utf-8')
    compressed = gzip.compress(json_bytes)
    b64_payload = base64.b64encode(compressed).decode('utf-8')

    # Write to dev-payload.txt
    output_path = Path(__file__).parent.parent / "src/core/viz/build/dev-payload.txt"
    output_path.write_text(b64_payload, encoding='utf-8')

    print(f"Dev payload generated: {output_path}")
    print(f"  Nodes: {len(nodes)}, Edges: {len(edges)}")
    print(f"  Original: {len(json_bytes)} bytes")
    print(f"  Compressed: {len(compressed)} bytes")
    print(f"  Base64: {len(b64_payload)} bytes")

    return b64_payload


if __name__ == '__main__':
    generate_dev_payload()
