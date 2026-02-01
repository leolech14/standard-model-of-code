# AI Billing Map

**Who gets paid when you use what**
**Updated:** 2026-01-30

---

## Visual Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           YOUR AI SPENDING                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌───────────────┐          ┌───────────────┐
│  SUBSCRIPTIONS │         │  PAY-PER-USE  │          │     FREE      │
│   (Monthly)    │         │   (Tokens)    │          │    (Limits)   │
└───────────────┘         └───────────────┘          └───────────────┘
        │                           │                           │
        ├── Z.ai ($3-15/mo)         ├── Anthropic (2 accounts!) ├── Gemini (free tier)
        ├── ElevenLabs (sub)        ├── OpenRouter              ├── HuggingFace Hub
        ├── Perplexity (sub?)       ├── Cerebras ($33 credit)   └── Groq (free tier)
        └── Tavus (sub)             ├── OpenAI
                                    ├── Replicate
                                    └── RunPod (GPU time)
```

---

## CRITICAL: You Have TWO Anthropic Accounts

| Command | API Key | Account | Billing |
|---------|---------|---------|---------|
| `claude` (default) | `sk-ant-api03-JAwd1...` (Doppler) | Account #1 | Pay-per-token |
| `claude-1m` | `sk-ant-api03-wzM10...` (hardcoded .zshrc) | Account #2 | Pay-per-token |

**These bill to DIFFERENT accounts.** Check both dashboards:
- https://console.anthropic.com (log in with each account)

---

## Detailed Billing Breakdown

### 1. SUBSCRIPTIONS (Fixed Monthly)

| Service | Command/Use | Cost | Billing Portal |
|---------|-------------|------|----------------|
| **Z.ai** | `zai`, `claude-zai` | $3/mo (Lite) or $15/mo (Pro) | https://z.ai/account |
| **ElevenLabs** | TTS API | Varies by tier | https://elevenlabs.io/subscription |
| **Perplexity** | Research MCP | Pro: $20/mo (or API pay-per-use) | https://perplexity.ai/settings |
| **Tavus** | Video AI | Enterprise pricing | https://tavus.io |

### 2. PAY-PER-USE (Token/Request Based)

| Service | Command/Use | Pricing | Billing Portal |
|---------|-------------|---------|----------------|
| **Anthropic #1** | `claude` (default) | ~$15/M input, ~$75/M output (Opus) | https://console.anthropic.com |
| **Anthropic #2** | `claude-1m` | Same rates, DIFFERENT account | https://console.anthropic.com |
| **OpenRouter** | `openrouter` switch | Varies by model (markup ~10-20%) | https://openrouter.ai/account |
| **Cerebras** | `cerebras` switch | $33 credit, then pay-per-token | https://cloud.cerebras.ai |
| **OpenAI** | Direct API | ~$5/M input, ~$15/M output (GPT-4o) | https://platform.openai.com/usage |
| **Replicate** | Image/model runs | Per-prediction (~$0.001-0.05/run) | https://replicate.com/account |
| **RunPod** | GPU compute | Per-second GPU time | https://runpod.io/console |
| **Vertex AI** | Google Cloud AI | GCP billing | https://console.cloud.google.com |

### 3. FREE TIERS (With Limits)

| Service | What's Free | Limits |
|---------|-------------|--------|
| **Gemini** | API access | Generous free tier |
| **HuggingFace** | Hub, Spaces, some inference | Rate limited |
| **Groq** | API (if you sign up) | Daily token limits |
| **Perplexity** | Basic queries | Limited/day |

---

## Cost Per Command

| Command | Bills To | Estimated Cost |
|---------|----------|----------------|
| `claude` | Anthropic Account #1 | ~$0.01-0.10/query |
| `claude-1m` | Anthropic Account #2 | ~$0.01-0.10/query |
| `zai` | Z.ai subscription | Included in $3-15/mo |
| `source...cerebras && claude` | Cerebras | From $33 credit |
| `source...openrouter && claude` | OpenRouter | ~$0.001-0.05/query |
| Perplexity MCP | Perplexity | Subscription or API |
| Browser MCP | Free | $0 |
| HF MCP | Free | $0 (Hub search) |

---

## Monthly Cost Estimation

### Minimum (Budget Mode)
```
Z.ai subscription:     $3/mo
Everything else:       Pay-per-use (can be $0 if careful)
─────────────────────────────
TOTAL:                 ~$3/mo
```

### Typical Developer
```
Z.ai subscription:     $15/mo  (Pro)
Anthropic usage:       $20-50/mo
OpenRouter/Cerebras:   $10-20/mo
ElevenLabs:            $5-22/mo
─────────────────────────────
TOTAL:                 ~$50-100/mo
```

### Heavy Usage
```
Z.ai subscription:     $15/mo
Anthropic usage:       $100-300/mo
Cerebras:              $50-100/mo
OpenRouter:            $20-50/mo
Replicate:             $10-50/mo
ElevenLabs:            $22-99/mo
─────────────────────────────
TOTAL:                 ~$200-600/mo
```

---

## Billing Portals Quick Links

| Service | Dashboard |
|---------|-----------|
| Anthropic | https://console.anthropic.com |
| Z.ai | https://z.ai/account |
| OpenRouter | https://openrouter.ai/account |
| Cerebras | https://cloud.cerebras.ai |
| OpenAI | https://platform.openai.com/usage |
| Replicate | https://replicate.com/account |
| HuggingFace | https://huggingface.co/settings/billing |
| ElevenLabs | https://elevenlabs.io/subscription |
| Perplexity | https://perplexity.ai/settings |
| RunPod | https://runpod.io/console |
| Google Cloud | https://console.cloud.google.com/billing |

---

## Action Items

### Consolidate Anthropic?
You have 2 separate Anthropic API keys billing to different accounts. Consider:
1. Check both dashboards for usage
2. Decide if you need both
3. Maybe consolidate to one account

### Check Subscription Status
```bash
# Are these active subscriptions or just API keys?
# - Z.ai: Check https://z.ai/account
# - ElevenLabs: Check https://elevenlabs.io/subscription
# - Perplexity: Check https://perplexity.ai/settings
```

### Set Spending Alerts
Most services allow budget alerts:
- Anthropic: Console → Usage → Set limit
- OpenRouter: Account → Billing → Set limit
- OpenAI: Platform → Usage → Set limit

---

## Payment Methods by Service

| Service | Accepts |
|---------|---------|
| Anthropic | Credit card |
| Z.ai | Credit card |
| OpenRouter | Credit card, crypto |
| Cerebras | Credit card |
| OpenAI | Credit card |
| Replicate | Credit card |
| HuggingFace | Credit card |
| Google Cloud | Credit card, invoicing |
| ElevenLabs | Credit card |
