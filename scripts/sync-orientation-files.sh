#!/bin/bash
# sync-orientation-files.sh
# Syncs key documentation files to an orientation folder for AI context export.
#
# Usage:
#   ./scripts/sync-orientation-files.sh              # One-time sync
#   ./scripts/sync-orientation-files.sh --watch      # Continuous watch mode (requires fswatch)
#   ./scripts/sync-orientation-files.sh --zip        # Sync + regenerate zip
#   ./scripts/sync-orientation-files.sh --dest /path # Override destination
#   ./scripts/sync-orientation-files.sh --source /path # Override source (repo root)
#
# This script can be run from any working directory.

set -e

# Compute repo root relative to script location (path-independent)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Defaults
SOURCE_DIR="$REPO_ROOT"
DEST_DIR="${DEST_DIR:-$HOME/Downloads/orientation-files}"
DO_WATCH=false
DO_ZIP=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --watch)
            DO_WATCH=true
            shift
            ;;
        --zip)
            DO_ZIP=true
            shift
            ;;
        --dest)
            DEST_DIR="$2"
            shift 2
            ;;
        --source)
            SOURCE_DIR="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--watch] [--zip] [--dest <path>] [--source <path>]"
            echo ""
            echo "Options:"
            echo "  --watch       Continuous watch mode (requires fswatch)"
            echo "  --zip         Regenerate orientation-files.zip after sync"
            echo "  --dest <path> Override destination folder (default: ~/Downloads/orientation-files)"
            echo "  --source <path> Override source repo root"
            echo "  -h, --help    Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage"
            exit 1
            ;;
    esac
done

sync_files() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Syncing orientation files..."
    echo "  Source: $SOURCE_DIR"
    echo "  Dest:   $DEST_DIR"
    mkdir -p "$DEST_DIR"

    # Core documentation files
    cp "$SOURCE_DIR/README.md" "$DEST_DIR/REPO_README.md" && echo "  ✓ REPO_README.md"
    cp "$SOURCE_DIR/docs/README.md" "$DEST_DIR/DOCS_README.md" && echo "  ✓ DOCS_README.md"
    cp "$SOURCE_DIR/docs/AGENT_CONTEXT.md" "$DEST_DIR/" 2>/dev/null && echo "  ✓ AGENT_CONTEXT.md" || true
    cp "$SOURCE_DIR/CLAUDE.md" "$DEST_DIR/" && echo "  ✓ CLAUDE.md"
    cp "$SOURCE_DIR/.agent/AGENT_INSTRUCTIONS.md" "$DEST_DIR/" 2>/dev/null && echo "  ✓ AGENT_INSTRUCTIONS.md" || true
    cp "$SOURCE_DIR/docs/GLOSSARY.md" "$DEST_DIR/" 2>/dev/null && echo "  ✓ GLOSSARY.md" || true
    cp "$SOURCE_DIR/docs/TOOL.md" "$DEST_DIR/" && echo "  ✓ TOOL.md"
    cp "$SOURCE_DIR/docs/theory/THEORY.md" "$DEST_DIR/" && echo "  ✓ THEORY.md"
    cp "$SOURCE_DIR/VISION.md" "$DEST_DIR/" 2>/dev/null && echo "  ✓ VISION.md" || true
    cp "$SOURCE_DIR/ROADMAP.md" "$DEST_DIR/" 2>/dev/null && echo "  ✓ ROADMAP.md" || true

    # Schema files
    cp "$SOURCE_DIR"/schema/*.json "$DEST_DIR/" 2>/dev/null && echo "  ✓ schema/*.json" || true

    # Roadmap docs
    cp "$SOURCE_DIR"/docs/roadmaps/*.md "$DEST_DIR/" 2>/dev/null && echo "  ✓ roadmaps/*.md" || true

    # Orientation system docs (if exists)
    cp "$SOURCE_DIR/docs/ORIENTATION_FILES.md" "$DEST_DIR/" 2>/dev/null && echo "  ✓ ORIENTATION_FILES.md" || true

    echo ""
    echo "Sync complete. $(ls "$DEST_DIR" | wc -l | xargs) files in $DEST_DIR"
}

generate_zip() {
    local ZIP_PATH="${DEST_DIR}.zip"
    local ZIP_DIR="$(dirname "$DEST_DIR")"
    local ZIP_NAME="$(basename "$DEST_DIR").zip"

    echo ""
    echo "Generating zip: $ZIP_PATH"

    # Remove old zip if exists
    rm -f "$ZIP_PATH"

    # Create new zip (from parent dir to preserve folder name)
    (cd "$ZIP_DIR" && zip -rq "$ZIP_NAME" "$(basename "$DEST_DIR")")

    echo "  ✓ Created $ZIP_PATH"
    echo "  Size: $(du -h "$ZIP_PATH" | cut -f1)"
}

watch_mode() {
    if ! command -v fswatch &> /dev/null; then
        echo "ERROR: fswatch not found."
        echo "Install with: brew install fswatch"
        exit 1
    fi

    echo "Watching for changes... (Ctrl+C to stop)"
    echo "  Watching: $SOURCE_DIR"
    sync_files

    fswatch -o \
        "$SOURCE_DIR/README.md" \
        "$SOURCE_DIR/CLAUDE.md" \
        "$SOURCE_DIR/VISION.md" \
        "$SOURCE_DIR/ROADMAP.md" \
        "$SOURCE_DIR/docs" \
        "$SOURCE_DIR/schema" \
        "$SOURCE_DIR/.agent" \
    | while read; do
        sync_files
        if $DO_ZIP; then
            generate_zip
        fi
    done
}

# Main execution
if $DO_WATCH; then
    watch_mode
else
    sync_files
    if $DO_ZIP; then
        generate_zip
    fi
fi
