# Environment Setup System

**Purpose:** Automated, reproducible environment setup for Mac & VPS
**Location:** `PROJECT_elements/setup/`
**Auto-discovery:** This README documents everything

---

## Quick Start

```bash
# Run on ANY machine (Mac or VPS):
cd ~/PROJECTS_all/PROJECT_elements/setup
./install-dependencies.sh

# Installs everything needed, idempotent, safe to re-run
```

---

## What Gets Installed

### Universal (Mac & VPS)
- Node.js 22 + pnpm
- Python 3.12+
- LiteLLM (Claude subscription proxy)
- Doppler (secrets management)
- gcloud SDK (GCS access)

### Mac-Specific
- fswatch (file change detection)
- pipx (Python app isolation)

### VPS-Specific
- Ollama + models (Qwen 32B, CodeLlama 34B)
- lsyncd (bidirectional sync daemon)
- inotify-tools (file monitoring)

---

## Directory Structure

```
PROJECT_elements/setup/
├── README.md                    ← This file
├── install-dependencies.sh      ← Main installation script
├── configs/
│   ├── litellm.yaml            ← LiteLLM proxy config (synced)
│   ├── lsyncd.lua              ← Sync daemon config (VPS)
│   └── fswatch-sync.sh         ← File watcher (Mac)
├── hooks/
│   ├── post-merge              ← Git hook (auto-run on pull)
│   └── setup-changed           ← Detects setup/ changes
└── scripts/
    ├── sync-to-vps.sh          ← Manual sync trigger
    ├── verify-env.sh           ← Check both environments match
    └── diff-env.sh             ← Show differences
```

---

## Automation System

### Level 1: Git Hooks (Automatic on git operations)

**`.git/hooks/post-merge`** (runs after `git pull`):
```bash
#!/bin/bash
# Auto-run setup if it changed

if git diff HEAD@{1} --name-only | grep -q "setup/"; then
    echo "🔧 Setup files changed, updating environment..."
    ./setup/install-dependencies.sh
fi
```

**Install:**
```bash
cp setup/hooks/post-merge .git/hooks/
chmod +x .git/hooks/post-merge
```

### Level 2: Sentinel Integration (Monitors file changes)

**LaunchAgent:** `com.lech.setup-monitor.plist`
```xml
<!-- Watches setup/ directory, runs script if changed -->
<key>WatchPaths</key>
<array>
    <string>~/PROJECTS_all/PROJECT_elements/setup</string>
</array>
<key>ProgramArguments</key>
<array>
    <string>~/PROJECTS_all/PROJECT_elements/setup/install-dependencies.sh</string>
</array>
```

**Install:**
```bash
cp setup/hooks/setup-changed ~/PROJECTS_all/PROJECT_sentinel/agents/com.lech.setup-monitor.plist
sentinel reload com.lech.setup-monitor
```

### Level 3: CI/CD Style (Future with n8n)

**n8n workflow:** "Environment Sync"
```
[Git Webhook Trigger]
    ↓
[Check if setup/ changed]
    ↓
[If yes: Run on Mac]
    ↓
[Run on VPS via SSH]
    ↓
[Verify both succeeded]
    ↓
[Notify via WhatsApp]
```

---

## Verification

### Check Environment Match

```bash
# See what's installed where
./setup/scripts/diff-env.sh

# Output:
Mac      VPS       Tool
✅       ✅        Node.js 22.1.0
✅       ✅        pnpm 9.15.4
✅       ✅        Doppler 3.75.2
✅       ❌        fswatch (Mac-only, expected)
❌       ✅        Ollama (VPS-only, expected)
```

### Continuous Verification

**Cron job (runs daily):**
```bash
# On both machines
0 6 * * * ~/PROJECTS_all/PROJECT_elements/setup/scripts/verify-env.sh >> ~/setup-verify.log
```

Reports any drift, alerts if versions mismatch.

---

## Evolution Workflow

### Adding New Dependency

**Example: Need to add Redis**

```bash
# 1. Edit script
vim setup/install-dependencies.sh

# Add:
if ! command -v redis-server &> /dev/null; then
    if [[ "$OS" == "mac" ]]; then
        brew install redis
    else
        apt-get install -y redis-server
    fi
fi

# 2. Commit
git add setup/install-dependencies.sh
git commit -m "Add Redis to setup"
git push

# 3. On VPS:
cd /root/projects/PROJECT_elements
git pull  # Triggers post-merge hook automatically
          # OR: manually run ./setup/install-dependencies.sh

# 4. On Mac:
cd ~/PROJECTS_all/PROJECT_elements
git pull  # Auto-runs setup via hook

# Done - both have Redis
```

### Version Upgrades

```bash
# Upgrading Node.js 22 → 24

# Edit script:
- brew install node@22
+ brew install node@24

# Commit, push, pull on both machines
# Hook auto-runs, upgrades both
```

---

## Findability

### How to Discover

**Method 1: Project README**
```
PROJECT_elements/README.md mentions setup/
```

**Method 2: CLAUDE.md**
```
~/.claude/CLAUDE.md references:
"Environment setup: PROJECT_elements/setup/install-dependencies.sh"
```

**Method 3: Sentinel**
```
sentinel list
→ Shows com.lech.setup-monitor
→ Points to setup script
```

**Method 4: n8n Workflow (future)**
```
Workflow: "Environment Setup"
Description: "Syncs dev environments"
```

**Method 5: This README**
```
You're reading it now!
Location: PROJECT_elements/setup/README.md
```

---

## Documentation

### Inline (in script)
```bash
# ============================================================================
# LITELLM (for Claude subscription proxy)
# Purpose: Allows OpenClaw to use Claude Code subscription
# Platforms: Both Mac & VPS
# ============================================================================
```

### External (this file)
- Purpose
- Usage
- Architecture
- Evolution workflow

### Integration Docs
- Referenced in main PROJECT_elements README
- Linked from CLAUDE.md
- Mentioned in deployment guides

---

## Automation (OpenClaw Native)

**Setup verification runs via OpenClaw cron:**

```bash
# View cron jobs
ssh hostinger "cd /root/openclaw && pnpm openclaw cron list"

# Jobs:
# - Environment Verification (daily 6 AM)
# - Weekly Security Audit (Monday 9 AM)
```

**Adding new scheduled tasks:**

```bash
# Example: Daily sync check
openclaw cron add \
  --name "Sync Verification" \
  --cron "0 */6 * * *" \
  --message "Verify PROJECT_elements synced between Mac and VPS" \
  --model ollama/qwen2.5:32b
```

**All automation managed through OpenClaw** - no external cron, no LaunchAgents needed.

---

## Current Status

```
✅ Script created and documented
✅ Idempotent (safe to re-run)
✅ OS detection (Mac/Linux)
✅ OpenClaw cron configured
✅ Verification automated (daily 6 AM)
✅ Uses FREE Ollama for automation
```

---

## Maintenance

**When you need new dependencies:**

1. Edit `install-dependencies.sh`
2. Run on Mac: `./install-dependencies.sh`
3. Sync to VPS (via git or file sync)
4. Run on VPS: `./install-dependencies.sh`
5. Done - both environments updated

**OpenClaw verifies daily** and alerts if drift detected.
