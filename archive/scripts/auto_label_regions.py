import json
import os
import math

CANVAS_PATH = "/Users/lech/PROJECTS_all/PROJECT_elements/THEORY_COMPLETE.canvas"
MAX_CLUSTER_DIST = 1500  # Distance to break clusters

def get_distance(n1, n2):
    c1x = n1["x"] + n1["width"]/2
    c1y = n1["y"] + n1["height"]/2
    c2x = n2["x"] + n2["width"]/2
    c2y = n2["y"] + n2["height"]/2
    return math.sqrt((c1x-c2x)**2 + (c1y-c2y)**2)

def main():
    with open(CANVAS_PATH, 'r') as f:
        data = json.load(f)

    nodes = [n for n in data.get("nodes", []) if n["type"] not in ["group", "link", "edge"]]
    existing_labels = [n for n in nodes if n["type"] == "text" and n.get("text", "").startswith("# ")]
    
    # Simple Clustering
    clusters = []
    
    # We will just sort by X then Y and simple gap check? 
    # Or strict connected components? Connected components is safer for 2D.
    
    # Initialize each node as a cluster
    node_clusters = {n["id"]: i for i, n in enumerate(nodes)}
    cluster_lists = {i: [n] for i, n in enumerate(nodes)}
    
    # Iterate and merge
    # This is O(N^2), N=400 -> 160k ops, fine.
    changed = True
    while changed:
        changed = False
        keys = list(cluster_lists.keys())
        for i in range(len(keys)):
            k1 = keys[i]
            if k1 not in cluster_lists: continue
            
            for j in range(i+1, len(keys)):
                k2 = keys[j]
                if k2 not in cluster_lists: continue
                
                # Check distance between clusters (min dist between any pair)
                # Optimization: Check bounding box dist first?
                # Let's just check if ANY node in C1 is close to ANY node in C2
                # Too slow?
                # Optimization: Check center of masses? No, shapes are irregular.
                # Optimization: Sort by X.
                
                c1_nodes = cluster_lists[k1]
                c2_nodes = cluster_lists[k2]
                
                # Quick bbox check
                b1 = (min(n["x"] for n in c1_nodes), min(n["y"] for n in c1_nodes), max(n["x"]+n["width"] for n in c1_nodes), max(n["y"]+n["height"] for n in c1_nodes))
                b2 = (min(n["x"] for n in c2_nodes), min(n["y"] for n in c2_nodes), max(n["x"]+n["width"] for n in c2_nodes), max(n["y"]+n["height"] for n in c2_nodes))
                
                # If X gap > MAX and Y gap > MAX, skip
                if (b1[2] < b2[0] - MAX_CLUSTER_DIST) or (b2[2] < b1[0] - MAX_CLUSTER_DIST): continue
                if (b1[3] < b2[1] - MAX_CLUSTER_DIST) or (b2[3] < b1[1] - MAX_CLUSTER_DIST): continue
                
                # Scan pairs (expensive part, but filtered by bbox)
                merged = False
                for n1 in c1_nodes:
                    for n2 in c2_nodes:
                        if get_distance(n1, n2) < MAX_CLUSTER_DIST:
                            # Merge k2 into k1
                            cluster_lists[k1].extend(cluster_lists[k2])
                            del cluster_lists[k2]
                            changed = True
                            merged = True
                            break
                    if merged: break
                if changed: break
            if changed: break

    # Analyze Clusters
    new_nodes = []
    print(f"Found {len(cluster_lists)} final clusters.")
    
    for cid, cnodes in cluster_lists.items():
        if len(cnodes) < 5: continue # Skip noise
        
        # Bounding box
        min_x = min(n["x"] for n in cnodes)
        min_y = min(n["y"] for n in cnodes)
        max_x = max(n["x"] + n["width"] for n in cnodes)
        
        # Color profile
        colors = [n.get("color", "unknown") for n in cnodes if "color" in n]
        if not colors: continue
        from collections import Counter
        common_color = Counter(colors).most_common(1)[0][0]
        
        # Identify Region Name
        region_name = "REGION"
        if common_color == "1": region_name = "LOGIC / FLOW"
        elif common_color == "3": region_name = "EXECUTION / INFRA"
        elif common_color == "4": region_name = "ORGANIZATION / STRUCTURE"
        elif common_color == "5": region_name = "DATA / FOUNDATIONS"
        elif common_color == "6": region_name = "THEORY & PHYSICS"
        
        # Check if label exists nearby (intersection with top area)
        # We look for large text nodes
        has_label = False
        for n in cnodes:
            if n["type"] == "text" and n["width"] > 300 and n["y"] < min_y + 500:
                # Likely a header
                # print(f"Cluster {region_name} has header: {n['text'][:20]}")
                has_label = True
                pass
        
        # Wait, if user wants us to LABEL them, we should ensure a CONSISTENT label format.
        # Let's add a "Region Map Label" if explicitly missing.
        
        # Actually, let's just Place a NEW Label at the top-left of the BBox
        
        label_id = f"label_auto_{cid}"
        label_text = f"# {region_name}\n**{len(cnodes)} Components**"
        
        # Create Node
        label_node = {
            "id": label_id,
            "type": "text",
            "text": label_text,
            "x": min_x,
            "y": min_y - 250, # Above
            "width": 600,
            "height": 200,
            "color": common_color
        }
        
        # Only add if we don't overlap existing nodes heavily? 
        # Or just verify coordinates.
        new_nodes.append(label_node)
        print(f"Adding label for {region_name} at {min_x}, {min_y - 250}")

    # Write Back
    data["nodes"].extend(new_nodes)
    with open(CANVAS_PATH, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    main()
