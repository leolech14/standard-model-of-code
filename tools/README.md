# Root Tools Index

> **Purpose:** Project-wide utility tools (outside realm classification)
> Updated: 2026-01-31

## File Management

| Tool | Purpose |
|------|---------|
| `file_explorer.py` | Interactive file browser with search |
| `file_viewer.py` | File content viewer |
| `file_scanner.py` | Filesystem scanning utilities |
| `generate_file_inventory.py` | Create file inventory CSV |

### File Explorer Features
- Full-text search across codebase
- File type filtering
- Preview with syntax highlighting
- 314KB - comprehensive implementation

## Documentation Tools

| Tool | Purpose |
|------|---------|
| `generate_reader_config.py` | Generate reader app configuration |
| `fix_reader_links.py` | Repair broken links in reader |
| `sync_to_notion.py` | Sync documentation to Notion |

## Quality Assurance

| Tool | Purpose |
|------|---------|
| `verify_counts.py` | Verify file counts |
| `verify_links.py` | Check for broken links |
| `verify_placeholders.py` | Find incomplete placeholders |

## Image Analysis

| Tool | Purpose |
|------|---------|
| `image_browser.py` | Browse and score images |
| `score_reference_images.py` | Score reference image quality |

### Data Files
| File | Description |
|------|-------------|
| `file_inventory.csv` | Complete file listing (2.6MB) |
| `image_scores.csv` | Image quality scores (1.7MB) |
| `image_scores_precision.csv` | Precision-scored images (1.8MB) |

## Specifications (In Progress)

| Document | Purpose |
|----------|---------|
| `FILE_EXPLORER_ENHANCEMENTS.md` | Enhancement roadmap |
| `FILE_EDITOR_SIDEBAR_PLAN.md` | Editor sidebar design |
| `FILE_VIEWER_SPEC.md` | Viewer specification |
| `FILE_VIEWER_STATUS.md` | Implementation status |

## Usage

```bash
# File exploration
python3 tools/file_explorer.py

# Generate inventory
python3 tools/generate_file_inventory.py > file_inventory.csv

# Verify links
python3 tools/verify_links.py
```

## Classification Note

These tools are **project-wide utilities** that don't fit the 3-fold realm classification:
- **Not PARTICLE**: Not core structural analysis
- **Not WAVE**: Not AI/semantic processing
- **Not OBSERVER**: Not governance/monitoring

They exist to support development workflow across all realms.

## See Also

- `scripts/` - Shell scripts
- `context-management/tools/` - Wave realm tools
- `standard-model-of-code/tools/` - Particle realm tools
