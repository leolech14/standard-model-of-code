import json
import os
import math

CANVAS_PATH = "/Users/lech/PROJECTS_all/PROJECT_elements/THEORY_COMPLETE.canvas"

# Known IDs for theory notes
THEORY_NODE_IDS = [
    "155c157c92d657e9", "aa46a4289777cb42", "391978d73f904486", 
    "dce12c4882197b32", "6b333db1e2925639", "quantum_note", 
    "2f1060e287ee2ec8", "0d44b6a504c198e6", "4fa65f09f2c78b82" 
]

LANE_CONFIG = {
    "data":  {"x": -1400, "color": "5", "name": "DATA", "group_color": "5"},
    "logic": {"x": -500,  "color": "1", "name": "LOGIC", "group_color": "1"},
    "org":   {"x": 400,   "color": "4", "name": "ORG",   "group_color": "4"},
    "exec":  {"x": 1300,  "color": "3", "name": "EXEC",  "group_color": "3"}
}

def get_node_lane(node):
    nid = node.get("id", "")
    text = node.get("text", "")
    color = node.get("color", "")
    
    if nid in THEORY_NODE_IDS: return "theory"
    if len(text) > 1000 and not text.startswith("# ") and "mermaid" not in text: return "theory"
    if "mermaid" in text: return "mermaid"
    if nid.startswith("law") or "11 LAWS" in text: return "laws"
    
    if color == "5": return "data"
    if color == "1": return "logic"
    if color == "4": return "org"
    if color == "3": return "exec"
    
    if "Data" in text: return "data"
    if "Logic" in text: return "logic"
    if "Organization" in text: return "org"
    if "Execution" in text: return "exec"
    
    # We remove header logic for 'misc' buckets, purely detection now
    # if "12 CONTINENTS" in text: return "quarks_header"
    # if "96 HADRONS" in text: return "hadrons_header"
    # if "SUBHADRONS" in text: return "subs_header"

    return "misc"

