import json
import csv
import sys
import os

CSV_PATH = "/Users/lech/PROJECTS_all/PROJECT_elements/384_several_false.csv"
CANVAS_PATH = "/Users/lech/PROJECTS_all/PROJECT_elements/THEORY_COMPLETE.canvas"

# Canvas color mapping
# 1=Red, 2=Orange, 3=Yellow/Amber, 4=Green, 5=Cyan, 6=Purple
COLOR_MAP = {
    "DATA_FOUNDATIONS": "5",
    "LOGIC_FLOW": "1",
    "ORGANIZATION": "4",
    "EXECUTION": "3",
    "IMPOSSIBLE": "1" # Red for impossible
}

# Values for Quarks in CSV might need normalization if they differ from keys above
# Looking at CSV: "quark_parent" col has values like "Aggregates", "Functions". Wait.
# checking line 2 of CSV: "quark_parent" is "Aggregates".
# Ah, "quark_parent" in the CSV seems to be the Fundamental?
# Let's check CSV line 2 again: "Entity", "Aggregates"
# Column headers: id,subhadron_name,base_hadron,quark_parent,responsibility...
# Line 2: 1,Entity_WithInvariants,Entity,Aggregates,...
# Line 10: 9,CommandHandler_Create,CommandHandler,Functions,...
# Line 16: 15,Repository_PureFunction,RepositoryImpl,Organization,...
# Wait, "Organization" is a Continent. "Aggregates" is a Fundamental.
# It seems the "quark_parent" column is mixed or I need to map Fundamentals to Continents.
# I have the mapping in `spectrometer_hadrons_engine.py` (which I read previously).
# Let's rely on a hardcoded map for safety.

FUNDAMENTAL_TO_CONTINENT = {
    "Bits": "DATA_FOUNDATIONS",
    "Bytes": "DATA_FOUNDATIONS",
    "Primitives": "DATA_FOUNDATIONS",
    "Variables": "DATA_FOUNDATIONS",
    "Expressions": "LOGIC_FLOW",
    "Statements": "LOGIC_FLOW",
    "Control Structures": "LOGIC_FLOW", 
    "Functions": "LOGIC_FLOW",
    "Aggregates": "ORGANIZATION",
    "Modules": "ORGANIZATION",
    "Files": "ORGANIZATION",
    "Executables": "EXECUTION",
    # Mappings from CSV values if they differ
    "Aggregates": "ORGANIZATION",
    "Functions": "LOGIC_FLOW",
    "Organization": "ORGANIZATION", # This row 16 seems to have Continent in that column?
    "Execution": "EXECUTION",
    "Infrastructure": "ORGANIZATION", # Wait, is Infrastructure a Fundamental? No.
    "Interface": "EXECUTION" # Map based on previous knowledge if possible.
}

# Wait, let's look at the CSV again.
# Line 16: RepositoryImpl, Organization.  "Organization" is a continent.
# Line 18: APIHandler, Execution. "Execution" is a continent.
# It seems the column `quark_parent` might be Continent for some and Fundamental for others?
# Or maybe the column name `quark_parent` implies Continent, but "Aggregates" is a fundamental.
# Actually, `spectrometer_hadrons_engine.py` has:
# "Entity": {"continent": Continent.ORGANIZATION, "fundamental": Fundamental.AGGREGATES}
# In the CSV line 2: 1,Entity_WithInvariants,Entity,Aggregates...
# So column 4 is "Aggregates".
# In spectrometer engine, Entity is in Organization.
# Let's trust the spectrometer engine mapping for the Base Hadron -> Continent.
# I will use the `spectrometer_hadrons_engine.py` to lookup the Continent for the `base_hadron`.

sys.path.append(os.getcwd())
try:
    from spectrometer_hadrons_engine import HADRON_CATALOG, Continent
except ImportError:
    # Fallback if import fails (e.g. env issues), though it should work.
    print("Warning: Could not import engine. Will attempt fallback logic.")
    HADRON_CATALOG = {}

def get_continent_color(base_hadron_name):
    # Lookup in catalog
    if base_hadron_name in HADRON_CATALOG:
        cont = HADRON_CATALOG[base_hadron_name]["continent"]
        # cont is an Enum, e.g. Continent.DATA_FOUNDATIONS
        curr_name = cont.name # "DATA_FOUNDATIONS"
        return COLOR_MAP.get(curr_name, "0")
    
    # Fallback based on known prefixes or guessing if catalog missing
    return "0" 

