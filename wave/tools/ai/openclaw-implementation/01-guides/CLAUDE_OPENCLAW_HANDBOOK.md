# Claude ↔ OpenClaw Handbook

**For:** Claude Code (or any Claude agent) working with OpenClaw
**Purpose:** Everything Claude needs to know to configure and work with OpenClaw
**Status:** Living document - update as you learn

---

## 🎯 WHAT IS THIS?

You (Claude) are working with a human who has:
- **OpenClaw Gateway** running on Hostinger VPS (82.25.77.221)
- **Rainmaker** = the OpenClaw agent (personality, memory, skills)
- **Workspace** shared between you and Rainmaker via inbox/outbox

Your job: Configure, maintain, and collaborate with OpenClaw.

---

## 🔑 ACCESS INFORMATION

### **SSH Access:**
```bash
ssh hostinger
# Connects to: root@82.25.77.221
```

### **OpenClaw Paths:**
```
/root/openclaw/                    # Source code (git repo)
/root/.openclaw/openclaw.json      # Main config
/root/.openclaw/workspace/         # Shared workspace
/root/.openclaw/logs/              # Gateway logs
```

### **Dashboard:**
```
# From Mac (via tunnel):
ssh -f -N -L 18789:127.0.0.1:18789 hostinger
# Then: http://localhost:18789/?token=51c8c0d43559c28bc7b5d79088bc788192dd617dcd5d5c2167d47d21b0eaa984
```

---

## 📬 INBOX/OUTBOX COMMUNICATION

### **How to send task to Rainmaker:**

```bash
# 1. Create task file locally
cat > /tmp/task-$(date +%s).md << 'EOF'
TASK: Your task title
FROM: claude-code
TO: rainmaker
PRIORITY: medium
TIMESTAMP: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
---

Task description here.
What you want Rainmaker to do.

EOF

# 2. Copy to VPS inbox
scp /tmp/task-*.md hostinger:/root/.openclaw/workspace/inbox/

# 3. Rainmaker will process on next heartbeat
```

### **How to check for responses:**

```bash
# Check outbox
ssh hostinger "ls -la /root/.openclaw/workspace/outbox/"

# Read response
ssh hostinger "cat /root/.openclaw/workspace/outbox/response-*.md"
```

### **Heartbeat frequency:**
- Rainmaker checks inbox every heartbeat
- Check `HEARTBEAT.md` for current config
- Current: checks inbox/outbox

---

## 🎛️ CONFIGURING OPENCLAW

### **Main Config File:**

```bash
# Edit config
ssh hostinger "vim /root/.openclaw/openclaw.json"

# Or edit locally and push:
scp /tmp/openclaw.json hostinger:/root/.openclaw/openclaw.json

# Restart gateway to apply:
ssh hostinger "systemctl --user restart openclaw-gateway"
```

### **Key Config Sections:**

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "ollama/qwen2.5:7b",
        "fallbacks": ["anthropic/claude-opus-4-5"]
      }
    }
  },
  "channels": {
    "whatsapp": {
      "allowFrom": ["+555499628402"]
    }
  }
}
```

---

## 🧩 ADDING SKILLS

### **1. List available skills:**

```bash
ssh hostinger "cd /root/openclaw && pnpm openclaw skills list"
```

### **2. Install skill from ClawHub:**

```bash
ssh hostinger "cd /root/openclaw && npx clawhub install <skill-name>"
```

### **3. Create custom skill:**

```bash
# Create skill directory
ssh hostinger "mkdir -p /root/openclaw/skills/my-skill"

# Create SKILL.md
cat > /tmp/SKILL.md << 'EOF'
---
name: my-skill
description: What this skill does
version: 1.0.0
author: Your name
---

# My Skill

Implementation details...
EOF

scp /tmp/SKILL.md hostinger:/root/openclaw/skills/my-skill/

