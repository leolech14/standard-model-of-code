#!/usr/bin/env python3
"""
Extract and analyze key data from THEORY_COMPLETE.canvas
This script processes the JSON canvas file and extracts structured information.
"""

import json
import re
from collections import defaultdict
from datetime import datetime
import sys

def load_canvas(filename):
    """Load the canvas JSON file."""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_key_info(canvas):
    """Extract key information from the canvas."""
    nodes = canvas.get('nodes', [])
    edges = canvas.get('edges', [])

    # Categorize nodes
    categories = {
        'laws': [],
        'continents': [],
        'hadrons': [],
        'subhadrons': [],
        'data_foundations': [],
        'logic_flow': [],
        'organization': [],
        'execution': [],
        'atoms': [],
        'large_texts': [],
        'missing_data': [],
        'quantum_extensions': []
    }

    # Key metrics
    metrics = {
        'total_nodes': len(nodes),
        'total_edges': len(edges),
        'text_nodes': 0,
        'large_text_nodes': 0,
        'missing_data_nodes': 0,
        'unique_concepts': set()
    }

    # Process each node
    for node in nodes:
        node_id = node.get('id', '')
        text = node.get('text', '')
        x = node.get('x', 0)
        y = node.get('y', 0)

        # Count text nodes
        if node.get('type') == 'text':
            metrics['text_nodes'] += 1

            # Track large text nodes (>500 chars)
            if len(text) > 500:
                metrics['large_text_nodes'] += 1
                categories['large_texts'].append({
                    'id': node_id,
                    'preview': text[:200] + '...' if len(text) > 200 else text,
                    'full_length': len(text),
                    'position': (x, y)
                })

        # Categorize by content and ID patterns
        if 'law' in node_id.lower() or node_id.startswith('law'):
            categories['laws'].append({'id': node_id, 'text': text, 'position': (x, y)})
            metrics['unique_concepts'].add(text)

        elif 'cont' in node_id.lower():
            categories['data_foundations'].append({'id': node_id, 'text': text, 'position': (x, y)})
            categories['logic_flow'].append({'id': node_id, 'text': text, 'position': (x, y)})
            categories['organization'].append({'id': node_id, 'text': text, 'position': (x, y)})
            categories['execution'].append({'id': node_id, 'text': text, 'position': (x, y)})

        elif 'atom' in node_id.lower():
            categories['atoms'].append({'id': node_id, 'text': text, 'position': (x, y)})
            metrics['unique_concepts'].add(text)

        elif 'missing' in text.lower() or '⚠️' in text:
            categories['missing_data'].append({'id': node_id, 'text': text, 'position': (x, y)})
            metrics['missing_data_nodes'] += 1

        elif 'quantum' in text.lower():
            categories['quantum_extensions'].append({'id': node_id, 'text': text, 'position': (x, y)})

        elif node_id in ['node1', 'node2', 'node3', 'node4', 'node5']:
            if '11 LAWS' in text:
                categories['laws'].append({'id': node_id, 'text': text, 'position': (x, y)})
            elif '12 CONTINENTS' in text or 'QUARKS' in text:
                categories['continents'].append({'id': node_id, 'text': text, 'position': (x, y)})
            elif '96 HADRONS' in text:
                categories['hadrons'].append({'id': node_id, 'text': text, 'position': (x, y)})
            elif 'SUBHADRONS' in text:
                categories['subhadrons'].append({'id': node_id, 'text': text, 'position': (x, y)})

    metrics['unique_concepts'] = len(metrics['unique_concepts'])

    return categories, metrics, edges

def extract_theoretical_numbers(text):
    """Extract numerical values that represent theoretical concepts."""
    numbers = {
        'laws': 11,
        'continents': 12,
        'hadrons': 96,
        'subhadrons_384_42': 384 - 42,  # From "384 - 42 SUBHADRONS"
        'subhadrons_1440': 1440,
        'possible_subhadrons': 342,  # 384 - 42
        'impossible_subhadrons': 42,  # From text
        'dimensions': 4  # From text about 4 fundamental forces
    }

    # Also search for numbers in the text
    found_numbers = re.findall(r'\b(\d+)\b', text)

    return numbers, found_numbers

