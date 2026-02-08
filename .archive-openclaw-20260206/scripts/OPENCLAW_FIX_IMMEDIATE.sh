#!/bin/bash
# OpenClaw Critical Fix - Run this on Hostinger VPS
# Fixes: Ollama auth + Model priority inversion
# Time: ~5 minutes
# Impact: Makes bot actually work as intended

set -e

echo "=================================="
echo "OpenClaw Critical Fix"
echo "=================================="
echo ""

# Backup current config
echo "[1/5] Backing up current config..."
cp /root/.openclaw/openclaw.json /root/.openclaw/openclaw.json.backup-$(date +%Y%m%d-%H%M%S)
cp /root/.openclaw/agents/main/agent/auth-profiles.json /root/.openclaw/agents/main/agent/auth-profiles.json.backup-$(date +%Y%m%d-%H%M%S)
echo "✓ Backups created"

# Fix 1: Add Ollama auth profile
echo ""
echo "[2/5] Adding Ollama auth profile..."
cat > /tmp/auth-profiles-fixed.json << 'EOF'
{
  "version": 1,
  "profiles": {
    "anthropic:leo-lbldomain.com": {
      "type": "token",
      "provider": "anthropic",
      "token": "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"
    },
    "ollama:default": {
      "type": "local",
      "provider": "ollama",
      "baseUrl": "http://localhost:11434"
    }
  },
  "lastGood": {
    "anthropic": "anthropic:leo-lbldomain.com",
    "ollama": "ollama:default"
  }
}
EOF

cp /tmp/auth-profiles-fixed.json /root/.openclaw/agents/main/agent/auth-profiles.json
echo "✓ Ollama auth profile added"

# Fix 2: Reverse model priority
echo ""
echo "[3/5] Fixing model priority (Ollama PRIMARY, Claude fallback)..."
python3 << 'PYEOF'
import json

with open('/root/.openclaw/openclaw.json', 'r') as f:
    config = json.load(f)

# Fix model priority
config['agents']['defaults']['model'] = {
    "primary": "ollama/qwen2.5:32b",
    "fallbacks": [
        "ollama/qwen2.5:7b",
        "anthropic/claude-sonnet-4-5-20250929",
        "anthropic/claude-opus-4-5-20251101"
    ]
}

with open('/root/.openclaw/openclaw.json', 'w') as f:
    json.dump(config, f, indent=2)

print("✓ Model priority fixed: Ollama → Claude")
PYEOF

# Fix 3: Restart gateway
echo ""
echo "[4/5] Restarting OpenClaw gateway..."
systemctl --user restart openclaw-gateway
sleep 3
echo "✓ Gateway restarted"

# Fix 4: Verify
echo ""
echo "[5/5] Verifying status..."
systemctl --user is-active openclaw-gateway && echo "✓ Gateway is running" || echo "✗ Gateway failed to start"
ollama list | grep -q qwen2.5:32b && echo "✓ Ollama model available" || echo "✗ Ollama model missing"

echo ""
echo "=================================="
echo "Fix Complete!"
echo "=================================="
echo ""
echo "NEXT STEPS:"
echo "1. Send WhatsApp message to: +55 54 99681-6430"
echo "2. Expected: Response from Ollama (free)"
echo "3. Check logs: tail -f /root/.openclaw/logs/*.log"
echo ""
echo "If still failing, check:"
echo "  journalctl --user -u openclaw-gateway -n 50"
echo ""
