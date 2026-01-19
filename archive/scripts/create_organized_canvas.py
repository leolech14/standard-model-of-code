#!/usr/bin/env python3
"""
Create a properly organized version of THEORY_COMPLETE.canvas with valid JSON.
"""

import json
import os
from datetime import datetime

def load_canvas(filename):
    """Load canvas file."""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_organized_structure():
    """Create an organized canvas structure with key content from the original."""

    # Load the original canvas
    original = load_canvas('THEORY_COMPLETE.canvas')

    # Create new organized structure
    organized = {
        "nodes": [],
        "edges": []
    }

    # Main title
    organized["nodes"].append({
        "id": "theory_title",
        "type": "text",
        "text": "# Standard Model of Software Architecture\n\n**A Complete Ontological Framework for Code Analysis**\n\n- 11 Fundamental Laws\n- 12 Quarks/Continents\n- 96 Hadrons\n- 384 Sub-hadrons (342 possible + 42 impossible)\n\n---\n\n*The Spectrometer v10 can detect architectural antimatter*",
        "x": -500,
        "y": -1800,
        "width": 600,
        "height": 250,
        "color": "6"
    })

    # Laws of Physics
    organized["nodes"].append({
        "id": "laws_group",
        "type": "group",
        "label": "11 Laws of Physics",
        "x": -550,
        "y": -1500,
        "width": 2200,
        "height": 350
    })

    organized["nodes"].append({
        "id": "laws_title",
        "type": "text",
        "text": "## 11 Laws of Physics\n\nFundamental constraints that govern all software architecture",
        "x": -500,
        "y": -1450,
        "width": 400,
        "height": 80,
        "color": "6"
    })

    # Add the 11 laws
    laws = [
        ("Free 3D", "Unbounded spatial freedom", -450, -1300, "1"),
        ("Disk 2D", "Flat storage optimization", -250, -1300, "1"),
        ("Plane 2.5D", "Surface with depth", -50, -1300, "1"),
        ("Sphere 2.5D", "Curved space", 150, -1300, "1"),
        ("Billiard", "Deterministic collisions", 350, -1300, "1"),
        ("EM Field A", "Electric component", 550, -1300, "2"),
        ("EM Field B", "Magnetic component", 750, -1300, "2"),
        ("EM Field C", "Combined field", 950, -1300, "2"),
        ("Cosmic", "Universal scale", 1150, -1300, "3"),
        ("Ocean", "Fluid dynamics", 1350, -1300, "3"),
        ("Subatomic", "Quantum level", 1550, -1300, "3")
    ]

    for i, (name, desc, x, y, color) in enumerate(laws):
        organized["nodes"].append({
            "id": f"law{i+1}",
            "type": "text",
            "text": f"**{name}**\n\n{desc}",
            "x": x,
            "y": y,
            "width": 180,
            "height": 80,
            "color": color
        })

    # Four Forces mapping
    organized["nodes"].append({
        "id": "forces_table",
        "type": "text",
        "text": "### The Four Forces Mapping\n\n| Force | Intensity | Software Dimension |\n|-------|-----------|-------------------|\n| Strong | 10³⁸ | Responsibility |\n| Electromagnetic | 10³⁶ | Purity |\n| Weak | 10²⁵ | Boundary |\n| Gravity | 10⁰ | Lifecycle |\n\n**This matches software pattern importance**",
        "x": -500,
        "y": -1100,
        "width": 500,
        "height": 150,
        "color": "5"
    })

    # Key Metrics section
    organized["nodes"].append({
        "id": "metrics_group",
        "type": "group",
        "label": "Key Metrics & Statistics",
        "x": -550,
        "y": -900,
        "width": 2200,
        "height": 400
    })

    organized["nodes"].append({
        "id": "metrics_title",
        "type": "text",
        "text": "## Key Metrics & Statistics\n\n**The Standard Model by the numbers**",
        "x": -500,
        "y": -850,
        "width": 400,
        "height": 80,
        "color": "6"
    })

    # Impossible Patterns
    organized["nodes"].append({
        "id": "impossible_patterns",
        "type": "text",
        "text": "### ⚛️ 42 IMPOSSIBLE PATTERNS\n\n**Architectural Antimatter**\n\nThese patterns violate fundamental laws:\n\n1. **CommandHandler::FindById** - Violates CQRS\n2. **QueryHandler::Save** - Violates CQRS\n3. **Entity::Stateless** - Identity contradiction\n4. **ValueObject::HasIdentity** - Value contradiction\n5. **RepositoryImpl::Pure** - I/O contradiction\n6. **PureFunction::ExternalIO** - Purity violation\n\n**These appear as \"black holes\" in the Spectrometer**",
        "x": 50,
        "y": -850,
        "width": 400,
        "height": 200,
        "color": "1"
    })

    # Performance Impact
    organized["nodes"].append({
        "id": "performance_impact",
        "type": "text",
        "text": "### Performance Impact\n\n✅ **97.3% faster** comprehension\n✅ **98.2% smaller** dependency graphs\n✅ **100%** violation detection\n✅ **<3 seconds** analysis time\n\n**Validated on 28 repositories**",
        "x": 500,
        "y": -850,
        "width": 300,
        "height": 150,
        "color": "2"
    })

    # 10.9% Constant
    organized["nodes"].append({
        "id": "constant",
        "type": "text",
        "text": "### The 10.9% Constant\n\nUniversal across representation systems:\n\n- OKLCH color space\n- Chemical elements\n- Unicode reserved chars\n- Software architecture patterns\n\n**The antimatter ratio is universal**",
        "x": 850,
        "y": -850,
        "width": 300,
        "height": 150,
        "color": "4"
    })

    # Spectrometer v10
    organized["nodes"].append({
        "id": "spectrometer_group",
        "type": "group",
        "label": "Spectrometer v10 - The Antimatter Detector",
        "x": -550,
        "y": -450,
        "width": 2200,
        "height": 350
    })

    organized["nodes"].append({
        "id": "spectrometer_title",
        "type": "text",
        "text": "## Spectrometer v10\n\n**The Antimatter Detector**\n\nReal-time detection of architectural violations",
        "x": -500,
        "y": -400,
        "width": 400,
        "height": 80,
        "color": "6"
    })

    organized["nodes"].append({
        "id": "spectrometer_features",
        "type": "text",
        "text": "### Core Capabilities\n\n- **AST parsing**\n- **Symbolic graph**\n- **96 + 11 rules**\n- **Real-time detection**\n- **Black hole markers**\n- **Force analysis**\n- **Architecture metrics**",
        "x": -50,
        "y": -400,
        "width": 300,
        "height": 200,
        "color": "1"
    })

    # Practical Applications
    organized["nodes"].append({
        "id": "applications_group",
        "type": "group",
        "label": "Practical Applications",
        "x": -550,
        "y": -50,
        "width": 2200,
        "height": 300
    })

    organized["nodes"].append({
        "id": "applications_title",
        "type": "text",
        "text": "## Practical Applications\n\n**Real-world uses of the Standard Model**",
        "x": -500,
        "y": 0,
        "width": 400,
        "height": 80,
        "color": "6"
    })

    applications = [
        ("Code Review", "Detect violations", -450, 100, "2"),
        ("Legacy Migration", "Map existing code", -200, 100, "2"),
        ("Team Training", "Establish standards", 50, 100, "2"),
        ("Code Generation", "Validate output", 300, 100, "2"),
        ("Architecture Design", "Pattern selection", 550, 100, "2"),
        ("Quality Assurance", "Automated checks", 800, 100, "2"),
        ("Documentation", "Auto-generate docs", 1050, 100, "2"),
        ("Refactoring", "Safe transformations", 1300, 100, "2")
    ]

    for i, (name, desc, x, y, color) in enumerate(applications):
        organized["nodes"].append({
            "id": f"app{i+1}",
            "type": "text",
            "text": f"**{name}**\n\n{desc}",
            "x": x,
            "y": y,
            "width": 200,
            "height": 80,
            "color": color
        })

    # Add edges (connections)
    organized["edges"] = [
        {"id": "edge_title_laws", "fromNode": "theory_title", "fromSide": "bottom", "toNode": "laws_title", "toSide": "top", "color": "6"},
        {"id": "edge_laws_forces", "fromNode": "laws_title", "fromSide": "bottom", "toNode": "forces_table", "toSide": "top", "color": "6"},
        {"id": "edge_forces_metrics", "fromNode": "forces_table", "fromSide": "bottom", "toNode": "metrics_title", "toSide": "top", "color": "6"},
        {"id": "edge_metrics_spectrometer", "fromNode": "metrics_group", "fromSide": "bottom", "toNode": "spectrometer_title", "toSide": "top", "color": "6"},
        {"id": "edge_spectrometer_apps", "fromNode": "spectrometer_group", "fromSide": "bottom", "toNode": "applications_title", "toSide": "top", "color": "6"}
    ]

    return organized

def save_canvas(data, filename):
    """Save canvas to file with proper JSON formatting."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent='\t', ensure_ascii=False)

def main():
    print("🎯 Creating organized canvas file...")
    print("-" * 50)

    # Create organized structure
    organized = create_organized_structure()

    # Save the file
    output_file = "THEORY_COMPLETE_ORGANIZED_v2.canvas"
    save_canvas(organized, output_file)

    print(f"✅ Created: {output_file}")
    print(f"   📊 Nodes: {len(organized['nodes'])}")
    print(f"   📊 Edges: {len(organized['edges'])}")
    print(f"   📊 Groups: 4 (Laws, Metrics, Spectrometer, Applications)")
    print(f"\n✅ This file has valid JSON and should open in Obsidian!")
    print(f"✅ The content is organized logically for better navigation.")

    # Verify the created file
    print(f"\n🔍 Verifying created file...")
    try:
        with open(output_file, 'r') as f:
            json.load(f)
        print("✅ File has valid JSON structure!")
    except json.JSONDecodeError as e:
        print(f"❌ JSON Error: {e}")

if __name__ == "__main__":
    main()