def generate_summary(categories, metrics, edges):
    """Generate a comprehensive summary of the canvas data."""
    summary = []

    # Header
    summary.append("=" * 80)
    summary.append("THEORY_COMPLETE.CANVAS - DATA EXTRACTION REPORT")
    summary.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary.append("=" * 80)
    summary.append("")

    # Basic Metrics
    summary.append("📊 BASIC METRICS")
    summary.append("-" * 40)
    summary.append(f"Total nodes: {metrics['total_nodes']}")
    summary.append(f"Total edges (connections): {metrics['total_edges']}")
    summary.append(f"Text nodes: {metrics['text_nodes']}")
    summary.append(f"Large text nodes (>500 chars): {metrics['large_text_nodes']}")
    summary.append(f"Missing data alerts: {metrics['missing_data_nodes']}")
    summary.append(f"Unique concepts identified: {metrics['unique_concepts']}")
    summary.append("")

    # Theory Structure
    summary.append("🔬 THEORY STRUCTURE (Standard Model of Code)")
    summary.append("-" * 40)
    summary.append(f"1. {len(categories['laws'])} Laws of Physics")
    summary.append(f"2. {len(categories['continents'])} Continents/Quarks")
    summary.append(f"3. {len(categories['hadrons'])} Hadrons")
    summary.append(f"4. {len(categories['subhadrons'])} Sub-hadrons")
    summary.append("")

    # Key Theoretical Numbers
    summary.append("📐 KEY THEORETICAL NUMBERS")
    summary.append("-" * 40)
    numbers, _ = extract_theoretical_numbers("")
    for key, value in numbers.items():
        summary.append(f"{key.replace('_', ' ').title()}: {value}")
    summary.append("")

    # Data Foundations
    if categories['data_foundations']:
        summary.append("💾 DATA FOUNDATIONS")
        summary.append("-" * 40)
        for item in categories['data_foundations'][:4]:  # Show first 4
            summary.append(f"• {item['text']}")
        summary.append("")

    # Atoms of Programming
    if categories['atoms']:
        summary.append("⚛️  ATOMS OF PROGRAMMING")
        summary.append("-" * 40)
        for item in categories['atoms']:
            summary.append(f"• {item['text']}")
        summary.append("")

    # Laws
    if categories['laws']:
        summary.append("⚖️  LAWS OF PHYSICS")
        summary.append("-" * 40)
        for item in categories['laws']:
            if item['text'] and not item['text'].startswith('#'):
                summary.append(f"• {item['text']}")
        summary.append("")

    # Missing Data
    if categories['missing_data']:
        summary.append("⚠️  MISSING DATA ALERTS")
        summary.append("-" * 40)
        for item in categories['missing_data']:
            summary.append(f"• {item['text']}")
        summary.append("")

    # Large Text Analysis
    if categories['large_texts']:
        summary.append("📚 LARGE TEXT DOCUMENTS")
        summary.append("-" * 40)
        for i, item in enumerate(categories['large_texts'], 1):
            summary.append(f"\nDocument {i} (ID: {item['id']})")
            summary.append(f"Length: {item['full_length']} characters")
            summary.append(f"Preview: {item['preview'][:100]}...")

            # Extract key insights
            full_text = item['preview']
            if '384' in full_text and '42' in full_text:
                summary.append("  → Contains 384-42 sub-hadron theory")
            if 'Spectrometer' in full_text:
                summary.append("  → Describes Spectrometer tool")
            if 'Higgs' in full_text:
                summary.append("  → References Higgs boson analogy")
        summary.append("")

    # Key Insights
    summary.append("💡 KEY INSIGHTS")
    summary.append("-" * 40)
    summary.append("• The canvas describes a 'Standard Model of Code' with:")
    summary.append("  - 11 fundamental laws")
    summary.append("  - 12 quarks/continents")
    summary.append("  - 96 hadrons")
    summary.append("  - 384 sub-hadrons (342 possible + 42 impossible)")
    summary.append("")
    summary.append("• The 42 'impossible' sub-hadrons represent architectural")
    summary.append("  anti-patterns that violate fundamental laws")
    summary.append("")
    summary.append("• Maps software architecture to 4 fundamental forces:")
    summary.append("  1. Strong Force = Responsibility (Domain)")
    summary.append("  2. Electromagnetic = Purity (side-effects)")
    summary.append("  3. Weak Force = Boundary (layer)")
    summary.append("  4. Gravity = Lifecycle (temporal)")
    summary.append("")

    return "\n".join(summary)

def save_extracted_data(categories, metrics, output_file):
    """Save extracted data to JSON file."""
    data = {
        'extraction_timestamp': datetime.now().isoformat(),
        'metrics': metrics,
        'categories': categories,
        'theoretical_numbers': {
            'laws': 11,
            'continents_quarks': 12,
            'hadrons': 96,
            'subhadrons_total': 384,
            'subhadrons_possible': 342,
            'subhadrons_impossible': 42,
            'dimensions': 4
        }
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Extracted data saved to: {output_file}")

def main():
    """Main execution function."""
    input_file = '/Users/lech/PROJECTS_all/PROJECT_elements/THEORY_COMPLETE.canvas'

    print("🔍 Loading canvas file...")
    try:
        canvas = load_canvas(input_file)
    except FileNotFoundError:
        print(f"❌ Error: File not found: {input_file}")
        sys.exit(1)

    print("📊 Extracting key information...")
    categories, metrics, edges = extract_key_info(canvas)

    print("📋 Generating summary...")
    summary = generate_summary(categories, metrics, edges)

    # Print summary to console
    print("\n" + summary)

    # Save detailed data
    output_file = '/Users/lech/PROJECTS_all/PROJECT_elements/canvas_extracted_data.json'
    save_extracted_data(categories, metrics, output_file)

    # Save summary to file
    summary_file = '/Users/lech/PROJECTS_all/PROJECT_elements/canvas_summary.txt'
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)

    print(f"\n✅ Summary saved to: {summary_file}")
    print("\n🎯 Extraction complete!")

if __name__ == "__main__":
    main()