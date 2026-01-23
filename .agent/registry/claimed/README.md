# Claimed Tasks Directory

> Atomic task reservation using filesystem operations.

## How It Works

When an agent claims a task, the task file is **moved** (not copied) from `active/` to `claimed/`:

```bash
# Atomic claim - exactly one agent wins on APFS
mv ../active/TASK-XXX.yaml ./$(date +%s)_${AGENT_ID}_TASK-XXX.yaml
```

## Why `mv` Is Safe

On macOS APFS (and POSIX filesystems):
- `mv` (rename) is **atomic** - completes fully or not at all
- If two processes call `mv` on the same source simultaneously:
  - **Exactly one succeeds** (gets the file)
  - **The other fails** with `ENOENT` (file not found)
- No race conditions possible

## Filename Format

```
{timestamp}_{agent_id}_TASK-XXX.yaml
```

Example:
```
1705968000_claude-opus_TASK-001.yaml
```

## Stale Claim Detection

Claims older than 30 minutes without activity are considered stale:

```bash
# Find stale claims (>30 min old)
find . -name "*.yaml" -mmin +30
```

Stale claims can be:
1. Moved back to `active/` for retry
2. Moved to `archive/` if abandoned

## Agent Protocol

### Claiming a Task

```bash
cd .agent/registry
TASK_ID="TASK-001"
AGENT_ID="claude-opus"
TIMESTAMP=$(date +%s)

# Atomic claim attempt
if mv active/${TASK_ID}.yaml claimed/${TIMESTAMP}_${AGENT_ID}_${TASK_ID}.yaml 2>/dev/null; then
    echo "Claimed ${TASK_ID}"
else
    echo "Task already claimed or doesn't exist"
    exit 1
fi
```

### Releasing a Task (Success)

```bash
# Move to archive with COMPLETE status
mv claimed/*_TASK-001.yaml archive/COMPLETE_TASK-001.yaml
```

### Releasing a Task (Failure)

```bash
# Move back to active for retry
CLAIMED_FILE=$(ls claimed/*_TASK-001.yaml)
mv "$CLAIMED_FILE" active/TASK-001.yaml
```

## Source

- Perplexity research: `20260122_220947_quick_technical_questions_*.md`
- Confirmed: `mv` is atomic on APFS, exactly one process wins
