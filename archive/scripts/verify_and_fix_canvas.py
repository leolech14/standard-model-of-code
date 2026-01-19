#!/usr/bin/env python3
"""
Verify and fix Obsidian canvas files for valid JSON structure.
This script checks canvas files and creates fixed versions if needed.
"""

import json
import os
import sys
from datetime import datetime

def verify_canvas_json(filepath):
    """Verify if a canvas file has valid JSON structure."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Try to parse the JSON
        data = json.loads(content)

        # Basic structure checks
        if not isinstance(data, dict):
            return False, "Root is not a dictionary"

        if 'nodes' not in data or 'edges' not in data:
            return False, "Missing 'nodes' or 'edges' keys"

        if not isinstance(data['nodes'], list) or not isinstance(data['edges'], list):
            return False, "nodes or edges are not lists"

        # Check each node has required fields
        for i, node in enumerate(data['nodes']):
            if not isinstance(node, dict):
                return False, f"Node {i} is not a dictionary"
            if 'id' not in node:
                return False, f"Node {i} missing 'id' field"
            if 'type' not in node:
                return False, f"Node {i} missing 'type' field"

        # Check each edge has required fields
        for i, edge in enumerate(data['edges']):
            if not isinstance(edge, dict):
                return False, f"Edge {i} is not a dictionary"
            if 'id' not in edge:
                return False, f"Edge {i} missing 'id' field"
            if 'fromNode' not in edge or 'toNode' not in edge:
                return False, f"Edge {i} missing connection fields"

        return True, "Valid JSON structure"

    except json.JSONDecodeError as e:
        return False, f"JSON Decode Error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def clean_json_content(content):
    """Remove JavaScript-style comments from JSON content."""
    # Remove single-line comments (// ...)
    lines = content.split('\n')
    cleaned_lines = []

    for line in lines:
        # Check if line has a comment outside of strings
        in_string = False
        comment_start = -1
        i = 0
        while i < len(line):
            if not in_string:
                if line[i:i+2] == '//':
                    comment_start = i
                    break
                elif line[i] == '"':
                    in_string = True
            else:
                if line[i] == '"' and (i == 0 or line[i-1] != '\\'):
                    in_string = False
            i += 1

        if comment_start >= 0:
            line = line[:comment_start].rstrip()
        cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)

def fix_canvas_file(input_path, output_path=None):
    """Fix a canvas file by removing comments and ensuring valid JSON."""
    if output_path is None:
        output_path = input_path.replace('.canvas', '_fixed.canvas')

    print(f"\n🔧 Fixing {input_path}...")

    # Read the original file
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Clean the content (remove comments)
    cleaned_content = clean_json_content(content)

    # Try to parse and reformat the JSON
    try:
        data = json.loads(cleaned_content)
        # Re-format with proper indentation
        formatted_json = json.dumps(data, indent='\t', ensure_ascii=False)

        # Write the fixed version
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted_json)

        print(f"✅ Fixed file saved as: {output_path}")

        # Verify the fixed file
        is_valid, message = verify_canvas_json(output_path)
        if is_valid:
            print(f"✅ Fixed file verification: {message}")
        else:
            print(f"❌ Fixed file verification failed: {message}")

        return True, output_path

    except Exception as e:
        print(f"❌ Failed to fix file: {str(e)}")
        return False, str(e)

def analyze_canvas_structure(filepath):
    """Analyze the structure of a canvas file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        nodes = data.get('nodes', [])
        edges = data.get('edges', [])

        # Count node types
        node_types = {}
        node_colors = {}
        node_count_by_type = {}

        for node in nodes:
            node_type = node.get('type', 'unknown')
            node_color = str(node.get('color', 'none'))

            node_types[node_type] = node_types.get(node_type, 0) + 1
            node_colors[node_color] = node_colors.get(node_color, 0) + 1
            node_count_by_type[node_type] = node_count_by_type.get(node_type, 0) + 1

        # Find canvas bounds
        x_positions = [node.get('x', 0) for node in nodes]
        y_positions = [node.get('y', 0) for node in nodes]

        bounds = {
            'min_x': min(x_positions) if x_positions else 0,
            'max_x': max(x_positions) if x_positions else 0,
            'min_y': min(y_positions) if y_positions else 0,
            'max_y': max(y_positions) if y_positions else 0,
            'width': max(x_positions) - min(x_positions) if x_positions else 0,
            'height': max(y_positions) - min(y_positions) if y_positions else 0
        }

        return {
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'node_types': node_types,
            'node_colors': node_colors,
            'bounds': bounds
        }

    except Exception as e:
        return {'error': str(e)}

def main():
    """Main verification and fixing process."""
    print("🔍 Obsidian Canvas Verification and Fix Tool")
    print("=" * 50)

    # List of canvas files to check
    canvas_files = [
        'THEORY_COMPLETE.canvas',
        'THEORY_COMPLETE_ORGANIZED.canvas',
        'THEORY_COMPLETE_FIXED.canvas',
        'THEORY_COMPLETE_CLEAN.canvas',
        'THEORY_COMPLETE_VALID.canvas'
    ]

    print(f"\n📁 Checking files in: {os.getcwd()}")
    print("-" * 50)

    results = {}

    # Check each file
    for filename in canvas_files:
        filepath = filename
        if not os.path.exists(filepath):
            print(f"❌ {filename}: File not found")
            results[filename] = {'exists': False}
            continue

        print(f"\n📄 Checking {filename}...")

        # Verify JSON structure
        is_valid, message = verify_canvas_json(filepath)
        results[filename] = {
            'exists': True,
            'is_valid': is_valid,
            'message': message
        }

        if is_valid:
            print(f"✅ {filename}: {message}")

            # Analyze structure
            analysis = analyze_canvas_structure(filepath)
            if 'error' not in analysis:
                print(f"   📊 Nodes: {analysis['total_nodes']}")
                print(f"   📊 Edges: {analysis['total_edges']}")
                print(f"   📊 Types: {list(analysis['node_types'].keys())}")
                print(f"   📊 Colors: {analysis['node_colors']}")
                print(f"   📊 Canvas size: {analysis['bounds']['width']} x {analysis['bounds']['height']}")
        else:
            print(f"❌ {filename}: {message}")

            # Try to fix it
            success, fixed_path = fix_canvas_file(filepath)
            results[filename]['fixed'] = success
            results[filename]['fixed_path'] = fixed_path

    # Summary
    print("\n" + "=" * 50)
    print("📋 SUMMARY")
    print("-" * 50)

    for filename, result in results.items():
        if not result.get('exists'):
            continue

        status = "✅ Valid" if result.get('is_valid') else "❌ Invalid"
        if result.get('fixed'):
            status += " → 🔧 Fixed"

        print(f"{status:15} {filename}")

    # Recommendation
    print("\n💡 RECOMMENDATION:")
    valid_files = [f for f, r in results.items() if r.get('is_valid')]

    if valid_files:
        best_file = None
        for f in valid_files:
            if 'ORGANIZED' in f or 'VALID' in f:
                best_file = f
                break

        if best_file:
            print(f"   Use: {best_file}")
            print(f"   This file has valid JSON and should open in Obsidian.")
        else:
            print(f"   Use: {valid_files[0]}")
            print(f"   This file has valid JSON structure.")
    else:
        print("   ❌ No valid files found. All files need fixing.")

if __name__ == "__main__":
    main()