import json
import re
from collections import defaultdict

def extract_number(node):
    text = node.get('text', '')
    node_id = node.get('id', '')
    match = re.search(r'#(\d+)', text)
    if match: return int(match.group(1))
    if node_id.startswith('sub_'):
        try: return int(node_id.split('_')[1])
        except: pass
    return None

def check_region(nodes, color_code, region_name):
    # Filter for Region
    region_nodes = [n for n in nodes if n.get('color') == color_code]
    
    if not region_nodes:
        print(f"No nodes found for {region_name} (Color {color_code}).")
        return

    # Group by X coordinate (Cluster into columns)
    x_values = sorted([n['x'] for n in region_nodes])
    if not x_values: return 
    
    clusters = {}
    for n in region_nodes:
        x = n['x']
        found_cluster = None
        for cx in clusters.keys():
            if abs(x - cx) < 100: 
                found_cluster = cx
                break
        if found_cluster is not None:
            clusters[found_cluster].append(n)
        else:
            clusters[x] = [n]

    sorted_column_keys = sorted(clusters.keys())
    
    print(f"\n--- {region_name} Ordering Check ---")
    print(f"Found {len(sorted_column_keys)} columns. Bounds X[{min(x_values)}, {max(x_values)}]")
    
    previous_col_max = -1
    
    for i, col_x in enumerate(sorted_column_keys):
        col_nodes = clusters[col_x]
        col_nodes.sort(key=lambda n: n['y'])
        
        # Numbers
        numbers = [extract_number(n) for n in col_nodes]
        valid_nums = [x for x in numbers if x is not None]

        if not valid_nums:
            print(f"Column {i+1}: [WARN] No identifiable numbers.")
            continue
            
        # print(f"Column {i+1} (X~{col_x}): {len(col_nodes)} nodes.")

        # Check Vertical
        if valid_nums != sorted(valid_nums):
            print(f"  [FAIL] Col {i+1} Vertical order broken.")
        else:
            # print(f"  [OK] Vertical order ascending.")
            pass
            
        # Check Horizontal Continuity
        if previous_col_max != -1:
             if valid_nums[0] < previous_col_max:
                 pass # print(f"  [INFO] Overlap/Reset: Previous ended {previous_col_max}, Current starts {valid_nums[0]}.")
             else:
                 pass # print(f"  [OK] Continues.")
        
        previous_col_max = valid_nums[-1]

def check_all(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    nodes = data.get('nodes', [])
    
    check_region(nodes, '1', 'LOGIC (Red)')
    check_region(nodes, '4', 'ORGANIZATION (Green)')
    check_region(nodes, '5', 'DATA (Cyan)')
    check_region(nodes, '3', 'EXCECUTION (Yellow)')

if __name__ == "__main__":
    check_all("/Users/lech/PROJECTS_all/PROJECT_elements/THEORY_COMPLETE.canvas")
