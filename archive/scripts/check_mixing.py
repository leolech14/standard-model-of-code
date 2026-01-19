import json
import re

def get_type_and_number(node):
    node_id = node.get('id', '')
    text = node.get('text', '')
    
    # Identify Type
    if node_id.startswith('hadron_'):
        n_type = 'HADRON'
    elif node_id.startswith('sub_'):
        n_type = 'SUB'
    else:
        n_type = 'OTHER'
        
    # Identify Number
    match = re.search(r'#(\d+)', text)
    if match:
        num = int(match.group(1))
    elif node_id.startswith('sub_'):
        try:
            num = int(node_id.split('_')[1])
        except:
            num = 999
    else:
        num = 999
        
    return n_type, num

def check_mixing(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
        
    logic_nodes = [n for n in data.get('nodes', []) if n.get('color') == '1']
    
    # We assume they are currently sorted by position (roughly) or we sort them by Y then X to see current layout order
    # Actually, let's sort by the same logic used in rearrange: Number
    # But better to check the *actual* proximity in X/Y space?
    # The user asked "are YOU mixing", I assume referencing the previous action.
    # So let's check the list sorted by Number.
    
    # Sort purely by number (the logic used)
    logic_nodes.sort(key=lambda n: (get_type_and_number(n)[1], n.get('id')))
    
    sequence = [get_type_and_number(n) for n in logic_nodes]
    
    switches = 0
    overlaps = []
    
    for i in range(len(sequence) - 1):
        curr_type, curr_num = sequence[i]
        next_type, next_num = sequence[i+1]
        
        if curr_type != next_type and curr_type != 'OTHER' and next_type != 'OTHER':
            switches += 1
            
        if curr_num == next_num and curr_type != next_type:
            overlaps.append(curr_num)
            
    print(f"Total Logic Nodes: {len(logic_nodes)}")
    print(f"Type Switches in Sequence: {switches}")
    print(f"Numerical Overlaps (Same number, different type): {len(overlaps)}")
    if overlaps:
        print(f"Examples: {overlaps[:10]}...")
        
    hadrons = len([x for x in sequence if x[0] == 'HADRON'])
    subs = len([x for x in sequence if x[0] == 'SUB'])
    print(f"Counts: Hadrons={hadrons}, Subs={subs}")

if __name__ == "__main__":
    check_mixing("/Users/lech/PROJECTS_all/PROJECT_elements/THEORY_COMPLETE.canvas")
