# Triplice Infrastructure Gaps and Actions

## Purpose
Translate the architecture map into concrete fixes and verification steps. This is the implementation checklist.

## Critical Gaps (Verified)
- Ollama auth missing for the agent, causing fallback failures.
- Model priority inverted relative to cost plan (Claude primary, Ollama unusable).
- Mac to VPS sync bridge not implemented.
- GCS cron backup not confirmed as active.

## P0 Actions (Fix Now)
1. Fix Ollama auth for the agent.
Verify file exists: `ssh hostinger "ls -l /root/.openclaw/agents/main/agent/auth-profiles.json"`
Copy from main profile if missing: `ssh hostinger "cp /root/.openclaw/agents/main/auth-profiles.json /root/.openclaw/agents/main/agent/auth-profiles.json"`

2. Invert model priority so Ollama is primary.
Check current model: `ssh hostinger "cat /root/.openclaw/openclaw.json | jq .agents.defaults.model"`
Update primary to Ollama and set Claude as fallback.
Restart gateway: `ssh hostinger "systemctl --user restart openclaw-gateway"`

3. Validate a real response path end to end.
Send test WhatsApp message.
Check logs: `ssh hostinger "tail -n 200 /root/.openclaw/logs/*.log"`

## P1 Actions (This Week)
1. Confirm GCS cron is active.
Check crontab: `ssh hostinger "crontab -l | grep gsutil"`
If missing, add the daily backup cron.

2. Verify workspace backups actually produce new GCS objects.
List newest objects: `ssh hostinger "gsutil ls -l gs://elements-archive-2026/openclaw-workspace/ | tail -n 20"`

3. Update documentation to reflect reality.
Align `START_HERE.md` and `ARQUITETURA_REAL.md` with current model routing.

## P2 Actions (Near Term)
1. Decide on Mac to VPS sync strategy.
Option A: keep manual SCP.
Option B: lsyncd + rsync.
Option C: git based workflows only.

2. If adopting sync, define exclusion rules.
Exclude secrets and private local data.
Document allowed paths explicitly.

## Risk Notes
- Rate limits on Claude will hard-fail if Ollama remains unusable.
- Any mismatch between docs and reality causes delayed incident response.
- If GCS backups are not automated, recovery RTO becomes manual and slow.

## Validation Checklist
- `openclaw-gateway` running and stable.
- Ollama requests succeed without auth errors.
- WhatsApp message gets a response.
- GCS backups appear daily.
