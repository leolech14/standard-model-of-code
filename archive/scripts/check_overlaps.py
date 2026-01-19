import json
import os

CANVAS_PATH = "/Users/lech/PROJECTS_all/PROJECT_elements/THEORY_COMPLETE.canvas"

def check_overlap(n1, n2):
    x1, y1, w1, h1 = n1['x'], n1['y'], n1['width'], n1['height']
    x2, y2, w2, h2 = n2['x'], n2['y'], n2['width'], n2['height']
    
    # Standard AABB overlap check
    if x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2:
        return True
    return False

def main():
    if not os.path.exists(CANVAS_PATH):
        print("Canvas file not found.")
        return

    with open(CANVAS_PATH, 'r') as f:
        data = json.load(f)

    nodes = data.get("nodes", [])
    groups = [n for n in nodes if n.get("type") == "group"]
    items = [n for n in nodes if n.get("type") != "group"]
    
    overlaps = []
    
    # Check Item vs Item
    print(f"Checking {len(items)} items for overlaps...")
    for i, n1 in enumerate(items):
        for j, n2 in enumerate(items):
            if i >= j: continue # Avoid duplicate checks and self-check
            
            if check_overlap(n1, n2):
                # Ignore label vs label if loose? No, strictly check.
                # Ignore loose text nodes? Maybe.
                overlaps.append(f"Overlap: '{n1.get('text','?')[:20]}' ({n1['id']}) <-> '{n2.get('text','?')[:20]}' ({n2['id']})")

    # Check Group vs Group
    print(f"Checking {len(groups)} groups for overlaps...")
    for i, g1 in enumerate(groups):
        for j, g2 in enumerate(groups):
            if i >= j: continue
            if check_overlap(g1, g2):
                 overlaps.append(f"Group Overlap: '{g1.get('label','?')}' <-> '{g2.get('label','?')}'")

    if overlaps:
        print(f"FOUND {len(overlaps)} OVERLAPS:")
        for o in overlaps[:20]:
            print(o)
        if len(overlaps) > 20:
            print(f"... and {len(overlaps)-20} more.")
    else:
        print("✅ NO OVERLAPS FOUND (Item-Item or Group-Group).")

if __name__ == "__main__":
    main()
