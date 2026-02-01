# File Explorer Enhancement Plan

## Current State (Completed)
- Touch ID / Face ID authentication
- Path traversal security (restricted to BROWSE_ROOT)
- Localhost-only binding
- 17 color categories with intense OKLCH colors
- 150+ file format mappings
- 17px card gap
- Sidebar showing current/parent folder
- Undo/redo for file operations
- Selection mode with drag-select
- Lightbox preview for files

---

## Proposed Enhancements

### 1. Header Filters
**Purpose:** Quick filtering by file type category

**UI Design:**
```
[Back][Up] [Undo][Redo] | Path/Breadcrumb | [Filters v] [+ New] [Search] [Select] [Size] [Settings]
```

**Filter Options:**
- All (default)
- Folders only
- Images (image + vector)
- Media (video + audio)
- Code
- Documents (doc + pdf)
- Data (data + notebook)
- Config
- Archives
- 3D Models
- Other (binary + font + executable + database)

**Implementation:**
- Dropdown menu with checkboxes (multi-select)
- Active filters shown as pills/tags
- Filter state persists during session
- Keyboard shortcut: Cmd+F to focus filters

---

### 2. Create New Folder
**Purpose:** Create folders without leaving the UI

**UI Design:**
- [+ New] button in header
- Click → inline rename field appears in grid
- Or modal dialog for folder name

**Implementation:**
- POST /api/create-folder endpoint
- Validate folder name (no special chars)
- Auto-navigate into new folder or stay in current
- Add to undo stack

---

### 3. Right-Click Context Menu
**Purpose:** Quick actions without toolbar

**Menu Structure:**

#### For Files:
```
├── Open                    (Enter)
├── Open With...            (→ submenu)
├── Quick Look              (Space)
├── ─────────────────────
├── Cut                     (Cmd+X)
├── Copy                    (Cmd+C)
├── Duplicate               (Cmd+D)
├── ─────────────────────
├── Rename                  (Enter after select)
├── Move to...              (→ folder picker)
├── Copy Path               (Cmd+Shift+C)
├── ─────────────────────
├── Compress                (→ .zip)
├── ─────────────────────
├── Get Info                (Cmd+I)
├── ─────────────────────
├── Move to Trash           (Cmd+Backspace)
```

#### For Folders:
```
├── Open                    (Enter)
├── Open in New Tab         (Cmd+Click) [future]
├── ─────────────────────
├── Cut                     (Cmd+X)
├── Copy                    (Cmd+C)
├── Duplicate               (Cmd+D)
├── ─────────────────────
├── Rename                  (Enter after select)
├── Move to...
├── Copy Path               (Cmd+Shift+C)
├── ─────────────────────
├── New Folder Inside
├── Compress
├── ─────────────────────
├── Get Info                (Cmd+I)
├── ─────────────────────
├── Move to Trash           (Cmd+Backspace)
```

#### For Empty Space (Grid Background):
```
├── New Folder              (Cmd+Shift+N)
├── New File...             (Cmd+N) [future]
├── ─────────────────────
├── Paste                   (Cmd+V)
├── ─────────────────────
├── Select All              (Cmd+A)
├── ─────────────────────
├── Sort by →
│   ├── Name
│   ├── Date Modified
│   ├── Size
│   ├── Type
├── View as →
│   ├── Grid (current)
│   ├── List [future]
│   ├── Columns [future]
├── ─────────────────────
├── Get Info (Folder)
├── ─────────────────────
├── Refresh                 (Cmd+R)
```

#### For Multiple Selection:
```
├── Open All
├── ─────────────────────
├── Cut                     (Cmd+X)
├── Copy                    (Cmd+C)
├── ─────────────────────
├── Move to...
├── ─────────────────────
├── Compress (N items)
├── ─────────────────────
├── Move to Trash           (Cmd+Backspace)
```

---

## New API Endpoints Required

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/create-folder` | POST | Create new folder |
| `/api/rename` | POST | Rename file/folder |
| `/api/duplicate` | POST | Duplicate file/folder |
| `/api/compress` | POST | Create zip archive |
| `/api/info` | GET | Get detailed file info |
| `/api/sort` | GET | List with sort options |

---

## Implementation Priority

### Phase 1: Core (This Session)
1. Header filters dropdown
2. Create new folder button + endpoint
3. Basic right-click menu (Open, Cut, Copy, Paste, Rename, Delete)

### Phase 2: Extended
4. Move to... with folder picker dialog
5. Duplicate functionality
6. Compress to zip
7. Get Info panel
8. Sort options

### Phase 3: Future
9. List/Column views
10. Tabs
11. New file creation
12. Drag-drop between folders

---

## Technical Considerations

### Context Menu Implementation
- Pure CSS/JS (no library)
- Position relative to click point
- Dismiss on click outside or Escape
- Keyboard navigation (arrow keys)
- Submenu on hover with delay

### State Management
- Filter state in localStorage
- Sort preference in localStorage
- Undo stack for new operations

### Accessibility
- ARIA roles for menu
- Keyboard shortcuts visible
- Focus management

---

## Validation Questions

1. Should filters be persistent across sessions (localStorage)?
2. Should "New Folder" open inline edit or modal?
3. Should context menu match macOS exactly or have custom style?
4. Priority: More features or polish existing?

---

## Decision: Recommended Approach

**Inline with macOS conventions** - Users expect familiar patterns:
- Context menu style matches macOS dark mode
- Keyboard shortcuts match Finder
- Animations subtle and fast (150ms)

**Progressive enhancement** - Core features first:
1. Filters (high value, low complexity)
2. New folder (essential)
3. Context menu (high value, medium complexity)

**Robust implementation:**
- All operations go through undo stack
- Optimistic UI with rollback on error
- Debounced updates for performance
