#!/usr/bin/env python3
"""
Cerebras Request Queue
======================
Centralized queue to prevent rate limit chaos from multiple agents.

PROBLEM:
- Multiple Claude sessions hitting Cerebras simultaneously
- 7 req/sec limit shared across ALL consumers
- No coordination = 429 errors everywhere

SOLUTION:
- File-based queue with lock
- First-come-first-served
- Rate limiting at queue level (not per-consumer)
- Automatic backoff on 429

Usage:
    # Submit a request to the queue
    python cerebras_queue.py submit "What is 2+2?"

    # Process the queue (run in background)
    python cerebras_queue.py worker

    # Check queue status
    python cerebras_queue.py status
"""

import os
import sys
import json
import time
import fcntl
import argparse
import requests
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
import uuid
import hashlib

# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
QUEUE_DIR = PROJECT_ROOT / "context-management" / "data" / "cerebras_queue"
QUEUE_DIR.mkdir(parents=True, exist_ok=True)

QUEUE_FILE = QUEUE_DIR / "queue.json"
RESULTS_DIR = QUEUE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

LOCK_FILE = QUEUE_DIR / ".queue.lock"

# Rate limiting - conservative to allow headroom
REQUESTS_PER_SECOND = 5  # Below 7/sec limit
MIN_INTERVAL = 1.0 / REQUESTS_PER_SECOND

CEREBRAS_API_URL = "https://api.cerebras.ai/v1/chat/completions"
CEREBRAS_MODEL = os.getenv("CEREBRAS_MODEL", "llama-3.3-70b")


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class QueueItem:
    """A single queued request."""
    id: str
    prompt: str
    system: str = ""
    max_tokens: int = 1000
    submitted_at: str = ""
    status: str = "pending"  # pending, processing, complete, failed
    result: str = ""
    error: str = ""
    completed_at: str = ""
    consumer: str = ""  # Who submitted this


# =============================================================================
# QUEUE OPERATIONS
# =============================================================================

class QueueLock:
    """Context manager for queue locking."""
    def __init__(self):
        self.lock_fd = None

    def __enter__(self):
        self.lock_fd = open(LOCK_FILE, 'w')
        fcntl.flock(self.lock_fd, fcntl.LOCK_EX)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock_fd:
            fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
            self.lock_fd.close()
        return False


def acquire_lock():
    """Acquire exclusive lock on queue. Returns context manager."""
    return QueueLock()


def release_lock(lock_fd):
    """Legacy - use context manager instead."""
    pass  # No-op, handled by context manager


def load_queue() -> List[Dict]:
    """Load queue from file."""
    if not QUEUE_FILE.exists():
        return []
    try:
        return json.loads(QUEUE_FILE.read_text())
    except Exception:
        return []


def save_queue(queue: List[Dict]):
    """Save queue to file."""
    QUEUE_FILE.write_text(json.dumps(queue, indent=2))


def submit_request(prompt: str, system: str = "", max_tokens: int = 1000,
                   consumer: str = "unknown") -> str:
    """
    Submit a request to the queue.
    Returns: request ID for checking result later.
    """
    request_id = str(uuid.uuid4())[:8]

    item = QueueItem(
        id=request_id,
        prompt=prompt,
        system=system,
        max_tokens=max_tokens,
        submitted_at=datetime.now().isoformat(),
        consumer=consumer
    )

    with acquire_lock():
        queue = load_queue()
        queue.append(asdict(item))
        save_queue(queue)

    return request_id


def get_result(request_id: str, wait: bool = True, timeout: int = 60) -> Optional[Dict]:
    """
    Get result for a request.
    If wait=True, blocks until result is available or timeout.
    """
    result_file = RESULTS_DIR / f"{request_id}.json"

    start = time.time()
    while True:
        if result_file.exists():
            return json.loads(result_file.read_text())

        if not wait:
            return None

        if time.time() - start > timeout:
            return {"status": "timeout", "error": "Result not ready within timeout"}

        time.sleep(0.5)


def cerebras_call(prompt: str, system: str = "", max_tokens: int = 1000) -> str:
    """Make actual Cerebras API call."""
    api_key = os.getenv("CEREBRAS_API_KEY")
    if not api_key:
        raise ValueError("CEREBRAS_API_KEY not set")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = requests.post(
        CEREBRAS_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": CEREBRAS_MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0
        },
        timeout=30
    )

    if response.status_code == 429:
        raise Exception("RATE_LIMITED")

    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")

    return response.json()["choices"][0]["message"]["content"]


# =============================================================================
# WORKER
# =============================================================================