def main():
    if not os.path.exists(CANVAS_PATH):
        print(f"Error: {CANVAS_PATH} not found.")
        return

    with open(CANVAS_PATH, 'r') as f:
        data = json.load(f)

    raw_nodes = data.get("nodes", [])
    unique_nodes = {}
    for n in raw_nodes:
        # Filter legacy headers by ID
        if n['id'] in ["node1", "node2", "node3", "node4", "node5"]:
             continue
        if n['id'] not in unique_nodes:
            unique_nodes[n['id']] = n
            
    clean_nodes = [
        n for n in unique_nodes.values()
        if not n.get("id", "").startswith("divider_") 
        and not n.get("id", "").startswith("h_divider_")
        and not n.get("id", "").startswith("label_")
        and not n.get("id", "").startswith("placeholder_")
        and n.get("type") != "group"
    ]
    edges = data.get("edges", [])
    
    parent_map = {}
    for e in edges:
        from_node = e.get("fromNode")
        to_node = e.get("toNode")
        if to_node and to_node.startswith("sub_"):
            if from_node not in parent_map: parent_map[from_node] = []
            parent_map[from_node].append(to_node)
            
    lanes = {
        "data": [], "logic": [], "org": [], "exec": [],
        "theory": [], "mermaid": [], "laws": [], "misc": [],
        "headers": [] # Should remain empty since we filtered
    }
    node_lookup = {n['id']: n for n in clean_nodes}
    
    for node in clean_nodes:
        lane = get_node_lane(node)
        if lane in lanes: lanes[lane].append(node)
        elif "header" in lane: lanes["headers"].append(node)
        else: lanes["misc"].append(node)

    current_y = 0
    
    # 1. LAWS
    laws = lanes["laws"]
    laws_header = [n for n in laws if "11 LAWS" in n.get("text", "")]
    laws_items = [n for n in laws if "11 LAWS" not in n.get("text", "")]
    
    if laws_header:
        # Re-use existing header if found (unlikely if node1 filtered)
        laws_header[0]['x'] = -200
        laws_header[0]['y'] = current_y
    else:
        # Create new one? We use label_t0 below?
        pass # We will add label
    
    start_x = -600
    row_h = 0
    for i, node in enumerate(laws_items):
        col = i % 4
        row = i // 4
        node['x'] = start_x + col * 270
        node['y'] = current_y + 150 + row * 100
        node['width'] = 250
        node['height'] = 80
        row_h = max(row_h, 150 + row * 100 + 80)
        
    current_y += row_h + 200
    y_continents_start = current_y
    
    # 2. CONTINENTS
    max_tier_h = 0
    t1_nodes = {}
    
    for k in ["data", "logic", "org", "exec"]:
        items = lanes[k]
        t1 = [n for n in items if n.get("id", "").startswith("atom") or n.get("id", "").startswith("cont") or n not in [x for x in items if x.get("id", "").startswith("hadron_") or x.get("id", "").startswith("sub_")]]
        t1.sort(key=lambda n: n.get("id", ""))
        
        lx = LANE_CONFIG[k]["x"]
        ly = y_continents_start
        for n in t1:
            n['x'] = lx
            n['y'] = ly
            n['width'] = 250
            n['height'] = 100 if "CONTINENT" in n.get("text","") else 60
            ly += n['height'] + 20
        
        tier_h = ly - y_continents_start
        if tier_h > max_tier_h: max_tier_h = tier_h
        t1_nodes[k] = t1
        
    current_y += max_tier_h + 200
    y_hadrons_start = current_y
    
    # 3. HADRONS
    max_tier_h = 0
    placed_hadrons = {}
    
    for k in ["data", "logic", "org", "exec"]:
        items = lanes[k]
        t2 = [n for n in items if n.get("id", "").startswith("hadron_")]
        t2.sort(key=lambda n: n.get("id", ""))
        
        lx = LANE_CONFIG[k]["x"]
        ly = y_hadrons_start
        
        placed_hadrons[k] = []
        for n in t2:
            n['x'] = lx
            n['y'] = ly
            n['width'] = 250
            n['height'] = 120
            ly += 140
            placed_hadrons[k].append(n['id'])
            
        tier_h = ly - y_hadrons_start
        if tier_h > max_tier_h: max_tier_h = tier_h

    current_y += max_tier_h + 200
    y_mermaid_start = current_y
    
    # 4. MERMAID
    mermaids = lanes["mermaid"]
    zoo = [n for n in mermaids if "zoo" in n.get("id", "")]
    cls = [n for n in mermaids if "classification" in n.get("id", "")]
    others = [n for n in mermaids if n not in zoo and n not in cls]
    
    ordered_mermaids = []
    if zoo: ordered_mermaids.extend(zoo)
    if cls: ordered_mermaids.extend(cls)
    ordered_mermaids.extend(others)
    
    slots_x = [-1000, 200, 1400]
    m_height = 0
    
    for i, n in enumerate(ordered_mermaids):
        if i < len(slots_x):
             n['x'] = slots_x[i]
        else:
             n['x'] = slots_x[-1] + (i-2)*1200 
             
        n['y'] = y_mermaid_start
        h = n.get("height", 1000)
        n['width'] = 1000
        if h > m_height: m_height = h
        
    current_y += m_height + 200
    y_subs_start = current_y
    
    # 5. SUBHADRONS
    max_tier_h = 0
    
    for k in ["data", "logic", "org", "exec"]:
        items = lanes[k]
        t3 = [n for n in items if n.get("id", "").startswith("sub_")]
        
        ordered = []
        seen = set()
        for hid in placed_hadrons.get(k, []):
            children = parent_map.get(hid, [])
            child_nodes = []
            for cid in children:
                if cid in node_lookup and cid not in seen and node_lookup[cid] in t3:
                    child_nodes.append(node_lookup[cid])
                    seen.add(cid)
            child_nodes.sort(key=lambda n: n.get("text", ""))
            ordered.extend(child_nodes)
        orphans = [n for n in t3 if n.get("id") not in seen]
        ordered.extend(orphans)
        
        lx = LANE_CONFIG[k]["x"]
        ly = y_subs_start
        
        for i, n in enumerate(ordered):
            col = i % 2
            row = i // 2
            n['x'] = lx + col * 270
            n['y'] = ly + row * 220
            n['width'] = 250
            n['height'] = 200
            
            h = (row + 1) * 220
            if h > max_tier_h: max_tier_h = h
            
    current_y += max_tier_h + 300
    y_1440_start = current_y
    
    # 6. MISC
    misc = lanes["misc"]
    misc_y = 1000
    misc_x = 3500
    for n in misc:
        n['x'] = misc_x
        n['y'] = misc_y
        misc_y += max(n.get("height", 100), 100) + 50
    
    # --- VISUALS ---
    viz_nodes = []
    
    if misc:
        viz_nodes.append({"id": "label_limbo", "type": "text", "text": "## LIMBO (Unclassified)", "x": misc_x, "y": 800, "width": 400, "height": 100, "color": "6"})
        
    viz_nodes.append({"id": "label_t0", "type": "text", "text": "# 1. 11 LAWS", "x": -200, "y": 0, "width": 400, "height": 100, "color": "0"})
    viz_nodes.append({"id": "label_t1", "type": "text", "text": "# 2. 12 CONTINENTS", "x": -200, "y": y_continents_start - 120, "width": 400, "height": 100, "color": "0"})
    viz_nodes.append({"id": "label_t2", "type": "text", "text": "# 3. 96 HADRONS", "x": -200, "y": y_hadrons_start - 120, "width": 400, "height": 100, "color": "0"})
    viz_nodes.append({"id": "label_t3", "type": "text", "text": "# 4. 384 SUBHADRONS (CLUSTERING APPLIED)", "x": -200, "y": y_subs_start - 120, "width": 400, "height": 100, "color": "0"})
    viz_nodes.append({"id": "label_t4", "type": "text", "text": "# 5. 1440 SUBHADRONS\n(Expansion)", "x": -200, "y": y_1440_start - 120, "width": 400, "height": 200, "color": "0"})

    total_h = y_1440_start + 2500 - y_continents_start + 400
    
    groups_config = [
        {"id": "group_data", "label": "DATA REGION", "x": -1800, "w": 850, "color": "5"},
        {"id": "group_logic", "label": "LOGIC REGION", "x": -940, "w": 890, "color": "1"}, 
        {"id": "group_org", "label": "ORG REGION", "x": -40, "w": 890, "color": "4"},
        {"id": "group_exec", "label": "EXEC REGION", "x": 860, "w": 840, "color": "3"}
    ]
    
    for g in groups_config:
        viz_nodes.append({
            "id": g["id"],
            "type": "group",
            "label": g["label"],
            "x": g["x"],
            "y": y_continents_start - 200,
            "width": g["w"],
            "height": total_h,
            "color": g["color"]
        })
        
    for lane_key in ["data", "logic", "org", "exec"]:
        lx = LANE_CONFIG[lane_key]["x"]
        viz_nodes.append({
            "id": f"placeholder_1440_{lane_key}",
            "type": "group",
            "label": f"1440 ZONE",
            "x": lx,
            "y": y_1440_start,
            "width": 550,
            "height": 2000,
            "color": LANE_CONFIG[lane_key]['color']
        })
        
    tx = 2400
    ty = 1000
    for n in lanes["theory"]:
        n['x'] = tx
        n['y'] = ty
        ty += n.get("height", 800) + 100

    final_nodes = viz_nodes + clean_nodes
    data["nodes"] = final_nodes
    
    with open(CANVAS_PATH, 'w') as f:
        json.dump(data, f, indent=4)
        
    print("V11 Layout (No Legacy Headers) Applied.")

if __name__ == "__main__":
    main()