# Restart gateway
ssh hostinger "systemctl --user restart openclaw-gateway"
```

---

## ⏰ CRON JOBS

### **List current cron jobs:**

```bash
ssh hostinger "cd /root/openclaw && pnpm openclaw cron list"
```

### **Add cron job:**

```bash
ssh hostinger "cd /root/openclaw && \
pnpm openclaw cron add \
  --name 'Daily Backup' \
  --cron '0 3 * * *' \
  --message 'Backup workspace to GCS'"
```

### **Current jobs:**
- Weekly Security Audit: Mondays 9 AM
- Environment Verification: Daily 6 AM

---

## 🧠 EDITING SOUL/MEMORY

### **Files you can edit:**

```
/root/.openclaw/workspace/
├── SOUL.md         → Rainmaker's personality
├── IDENTITY.md     → Name, emoji, vibe
├── MEMORY.md       → Long-term memory
├── USER.md         → Info about Leo
├── AGENTS.md       → Operating instructions
├── HEARTBEAT.md    → Heartbeat config
└── TOOLS.md        → Tool notes
```

### **How to edit:**

```bash
# Method 1: SSH + vim
ssh hostinger "vim /root/.openclaw/workspace/SOUL.md"

# Method 2: Edit locally, then push
vim /tmp/SOUL.md
scp /tmp/SOUL.md hostinger:/root/.openclaw/workspace/SOUL.md

# Changes take effect on next session
```

### **Important:**
- **SOUL.md** = personality, don't change lightly
- **MEMORY.md** = append only (don't delete history)
- **HEARTBEAT.md** = what Rainmaker checks automatically

---

## 🚀 DEPLOYING CHANGES

### **When you modify OpenClaw code:**

```bash
# 1. If you edited source locally:
git commit -am "Your changes"
git push

# 2. On VPS, pull changes:
ssh hostinger "cd /root/openclaw && git pull"

# 3. Rebuild if needed:
ssh hostinger "cd /root/openclaw && pnpm install && pnpm build"

# 4. Restart gateway:
ssh hostinger "systemctl --user restart openclaw-gateway"

# 5. Verify:
ssh hostinger "cd /root/openclaw && pnpm openclaw status"
```

---

## 🔍 DEBUGGING

### **Check gateway status:**

```bash
ssh hostinger "systemctl --user status openclaw-gateway"
```

### **View logs:**

```bash
# Live logs
ssh hostinger "tail -f /root/.openclaw/logs/*.log"

# Last 50 lines
ssh hostinger "tail -50 /root/.openclaw/logs/*.log"
```

### **Check if WhatsApp linked:**

```bash
ssh hostinger "cd /root/openclaw && pnpm openclaw status"
# Look for: WhatsApp: linked ✓
```

### **Restart gateway:**

```bash
ssh hostinger "systemctl --user restart openclaw-gateway"
```

### **Check Ollama models:**

```bash
ssh hostinger "ollama list"
```

---

## 💾 BACKUP/RESTORE

### **Backup workspace:**

```bash
# To local Mac:
rsync -avz hostinger:/root/.openclaw/workspace/ ~/backup/openclaw-workspace/

# To GCS:
ssh hostinger "gsutil -m rsync -r /root/.openclaw/workspace gs://elements-archive-2026/openclaw-workspace/\$(date +%Y%m%d)/"
```

### **Restore workspace:**

```bash
# From local Mac:
rsync -avz ~/backup/openclaw-workspace/ hostinger:/root/.openclaw/workspace/

# From GCS:
ssh hostinger "gsutil -m rsync -r gs://elements-archive-2026/openclaw-workspace/20260203/ /root/.openclaw/workspace/"
```

---

## 📊 MONITORING

### **Key things to monitor:**

```bash
# 1. Gateway running?
ssh hostinger "systemctl --user is-active openclaw-gateway"

# 2. WhatsApp linked?
ssh hostinger "cd /root/openclaw && pnpm openclaw status | grep WhatsApp"

# 3. Disk space?
ssh hostinger "df -h | grep /dev/vda"

