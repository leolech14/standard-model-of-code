# Obsidian Canvas - Complete Guide for Seamless Canvas Creation

## What is Obsidian Canvas?

Obsidian Canvas is a visual workspace that allows you to create infinite, zoomable whiteboards with cards, connections, and embedded content. It's perfect for:
- Mind mapping
- Project planning
- Knowledge organization
- Visual note-taking
- Creating theory diagrams (like your Standard Model of Software Architecture)

## Creating a New Canvas

### Method 1: Using Command Palette
1. Open Obsidian
2. Press `Cmd+P` (Mac) or `Ctrl+P` (Windows/Linux)
3. Type "New canvas" and press Enter
4. Name your canvas file

### Method 2: Manual File Creation
1. Create a new file with `.canvas` extension
2. Add the basic canvas structure:
```json
{
  "nodes": [],
  "edges": []
}
```

## Canvas File Structure

### Complete Canvas JSON Schema
```json
{
  "nodes": [
    {
      "id": "unique-id",
      "type": "text|file|image|webpage|link|group",
      "x": 0,
      "y": 0,
      "width": 200,
      "height": 100,
      "color": "1|2|3|4|5|6",  // Node colors
      "text": "Your text content",
      "url": "https://example.com",  // For webpage nodes
      "file": "path/to/file.md",     // For file nodes
      "subpath": "#section",        // For linking to sections
      "collapsed": false            // For group nodes
    }
  ],
  "edges": [
    {
      "id": "edge-id",
      "fromNode": "node-id-1",
      "fromSide": "top|right|bottom|left",
      "toNode": "node-id-2",
      "toSide": "top|right|bottom|left",
      "color": "1|2|3|4|5|6",
      "label": "Edge label"
    }
  ]
}
```

## Node Types

### 1. Text Nodes
```json
{
  "id": "text-node",
  "type": "text",
  "x": 100,
  "y": 100,
  "width": 300,
  "height": 200,
  "color": "1",
  "text": "# Your Title\n\nYour content with **markdown** support"
}
```

### 2. File Nodes (Links to Obsidian Notes)
```json
{
  "id": "file-node",
  "type": "file",
  "x": 500,
  "y": 100,
  "width": 300,
  "height": 200,
  "file": "MyNote.md"
}
```

### 3. Image Nodes
```json
{
  "id": "image-node",
  "type": "image",
  "x": 100,
  "y": 400,
  "width": 400,
  "height": 300,
  "file": "images/diagram.png"
}
```

### 4. Webpage Nodes
```json
{
  "id": "web-node",
  "type": "webpage",
  "x": 600,
  "y": 400,
  "width": 400,
  "height": 300,
  "url": "https://obsidian.md",
  "title": "Obsidian Website"
}
```

### 5. Group Nodes (Containers)
```json
{
  "id": "group-node",
  "type": "group",
  "x": 200,
  "y": 200,
  "width": 800,
  "height": 600,
  "label": "Group Name",
  "collapsed": false
}
```

## Edge Connections

### Creating Edges
```json
{
  "id": "connection-1",
  "fromNode": "node-a",
  "fromSide": "right",
  "toNode": "node-b",
  "toSide": "left",
  "color": "6",
  "label": "influences"
}
```

### Edge Colors
- `1`: Gray (default)
- `2`: Red
- `3`: Orange
- `4`: Yellow
- `5`: Green
- `6`: Blue

## Best Practices for Seamless Canvases

### 1. Use a Grid System
```javascript
// Maintain consistent spacing
const GRID_SIZE = 50;
x: Math.round(x / GRID_SIZE) * GRID_SIZE,
y: Math.round(y / GRID_SIZE) * GRID_SIZE
```

### 2. Organize with Groups
- Use group nodes to create logical sections
- Keep related concepts together
- Use colors to distinguish categories

### 3. Smart IDs
Use descriptive IDs:
```json
"id": "theory-standard-model-node-1"  // Good
"id": "n1"                            // Hard to maintain
```

### 4. Consistent Sizing
- Text nodes: 200-400 width
- File nodes: 300-400 width
- Group nodes: Large enough to contain children
- Maintain aspect ratios for images

## Advanced Features

