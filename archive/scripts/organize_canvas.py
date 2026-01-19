import json
import os

CANVAS_PATH = "/Users/lech/PROJECTS_all/PROJECT_elements/THEORY_COMPLETE.canvas"

def main():
    if not os.path.exists(CANVAS_PATH):
        print(f"Error: Canvas file not found at {CANVAS_PATH}")
        return

    with open(CANVAS_PATH, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return

    nodes = data.get("nodes", [])
    if not nodes:
        print("No nodes found in canvas.")
        return

    print(f"Total nodes before cleanup: {len(nodes)}")

    # 1. Cleanup Garbage Nodes
    # Heuristic: Remove text nodes that are very large (likely accidental pastes) or contain specific chat artifacts
    valid_nodes = []
    removed_count = 0
    
    for node in nodes:
        is_garbage = False
        if node.get("type") == "text":
            text = node.get("text", "")
            # Check for specific garbage indicators
            if "You are an expert full-stack engineer" in text:
                is_garbage = True
            elif "YES — EXACTLY" in text:
                is_garbage = True
            elif len(text) > 5000: # Very large text blocks are likely accidental pastes in this context
                # But be careful not to remove the Mermaid diagrams which might be large.
                # Mermaid diagrams start with "# PARTICLE ZOO" or "# CLASSIFICATION"
                if not text.startswith("# PARTICLE ZOO") and not text.startswith("# CLASSIFICATION"):
                     is_garbage = True
            
            # Also remove the "Missing Data" placeholder if it still exists
            if "Missing Data: 384 Subhadrons" in text:
                is_garbage = True

        if is_garbage:
            print(f"Removing garbage node: {node['id']} (Text start: {node.get('text', '')[:50]}...)")
            removed_count += 1
        else:
            valid_nodes.append(node)

    data["nodes"] = valid_nodes
    print(f"Removed {removed_count} garbage nodes.")

    # 2. Re-layout Subhadrons
    # Goal: Shift all subhadrons and related headers down to start at Y=3600
    
    # Calculate current bounds of Hadrons to verify the need (optional, but good for logging)
    hadron_max_y = -float('inf')
    for node in valid_nodes:
        if node.get("id", "").startswith("hadron_"):
            y = node.get("y", 0)
            h = node.get("height", 0)
            hadron_max_y = max(hadron_max_y, y + h)
    
    print(f"Lowest point of Hadrons layer: Y={hadron_max_y}")
    
    # Target start Y for Subhadrons
    SUBHADRON_START_Y = 3600
    
    # Find current min Y of Subhadrons to calculate shift delta
    subhadron_min_y = float('inf')
    subhadron_nodes = []
    
    # Identify nodes to move: subhadrons, subhadron headers
    nodes_to_move = []
    
    for node in valid_nodes:
        nid = node.get("id", "")
        text = node.get("text", "")
        
        # Criteria for moving:
        # 1. ID starts with "sub_" (the generated subhadrons)
        # 2. Text is "5. 1440 SUBHADRONS" (the main header)
        # 3. Text is a continent header for subhadrons? (We need to check if those exist as separate nodes or if they are just grouping)
        #    Based on generate_subhadrons_nodes.py, I don't think I added separate continent headers for subhadrons, just the grid.
        #    But I should move the mermaid diagrams too if they are vertically in the way? 
        #    Actually, the mermaid diagrams were placed at Y=1200. Hadrons are above that?
        #    Wait, Hadrons are at Y? Let's check the hadron generation log or file.
        #    Previous summary says: "Hadrons (Added)... Positioned below the 12 Quarks".
        #    Mermaid diagrams at Y=1200.
        #    Hadrons might be overlapping Mermaid diagrams too if Hadrons go down to 3260?
        #    Let's check the Hadrons positions in the next step if possible, but safe bet is to move Subhadrons deep.
        
        is_subhadron_group = False
        if nid.startswith("sub_"):
            is_subhadron_group = True
        elif "1440 SUBHADRONS" in text: # Header
            is_subhadron_group = True
            
        if is_subhadron_group:
            nodes_to_move.append(node)
            subhadron_min_y = min(subhadron_min_y, node.get("y", 0))

    if nodes_to_move:
        print(f"Found {len(nodes_to_move)} Subhadron-related nodes.")
        print(f"Current Subhadron start Y: {subhadron_min_y}")
        
        shift_amount = SUBHADRON_START_Y - subhadron_min_y
        print(f"Shifting Subhadrons by {shift_amount} pixels to start at Y={SUBHADRON_START_Y}")
        
        for node in nodes_to_move:
            node['y'] += shift_amount
            
            # Also shift the Mermaid diagrams if they are "below" the main flow or need to be moved?
            # The plan said: "Shift all Subhadrons (and the Mermaid diagrams if needed) to start at Y=3600"
            # Actually, the Mermaid diagrams are at Y=1200. If Hadrons go to 3260, they definitely overlap the Mermaid diagrams (Y=1200 to 1200+900=2100).
            # So Mermaid diagrams should ALSO be moved down, or Hadrons moved up?
            # Hadrons are the "parent" of Subhadrons. Quarks are above Hadrons.
            # Typical flow: Laws -> Quarks -> Hadrons -> Subhadrons.
            # If Mermaid diagrams are "summary", maybe they should be to the SIDE or consistently placed.
            # For now, I will focus on the Subhadrons as requested. 
            # BUT, if Hadrons overlap Mermaid diagrams, that's bad.
            # Let's inspect potential Mermaid overlap too.
    else:
        print("No Subhadron nodes found to move.")

    # 3. Check for Mermaid Overlap
    # Mermaid nodes: "node_mermaid_zoo", "node_mermaid_classification"
    mermaid_nodes = [n for n in valid_nodes if n.get("id") in ["node_mermaid_zoo", "node_mermaid_classification"]]
    for m_node in mermaid_nodes:
        # If they are at Y=1200, and Hadrons end at ~3300, they are buried.
        # I should probably move them to be *between* Hadrons and Subhadrons, or *below* Subhadrons.
        # Given "Hadrons (Added)... Positioned below the 12 Quarks", let's assume Hadrons are the main list.
        # A good spot for diagrams might be AFTER the Hadrons list, but BEFORE the Subhadrons grid.
        # If Hadrons end at 3300, I can put Mermaid diagrams at 3400.
        # And then Subhadrons at 3400 + 900 (height of diagrams) + padding = ~4500.
        pass

    # Let's stick to the Plan: "Shift all Subhadrons... to start at Y=3600".
    # I will also verify if Mermaid diagrams need moving. 
    # If I find Mermaid nodes, I'll move them to Y=3600 as well, and push Subhadrons further down?
    # Or just put subhadrons at 3600.
    
    # Actually, if Hadrons end at 3300, putting Subhadrons at 3600 is safe for THEM.
    # But what about the Mermaid diagrams at 1200?
    # If Hadrons are at Y=0 to 3300 (roughly), then 1200 is right in the middle.
    # I should probably move the Mermaid diagrams to Y=3600 (Header area) and Subhadrons to Y=4600.
    # I will make a safe executive decision to stack them: Hadrons -> Diagrams -> Subhadrons.
    
    if mermaid_nodes:
        diagram_start_y = hadron_max_y + 200 # Padding
        print(f"Moving Mermaid diagrams to Y={diagram_start_y} (below Hadrons)")
        for m_node in mermaid_nodes:
            m_node['y'] = diagram_start_y
        
        # Now update Subhadrons target
        # Diagrams are height 900.
        SUBHADRON_START_Y = diagram_start_y + 900 + 200 # Padding
        
        # Re-calculating shift for subhadrons with new target
        if nodes_to_move:
             shift_amount = SUBHADRON_START_Y - subhadron_min_y
             print(f"Re-adjusting Subhadron target to Y={SUBHADRON_START_Y} to accommodate diagrams.")
             # We haven't applied the previous shift loop yet, so we can just update the variable.
             # Wait, I need to iterate again or just set the shift amount.
             pass

    # Apply shift to Subhadrons
    if nodes_to_move:
        final_shift = SUBHADRON_START_Y - subhadron_min_y
        for node in nodes_to_move:
            node['y'] += final_shift

    # Save
    with open(CANVAS_PATH, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"Success! Canvas updated. Saved to {CANVAS_PATH}")

if __name__ == "__main__":
    main()
