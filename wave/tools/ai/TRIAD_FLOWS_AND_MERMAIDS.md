# Triplice Infrastructure Flows and Mermaids

## Purpose
Document the operational flows that connect MacBook, Hostinger VPS, and GCloud. This is a practical reference for debugging and implementation work.

## Control Plane and Config Flow

```mermaid
flowchart LR
  M[MacBook]
  C["/root/.openclaw/openclaw.json"]
  A["/root/.openclaw/agents/main/agent/auth-profiles.json"]
  G[openclaw-gateway.service]

  M -->|edit + scp| C
  M -->|copy auth profile| A
  C -->|restart| G
  A -->|restart| G
```

Notes
- Config is applied only after `systemctl --user restart openclaw-gateway`.
- If `auth-profiles.json` is missing for the agent, Ollama fails and fallback triggers.

## WhatsApp Message Flow (Observed Failure Path Included)

```mermaid
sequenceDiagram
  participant U as User (WhatsApp)
  participant WA as WhatsApp Cloud API
  participant GW as OpenClaw Gateway
  participant AG as Rainmaker Agent
  participant OL as Ollama
  participant CL as Claude API

  U->>WA: message
  WA->>GW: webhook
  GW->>AG: load session + context
  AG->>OL: inference (primary)
  alt Ollama auth missing
    OL-->>AG: auth error
    AG->>CL: fallback
  end
  AG-->>GW: response
  GW-->>WA: send
  WA-->>U: reply
```

## Data Lifecycle Flow (Hot, Warm, Cold)

```mermaid
flowchart LR
  M[MacBook hot data]
  V[Hostinger warm data]
  G[GCS cold archive]

  M -->|manual scp / git| V
  V -->|gsutil rsync| G
  G -->|restore gsutil| V
  V -->|scp restore| M
```

## Access Paths and Connectivity

```mermaid
flowchart LR
  M[MacBook]
  V[Hostinger VPS]
  TS[Tailscale mesh]
  TUN[SSH tunnel :18789]

  M -->|ssh| V
  M -->|tunnel| TUN --> V
  M --- TS
  V --- TS
```

## Observability Flow

```mermaid
flowchart LR
  GW[OpenClaw Gateway]
  LOGS["/root/.openclaw/logs"]
  DASH[Dashboard :18789]
  M[MacBook]

  GW --> LOGS
  GW --> DASH
  M -->|ssh tail -f| LOGS
  M -->|tunnel| DASH
```