### 1. Embedding Canvas in Canvas
You can reference another canvas as a node:
```json
{
  "id": "subcanvas",
  "type": "file",
  "x": 100,
  "y": 100,
  "file": "sub-canvas.canvas"
}
```

### 2. Using Templates
Create templates for common patterns:
```json
// concept-node.json
{
  "id": "{{concept-id}}",
  "type": "text",
  "x": {{x}},
  "y": {{y}},
  "width": 300,
  "height": 200,
  "color": "{{color}}",
  "text": "# {{title}}\n\n{{content}}"
}
```

### 3. Zoom and Pan Coordinates
```json
{
  "view": {
    "x": 0,
    "y": 0,
    "zoom": 1.0
  }
}
```

## Keyboard Shortcuts

- `Cmd/Ctrl + Click`: Multi-select nodes
- `Delete`: Remove selected nodes/edges
- `Cmd/Ctrl + D`: Duplicate selected
- `Cmd/Ctrl + G`: Group selected nodes
- `Space + Drag`: Pan canvas
- `Cmd/Ctrl + Scroll`: Zoom in/out
- `Cmd/Ctrl + Z`: Undo
- `Cmd/Ctrl + Y`: Redo

## Working with Your THEORY_COMPLETE.canvas

### Importing to Obsidian
1. Copy `THEORY_COMPLETE_with_extracts.canvas` to your Obsidian vault
2. Open it in Obsidian (double-click the file)
3. Obsidian will automatically render the visual canvas

### Making it Interactive
1. Right-click on nodes to access context menu
2. Use `Cmd/Ctrl + Click` to select multiple nodes
3. Drag to create connections between nodes
4. Use the color palette to organize categories

### Linking to Other Notes
```json
{
  "id": "link-to-theory",
  "type": "file",
  "x": 100,
  "y": 100,
  "file": "THEORY_COMPREHENSIVE_REPORT.md",
  "subpath": "#executive-summary"
}
```

## Automation Scripts

### Python Script to Generate Canvas
```python
import json

def create_canvas_node(node_id, node_type, x, y, text=None, file=None, width=300, height=200):
    node = {
        "id": node_id,
        "type": node_type,
        "x": x,
        "y": y,
        "width": width,
        "height": height
    }
    if text:
        node["text"] = text
    if file:
        node["file"] = file
    return node

def create_canvas_edge(edge_id, from_node, to_node, label=None):
    edge = {
        "id": edge_id,
        "fromNode": from_node,
        "fromSide": "right",
        "toNode": to_node,
        "toSide": "left"
    }
    if label:
        edge["label"] = label
    return edge

# Create your canvas
canvas = {
    "nodes": [
        create_canvas_node("node1", "text", 100, 100, text="# Hello World\n\nThis is a node"),
        create_canvas_node("node2", "text", 500, 100, text="# Another Node\n\nConnected!"),
    ],
    "edges": [
        create_canvas_edge("edge1", "node1", "node2", "connects to")
    ]
}

# Save to file
with open("my-canvas.canvas", "w") as f:
    json.dump(canvas, f, indent=2)
```

## Tips for Large Canvases

1. **Use Groups**: Keep related items in group nodes
2. **Color Code**: Use consistent colors for categories
3. **Break It Down**: Split huge canvases into linked sub-canvases
4. **Use Search**: Obsidian's search works on canvas content
5. **Version Control**: Track canvas files in git

## Community Plugins for Canvas

1. **Advanced Tables**: Create tables in text nodes
2. **Mermaid**: Add diagrams within text nodes
3. **Excalidraw**: Integrate hand-drawn diagrams
4. **Dataview**: Query and display vault data in canvas

## Troubleshooting

### Canvas Not Loading
- Check JSON syntax with a validator
- Ensure proper UTF-8 encoding
- Verify all referenced files exist

### Performance Issues
- Break large canvases into smaller ones
- Avoid very high-resolution images
- Use fewer nodes with grouped content

### File Paths Not Working
- Use relative paths from vault root
- Check case sensitivity (important on Linux/Mac)
- Escape special characters in filenames

## Export Options

1. **PNG Image**: `File → Export → Export as PNG`
2. **SVG**: `File → Export → Export as SVG`
3. **Markdown**: `File → Export → Export as Markdown`
4. **PDF**: Print to PDF from browser

Remember: Canvas files are just JSON, so you can version control them, edit them programmatically, and share them easily!