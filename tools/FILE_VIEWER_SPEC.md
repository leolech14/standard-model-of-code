# File Viewer - Full Implementation Spec

## Layout
```
+------------------+--------------------------------+
|                  |                                |
|    SIDEBAR       |        PREVIEW / EDIT          |
|   (220px)        |        (flex: 1)               |
|                  |                                |
|  [Grouped        |   Format-specific              |
|   Drawers]       |   view + edit tools            |
|                  |                                |
|  - Folders       |                                |
|  - Images        |                                |
|  - Code          |                                |
|  - Documents     |                                |
|  - etc.          |                                |
|                  |                                |
+------------------+--------------------------------+
```

## Core Behavior
- Popup modal (not full page)
- Click backdrop = close
- ESC = close
- Compact, minimal design
- Dark theme

---

## Format-Specific Features

### CODE FILES (.py, .js, .ts, .html, .css, .json, etc.)
**View:**
- Syntax highlighting (highlight.js)
- Line numbers
- Word wrap toggle

**Edit:**
- Monaco Editor or CodeMirror
- Save (Cmd+S)
- Undo/Redo
- Find/Replace (Cmd+F)
- Format/Prettify
- Copy all

**Toolbar:**
`[Save] [Format] [Copy] [Wrap]`

---

### MARKDOWN (.md)
**View:**
- Rendered markdown
- Toggle: Rendered / Source / Split

**Edit:**
- Live preview split view
- Bold/Italic/Link shortcuts
- Insert image/table
- Save

**Toolbar:**
`[Save] [Preview|Source|Split] [Bold] [Italic] [Link]`

---

### IMAGES (.jpg, .png, .gif, .webp, .svg)
**View:**
- Fit to container
- Zoom in/out
- Actual size

**Edit:**
- Rotate (90 CW/CCW)
- Flip H/V
- Crop (basic)
- Resize
- Save as (format convert)

**Toolbar:**
`[Zoom -] [100%] [Zoom +] [Rotate] [Flip] [Crop] [Save As]`

---

### PDF (.pdf)
**View:**
- PDF.js embedded viewer
- Page navigation
- Zoom

**Edit:**
- Extract pages (select range)
- Rotate pages
- Delete pages
- Merge with another PDF

**Toolbar:**
`[Page: 1/10] [Zoom] [Rotate Page] [Extract] [Delete Page]`

---

### VIDEO (.mp4, .webm, .mov)
**View:**
- Video player with controls
- Fullscreen toggle

**Edit:**
- Trim (set start/end)
- Extract frame as image
- Extract audio
- Mute audio

**Toolbar:**
`[Play] [Trim] [Screenshot] [Extract Audio]`

---

### AUDIO (.mp3, .wav, .flac, .ogg)
**View:**
- Waveform visualization
- Audio player

**Edit:**
- Trim
- Normalize volume
- Fade in/out

**Toolbar:**
`[Play] [Trim] [Normalize] [Fade]`

---

### DATA FILES (.csv, .json, .yaml, .xml)
**View:**
- CSV: Table view
- JSON: Tree view with collapse/expand
- YAML: Formatted view

**Edit:**
- CSV: Inline cell editing
- JSON: Add/remove/edit keys
- Sort columns
- Filter rows

**Toolbar:**
`[Save] [Sort] [Filter] [Add Row] [Table|Raw]`

---

### ARCHIVES (.zip, .tar, .gz)
**View:**
- List contents (tree view)
- File sizes
- Compression ratio

**Actions:**
- Extract all
- Extract selected
- Add files
- Remove files

**Toolbar:**
`[Extract All] [Extract Selected] [Add] [Remove]`

---

### 3D MODELS (.glb, .gltf, .stl, .obj)
**View:**
- 3D viewer with orbit controls
- Auto-rotate toggle
- Wireframe toggle

**Edit:**
- Scale
- Center
- Convert format
- Export

**Toolbar:**
`[Rotate] [Wireframe] [Scale] [Export As]`

---

### FONTS (.ttf, .otf, .woff)
**View:**
- Sample text preview
- Character map
- Font info (name, style, weight)

**Edit:**
- Change sample text
- Change sample size

**Toolbar:**
`[Size: 24px] [Sample Text Input]`

---

### DOCUMENTS (.docx, .odt, .rtf)
**View:**
- Rendered document (mammoth.js for docx)
- Page-like display

**Edit:**
- Limited - export to different format
- Copy text

**Toolbar:**
`[Copy Text] [Export as PDF] [Export as MD]`

---

## Sidebar Drawers

| Group | Extensions | Icon |
|-------|------------|------|
| Folders | (directories) | folder |
| Images | jpg, png, gif, webp, svg, bmp, heic | image |
| Videos | mp4, webm, mov, avi, mkv | video |
| Audio | mp3, wav, flac, ogg, m4a | audio |
| Code | py, js, ts, html, css, json, yaml, sh... | code |
| Documents | md, txt, doc, docx, rtf, odt | file |
| PDFs | pdf | pdf |
| Data | csv, xls, xlsx, sqlite, db | data |
| Archives | zip, tar, gz, rar, 7z | archive |
| 3D Models | glb, gltf, stl, obj, fbx | cube |
| Fonts | ttf, otf, woff, woff2 | type |
| Other | * | file |

---

## Persistence
- Drawer open/closed states per folder (localStorage)
- Last opened file
- Editor preferences (font size, wrap)
- Window size/position

---

## Libraries Needed
- **Monaco Editor** - Code editing
- **PDF.js** - PDF viewing/manipulation
- **Mammoth.js** - DOCX viewing
- **WaveSurfer.js** - Audio waveform
- **Three.js** - 3D models
- **JSZip** - Archive handling
- **Sharp** (server-side) - Image manipulation
- **FFmpeg.wasm** - Video/audio processing

---

## API Endpoints

```
GET  /api/list?path=...        # List directory
GET  /api/content?path=...     # Get file content (text)
GET  /file/...                 # Serve raw file
POST /api/save                 # Save file content
POST /api/image/rotate         # Rotate image
POST /api/image/resize         # Resize image
POST /api/pdf/extract          # Extract PDF pages
POST /api/archive/extract      # Extract archive
POST /api/archive/list         # List archive contents
```

---

## Priority Implementation Order

### Phase 1 - Core Viewing
1. Code files with syntax highlighting
2. Images with zoom
3. Markdown rendered
4. PDF embedded
5. Video/Audio players

### Phase 2 - Code Editing
1. Monaco Editor integration
2. Save functionality
3. Format/prettify
4. Find/replace

### Phase 3 - Media Editing
1. Image rotate/crop
2. PDF page operations
3. Video trim/screenshot

### Phase 4 - Advanced
1. Archive operations
2. 3D model viewer
3. Font preview
4. Document conversion
