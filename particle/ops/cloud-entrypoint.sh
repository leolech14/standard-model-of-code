#!/bin/bash
set -e

echo "[Cloud Run] Starting Full-Power Socratic Audit..."

# Create the mirror directory if it doesn't exist
mkdir -p /app/repo_mirror

# Sync latest repository mirror from GCS (Excluding large archives for speed)
echo "[Cloud Run] Syncing repository mirror from GCS..."
gsutil -m rsync -r -x ".*archive/.*|.*references/.*" gs://elements-archive-2026/repository_mirror/latest/ /app/repo_mirror

# Fetch Parametric Config (Layer 2)
echo "[Cloud Run] Fetching parametric config from GCS..."
CONFIG_PATH="/app/refinery_config.yaml"
gsutil cp gs://elements-archive-2026/config/refinery_config.yaml $CONFIG_PATH || echo "[Cloud Run] No external config found. Using defaults."

# Work inside the mirror
cd /app/repo_mirror

# Run the Refinery Pipeline (Ingest -> Atomize -> Neo4j)
echo "[Cloud Run] BATCH START: Running Refinery Pipeline..."
export PYTHONPATH=$PYTHONPATH:/app:/app/repo_mirror

# Use the fetched config if it exists
if [ -f "$CONFIG_PATH" ]; then
    python3 /app/context-management/tools/refinery/pipeline.py . --config $CONFIG_PATH
else
    python3 /app/context-management/tools/refinery/pipeline.py .
fi

# Run the Socratic Audit
echo "[Cloud Run] Running Audit..."
# Use smaller context set + Flash model to avoid rate limits
python3 /app/context-management/tools/ai/analyze.py \
    --verify pipeline \
    --set agent_kernel \
    --model gemini-1.5-flash \
    --max-files 20 \
    "$@"

echo "[Cloud Run] Audit complete."
