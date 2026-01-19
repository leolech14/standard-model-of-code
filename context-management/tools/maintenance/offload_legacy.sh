#!/bin/bash
# ============================================================================
# DEPRECATED - Use ./tools/archive/archive.py instead
# ============================================================================
# This script has been replaced by the archive module.
#
# New usage:
#   ./tools/archive/archive.py offload --dry-run
#   ./tools/archive/archive.py offload
#   ./tools/archive/archive.py offload --delete
#   ./tools/archive/archive.py restore <archive_id>
#
# See: tools/archive/README.md
# ============================================================================

echo "DEPRECATED: Use ./tools/archive/archive.py instead"
echo ""
echo "Commands:"
echo "  ./tools/archive/archive.py offload --dry-run   # Preview"
echo "  ./tools/archive/archive.py offload             # Upload"
echo "  ./tools/archive/archive.py offload --delete    # Upload + delete local"
echo ""
exit 1

# ============================================================================
# OLD CODE BELOW (kept for reference)
# ============================================================================
# OFFLOAD_TO_GCLOUD.SH
# Offloads large files to GCS archive bucket and optionally deletes local copies
# ============================================================================
#
# Usage:
#   ./tools/offload_to_gcloud.sh --dry-run     # Preview what would be uploaded
#   ./tools/offload_to_gcloud.sh --upload      # Upload to GCS (keep local)
#   ./tools/offload_to_gcloud.sh --upload --delete  # Upload and delete local
#
# Bucket: gs://elements-archive-2026
# Account: leonardolech3@gmail.com
# Storage Class: ARCHIVE (cheapest, $0.0012/GB/month)
#
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUCKET="gs://elements-archive-2026"
GCLOUD_ACCOUNT="leonardolech3@gmail.com"

DRY_RUN=false
UPLOAD=false
DELETE_LOCAL=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=true
            ;;
        --upload)
            UPLOAD=true
            ;;
        --delete)
            DELETE_LOCAL=true
            ;;
        --help|-h)
            echo "Usage: $0 [--dry-run] [--upload] [--delete]"
            echo ""
            echo "  --dry-run   Preview what would be uploaded"
            echo "  --upload    Upload files to GCS"
            echo "  --delete    Delete local files after upload (requires --upload)"
            exit 0
            ;;
    esac
done

if [ "$DELETE_LOCAL" = true ] && [ "$UPLOAD" = false ]; then
    echo "Error: --delete requires --upload"
    exit 1
fi

echo "============================================"
echo "PROJECT ELEMENTS → GCS ARCHIVE OFFLOAD"
echo "============================================"
echo ""
echo "Bucket: $BUCKET"
echo "Account: $GCLOUD_ACCOUNT"
echo "Mode: $([ "$DRY_RUN" = true ] && echo "DRY RUN" || ([ "$UPLOAD" = true ] && echo "UPLOAD" || echo "PREVIEW"))"
echo ""

# Switch to correct account
gcloud config set account "$GCLOUD_ACCOUNT" 2>/dev/null

# Define what to offload
declare -a OFFLOAD_PATHS=(
    "standard-model-of-code/output/audit"
    "standard-model-of-code/output/*.html"
    "standard-model-of-code/output/*.json"
    "standard-model-of-code/.collider"
    "standard-model-of-code/collider_output"
    "standard-model-of-code/.archive/audio"
    "archive/images"
    "archive/spectrometer_system_audit.zip"
)

# Calculate sizes
echo "=== FILES TO OFFLOAD ==="
echo ""

TOTAL_SIZE=0
for pattern in "${OFFLOAD_PATHS[@]}"; do
    full_path="$PROJECT_ROOT/$pattern"
    if [ -e "$full_path" ] || ls $full_path 1>/dev/null 2>&1; then
        size=$(du -sh $full_path 2>/dev/null | head -1 | awk '{print $1}')
        echo "  $size  $pattern"
        # Add to total (approximate)
        size_bytes=$(du -sb $full_path 2>/dev/null | awk '{sum+=$1} END {print sum}')
        TOTAL_SIZE=$((TOTAL_SIZE + size_bytes))
    else
        echo "  [NOT FOUND] $pattern"
    fi
done

echo ""
echo "Total: $(echo $TOTAL_SIZE | awk '{printf "%.2f GB", $1/1024/1024/1024}')"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo "=== DRY RUN - No files uploaded ==="
    echo ""
    echo "To upload, run: $0 --upload"
    echo "To upload and delete local: $0 --upload --delete"
    exit 0
fi

if [ "$UPLOAD" = false ]; then
    echo "=== PREVIEW ONLY ==="
    echo ""
    echo "To upload, run: $0 --upload"
    exit 0
fi

# Perform upload
echo "=== UPLOADING TO $BUCKET ==="
echo ""

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_PREFIX="archive_$TIMESTAMP"

for pattern in "${OFFLOAD_PATHS[@]}"; do
    full_path="$PROJECT_ROOT/$pattern"
    if [ -e "$full_path" ] || ls $full_path 1>/dev/null 2>&1; then
        dest_path="$BUCKET/$ARCHIVE_PREFIX/$pattern"
        echo "Uploading: $pattern → $dest_path"

        if [ -d "$full_path" ]; then
            gcloud storage cp -r "$full_path" "$dest_path" 2>&1 | tail -5
        else
            gcloud storage cp $full_path "$dest_path/" 2>&1 | tail -5
        fi

        if [ "$DELETE_LOCAL" = true ]; then
            echo "  Deleting local: $full_path"
            rm -rf $full_path
        fi
        echo ""
    fi
done

echo "=== UPLOAD COMPLETE ==="
echo ""
echo "Archive location: $BUCKET/$ARCHIVE_PREFIX/"
echo ""

# Verify
echo "=== VERIFICATION ==="
gcloud storage ls "$BUCKET/$ARCHIVE_PREFIX/" 2>/dev/null | head -10
echo ""

if [ "$DELETE_LOCAL" = true ]; then
    echo "=== LOCAL FILES DELETED ==="
    echo "Space freed: $(echo $TOTAL_SIZE | awk '{printf "%.2f GB", $1/1024/1024/1024}')"
fi

echo ""
echo "To restore later:"
echo "  gcloud storage cp -r $BUCKET/$ARCHIVE_PREFIX/<path> /local/path/"
echo ""
echo "Done."
