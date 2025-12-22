
import json
import re
from pathlib import Path

GRAPH_PATH = "output/atman_scan_v1_full/graph.json"
TEMPLATE_PATH = "demos/spectrometer_pro.html"
OUTPUT_PATH = "output/atman_scan_v1_full/spectrometer_viz.html"

def main():
    print(f"Loading {GRAPH_PATH}...")
    with open(GRAPH_PATH, 'r') as f:
        graph_data = json.load(f)
    
    components = graph_data.get("components", {})
    edges = graph_data.get("edges", [])
    
    print(f"Found {len(components)} components and {len(edges)} edges.")
    
    # 1. Convert Nodes (Filter for performance if needed, but let's try full set or minimal filter)
    # We will filter out 'isolated' nodes with 0 degree to save space?
    # Or just top 2000?
    
    # Let's map all VALID components
    particles = []
    valid_ids = set()
    
    for cid, comp in components.items():
        # Heuristic to determine layer/role from ID or type
        layer = "App"
        role = "Worker"
        
        # Simple heuristics based on ID prefix
        id_str = str(comp.get("id", ""))
        if id_str.startswith("LOG"): 
            layer = "Core"
            role = "Worker"
        elif id_str.startswith("DAT"):
            layer = "Data"
            role = "Data"
        elif id_str.startswith("EXE"):
            layer = "App"
            role = "Orchestrator"
        elif id_str.startswith("UI"):
             layer = "Interface"
        
        # Override with explicit layer/role if available
        if comp.get("layer"): layer = comp["layer"]
        if comp.get("role"): role = comp["role"]
        
        # Normalize Layer to match Template Colors: Interface, App, Core, Infra, Data, Tests
        # (You can expand the template colors later if needed)
        
        particles.append({
            "id": cid,
            "label": comp.get("name", cid[:10]),
            "layer": layer or "App",
            "role": role or "Worker",
            "boundary": "Internal", # default
            "state": "Stateless",
            "activation": "Direct",
            "lifetime": "Transient"
        })
        valid_ids.add(cid)
        
    # 2. Convert Edges
    # We must ensure source/target are in valid_ids.
    # The edges in graph.json might use IDs or Names. We need to resolve.
    connection_list = []
    
    # Create name->id map for fallback
    name_to_id = {c["label"]: c["id"] for c in particles}
    
    for e in edges:
        src = e.get("source")
        dst = e.get("target")
        
        # Resolve IDs
        final_src = src if src in valid_ids else name_to_id.get(src)
        final_dst = dst if dst in valid_ids else name_to_id.get(dst)
        
        if final_src and final_dst:
            connection_list.append({
                "from": final_src,
                "to": final_dst,
                "type": e.get("edge_type", "CALLS").upper()
            })
            
    print(f"Mapped {len(particles)} particles and {len(connection_list)} connections.")
    
    # 3. Inject into Template
    with open(TEMPLATE_PATH, 'r') as f:
        html = f.read()
    
    # Replace particles const
    # We use regex to be safe against formatting
    # target: const particles = [ ... ];
    
    particles_json = json.dumps(particles)
    connections_json = json.dumps(connection_list)
    
    html = re.sub(r"const particles = \[.*?\];", lambda m: f"const particles = {particles_json};", html, flags=re.DOTALL)
    html = re.sub(r"const connections = \[.*?\];", lambda m: f"const connections = {connections_json};", html, flags=re.DOTALL)
    
    with open(OUTPUT_PATH, 'w') as f:
        f.write(html)
        
    print(f"Saved visualization to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
