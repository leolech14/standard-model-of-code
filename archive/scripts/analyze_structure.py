import json

def analyze_structure(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    nodes = data.get('nodes', [])
    
    colors = {
        '1': 'Red (Logic)',
        '4': 'Green (Org)',
        '3': 'Yellow (Exec)',
        '5': 'Cyan (Data)'
    }
    
    print("--- Canvas Structure Analysis ---")
    
    regions = {}
    
    for c, name in colors.items():
        r_nodes = [n for n in nodes if n.get('color') == c]
        if not r_nodes:
            continue
            
        # Bounds
        min_x = min(n['x'] for n in r_nodes)
        max_x = max(n['x'] + n.get('width', 300) for n in r_nodes)
        min_y = min(n['y'] for n in r_nodes)
        max_y = max(n['y'] + n.get('height', 220) for n in r_nodes)
        
        # Counts
        hadrons = len([n for n in r_nodes if n.get('id', '').startswith('hadron_') or 'HADRON' in str(n)])
        # Heuristic for hadrons if ID not set? Assuming the rest are subs
        subs = len(r_nodes) - hadrons # Rough approx
        
        # Better split check using logic from previous scripts
        h_list = []
        s_list = []
        for n in r_nodes:
            is_hyd = False
            if n.get('id', '').startswith('hadron_'): is_hyd = True
            # Manual check
            # For Yellow/Cyan we haven't seen the IDs yet.
            if is_hyd: h_list.append(n)
            else: s_list.append(n)
            
        regions[c] = {
            'name': name,
            'count': len(r_nodes),
            'hadrons': len(h_list), # This might be inaccurate if IDs aren't clean
            'subs': len(s_list),
            'min_x': min_x,
            'max_x': max_x,
            'max_y': max_y,
            'width': max_x - min_x
        }
        
        print(f"{name}: {len(r_nodes)} Nodes")
        print(f"  Bounds: X[{min_x}, {max_x}] Y[{min_y}, {max_y}]")
        print(f"  Width: {max_x - min_x}")
        # print(f"  Approx Split: {len(h_list)} Hadrons, {len(s_list)} Subs")

    return regions

if __name__ == "__main__":
    analyze_structure("/Users/lech/PROJECTS_all/PROJECT_elements/THEORY_COMPLETE.canvas")