def process_queue():
    """Process pending requests in the queue."""
    print(f"[{datetime.now().isoformat()}] Queue worker starting...")
    print(f"Rate: {REQUESTS_PER_SECOND} req/sec (interval: {MIN_INTERVAL:.2f}s)")

    last_request = 0
    backoff = MIN_INTERVAL
    processed = 0
    errors = 0

    while True:
        # Get next pending item
        item = None
        with acquire_lock():
            queue = load_queue()
            pending = [q for q in queue if q["status"] == "pending"]

            if pending:
                item = pending[0]
                item["status"] = "processing"
                save_queue(queue)

        if item is None:
            time.sleep(1)
            continue

        # Rate limit
        elapsed = time.time() - last_request
        if elapsed < backoff:
            time.sleep(backoff - elapsed)

        # Process
        try:
            result = cerebras_call(
                item["prompt"],
                item.get("system", ""),
                item.get("max_tokens", 1000)
            )
            item["status"] = "complete"
            item["result"] = result
            item["completed_at"] = datetime.now().isoformat()
            backoff = MIN_INTERVAL  # Reset backoff on success
            processed += 1

        except Exception as e:
            if "RATE_LIMITED" in str(e):
                # Back off and retry
                backoff = min(backoff * 2, 10.0)
                print(f"Rate limited, backing off to {backoff:.1f}s")
                item["status"] = "pending"  # Put back in queue
            else:
                item["status"] = "failed"
                item["error"] = str(e)
                item["completed_at"] = datetime.now().isoformat()
                errors += 1

        last_request = time.time()

        # Save result
        if item["status"] in ("complete", "failed"):
            result_file = RESULTS_DIR / f"{item['id']}.json"
            result_file.write_text(json.dumps(item, indent=2))

        # Update queue
        with acquire_lock():
            queue = load_queue()
            for i, q in enumerate(queue):
                if q["id"] == item["id"]:
                    queue[i] = item
                    break
            save_queue(queue)

        print(f"Processed: {processed}, Errors: {errors}, Pending: {len(pending)-1}")


def get_queue_status() -> Dict:
    """Get current queue status."""
    queue = load_queue()
    status_counts = {}
    for item in queue:
        s = item.get("status", "unknown")
        status_counts[s] = status_counts.get(s, 0) + 1

    return {
        "total": len(queue),
        "by_status": status_counts,
        "oldest_pending": None,
        "results_available": len(list(RESULTS_DIR.glob("*.json")))
    }


# =============================================================================
# SYNC API (for simple use cases)
# =============================================================================

def query_sync(prompt: str, system: str = "", max_tokens: int = 1000,
               timeout: int = 60) -> str:
    """
    Submit and wait for result. Simple synchronous API.

    Usage:
        from cerebras_queue import query_sync
        result = query_sync("What is 2+2?")
    """
    request_id = submit_request(prompt, system, max_tokens)
    result = get_result(request_id, wait=True, timeout=timeout)

    if result is None:
        raise TimeoutError("Request timed out")

    if result.get("status") == "failed":
        raise Exception(result.get("error", "Unknown error"))

    return result.get("result", "")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Cerebras Request Queue")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # submit
    submit_p = subparsers.add_parser("submit", help="Submit request to queue")
    submit_p.add_argument("prompt", help="The prompt to send")
    submit_p.add_argument("--system", default="", help="System message")
    submit_p.add_argument("--max-tokens", type=int, default=1000)
    submit_p.add_argument("--consumer", default="cli", help="Consumer identifier")

    # get
    get_p = subparsers.add_parser("get", help="Get result for request")
    get_p.add_argument("request_id", help="Request ID")
    get_p.add_argument("--no-wait", action="store_true", help="Don't wait for result")
    get_p.add_argument("--timeout", type=int, default=60)

    # worker
    subparsers.add_parser("worker", help="Run queue worker")

    # status
    subparsers.add_parser("status", help="Show queue status")

    # query (sync)
    query_p = subparsers.add_parser("query", help="Submit and wait for result")
    query_p.add_argument("prompt", help="The prompt")
    query_p.add_argument("--timeout", type=int, default=60)

    args = parser.parse_args()

    if args.command == "submit":
        request_id = submit_request(
            args.prompt,
            args.system,
            args.max_tokens,
            args.consumer
        )
        print(f"Submitted: {request_id}")

    elif args.command == "get":
        result = get_result(args.request_id, wait=not args.no_wait, timeout=args.timeout)
        if result:
            print(json.dumps(result, indent=2))
        else:
            print("No result yet")

    elif args.command == "worker":
        process_queue()

    elif args.command == "status":
        status = get_queue_status()
        print("=" * 50)
        print("CEREBRAS QUEUE STATUS")
        print("=" * 50)
        print(f"Total items: {status['total']}")
        print(f"By status: {status['by_status']}")
        print(f"Results available: {status['results_available']}")

    elif args.command == "query":
        try:
            result = query_sync(args.prompt, timeout=args.timeout)
            print(result)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
