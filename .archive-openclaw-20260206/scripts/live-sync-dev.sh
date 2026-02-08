#!/bin/bash
# Live Development Sync - Mac ↔ VPS
# Watches for changes and syncs immediately

VPS_HOST="hostinger"
PROJECTS=(
  "PROJECT_elements"
  "PROJECT_sentinel"
  "PROJECT_atman"
  "PROJECT_orchestra"
)

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

sync_project() {
  local project=$1
  local direction=$2  # "push" or "pull"

  if [ "$direction" = "push" ]; then
    # Mac → VPS
    echo -e "${BLUE}→ Syncing ${project} to VPS...${NC}"
    rsync -avz --delete \
      --exclude 'node_modules/' \
      --exclude '.git/' \
      --exclude '__pycache__/' \
      --exclude '*.pyc' \
      --exclude '.DS_Store' \
      ~/PROJECTS_all/${project}/ \
      ${VPS_HOST}:/root/projects/${project}/
  else
    # VPS → Mac
    echo -e "${BLUE}← Pulling ${project} from VPS...${NC}"
    rsync -avz --delete \
      --exclude 'node_modules/' \
      --exclude '.git/' \
      --exclude '__pycache__/' \
      ${VPS_HOST}:/root/projects/${project}/ \
      ~/PROJECTS_all/${project}/
  fi

  echo -e "${GREEN}✓ ${project} synced${NC}"
}

# Initial full sync
echo "Initial sync..."
for project in "${PROJECTS[@]}"; do
  sync_project "$project" "push"
done

# Watch for changes (using fswatch on Mac)
if ! command -v fswatch &> /dev/null; then
  echo "Installing fswatch..."
  brew install fswatch
fi

echo "Watching for changes... (Ctrl+C to stop)"

for project in "${PROJECTS[@]}"; do
  fswatch -o ~/PROJECTS_all/${project} | while read; do
    sync_project "$project" "push"
  done &
done

wait
