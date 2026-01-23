#!/bin/bash
# =============================================================================
# CUTTING_PLAN Phase 1 Execution Script
# =============================================================================
# Archives dead weight files with forensic provenance.
# Safe by default (dry-run mode). Use --execute to perform actual operations.
#
# Usage:
#   ./execute_cutting_phase1.sh           # Dry run (shows what would happen)
#   ./execute_cutting_phase1.sh --execute # Actually performs the archive
#
# Reference: .agent/specs/CUTTING_PLAN.md
# Task: .agent/registry/active/TASK-004.yaml
# =============================================================================

set -e  # Exit on error

# --- Configuration ---
ARCHIVE_DIR="archive/agent_cuts/2026-01-23"
OPERATOR="${CLAUDE_MODEL:-manual}"
DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DRY_RUN=true

# --- Parse Arguments ---
if [[ "$1" == "--execute" ]]; then
    DRY_RUN=false
    echo "=== EXECUTION MODE ==="
else
    echo "=== DRY RUN MODE (use --execute to perform actual operations) ==="
fi

echo "Archive location: $ARCHIVE_DIR"
echo "Operator: $OPERATOR"
echo "Date: $DATE"
echo ""

# --- Helper Functions ---
archive_file() {
    local src="$1"
    local dst="$2"
    if [ -f "$src" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo "  [DRY] Would archive: $src -> $dst"
        else
            mkdir -p "$(dirname "$dst")"
            cp "$src" "$dst"
            echo "  [OK] Archived: $src -> $dst"
        fi
        return 0
    else
        echo "  [SKIP] Not found: $src"
        return 1
    fi
}

remove_original() {
    local src="$1"
    if [ -f "$src" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo "  [DRY] Would remove: $src"
        else
            rm "$src"
            echo "  [OK] Removed: $src"
        fi
    fi
}

# --- Phase 1: Archive Dead Weight ---
echo "=== Phase 1: Archive Dead Weight ==="
echo ""

# Create archive directory structure
if [ "$DRY_RUN" = false ]; then
    mkdir -p "$ARCHIVE_DIR"/{truths_history,workflows,orientation}
fi

# 1. Archive truths/history files
echo "[1/4] Archiving truths/history/..."
TRUTHS_ARCHIVED=0
for f in .agent/intelligence/truths/history/*.yaml 2>/dev/null; do
    if [ -f "$f" ]; then
        archive_file "$f" "$ARCHIVE_DIR/truths_history/$(basename "$f")" && ((TRUTHS_ARCHIVED++)) || true
    fi
done
echo "      Found: $TRUTHS_ARCHIVED files"

# 2. Archive misplaced workflow
echo "[2/4] Archiving workflows/testing_suite.md..."
archive_file ".agent/workflows/testing_suite.md" "$ARCHIVE_DIR/workflows/testing_suite.md" || true

# 3. Archive stale context-management files
echo "[3/4] Archiving context-management/.agent/ stale files..."
if [ -d "context-management/.agent/orientation" ]; then
    for f in context-management/.agent/orientation/*.md 2>/dev/null; do
        [ -f "$f" ] && archive_file "$f" "$ARCHIVE_DIR/orientation/$(basename "$f")" || true
    done
fi
archive_file "context-management/.agent/workflows/publish.md" "$ARCHIVE_DIR/workflows/publish.md" || true

# 4. Generate manifests (only in execute mode)
echo "[4/4] Generating provenance files..."
if [ "$DRY_RUN" = false ]; then
    # Generate MANIFEST.md
    cat > "$ARCHIVE_DIR/MANIFEST.md" << EOF
# Agent Cuts Archive - 2026-01-23

**Operation ID:** CUT-2026-01-23-001
**Date:** $DATE
**Operator:** $OPERATOR
**Plan Reference:** .agent/specs/CUTTING_PLAN.md
**Task Reference:** .agent/registry/active/TASK-004.yaml

## Archived Files

| Original Location | Archive Location | Reason |
|-------------------|------------------|--------|
| .agent/intelligence/truths/history/*.yaml | truths_history/ | DEAD_WEIGHT - No consumer |
| .agent/workflows/testing_suite.md | workflows/ | MISPLACED - Experiment doc |
| context-management/.agent/orientation/* | orientation/ | STALE - Git shows deleted |
| context-management/.agent/workflows/publish.md | workflows/ | STALE - Git shows deleted |

## Restoration

See PROVENANCE.yaml for machine-readable restore commands.

\`\`\`bash
# Example restore:
cp archive/agent_cuts/2026-01-23/workflows/testing_suite.md .agent/workflows/
\`\`\`
EOF
    echo "  [OK] Created MANIFEST.md"

    # Generate PROVENANCE.yaml with checksums
    cat > "$ARCHIVE_DIR/PROVENANCE.yaml" << EOF
# Machine-readable archive provenance
# Generated: $DATE

archive_operation:
  id: "CUT-2026-01-23-001"
  date: "$DATE"
  operator: "$OPERATOR"
  plan_reference: ".agent/specs/CUTTING_PLAN.md"
  task_reference: ".agent/registry/active/TASK-004.yaml"

rationale: |
  Bulk-to-lean cutting phase. Removing dead weight, consolidating
  overlapping docs, simplifying state machine. Full provenance preserved.

files:
EOF

    # Add each archived file with checksum
    for f in $(find "$ARCHIVE_DIR" -type f -not -name "MANIFEST.md" -not -name "PROVENANCE.yaml" 2>/dev/null); do
        rel_path="${f#$ARCHIVE_DIR/}"
        sha=$(shasum -a 256 "$f" | cut -d' ' -f1)

        # Determine original path
        case "$rel_path" in
            truths_history/*) orig=".agent/intelligence/truths/history/$(basename "$f")" ;;
            workflows/publish.md) orig="context-management/.agent/workflows/publish.md" ;;
            workflows/*) orig=".agent/workflows/$(basename "$f")" ;;
            orientation/*) orig="context-management/.agent/orientation/$(basename "$f")" ;;
            *) orig="unknown" ;;
        esac

        cat >> "$ARCHIVE_DIR/PROVENANCE.yaml" << EOF
  - original_path: "$orig"
    archive_path: "$rel_path"
    sha256: "$sha"
    restore_command: "cp $ARCHIVE_DIR/$rel_path $orig"
EOF
    done

    cat >> "$ARCHIVE_DIR/PROVENANCE.yaml" << EOF

version: "1.0"
restoration_history: []
EOF
    echo "  [OK] Created PROVENANCE.yaml with checksums"
else
    echo "  [DRY] Would create MANIFEST.md and PROVENANCE.yaml"
fi

echo ""

# --- Remove Originals (only in execute mode) ---
if [ "$DRY_RUN" = false ]; then
    echo "=== Removing Original Files ==="
    for f in .agent/intelligence/truths/history/*.yaml 2>/dev/null; do
        [ -f "$f" ] && remove_original "$f"
    done
    remove_original ".agent/workflows/testing_suite.md"
    # Note: context-management stale files may already be git-deleted
    echo ""
fi

# --- Summary ---
echo "=== Phase 1 Summary ==="
if [ "$DRY_RUN" = true ]; then
    echo "Status: DRY RUN COMPLETE"
    echo ""
    echo "To execute for real:"
    echo "  ./.agent/tools/execute_cutting_phase1.sh --execute"
else
    echo "Status: EXECUTION COMPLETE"
    echo ""
    echo "Verification:"
    echo "  ls -la $ARCHIVE_DIR/"
    echo "  cat $ARCHIVE_DIR/PROVENANCE.yaml"
    echo ""
    echo "Next: Proceed to Phase 2 (Create META_REGISTRY.yaml)"
fi
