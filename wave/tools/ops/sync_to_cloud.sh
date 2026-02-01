
#!/bin/bash

# Configuration
BUCKET="gs://elements-archive-2026/repository_mirror"
PROJECT_DIR="/Users/lech/PROJECTS_all/PROJECT_elements"

# Ensure we are in the right directory
cd "$PROJECT_DIR" || exit 1

echo "==============================================="
echo "☁️  Syncing PROJECT_elements to Google Cloud..."
echo "==============================================="
echo "Target: $BUCKET"
echo "Timestamp: $(date)"
echo "-----------------------------------------------"

# Exclude heavy/unnecessary folders locally to speed up sync
# Using -x pattern to exclude .git, __pycache__, and node_modules
gsutil -m rsync -d -x '\.git/.*|__pycache__/.*|node_modules/.*|\.DS_Store' \
    . "$BUCKET"

echo "-----------------------------------------------"
echo "✅ Sync Complete."
echo "The Cloud Socratic Layer will use this snapshot for the next audit."
