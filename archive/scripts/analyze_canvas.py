import json
from collections import defaultdict

def analyze_canvas(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    nodes = data.get('nodes', [])
    
    # Region definitions
    regions = {
        "1": "LOGIC / FLOW",
        "3": "EXECUTION / INFRA",
        "4": "ORGANIZATION / STRUCTURE",
        "5": "DATA / FOUNDATIONS", 
        "6": "META / THEORY",
        "0": "LABELS/OTHER"
    }

    region_nodes = defaultdict(list)
    total_nodes = 0
    
    print(f"--- Canvas Analysis: {file_path} ---")

    for node in nodes:
        color = node.get('color', '0') # Default to 0/Label if no color
        region_nodes[color].append(node)
        total_nodes += 1

    # 1. Component Counts
    print("\n[1. Component Counts per Region]")
    sorted_colors = sorted(region_nodes.keys(), key=lambda k: len(region_nodes[k]), reverse=True)
    
    for color in sorted_colors:
        count = len(region_nodes[color])
        name = regions.get(color, f"Unknown Color {color}")
        print(f"  - {name}: {count} components")

    # 2. Grid Alignment (Check modulo 10)
    print("\n[2. Grid Alignment Check (Mod 10)]")
    misaligned_count = 0
    for node in nodes:
        x = node.get('x', 0)
        y = node.get('y', 0)
        if x % 10 != 0 or y % 10 != 0:
            misaligned_count += 1
            # print(f"    - Misaligned Node: {node.get('id')} at ({x}, {y})")
    
    if misaligned_count == 0:
        print("  - All nodes are aligned to a 10px grid.")
    else:
        print(f"  - {misaligned_count} nodes are NOT aligned to a 10px grid.")

    # 3. Y-Alignment Analysis (Row consistency)
    # Group by rough Y to see if they form clean rows
    print("\n[3. Row Alignment Analysis]")
    for color in sorted_colors:
        if color == '0' or color == '6': continue # Skip labels/meta for row analysis
        
        region_name = regions.get(color)
        r_nodes = region_nodes[color]
        if not r_nodes: continue
            
        y_coords = sorted([n.get('y') for n in r_nodes])
        # Find unique Ys
        unique_ys = sorted(list(set(y_coords)))
        
        print(f"  Region: {region_name}")
        print(f"    - Found {len(unique_ys)} unique Y rows.")
        
        # Heuristic: if many unique Ys are close to each other, it's messy
        close_rows = 0
        for i in range(len(unique_ys) - 1):
            if unique_ys[i+1] - unique_ys[i] < 20: # arbitrary small delta
                close_rows += 1
        
        if close_rows > 0:
            print(f"    - WARNING: {close_rows} pairs of rows are very close (<20px) but not exact.")
        else:
            print("    - Row alignment looks clean (no micro-misalignments detected).")

if __name__ == "__main__":
    analyze_canvas("/Users/lech/PROJECTS_all/PROJECT_elements/THEORY_COMPLETE.canvas")