def main():
    nodes = []
    
    # Grid settings
    START_X = 0
    START_Y = 2000 # Below Hadrons (which are at 1000)
    COL_WIDTH = 400
    ROW_HEIGHT = 250 # Taller cards for subhadrons
    COLS_PER_ROW = 8 # 384 is a lot. 8 wide -> 48 rows.
    
    # Group by Continent for layout?
    # Or just one massive grid?
    # The user plan said: "grouped by their Parent Quark (Continent)"
    # So I should create 4 separate areas like the Hadrons.
    
    subhadrons_by_continent = {
        "DATA_FOUNDATIONS": [],
        "LOGIC_FLOW": [],
        "ORGANIZATION": [],
        "EXECUTION": []
    }
    
    with open(CSV_PATH, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            base = row['base_hadron']
            
            # Determine continent
            continent_name = "UNKNOWN"
            if base in HADRON_CATALOG:
                 continent_name = HADRON_CATALOG[base]["continent"].name
            else:
                # Try to map from 'quark_parent' column if catalog fails
                qp = row['quark_parent'].upper()
                if "DATA" in qp: continent_name = "DATA_FOUNDATIONS"
                elif "LOGIC" in qp or "FUNCTION" in qp: continent_name = "LOGIC_FLOW"
                elif "ORG" in qp or "AGGREGATE" in qp: continent_name = "ORGANIZATION"
                elif "EXEC" in qp: continent_name = "EXECUTION"
            
            if continent_name not in subhadrons_by_continent:
                # Handle edge cases or put in Organization default
                continent_name = "ORGANIZATION"
                
            subhadrons_by_continent[continent_name].append(row)

    # Layout Config
    # X offsets for the 4 continents matching the Hadrons/Quarks layout
    # Quarks x: 500, 800, 1100, 1400. Width 250.
    # We need more space for 384 nodes.
    # Let's spread them wider.
    
    X_OFFSETS = {
        "DATA_FOUNDATIONS": 0,
        "LOGIC_FLOW": 1000,
        "ORGANIZATION": 2000,
        "EXECUTION": 3000
    }
    
    COLUMN_WIDTH_INTERNAL = 400
    
    node_id_list = []
    
    for continent, rows in subhadrons_by_continent.items():
        base_x = X_OFFSETS.get(continent, 0)
        current_y = START_Y
        
        # We'll do 2 columns per continent to save vertical space
        # or maybe 1 column if we want to read down.
        # 384 / 4 = ~96 per continent.
        # 96 rows is very tall.
        # Let's do 3 columns per continent block.
        COLS = 2
        
        for i, row in enumerate(rows):
            is_impossible = row['is_impossible'].lower() == 'true'
            
            # Text content
            # Name, ID, Rarity, Reason if impossible
            
            icon = "🏆"
            rarity_label = f"Rarity: {row['emergence_rarity_2025']}"
            
            if is_impossible:
                icon = "⚫" # Black hole representation
                color = COLOR_MAP["IMPOSSIBLE"]
                rarity_label = "**IMPOSSIBLE**"
                reason = row.get('impossible_reason', '')
                content_md = f"### {icon} {row['subhadron_name']}\n**ANTIMATTER DETECTED**\n\nReason: {reason}\n\nType: {row['base_hadron']}"
            else:
                # Valid
                color = COLOR_MAP.get(continent, "0")
                visual = row.get('visual_3d', '')
                content_md = f"### {icon} {row['subhadron_name']}\n{rarity_label}\n\nVisual: {visual}\nType: {row['base_hadron']}"
            
            node_id = f"sub_{row['id']}"
            node_id_list.append(node_id)
            
            # Grid calc
            col_idx = i % COLS
            row_idx = i // COLS
            
            x = base_x + (col_idx * (COLUMN_WIDTH_INTERNAL + 20))
            y = current_y + (row_idx * (ROW_HEIGHT + 20)) # +20 padding
            
            node = {
                "id": node_id,
                "type": "text",
                "text": content_md,
                "x": x,
                "y": y,
                "width": COLUMN_WIDTH_INTERNAL,
                "height": ROW_HEIGHT,
                "color": color
            }
            nodes.append(node)

    # Load and Update Canvas
    try:
        with open(CANVAS_PATH, 'r') as f:
            canvas = json.load(f)
    except Exception as e:
        print(f"Error loading canvas: {e}")
        sys.exit(1)
        
    # Remove placeholder
    canvas["nodes"] = [n for n in canvas.get("nodes", []) if n["id"] != "missing_subhadrons"]
    canvas["edges"] = [e for e in canvas.get("edges", []) if e["id"] != "edge_m2"]
    
    # Add new nodes
    canvas["nodes"].extend(nodes)
    
    # Write back
    with open(CANVAS_PATH, 'w') as f:
        json.dump(canvas, f, indent=4)
        
    print(f"Successfully added {len(nodes)} subhadron nodes to {CANVAS_PATH}")

if __name__ == "__main__":
    main()
