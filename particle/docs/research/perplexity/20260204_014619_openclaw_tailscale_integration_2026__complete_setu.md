# Perplexity Research: OpenClaw Tailscale integration 2026: complete setup guide, Tailscale Serve vs Funnel configuration, ...

> **Date:** 2026-02-04 01:46:19
> **Model:** sonar-pro
> **Query Length:** 312 chars

---

## Query

OpenClaw Tailscale integration 2026: complete setup guide, Tailscale Serve vs Funnel configuration, authentication methods (token vs Tailscale SSO), WebSocket pairing required error solutions, controlUi auth settings, gateway.auth.mode options, production Tailscale deployment patterns, community troubleshooting

---

## Response

### OpenClaw Tailscale Integration Setup Guide

OpenClaw integrates with Tailscale via auth keys to join a tailnet, securing access to the gateway (port 18789) and control UI (port 18791) without public exposure, while retaining SSH (port 22) as a fallback.[1] Use Pulumi for automated deployment on AWS or Hetzner, installing Tailscale post-dependencies and enabling Tailscale SSH for keyless access.[1]

#### Complete Setup Steps
1. **Generate Tailscale Auth Key**: In Tailscale Admin Console, generate a reusable auth key and store it securely in Pulumi ESC (e.g., `Pulumi.dev.yaml` with `environment: - <your-org>/openclaw-secrets`).[1]
2. **Configure Pulumi Program**: Provide tailnet name (e.g., `tailxxxxx.ts.net` from DNS section) and auth key; program removes public gateway/UI ports, installs Tailscale, joins tailnet, and runs `openclaw onboard --non-interactive` via cloud-init.[1]
3. **Deploy**: Run `pulumi up`; outputs include `tailscaleUrlWithToken` (MagicDNS hostname + token) for direct web UI access.[1]
4. **Access UI**: Paste `pulumi stack output tailscaleUrlWithToken` into browser; configure integrations (e.g., WhatsApp, Discord) from there.[1]
5. **Verify**: Check Tailscale Machines tab for device; SSH via `ssh ubuntu@<tailscale-ip>` or `systemctl --user status openclaw-gateway`.[1]

**Production Tips**: Rotate auth keys regularly, monitor admin console for unauthorized devices, use Pulumi ESC for secrets, and consider removing SSH fallback post-verification for zero public ports.[1]

#### Tailscale Serve vs Funnel Configuration
Search results lack direct OpenClaw-specific comparisons; Serve exposes services to tailnet only, while Funnel exposes to the internet via HTTPS with Tailscale auth (both post-2025 updates).[4] For OpenClaw, use auth key integration over Serve/Funnel to auto-join tailnet without port exposure.[1]

#### Authentication Methods: Token vs Tailscale SSO
- **Token (Auth Key)**: Preferred for automation; one-time reusable key joins device to tailnet during provisioning, embeds in `tailscaleUrlWithToken` for UI access.[1]
- **Tailscale SSO**: Not detailed for OpenClaw; general device approval via admin console (Machines tab, approve pending devices) or QR code login if org requires it.[2] Token is simpler for headless deploys vs SSO's interactive approval.[1][2]

#### WebSocket Pairing Required Error Solutions
Set `controlUi.allowInsecureAuth` and `trustedProxies` in OpenClaw config to bypass pairing when accessed via Tailscale (assumes Tailscale encryption).[1] If error persists, SSH troubleshoot gateway status or re-run onboarding.[1]

#### controlUi Auth Settings and gateway.auth.mode Options
- **controlUi**: Use `controlUi.allowInsecureAuth` for Tailscale-only access to skip device pairing.[1]
- **gateway.auth.mode**: Configured via `openclaw onboard` flags in cloud-init; results imply token-based auth for secure Tailscale URLs, no explicit mode options listed.[1]

#### Production Tailscale Deployment Patterns
- **IaC with Pulumi**: Auto-provision VM, install Tailscale post-deps, join tailnet, secure ports; scales to AWS/Hetzner.[1]
- **Fallbacks**: Keep SSH public initially, enable Tailscale SSH, monitor/rotate keys.[1]
- **Zero-Trust**: Tailscale mesh VPN encrypts API keys in transit, reduces attack surface to SSH only.[1]
- **Device Management**: Approve via admin console if org policy enabled; use QR for manual adds.[2]

#### Community Troubleshooting
- **Access Issues**: Verify tailnet DNS/MagicDNS in admin console, check machine status, use `tailscaleUrlWithToken`.[1]
- **Device Approval**: If "needs approval" badge, approve in Machines tab (requires admin role).[2]
- **Gateway Down**: `systemctl --user status openclaw-gateway` via Tailscale SSH.[1]
- **General**: Pulumi Slack/GitHub Discussions for IaC issues; Tailscale admin console for network problems.[1] No 2026-specific OpenClaw v2026.1 changes detailed beyond security updates.[5][8]

---

## Citations

1. https://www.pulumi.com/blog/deploy-openclaw-aws-hetzner/
2. https://www.youtube.com/watch?v=cpXRJwZYPjM
3. https://www.youtube.com/watch?v=CGceyY70cRE
4. https://tailscale.com/blog/january-26-product-update
5. https://www.nxcode.io/resources/news/openclaw-complete-guide-2026
6. https://o-mega.ai/articles/openclaw-creating-the-ai-agent-workforce-ultimate-guide-2026
7. https://www.eesel.ai/blog/clawd-bot-telegram-integration
8. https://aicybr.com/blog/openclaw-guide

---

## Usage Stats

- Input tokens: 60
- Output tokens: 964
