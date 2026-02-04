# Leveraging Existing AI Subscriptions

**Critical Context:** User pays $200-400/mo for Claude Code + ChatGPT subscriptions
**Goal:** Route OpenClaw through existing subscriptions, NOT additional API costs

---

## Current Subscription Inventory

| Service | Subscription | Monthly Cost | What It Includes |
|---------|-------------|--------------|------------------|
| **Claude Code** | Active | $20/mo? | CLI access, API credits, Sonnet/Opus |
| **ChatGPT** | Pro/Plus | $20-200/mo | Web unlimited, API credits? |
| **TOTAL** | | **$220-420/mo** | Already paying! |

**Problem:**
- Architecture doc assumed NEW API costs ($50-100/mo)
- But you're ALREADY paying for AI access
- Need to route through existing subscriptions

---

## What Your Subscriptions Include

### Claude Code (Current Session)

```bash
# Check your current API access
echo $ANTHROPIC_API_KEY

# Check usage/limits
# (Need to verify what's included)
```

**Likely Includes:**
- ✅ Anthropic API access
- ✅ Sonnet 4.5 (what we're using now)
- ✅ Opus 4.5 access
- ✅ Some monthly token limit

**Need to Verify:**
- How many tokens/month?
- Can same key be used from VPS?
- Rate limits?

---

### ChatGPT Pro/Plus

**Web Interface:**
- ✅ Unlimited GPT-4 usage (web only)
- ✅ DALL-E, browsing, code interpreter

**API Access:**
- ⚠️ Separate from subscription?
- Need to check if Pro includes API credits

---

## Architecture: Leveraging Subscriptions

### Option 1: Direct API Reuse (Recommended)

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Your Subscriptions                                        │
│   ├─ Claude Code ($20/mo) → Anthropic API key              │
│   └─ ChatGPT Pro ($200/mo) → OpenAI API key?               │
│                                                             │
│   Same API Keys Used By:                                    │
│   ├─ Claude Code CLI (Mac) ✅                               │
│   ├─ OpenClaw Gateway (VPS) ✅                              │
│   └─ n8n Workflows (VPS) ✅                                 │
│                                                             │
│   NO ADDITIONAL COST - Using what you already pay for      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Setup:**
```bash
# On Hostinger VPS
export ANTHROPIC_API_KEY="your-claude-code-key"
export OPENAI_API_KEY="your-chatgpt-key"

# Configure OpenClaw
cd /root/openclaw
pnpm openclaw config set ai.backends.anthropic.key $ANTHROPIC_API_KEY
pnpm openclaw config set ai.backends.openai.key $OPENAI_API_KEY
```

**Benefits:**
- ✅ Zero additional cost
- ✅ Same rate limits you already have
- ✅ Unified billing (already paying)

---

### Option 2: Web Automation (If No API Access)

If subscriptions don't include API access:

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   OpenClaw Gateway                                          │
│        ↓                                                    │
│   Puppeteer/Playwright                                      │
│        ↓                                                    │
│   claude.ai web interface (automated)                       │
│   chatgpt.com web interface (automated)                     │
│                                                             │
│   Uses your subscription login                              │
│   Sends queries via web                                     │
│   Scrapes responses                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Pros:**
- ✅ Uses unlimited web access
- ✅ No additional API costs

**Cons:**
- ❌ Slower (browser automation)
- ❌ Fragile (breaks if UI changes)
- ❌ More complex
- ❌ Rate limits still apply

**Not Recommended** unless API access unavailable

---

### Option 3: Hybrid Approach

```
Query arrives at OpenClaw
    ↓
Router decides:
    ├─ Complex reasoning → Claude Code API (subscription)
    ├─ Fast/simple → ChatGPT API (subscription)
    ├─ Code tasks → Ollama (FREE, local)
    └─ Research → Perplexity ($5/mo only)
```

**Cost Optimization:**
- Use FREE Ollama for 40% of queries (code, simple QA)
- Use YOUR subscriptions for 50% (complex tasks)
- Only pay Perplexity $5/mo for research
- **Total NEW cost: $5-10/mo** (down from $50-100)

---

## Revised Cost Structure

### Before (Assumed in Docs)

| Item | Cost |
|------|------|
| Hostinger VPS | $30/mo |
| 360dialog/WhatsApp | $0 |
| **Claude API** | **$20-50/mo** ❌ |
| **Cerebras API** | **$5-10/mo** ❌ |
| Perplexity API | $5/mo |
| **TOTAL** | **$60-95/mo** |

### After (Leveraging Subscriptions)

| Item | Cost | Notes |
|------|------|-------|
| Hostinger VPS | $30/mo | Same |
| 360dialog/WhatsApp | $0 | Same |
| **Claude Code subscription** | **$20/mo** | ✅ Already paying |
| **ChatGPT subscription** | **$200/mo** | ✅ Already paying |
| Perplexity API | $5/mo | New (research only) |
| **TOTAL NEW** | **$35/mo** | **Was $60-95!** |
| **TOTAL REAL** | **$255/mo** | Including subscriptions |

**Savings: $25-60/mo** by reusing subscriptions instead of duplicate API costs

---

## Action Plan: Verify & Configure

### Step 1: Verify Claude Code API Access

```bash
# On your Mac
echo $ANTHROPIC_API_KEY

# If empty, find it:
cat ~/.claude.json | grep -i api
# OR
cat ~/.config/claude/config.json | grep -i api

# Test it:
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 10,
    "messages": [{"role": "user", "content": "Hi"}]
  }'
```

**Expected:** Should work if you have API access

---

### Step 2: Check ChatGPT API Access

```bash
# Find your OpenAI key
# Usually at: https://platform.openai.com/api-keys

# OR check if Pro includes credits:
# https://platform.openai.com/account/usage

# Test it:
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer YOUR_OPENAI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hi"}],
    "max_tokens": 10
  }'
```

---

### Step 3: Configure OpenClaw with Your Keys

```bash
# SSH to Hostinger VPS
ssh hostinger

# Set environment variables
cd /root/openclaw

# Option A: Via environment (temporary)
export ANTHROPIC_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"

# Option B: Via Doppler (recommended)
doppler secrets set ANTHROPIC_API_KEY
doppler secrets set OPENAI_API_KEY

# Option C: Via OpenClaw config
pnpm openclaw config set ai.anthropic.apiKey "your-key"
pnpm openclaw config set ai.openai.apiKey "your-key"

# Restart gateway
pnpm openclaw gateway restart
```

---

### Step 4: Update Routing Logic

```javascript
// OpenClaw routing configuration
{
  "routing": {
    "default": "anthropic:claude-opus-4",  // Your subscription
    "rules": [
      {
        "if": "query.type === 'code'",
        "use": "ollama:codellama"  // Free local
      },
      {
        "if": "query.complexity === 'simple'",
        "use": "openai:gpt-4"  // Your subscription
      },
      {
        "if": "query.needsSearch",
        "use": "perplexity:sonar"  // Only paid add-on
      }
    ]
  }
}
```

---

## What Changes in the Architecture

### Updated AI Backend Strategy

| Query Type | Old Plan | New Plan | Cost |
|------------|----------|----------|------|
| **Complex reasoning** | Cerebras | Claude Opus (subscription) | $0 |
| **Fast simple** | Cerebras | ChatGPT (subscription) | $0 |
| **Code tasks** | Ollama | Ollama (local) | $0 |
| **Research** | Perplexity | Perplexity | $5/mo |

**Result: $5/mo instead of $50-100/mo**

---

### Revised Monthly Costs

```
INFRASTRUCTURE:
├─ Hostinger VPS KVM 8        $30/mo
├─ 360dialog WhatsApp         FREE
└─ GCS storage                ~$2/mo
                              ───────
                              $32/mo

AI SERVICES (Already Paying):
├─ Claude Code subscription   $20/mo ✅
├─ ChatGPT Pro                $200/mo ✅
└─ Perplexity API (NEW)       $5/mo
                              ───────
                              $225/mo

TOTAL:                        $257/mo
NEW COSTS ONLY:               $37/mo  (VPS + storage + Perplexity)
```

**vs original plan of $110-205/mo in NEW costs**
**Savings: $73-168/mo** 🎉

---

## Rate Limits to Monitor

### Claude Code Subscription

**Need to verify:**
- Tokens per day?
- Requests per minute?
- Opus vs Sonnet limits?

**Strategy if hitting limits:**
- Use Ollama for code (most queries)
- Reserve Claude for complex reasoning
- Monitor usage via Anthropic dashboard

---

### ChatGPT Pro

**Limits (typical):**
- ~40 messages per 3 hours (GPT-4)
- ~Unlimited GPT-3.5

**Strategy:**
- Use for fast simple queries
- Fallback to Ollama if rate limited
- Monitor via OpenAI dashboard

---

## Fallback Strategy

```
Query arrives
    ↓
Try: Your Claude subscription
    ├─ Success → Return
    └─ Rate limited → Try ChatGPT subscription
              ├─ Success → Return
              └─ Rate limited → Ollama (FREE local)
                        └─ Always works
```

**Guarantees:**
- ✅ Always have a working AI
- ✅ Use cheapest option first
- ✅ Graceful degradation

---

## Action Items

### Immediate (Next 10 minutes):

- [ ] Verify Claude Code API key exists
- [ ] Test Claude API call from Mac
- [ ] Check ChatGPT API access
- [ ] Store keys in Doppler

### Phase 1 (WhatsApp Setup):

- [ ] Configure OpenClaw with your API keys
- [ ] Test routing logic
- [ ] Verify no additional charges

### Phase 3 (Ollama Install):

- [ ] Install Ollama on VPS
- [ ] Download CodeLlama 34B
- [ ] Configure as primary for code tasks
- [ ] Measure cost savings

---

## Expected Savings Timeline

```
Month 1 (Setup):
├─ New costs: VPS ($30) + Perplexity ($5) = $35
└─ Using: Existing subscriptions ($220)
Total: $255/mo

Month 2 (Ollama added):
├─ Ollama handles 40% of queries
├─ Less stress on Claude/GPT rate limits
└─ Same total cost: $255/mo

Month 3+ (Optimized):
├─ Could potentially downgrade ChatGPT Pro → Plus
├─ Savings: $180/mo
└─ New total: $75/mo (if comfortable with limits)
```

---

## Key Principle Change

```
❌ OLD THINKING:
"Pay for separate API access on top of subscriptions"

✅ NEW THINKING:
"Route OpenClaw through existing subscriptions"

Result: Use what you already pay for!
```

---

**Last Updated:** 2026-02-03
**Status:** Action plan - verify API access next
**Expected Savings:** $73-168/mo by leveraging subscriptions
