import json
import re

def extract_number(node):
    text = node.get('text', '')
    node_id = node.get('id', '')
    match = re.search(r'#(\d+)', text)
    if match: return int(match.group(1))
    if node_id.startswith('sub_'):
        try: return int(node_id.split('_')[1])
        except: pass
    return 999999

def is_hadron(node):
    nid = node.get('id', '')
    if nid.startswith('hadron_'): return True
    if nid.startswith('sub_'): return False
    
    # Fallback heuristics based on observed ranges (if IDs are missing)
    num = extract_number(node)
    
    # Logic (Red): 18-42 roughly
    if node.get('color') == '1' and 18 <= num <= 42: return True
    
    # Org (Green): 43-58
    if node.get('color') == '4' and 43 <= num <= 58: return True
    
    # Cyan (Data)? Range unknown but likely distinct block.
    # Yellow (Exec)? Range unknown.
    
    return False

def layout_block(nodes, start_x, start_y, items_per_col=12):
    COL_WIDTH = 300
    ROW_HEIGHT = 220
    
    current_col = 0
    current_row = 0
    max_y = start_y  
    
    for node in nodes:
        node['x'] = start_x + (current_col * COL_WIDTH)
        node['y'] = start_y + (current_row * ROW_HEIGHT)
        
        node_h = node.get('height', ROW_HEIGHT)
        if node['y'] + node_h > max_y:
            max_y = node['y'] + node_h
        
        current_row += 1
        if current_row >= items_per_col:
            current_row = 0
            current_col += 1
    
    width = (current_col + 1) * COL_WIDTH
    return width, max_y

def process_region(nodes, color_code, start_x, start_y, body_items_per_col=12):
    region_nodes = [n for n in nodes if n.get('color') == color_code]
    if not region_nodes: return 0, 0, 0

    hadrons = [n for n in region_nodes if is_hadron(n)]
    subs = [n for n in region_nodes if not is_hadron(n)]
    
    # If detection failed (0 hadrons), assume smallest numbers are hadrons?
    # Or just treat everything as subs?
    # Let's try to detect if we missed hadrons by checking counts.
    # If 0 hadrons and > 0 subs, maybe try to take top X subs as hadrons?
    # No, risky. Let's assume user labeled them or ranges are right.
    
    hadrons.sort(key=lambda n: (extract_number(n), n.get('id')))
    subs.sort(key=lambda n: (extract_number(n), n.get('id')))
    
    # Header
    width_h, max_y_h = layout_block(hadrons, start_x, start_y, items_per_col=1)
    
    # Body
    VERTICAL_GAP = 600
    START_Y_BODY = max_y_h + VERTICAL_GAP
    if not hadrons: START_Y_BODY = start_y # No header, start body at top
    
    width_b, max_y_b = layout_block(subs, start_x, START_Y_BODY, items_per_col=body_items_per_col)
    
    final_width = max(width_h, width_b)
    final_height = max_y_b - start_y
    
    print(f"Region {color_code} Layout: {len(hadrons)} Hadrons, {len(subs)} Subs.")
    print(f"  Width: {final_width}, Height: {final_height}")
    
    return final_width, final_height, max_y_b

def rearrange_canvas(file_path):
    print(f"Loading {file_path}...")
    with open(file_path, 'r') as f:
        data = json.load(f)

    nodes = data.get('nodes', [])
    
    # 1. Analyze Red (Color 1)
    red_nodes = [n for n in nodes if n.get('color') == '1']
    min_x_red = min(n['x'] for n in red_nodes)
    max_x_red = max(n['x'] + n.get('width', 300) for n in red_nodes)
    max_y_red = max(n['y'] + n.get('height', 220) for n in red_nodes)
    min_y_red = min(n['y'] for n in red_nodes) # Top of Red
    
    # 2. Green (Color 4) - Below Red
    # Re-calc position to be sure
    GAP_Y = 1000
    START_X_GREEN = min_x_red
    START_Y_GREEN = max_y_red + GAP_Y
    
    _, _, max_y_green = process_region(nodes, '4', START_X_GREEN, START_Y_GREEN, body_items_per_col=2)
    
    # 3. Cyan (Color 5) - Below Green
    START_X_CYAN = min_x_red
    START_Y_CYAN = max_y_green + GAP_Y
    
    # Cyan is small (20 nodes). Use N=2 for wide spread like Green.
    process_region(nodes, '5', START_X_CYAN, START_Y_CYAN, body_items_per_col=2)
    
    # 4. Yellow (Color 3) - Right of Red
    GAP_X = 2000
    START_X_YELLOW = max_x_red + GAP_X
    START_Y_YELLOW = min_y_red # Align top with Red
    
    # Yellow is big (150 nodes). Use N=10 for square-ish grid? Or N=5 for wide spread?
    # User said "wider spread... N=1 or 2". 
    # If we do N=2 for 150 nodes, that's 75 columns = 22,000 px! Too wide.
    # Logic: Red (250 nodes) -> N=12.
    # Green (24 nodes) -> N=2.
    # Cyan (20 nodes) -> N=2.
    # Yellow (150 nodes). 
    # Yellow is big (150 nodes). User request: "make it 3"
    # 112 subs / 3 = 38 columns. Matches header width perfectly (38 hadrons).
    process_region(nodes, '3', START_X_YELLOW, START_Y_YELLOW, body_items_per_col=3)

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4) 
        
    print(f"File saved.")

if __name__ == "__main__":
    rearrange_canvas("/Users/lech/PROJECTS_all/PROJECT_elements/THEORY_COMPLETE.canvas")
