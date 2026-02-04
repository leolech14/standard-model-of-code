# Perplexity Research: OpenClaw WebSocket authentication 2026: how dashboard connects to gateway, token passing in WebSocke...

> **Date:** 2026-02-04 01:46:40
> **Model:** sonar-pro
> **Query Length:** 263 chars

---

## Query

OpenClaw WebSocket authentication 2026: how dashboard connects to gateway, token passing in WebSocket handshake, HTTPS vs WSS authentication, Tailscale proxy header authentication, secure remote access patterns without exposing tokens, production-grade auth setup

---

## Response

OpenClaw's dashboard (React-based frontend) connects to the gateway (Node.js/Python backend on `localhost:18789` by default) via WebSocket, parsing a `gatewayUrl` query parameter (e.g., `?gatewayUrl=ws://example.com`) and automatically establishing the connection while attaching the user's **authentication token** from LocalStorage during the handshake.[1][3][6]

This token-passing mechanism in the WebSocket handshake—typically as JSON like `{"type": "hello", "auth": {"token": "sk-test-12345..."}}`—enabled **CVE-2026-25253** (fixed in v2026.1.29), where malicious links hijacked connections to attacker servers, exfiltrating tokens for replay against the victim's gateway, leading to RCE.[1][2][3]

### HTTPS vs. WSS Authentication
- **WSS (WebSocket Secure)** is the secure protocol equivalent for WebSockets over TLS/HTTPS, encrypting handshakes and payloads to prevent token interception (unlike insecure `ws://`).[1]
- Authentication remains **token-based bearer auth** in both: the client sends the token in the initial frame post-handshake; no separate HTTPS auth layer is required, but gateway config enforces it (fail-closed by default).[1][4][5]
- Production setups mandate WSS with valid certificates; insecure `ws://` triggers warnings or blocks.[4][5]

### Tailscale Proxy Header Authentication
OpenClaw supports Tailscale (or VPNs like WireGuard) for secure remote access:
- Run gateway behind Tailscale; clients connect via Tailscale IPs/hostname (e.g., `wss://100.x.x.x:18789`).[4]
- Configure `gateway.trustedProxies` with Tailscale proxy IPs to trust **X-Forwarded-For** or **X-Real-IP** headers for IP-based local checks and pairing.[5]
- Enable `allowInsecureAuth: true` only on trusted Tailscale networks (removes crypto verification); otherwise, use pairing mode.[4]
- Proxy (e.g., nginx) must overwrite forwarded headers and block direct port access.[5]

### Secure Remote Access Patterns (No Token Exposure)
Avoid CVE-2026-25253-style leaks with these production-grade patterns (post-fix in v2026.1.29+):
- **TOFU + Origin Validation**: Patched frontend whitelists `gatewayUrl`, prompts user confirmation for untrusted origins, and halts auto-connect.[1]
- **Auth Modes** in `~/.config/openclaw/config.json`:[4]
  | Mode     | Description                          | Use Case                  | Security Level |
  |----------|--------------------------------------|---------------------------|----------------|
  | **token** | Bearer token in WS handshake        | Simple local/remote      | Medium        |
  | **password** | Password challenge-response        | Shared access            | Medium-High   |
  | **pairing** | Crypto device pairing (recommended) | Remote/multi-device      | High          |
- **mDNS Discovery** (Bonjour): Limited "lite" mode exposes only role/port (not CLI/SSH paths); disable via `OPENCLAW_DISABLE_BONJOUR=1`.[5]
- **Reverse Proxy Lockdown**: Nginx/Caddy → gateway; validate origins, enforce WSS, add external auth (e.g., OAuth proxy).[5]
- **VPN-Only Exposure**: Bind to loopback/Tailscale; never public ports. Onboard generates tokens; `openclaw status` verifies.[4]

### Production-Grade Auth Setup Template
```json
{
  "gateway": {
    "mode": "remote",
    "port": 18789,
    "bind": "tailscale-ip",
    "auth": {
      "mode": "pairing"
    },
    "trustedProxies": ["100.64.0.0/10"],  // Tailscale range[5]
    "controlUi": {
      "enabled": true,
      "allowInsecureAuth": false
    }
  }
}
```
Pair devices via `openclaw dashboard` (generates `?pairing=true` URL).[4] Update to **2026.1.29+**; audit with `openclaw security audit`.[3][5] Error 1008 (auth fail) diagnostics: check config mismatches, restart gateway.[4]

---

## Citations

1. https://www.penligent.ai/hackinglabs/cve-2026-25253-openclaw-bug-enables-one-click-remote-code-execution-via-malicious-link/
2. https://www.runzero.com/blog/openclaw/
3. https://cvefeed.io/vuln/detail/CVE-2026-25253
4. https://community.popupsmart.com/t/solved-openclaw-websocket-error-1008-complete-troubleshooting-guide/469
5. https://docs.openclaw.ai/gateway/security
6. https://www.thehackerwire.com/openclaw-client-side-websocket-token-leak-cve-2026-25253/
7. https://www.nxcode.io/resources/news/openclaw-complete-guide-2026

---

## Usage Stats

- Input tokens: 46
- Output tokens: 932
