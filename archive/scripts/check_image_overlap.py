import json

def check_overlap(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Image Bounds from previous read
    IMG_X = -847
    IMG_Y = -12355
    IMG_W = 10367
    IMG_H = 6955
    IMG_X2 = IMG_X + IMG_W
    IMG_Y2 = IMG_Y + IMG_H
    
    print(f"Checking overlaps for Image Rect: [{IMG_X}, {IMG_Y}, {IMG_X2}, {IMG_Y2}]")
    
    nodes = data.get('nodes', [])
    overlapping = []
    
    for n in nodes:
        if n.get('type') == 'file': continue # Skip the image itself
        
        nx = n['x']
        ny = n['y']
        nw = n.get('width', 0)
        nh = n.get('height', 0)
        
        # Simple AABB check
        if (nx < IMG_X2 and nx + nw > IMG_X and
            ny < IMG_Y2 and ny + nh > IMG_Y):
            overlapping.append(n)
            
    print(f"Found {len(overlapping)} nodes overlapping with the image.")
    for n in overlapping:
        print(f" - [{n['type']}] {n.get('id')} at ({n['x']}, {n['y']}): {n.get('text', n.get('label', ''))[:50]}...")

if __name__ == "__main__":
    check_overlap("/Users/lech/PROJECTS_all/PROJECT_elements/THEORY_COMPLETE.canvas")
