import json
import re
import sys
import os

CANVAS_PATH = "/Users/lech/PROJECTS_all/PROJECT_elements/THEORY_COMPLETE.canvas"
SOURCE_MD_PATH = "/Users/lech/PROJECTS_all/PROJECT_elements/spectrometer_v12_minimal/HADRONS_MERMAID_DIAGRAM.md"

def extract_mermaid(content, header):
    # Find header
    header_idx = content.find(header)
    if header_idx == -1:
        print(f"Warning: Header '{header}' not found.")
        return None
    
    # Find next mermaid block after header
    mermaid_start = content.find("```mermaid", header_idx)
    if mermaid_start == -1:
        print(f"Warning: Mermaid block not found after '{header}'.")
        return None
        
    start_content = mermaid_start + len("```mermaid")
    mermaid_end = content.find("```", start_content)
    
    if mermaid_end == -1:
        print(f"Warning: Mermaid block end not found after '{header}'.")
        return None
        
    return content[start_content:mermaid_end].strip()

def main():
    try:
        with open(SOURCE_MD_PATH, 'r') as f:
            md_content = f.read()
    except Exception as e:
        print(f"Error reading source MD: {e}")
        sys.exit(1)

    # Extract 1: Classification Diagram
    class_diag = extract_mermaid(md_content, "COMPLETE HADRON CLASSIFICATION DIAGRAM")
    if class_diag:
        class_node_text = f"```mermaid\n{class_diag}\n```"
    else:
        print("Failed to extract Classification Diagram")
        sys.exit(1)

    # Extract 2: Particle Zoo
    zoo_diag = extract_mermaid(md_content, "COMPLETE PARTICLE ZOO DIAGRAM")
    if zoo_diag:
        # Mindmap needs to be careful with indentation, usually strict.
        # extraction strip() might remove leading spaces of first line but mindmap root usually has 0 indent.
        zoo_node_text = f"```mermaid\n{zoo_diag}\n```"
    else:
        print("Failed to extract Particle Zoo Diagram")
        sys.exit(1)

    # Load Canvas
    try:
        with open(CANVAS_PATH, 'r') as f:
            canvas = json.load(f)
    except Exception as e:
        print(f"Error reading canvas: {e}")
        sys.exit(1)

    # Define new nodes
    new_nodes = [
        {
            "id": "node_mermaid_zoo",
            "type": "text",
            "text": f"# PARTICLE ZOO\n{zoo_node_text}",
            "x": -900,
            "y": 1200,
            "width": 800,
            "height": 900,
            "color": "6" # Purple
        },
        {
            "id": "node_mermaid_classification",
            "type": "text",
            "text": f"# CLASSIFICATION\n{class_node_text}",
            "x": 1800,
            "y": 1200,
            "width": 800,
            "height": 900,
            "color": "2" # Orange
        }
    ]

    # Remove existing if they exist (to allow re-running)
    existing_ids = {n["id"] for n in new_nodes}
    canvas["nodes"] = [n for n in canvas.get("nodes", []) if n["id"] not in existing_ids]
    
    # Add new
    canvas["nodes"].extend(new_nodes)

    # Save
    try:
        with open(CANVAS_PATH, 'w') as f:
            json.dump(canvas, f, indent=4)
        print(f"Successfully added {len(new_nodes)} Mermaid nodes to {CANVAS_PATH}")
    except Exception as e:
        print(f"Error saving canvas: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
