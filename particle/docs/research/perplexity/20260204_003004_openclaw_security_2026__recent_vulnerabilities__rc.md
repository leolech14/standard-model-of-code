# Perplexity Research: OpenClaw security 2026: recent vulnerabilities (RCE CVEs), skill malware detection, sandbox configur...

> **Date:** 2026-02-04 00:30:04
> **Model:** sonar-pro
> **Query Length:** 320 chars

---

## Query

OpenClaw security 2026: recent vulnerabilities (RCE CVEs), skill malware detection, sandbox configuration, credential storage best practices, network isolation, authentication methods, production security checklist, penetration testing findings, security researcher recommendations, zero-trust architecture for AI agents

---

## Response

**OpenClaw, an open-source local AI personal assistant (formerly Clawdbot/Moltbot), has recent high-severity RCE vulnerabilities including CVE-2026-25253 (CVSS 8.8, unauthenticated one-click RCE via WebSocket token exfiltration) and CVE-2026-24763 (authenticated command injection in Docker sandbox via PATH variable).** Both affect versions before 2026.1.29 (released January 30, 2026) and are patched in that update.[1][2][4][5]

### Recent RCE CVEs
- **CVE-2026-25253**: Remote unauthenticated attacker exploits unvalidated WebSocket origin and query string gatewayUrl in Control UI, exfiltrating auth tokens via malicious link or site. Attacker gains operator.admin access, disables sandbox/approvals, sets tools.exec.host to gateway for RCE. Exploitable even on loopback-only setups as browser bridges connection; milliseconds to compromise.[1][2][3][5][7][8]
- **CVE-2026-24763**: Authenticated command injection in Docker execution from unsafe PATH handling; attacker controls env vars to inject commands in container.[4]

Update immediately to 2026.1.29; runZero query `vendor:=OpenClaw product:=OpenClaw` detects vulnerable systems.[1]

### Skill Malware Detection and Sandbox Configuration
Sandbox relies on Docker but was bypassed in exploits by API config changes (e.g., setting exec.approvals.set to "off", tools.exec.host to "gateway"). Defenses target LLM prompt injection, not external token theft; researcher Mav Levin notes they fail to limit RCE blast radius.[2][3][4] No specific malware detection for skills mentioned; post-patch, validate WebSocket origins and env vars.[1][2]

### Credential Storage Best Practices
Tokens stored locally with operator.admin/operator.approvals scopes; exfiltrated via client-side JS on malicious pages. Avoid query-string trust; use validated, short-lived tokens without privileged scopes for UI. Steinberger advisory: auto-connects send tokens without validation.[2]

### Network Isolation
Binds to loopback by default, but vuln exploits outbound browser WebSocket, bypassing isolation. Enforce strict origin checks on WebSocket; block non-localhost API access.[1][2][3]

### Authentication Methods
Relies on gateway tokens over WebSocket; vuln allows bypass via stolen tokens. Implement origin validation, token binding to origin, and least-privilege scopes.[2]

### Production Security Checklist
| Area | Recommendation |
|------|----------------|
| **Updates** | Upgrade to ≥2026.1.29; monitor for patches amid ongoing ecosystem issues.[1][3] |
| **Network** | Bind to loopback; validate WebSocket origins; firewall non-local ports.[1][2] |
| **Sandbox** | Audit Docker PATH handling; enable confirmations; restrict API config changes.[2][4] |
| **Auth/Creds** | Short-lived tokens; no query-string trust; scope minimization.[2] |
| **Monitoring** | Scan for OpenClaw assets; log WebSocket connects.[1] |
| **Ecosystem** | Avoid linking to exposed services like Moltbook (past DB leaks with API keys).[3] |

### Penetration Testing Findings
Researchers (Mav Levin/DepthFirst, Jamieson O'Reilly) disclosed rapid one-click chains: malicious page → token theft → sandbox disable → RCE. WebSocket hijacking ignores localhost; even safe configs compromised. O'Reilly joined project post-findings.[2][3]

### Security Researcher Recommendations
Levin: Sandbox limits ineffective against token attacks; rethink API safety management.[2] O'Reilly: Patch quickly, contribute findings; watch adjacent projects like Moltbook for misconfigs.[3] General: Treat as high-risk in business envs due to privileged host control.[6]

### Zero-Trust Architecture for AI Agents
No direct OpenClaw zero-trust guidance in results, but apply principles: assume breach (validate all origins/tokens), micro-segment (loopback + API gates), least-privilege (narrow scopes, no admin UI tokens), continuous verification (audit logs, no persistent creds). Levin implies current arch trusts UI/gateway excessively.[2][3] Ecosystem holes (e.g., Moltbook) underscore isolating agents from external nets.[3]

---

## Citations

1. https://www.runzero.com/blog/openclaw/
2. https://thehackernews.com/2026/02/openclaw-bug-enables-one-click-remote.html
3. https://www.theregister.com/2026/02/02/openclaw_security_issues/
4. https://cvefeed.io/vuln/detail/CVE-2026-24763
5. https://nvd.nist.gov/vuln/detail/CVE-2026-25253
6. https://www.darkreading.com/application-security/openclaw-ai-runs-wild-business-environments
7. https://www.tenable.com/plugins/pipeline/issues/211050
8. https://socradar.io/blog/cve-2026-25253-rce-openclaw-auth-token/

---

## Usage Stats

- Input tokens: 53
- Output tokens: 916
