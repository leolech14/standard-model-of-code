#!/bin/bash
# UPDATE_TIMESTAMPS.SH
# ====================
# Wrapper script to regenerate file timestamp CSV.
# Called by boot.sh during agent initialization.
#
# Usage:
#     ./update_timestamps.sh [--quiet] [--stats]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
GENERATOR="$REPO_ROOT/standard-model-of-code/scripts/generate_repo_timestamps.py"
OUTPUT_FILE="$REPO_ROOT/project_elements_file_timestamps.csv"

QUIET=false
STATS=false

for arg in "$@"; do
    case $arg in
        --quiet|-q)
            QUIET=true
            ;;
        --stats|-s)
            STATS=true
            ;;
    esac
done

if [ ! -f "$GENERATOR" ]; then
    echo "Error: Generator script not found at $GENERATOR" >&2
    exit 1
fi

if [ "$QUIET" = false ]; then
    echo "Updating file timestamps..."
fi

# Run the generator
python3 "$GENERATOR" --output "$OUTPUT_FILE" > /dev/null 2>&1

if [ "$QUIET" = false ]; then
    LINE_COUNT=$(wc -l < "$OUTPUT_FILE" | tr -d ' ')
    echo "Done. Tracked $((LINE_COUNT - 1)) files."
fi

if [ "$STATS" = true ]; then
    echo ""
    echo "=== Timestamp Statistics ==="
    python3 "$SCRIPT_DIR/timestamps.py" summary 2>/dev/null || echo "(timestamps.py summary unavailable)"
fi