# 4. Memory usage?
ssh hostinger "free -h"

# 5. Recent errors?
ssh hostinger "tail -100 /root/.openclaw/logs/*.log | grep ERROR"
```

---

## 🎯 COMMON TASKS

### **Add new person to allowlist:**

```bash
# Edit config
ssh hostinger "cd /root/openclaw && \
cat /root/.openclaw/openclaw.json | \
jq '.channels.whatsapp.allowFrom += [\"+555499999999\"]' | \
tee /root/.openclaw/openclaw.json.new && \
mv /root/.openclaw/openclaw.json.new /root/.openclaw/openclaw.json"

# Restart
ssh hostinger "systemctl --user restart openclaw-gateway"
```

### **Change primary model:**

```bash
ssh hostinger "cd /root/openclaw && \
pnpm openclaw models set ollama/qwen2.5:32b"
```

### **Send message to Rainmaker (via inbox):**

```bash
echo "Test message from Claude" > /tmp/task-test.md
scp /tmp/task-test.md hostinger:/root/.openclaw/workspace/inbox/
```

---

## ⚠️ IMPORTANT RULES

### **DO:**
- ✅ Use inbox/outbox for async communication with Rainmaker
- ✅ Test changes on a copy first if critical
- ✅ Backup before major config changes
- ✅ Check logs after deploying
- ✅ Document what you changed (in git commit or notes)

### **DON'T:**
- ❌ Delete MEMORY.md history (append only)
- ❌ Change SOUL.md without user approval
- ❌ Push to production without testing
- ❌ Restart gateway during active user conversations
- ❌ Expose gateway token in logs or commits

---

## 🔗 USEFUL COMMANDS (Copy-Paste Ready)

```bash
# Quick status check
ssh hostinger "cd /root/openclaw && pnpm openclaw status"

# View inbox
ssh hostinger "ls -la /root/.openclaw/workspace/inbox/"

# View outbox
ssh hostinger "ls -la /root/.openclaw/workspace/outbox/"

# Live logs
ssh hostinger "tail -f /root/.openclaw/logs/*.log"

# Restart gateway
ssh hostinger "systemctl --user restart openclaw-gateway"

# Check Ollama
ssh hostinger "ollama list"

# Backup workspace
rsync -avz hostinger:/root/.openclaw/workspace/ ~/backup/openclaw-workspace-$(date +%Y%m%d)/
```

---

## 🧪 TESTING

### **Test workflow:**

```bash
# 1. Check connection
ssh hostinger "echo 'Connected!'"

# 2. Check gateway
ssh hostinger "systemctl --user status openclaw-gateway"

# 3. Send test task
echo "TEST: ping from Claude" > /tmp/test-$(date +%s).md
scp /tmp/test-*.md hostinger:/root/.openclaw/workspace/inbox/

# 4. Wait 1-2 minutes (heartbeat)

# 5. Check for response
ssh hostinger "ls -la /root/.openclaw/workspace/outbox/"
```

---

## 📚 LEARN MORE

- **OpenClaw Source:** `/root/openclaw/` (on VPS)
- **Docs:** `/root/openclaw/docs/`
- **Skills:** `/root/openclaw/skills/`
- **Config reference:** `/root/.openclaw/openclaw.json`

---

## 🆘 EMERGENCY

### **If gateway is down:**

```bash
# 1. Check status
ssh hostinger "systemctl --user status openclaw-gateway"

# 2. Check logs for errors
ssh hostinger "tail -100 /root/.openclaw/logs/*.log"

# 3. Try restart
ssh hostinger "systemctl --user restart openclaw-gateway"

# 4. If still broken, check Ollama
ssh hostinger "ollama list"

# 5. Last resort: reboot VPS
# Via Hostinger panel: https://hpanel.hostinger.com/vps
```

---

**This is your handbook. Update it as you learn more about the system.**

**Last updated:** 2026-02-03
**Maintained by:** Claude Code + Leo
