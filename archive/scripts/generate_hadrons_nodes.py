import json
import sys
import os

# Add current directory to path to import the engine
sys.path.append(os.getcwd())

from spectrometer_hadrons_engine import HADRON_CATALOG, Continent, Fundamental

# Map Fundamentals to Canvas Atom Node IDs
FUNDAMENTAL_NODE_MAP = {
    Fundamental.BITS: "atom1",
    Fundamental.BYTES: "atom2",
    Fundamental.PRIMITIVES: "atom3",
    Fundamental.VARIABLES: "atom4",
    Fundamental.EXPRESSIONS: "atom5",
    Fundamental.STATEMENTS: "atom6",
    Fundamental.CONTROL_STRUCTURES: "atom7",
    Fundamental.FUNCTIONS: "atom8",
    Fundamental.AGGREGATES: "atom9",
    Fundamental.MODULES: "atom10",
    Fundamental.FILES: "atom11",
    Fundamental.EXECUTABLES: "atom12"
}

# Colors for continents (approximate for Canvas)
# Canvas colors: 1=red, 2=orange, 3=yellow, 4=green, 5=cyan, 6=purple
CONTINENT_COLOR_MAP = {
    Continent.DATA_FOUNDATIONS: "5", # Cyan
    Continent.LOGIC_FLOW: "1",       # Red
    Continent.ORGANIZATION: "4",     # Green
    Continent.EXECUTION: "3"         # Amber/Orange
}

nodes = []
edges = []

# Group hadrons
hadrons_by_fundamental = {}
for name, data in HADRON_CATALOG.items():
    fund = data["fundamental"]
    if fund not in hadrons_by_fundamental:
        hadrons_by_fundamental[fund] = []
    hadrons_by_fundamental[fund].append((name, data))

# Layout parameters
START_Y = 1100
COL_WIDTH = 350
ROW_HEIGHT = 120
X_OFFSETS = {
    Continent.DATA_FOUNDATIONS: 0,
    Continent.LOGIC_FLOW: 600,
    Continent.ORGANIZATION: 1200,
    Continent.EXECUTION: 1800
}

# Track Y positions per column (Continent)
current_y_by_continent = {
    Continent.DATA_FOUNDATIONS: START_Y,
    Continent.LOGIC_FLOW: START_Y,
    Continent.ORGANIZATION: START_Y,
    Continent.EXECUTION: START_Y
}

# Order of Fundamentals to ensure vertical flow matches Atoms if possible
fundamental_order = [
    Fundamental.BITS, Fundamental.BYTES, Fundamental.PRIMITIVES, Fundamental.VARIABLES,
    Fundamental.EXPRESSIONS, Fundamental.STATEMENTS, Fundamental.CONTROL_STRUCTURES, Fundamental.FUNCTIONS,
    Fundamental.AGGREGATES, Fundamental.MODULES, Fundamental.FILES,
    Fundamental.EXECUTABLES
]

for fund in fundamental_order:
    if fund not in hadrons_by_fundamental:
        continue
    
    group_hadrons = hadrons_by_fundamental[fund]
    # Get arbitrary hadron to find continent (all in group should match)
    continent = group_hadrons[0][1]["continent"]
    
    base_x = X_OFFSETS[continent]
    base_y = current_y_by_continent[continent]
    
    parent_node_id = FUNDAMENTAL_NODE_MAP[fund]
    color = CONTINENT_COLOR_MAP[continent]
    
    # Create a visual cluster for this fundamental's hadrons
    # We will arrange them in a mini-grid 2-wide
    
    idx = 0
    for name, data in group_hadrons:
        hadron_id = f"hadron_{name}"
        
        # Grid layout for hadrons within the fundamental block
        col_idx = idx % 2
        row_idx = idx // 2
        
        x = base_x + (col_idx * 220)
        y = base_y + (row_idx * 120)
        
        # Generate description text
        # You would ideally parse the "Rule" from the markdown table, but for now we just show Name + ID
        text = f"**{name}**\n#{data.get('id', '?')}\n*{data['form']}*"
        
        node = {
            "id": hadron_id,
            "type": "text",
            "text": text,
            "x": x,
            "y": y,
            "width": 200,
            "height": 100,
            "color": color
        }
        nodes.append(node)
        
        # Edge from Parent Atom to Hadron
        edges.append({
            "id": f"edge_{parent_node_id}_{hadron_id}",
            "fromNode": parent_node_id,
            "fromSide": "bottom",
            "toNode": hadron_id,
            "toSide": "top"
        })
        
        idx += 1
    
    # Update cursor for next Fundamental in this continent
    # Calculate height used: rows * 120
    rows_used = (idx + 1) // 2
    height_block = rows_used * 120
    current_y_by_continent[continent] += height_block + 100 # Gap between groups

# Identify items to remove
remove_ids = {"missing_hadrons", "edge_m1"}

# Load existing canvas
canvas_path = "/Users/lech/PROJECTS_all/PROJECT_elements/THEORY_COMPLETE.canvas"
try:
    with open(canvas_path, 'r') as f:
        canvas_data = json.load(f)
except Exception as e:
    print(f"Error loading canvas: {e}")
    sys.exit(1)

# Filter out removed items
canvas_data["nodes"] = [n for n in canvas_data.get("nodes", []) if n["id"] not in remove_ids]
canvas_data["edges"] = [e for e in canvas_data.get("edges", []) if e["id"] not in remove_ids]

# Append new items
canvas_data["nodes"].extend(nodes)
canvas_data["edges"].extend(edges)

# Save back
try:
    with open(canvas_path, 'w') as f:
        json.dump(canvas_data, f, indent=4)
    print(f"Successfully added {len(nodes)} nodes and {len(edges)} edges to {canvas_path}")
except Exception as e:
    print(f"Error saving canvas: {e}")
    sys.exit(1)
