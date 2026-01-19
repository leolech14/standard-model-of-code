import json
import os

CANVAS_PATH = "/Users/lech/PROJECTS_all/PROJECT_elements/THEORY_COMPLETE.canvas"

def check_misplaced():
    with open(CANVAS_PATH, 'r') as f:
        data = json.load(f)

    nodes = data.get("nodes", [])
    groups = {n["id"]: n for n in nodes if n["type"] == "group"}
    
    # 1. Define Main Horizontal Swimlanes based on Group Headers? 
    # Or just use the Group definitions found in JSON.
    
    # We have clear Groups: group_data, group_logic, group_org, group_exec
    # And 1440 zones.
    
    misplaced = []
    
    # Map color to logical group
    # 1=Red=Logic, 2=Orange=?, 3=Yellow=Exec, 4=Green=Org, 5=Cyan=Data, 6=Purple=Zoo
    color_map = {
        "1": "group_logic",
        "2": "group_logic", # Sometimes orange is logic variance
        "3": "group_exec",
        "4": "group_org",
        "5": "group_data",
        "6": "group_zoo" # or theory
    }
    
    for n in nodes:
        if n["type"] == "group": continue
        if "label" in n.get("id", ""): continue # headings
        
        # Check if node is inside its intended Semantic Group
        # We rely on 'color' metadata if present
        
        node_color = n.get("color", "")
        if not node_color: continue 
        
        target_group_id = color_map.get(node_color)
        if not target_group_id: continue
        
        target_group = groups.get(target_group_id)
        if not target_group: continue
        
        # Check bounds
        nx, ny = n["x"], n["y"]
        gx, gy = target_group["x"], target_group["y"]
        gw, gh = target_group["width"], target_group["height"]
        
        # A bit of tolerance
        if not (gx - 100 <= nx <= gx + gw + 100 and gy - 100 <= ny <= gy + gh + 100):
            misplaced.append({
                "id": n["id"],
                "text": n.get("text", "")[:30].replace("\n", " "),
                "color": node_color,
                "expected_group": target_group.get("label", target_group_id),
                "actual_pos": (nx, ny),
                "group_bounds": (gx, gy, gx+gw, gy+gh)
            })
            
    # Report
    print(f"Found {len(misplaced)} potentially misplaced items based on Color Logic:")
    for m in misplaced:
        print(f"- [{m['color']}] {m['text']} id:{m['id']} at {m['actual_pos']}")
        print(f"  Expected inside: {m['expected_group']} {m['group_bounds']}")
        print("---")

if __name__ == "__main__":
    check_misplaced()
