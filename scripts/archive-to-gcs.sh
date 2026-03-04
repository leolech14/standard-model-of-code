#!/usr/bin/env bash
# Archive Zone 3 (Generated Output) to GCS
# Bucket: gs://elements-archive-2026/
#
# Usage:
#   bash scripts/archive-to-gcs.sh           # Dry-run (shows what would sync)
#   bash scripts/archive-to-gcs.sh --execute # Real sync
#
# Requires: gcloud CLI authenticated (leonardolech3@gmail.com)

set -euo pipefail

BUCKET="gs://elements-archive-2026/zone3-generated"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DRY_RUN=true

if [[ "${1:-}" == "--execute" ]]; then
    DRY_RUN=false
fi

# Zone 3 directories to archive
DIRS=(
    "research"
    "reports"
    "observer"
    "wave/library"
    "particle/docs/research"
    "particle/docs/ui/corpus"
    "notebook-lm"
)

echo "=== Archive Zone 3 to GCS ==="
echo "Bucket: $BUCKET"
echo "Mode: $(if $DRY_RUN; then echo 'DRY-RUN (use --execute for real sync)'; else echo 'EXECUTE'; fi)"
echo ""

for dir in "${DIRS[@]}"; do
    src="$PROJECT_ROOT/$dir"
    if [[ ! -d "$src" ]]; then
        echo "SKIP: $dir (not found)"
        continue
    fi

    dest="$BUCKET/$dir/"
    file_count=$(find "$src" -type f | wc -l | tr -d ' ')
    echo "SYNC: $dir ($file_count files) -> $dest"

    if ! $DRY_RUN; then
        gsutil -m rsync -r -d "$src" "$dest"
    fi
done

echo ""
if $DRY_RUN; then
    echo "Dry-run complete. Run with --execute to sync."
else
    echo "Archive sync complete."
fi
