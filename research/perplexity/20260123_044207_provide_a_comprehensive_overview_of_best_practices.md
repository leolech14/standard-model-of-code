# Perplexity Research: Provide a comprehensive overview of best practices for distributed task coordination and locking in ...

> **Date:** 2026-01-23 04:42:07
> **Model:** sonar-pro
> **Source:** MCP Server (auto-saved)
> **Raw JSON:** `raw/20260123_044207_provide_a_comprehensive_overview_of_best_practices.json`

---

## Query

Provide a comprehensive overview of best practices for distributed task coordination and locking in a multi-agent system where agents are stateless workers operating on a shared file system.

Context:
- Agents are shell-script-based and can be restarted, losing in-memory state (amnesiac property).
- A file-based locking mechanism is used, where claiming a task is an atomic 'mv' command.
- The system needs to be resilient to race conditions, especially after an agent restores its session and might have stale knowledge of a task it previously held.

Questions to answer:
1. What are the standard design patterns for ensuring only one agent works on a task at a time in this environment (e.g., leader election, distributed locks)? How does an atomic 'mv' fit into these patterns?
2. Compare the robustness of two approaches for state synchronization after an agent restores:
   a) Storing claim status in a context summary that is restored with the agent.
   b) Forcing the agent to always perform a live check-and-claim against the file system after restore.
3. What are the pitfalls of file-based locking (e.g., stale locks)?
4. Propose a "defense in depth" strategy, including mechanisms like heartbeats (timestamp updates) and stale lock detection (reapers/janitors), to make the system fault-tolerant.
5. Provide code examples or pseudo-code in shell script for implementing an idempotent and robust task claiming function.

---

## Response

### 1. Standard Design Patterns for Exclusive Task Coordination

In distributed task queues for stateless workers, common patterns ensure mutual exclusion via **distributed locks** or **leader election**, where workers atomically claim tasks to prevent concurrent execution. Workers monitor a shared queue (e.g., file directory) and use atomic operations to transition tasks from "available" to "claimed" states, enabling parallelism while handling failures through retries and persistence.[1] Atomic `mv` fits as a **file-based distributed lock**: renaming a task file (e.g., `task-123.available` to `task-123.claimed-by-$HOSTNAME`) is atomic on shared filesystems like NFS, serving as a lightweight lock without external services like ZooKeeper or Redis, ideal for shell-script agents.[1]

### 2. Robustness Comparison: State Synchronization After Restore

| Approach | Description | Robustness Pros | Robustness Cons |
|----------|-------------|-----------------|-----------------|
| **a) Context Summary Restore** | Agent restores prior claim from a summary file (e.g., JSON with task IDs it "owns"). | Faster startup; reduces filesystem I/O. | Vulnerable to **stale state**: post-crash, another agent may have claimed/released the task via live `mv`, leading to duplicate work or conflicts if summary lags. |
| **b) Live Check-and-Claim** | Agent discards in-memory/session state on restore, always re-running atomic `mv` to re-claim. | Highly robust; **always verifies current filesystem truth**, eliminating staleness and race conditions even after restarts. | Minor overhead from repeated claims; potential thundering herd if many agents restore simultaneously. |

**Live check-and-claim (b) is more robust** for amnesiac agents, as it enforces **idempotency** and current-state consensus without assuming persisted knowledge survives restarts or external changes.[1]

### 3. Pitfalls of File-Based Locking

File-based locking on shared filesystems is simple but prone to issues:
- **Stale locks**: Crashed agents leave "claimed" files indefinitely; no auto-release without timeouts.[1]
- **Race conditions on restore**: Agents with stale session state may assume ownership without re-checking.
- **Filesystem inconsistencies**: NFS stale file handles, lease expirations, or network partitions cause `mv` failures or phantom locks.
- **No fencing**: Multiple agents might see the same file state briefly during propagation delays.
- **Scalability limits**: Directory scans for available tasks become O(n) bottlenecks at high task volumes; no built-in priorities or retries.[1]
- **No durability guarantees**: Filesystem crashes lose queues unless replicated.

### 4. Defense-in-Depth Strategy for Fault Tolerance

