import json
import os
import math

CANVAS_PATH = "/Users/lech/PROJECTS_all/PROJECT_elements/THEORY_COMPLETE.canvas"
X_TOLERANCE = 40  # Nodes within 40px distinct X are considered same column
MIN_Y_GAP = 30    # Minimum vertical gap between nodes
GROUP_PADDING = 50

def main():
    if not os.path.exists(CANVAS_PATH):
        print("Canvas file not found.")
        return

    with open(CANVAS_PATH, 'r') as f:
        data = json.load(f)

    nodes = data.get("nodes", [])
    
    # Separate content nodes from huge groups
    content_nodes = [n for n in nodes if n.get("type") != "group" and n.get("id") != "node_mermaid_12" and "mermaid" not in n.get("text", "").lower()]
    # Groups and Mermaids we leave alone generally, or snap strictly
    # Actually, let's treat everyone, but be careful with huge items.
    # User said "micro adjustments".
    
    # 1. X-SNAPPING
    # Collect all X centers or lefts. Canvas Key is 'x' (left).
    # We ignore "Groups" for snapping usually, they are containers.
    # Let's focused on "Cards" (Text/File/Link).
    
    target_nodes = [n for n in nodes if n.get("type") != "group"]
    
    # Sort by X
    target_nodes.sort(key=lambda n: n.get("x", 0))
    
    # Cluster X
    if not target_nodes: return
    
    clusters = []
    current_cluster = [target_nodes[0]]
    
    for i in range(1, len(target_nodes)):
        n = target_nodes[i]
        prev = current_cluster[-1]
        
        if abs(n.get("x", 0) - current_cluster[0].get("x", 0)) <= X_TOLERANCE:
            current_cluster.append(n)
        else:
            clusters.append(current_cluster)
            current_cluster = [n]
    clusters.append(current_cluster)
    
    # Apply Snap
    for cluster in clusters:
        # Calculate mode or average X?
        # Mode is better to stick to grid. 
        # Or simple average.
        # Let's use the X of the first element (often the header or top item) as anchor
        # logic: User likely placed top item then others.
        # Check if there is a 'label' or Header?
        # Let's just take the most common X (Mode) to be safe.
        xs = [n.get("x", 0) for n in cluster]
        from collections import Counter
        common_x = Counter(xs).most_common(1)[0][0]
        
        for n in cluster:
            n['x'] = common_x
            
    print(f"X-Snapping complete. Processed {len(clusters)} columns.")

    # 2. Y-DISTRIBUTION (Anti-Overlap)
    # Re-group by NEW X
    cols = {}
    for n in target_nodes:
        x = n.get("x", 0)
        if x not in cols: cols[x] = []
        cols[x].append(n)
        
    for x_val, col_nodes in cols.items():
        # Sort by Y
        col_nodes.sort(key=lambda n: n.get("y", 0))
        
        # Iterate and push
        for i in range(len(col_nodes) - 1):
            top = col_nodes[i]
            bot = col_nodes[i+1]
            
            bottom_of_top = top.get("y", 0) + top.get("height", 0)
            top_of_bot = bot.get("y", 0)
            
            gap = top_of_bot - bottom_of_top
            
            if gap < MIN_Y_GAP:
                # Collision or too tight!
                push = MIN_Y_GAP - gap
                # Push bot and ALL subsequent nodes in this column
                # This ensures we don't just squash the next one
                for k in range(i + 1, len(col_nodes)):
                    col_nodes[k]['y'] += push
                    
    print("Y-Distribution complete (Anti-overlap).")
    
    with open(CANVAS_PATH, 'w') as f:
        json.dump(data, f, indent=4) # Compact JSON or Indent? User had compact-ish. Indent 4 is standard readable.

if __name__ == "__main__":
    main()