Layer multiple mechanisms for resilience:
- **Atomic Claiming (Base Layer)**: Use `mv` for instantaneous mutual exclusion.
- **Heartbeats (Liveness)**: On claim, create/update a **lockfile** with timestamp (e.g., `task-123.lock` containing `claim_time=$(date +%s); hostname`). Worker periodically (e.g., every 30s) touches it via `echo $(( $(date +%s) )) > task-123.lock` during processing.[1]
- **Stale Lock Detection (Cleanup Layer)**: Run **janitor/reaper** cron jobs (separate from workers) every 1-5 minutes: for each `.claimed` or `.lock` file, check if `age > max_lease (e.g., 10min)` and hostname pingable; if stale, `mv back to .available` or delete lock.[1]
- **Idempotent Double-Check**: Before processing, verify `test -f task-123.lock && grep $(hostname) task-123.lock`.
- **Leases with Fencing**: Embed sequence numbers or UUIDs in filenames; reject non-monotonic claims.
- **Monitoring**: Log claim attempts/failures; alert on reaper activity > threshold.[1]
- **Backpressure**: If queue > threshold, pause producers.

This ensures **progress** (no permanent lockouts) and **safety** (no duplicates) even with crashes, partitions, or high churn.

### 5. Shell Script Pseudo-Code: Idempotent Task Claiming Function

```bash
#!/bin/bash

# Config
MAX_LEASE_SECS=600  # 10min
LOCK_DIR="/shared/tasks"
REAPER_INTERVAL=60  # For heartbeat

# Idempotent claim: always live-check filesystem, heartbeat-aware
claim_task() {
    local task_id="$1"
    local available="$LOCK_DIR/task-${task_id}.available"
    local claimed="$LOCK_DIR/task-${task_id}.claimed"
    local lockfile="$LOCK_DIR/task-${task_id}.lock"

    # Atomic claim via mv (fails if already moved)
    if ! mv "$available" "$claimed" 2>/dev/null; then
        echo "Claim failed: task ${task_id} unavailable or claimed" >&2
        return 1
    fi

    # Write initial lock with claim time + host (fencing)
    echo "$(date +%s) $(hostname)" > "$lockfile"

    echo "Claimed task ${task_id}" >&2
    return 0
}

# Heartbeat: touch lock during processing (call in loop)
heartbeat() {
    local task_id="$1"
    local lockfile="$LOCK_DIR/task-${task_id}.lock"
    echo "$(date +%s) $(hostname)" > "$lockfile"
}

# Release on completion/failure
release_task() {
    local task_id="$1"
    local claimed="$LOCK_DIR/task-${task_id}.claimed"
    local lockfile="$LOCK_DIR/task-${task_id}.lock"
    rm -f "$claimed" "$lockfile"
}

# Live verify before processing (defense vs. races)
verify_ownership() {
    local task_id="$1"
    local lockfile="$LOCK_DIR/task-${task_id}.lock"
    if [ ! -f "$lockfile" ]; then
        echo "No lock for ${task_id}" >&2
        return 1
    fi
    if ! grep -q "$(hostname)" "$lockfile"; then
        echo "Not owner of ${task_id}" >&2
        return 1
    fi
    local age=$(( $(date +%s) - $(cut -d' ' -f1 "$lockfile") ))
    if [ $age -gt $MAX_LEASE_SECS ]; then
        echo "Lease expired for ${task_id}" >&2
        return 1
    fi
    return 0
}

# Usage in worker loop (post-restore: ALWAYS call claim_task, ignore "memory")
process_loop() {
    for task_id in $(ls $LOCK_DIR/*.available | sed 's|.*/task-\([0-9]*\)\.available|\1|'); do
        if claim_task "$task_id" && verify_ownership "$task_id"; then
            # Process...
            while verify_ownership "$task_id"; do
                # Do work
                sleep 30 && heartbeat "$task_id"  # Or in work loop
            done
            release_task "$task_id"
        fi
    done
}

# Separate reaper script (cron: */1 * * * *)
reap_stale() {
    for lockfile in $LOCK_DIR/*.lock; do
        task_id=$(basename "$lockfile" .lock | sed 's|task-||')
        claimed="$LOCK_DIR/task-${task_id}.claimed"
        age=$(( $(date +%s) - $(cut -d' ' -f1 "$lockfile") ))
        host=$(cut -d' ' -f2 "$lockfile")
        if [ $age -gt $MAX_LEASE_SECS ] || ! ping -c1 -W1 "$host" >/dev/null 2>&1; then
            mv "$claimed" "$LOCK_DIR/task-${task_id}.available" 2>/dev/null || rm -f "$claimed"
            rm -f "$lockfile"
        fi
    done
}
```

This implementation is **restart-safe** (no state reliance), handles staleness via reaper, and scales via simple cron. Test on NFS for atomicity.[1]

---

## Citations

1. https://www.geeksforgeeks.org/system-design/distributed-task-queue-distributed-systems/
2. https://arxiv.org/html/2512.11643v1
3. https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/web-queue-worker

---

## Usage Stats

- Prompt tokens: 294
- Completion tokens: 1736
- Total tokens: 2030
