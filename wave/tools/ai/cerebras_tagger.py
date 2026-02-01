#!/usr/bin/env python3
"""
Cerebras Batch Tagger - Fast D1-D8 Classification

Uses Cerebras (33x faster, $0.60/M tokens) for bulk file classification,
then validates with Claude for accuracy.

Usage:
    # Tag all Python files
    python cerebras_tagger.py tag --pattern "**/*.py"

    # Tag specific directory
    python cerebras_tagger.py tag --path particle/src/

    # Validate with Claude (samples 10%)
    python cerebras_tagger.py validate --sample 0.1

    # Full pipeline: tag then validate
    python cerebras_tagger.py pipeline --pattern "**/*.py" --sample 0.1

Output: wave/data/tags/

Rate Limits (llama-3.3-70b):
    - 3,000 requests/minute (50/sec burst limit)
    - 4,000,000 tokens/minute
"""

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict
import requests

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
TAGS_DIR = PROJECT_ROOT / "wave" / "data" / "tags"
TAGS_DIR.mkdir(parents=True, exist_ok=True)

# Cerebras config
CEREBRAS_API_URL = "https://api.cerebras.ai/v1/chat/completions"
CEREBRAS_MODEL = "llama-3.3-70b"

# Rate limiting - Cerebras enforces per-SECOND burst limits
# 3000 RPM = 50/sec max, but burst limit is stricter (~7/sec safe)
MIN_REQUEST_INTERVAL = 0.15  # ~7 requests/sec to avoid 429s

# Standard Model Dimensions
DIMENSIONS = {
    "D1_WHAT": ["ENTITY", "SERVICE", "REPOSITORY", "CONTROLLER", "FACTORY", "ADAPTER", "GATEWAY", "EXTRACTOR", "TRANSFORMER", "VALIDATOR", "CONFIG", "UTIL", "TEST", "CLI", "SCRIPT", "UNKNOWN"],
    "D2_LAYER": ["CORE", "DOMAIN", "APPLICATION", "INFRASTRUCTURE", "PRESENTATION", "TEST", "CONFIG", "UNKNOWN"],
    "D3_ROLE": ["SERVICE", "REPOSITORY", "FACTORY", "ADAPTER", "GATEWAY", "CONTROLLER", "ENTITY", "VALUE_OBJECT", "AGGREGATE", "EVENT", "COMMAND", "QUERY", "UNKNOWN"],
    "D4_BOUNDARY": ["INTERNAL", "EXTERNAL", "HYBRID", "UNKNOWN"],
    "D5_STATE": ["STATELESS", "STATEFUL", "IMMUTABLE", "UNKNOWN"],
    "D6_EFFECT": ["PURE", "IMPURE", "MIXED", "UNKNOWN"],
    "D7_LIFECYCLE": ["PRODUCTION", "DEVELOPMENT", "TEST", "BUILD", "UNKNOWN"],
    "D8_TRUST": ["INTERNAL", "EXTERNAL", "USER_INPUT", "UNKNOWN"]
}


@dataclass
class FileTag:
    file_path: str
    D1_WHAT: str
    D2_LAYER: str
    D3_ROLE: str
    D4_BOUNDARY: str
    D5_STATE: str
    D6_EFFECT: str
    D7_LIFECYCLE: str
    D8_TRUST: str
    confidence: float
    reasoning: str
    tagged_at: str
    model: str


# Track last request time for rate limiting
_last_request_time = 0.0


def get_cerebras_key() -> str:
    """Get Cerebras API key from environment or Doppler."""
    key = os.getenv("CEREBRAS_API_KEY")
    if not key:
        try:
            result = subprocess.run(
                ["doppler", "secrets", "get", "CEREBRAS_API_KEY", "--plain",
                 "--project", "ai-tools", "--config", "dev"],
                capture_output=True, text=True
            )
            key = result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            pass
    if not key:
        print("Error: CEREBRAS_API_KEY not found", file=sys.stderr)
        sys.exit(1)
    return key


def read_file_content(file_path: Path, max_lines: int = 100) -> str:
    """Read file content, truncated for context efficiency."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()[:max_lines]
            return ''.join(lines)
    except Exception as e:
        return f"# Error reading file: {e}"


def build_classification_prompt(file_path: str, content: str) -> str:
    """Build the classification prompt."""
    return f"""Classify this code file using the Standard Model dimensions.

FILE: {file_path}

CODE:
```
{content}
```

Respond with ONLY valid JSON (no markdown, no explanation):
{{
  "D1_WHAT": "<one of: ENTITY, SERVICE, REPOSITORY, CONTROLLER, FACTORY, ADAPTER, GATEWAY, EXTRACTOR, TRANSFORMER, VALIDATOR, CONFIG, UTIL, TEST, CLI, SCRIPT, UNKNOWN>",
  "D2_LAYER": "<one of: CORE, DOMAIN, APPLICATION, INFRASTRUCTURE, PRESENTATION, TEST, CONFIG, UNKNOWN>",
  "D3_ROLE": "<one of: SERVICE, REPOSITORY, FACTORY, ADAPTER, GATEWAY, CONTROLLER, ENTITY, VALUE_OBJECT, AGGREGATE, EVENT, COMMAND, QUERY, UNKNOWN>",
  "D4_BOUNDARY": "<one of: INTERNAL, EXTERNAL, HYBRID, UNKNOWN>",
  "D5_STATE": "<one of: STATELESS, STATEFUL, IMMUTABLE, UNKNOWN>",
  "D6_EFFECT": "<one of: PURE, IMPURE, MIXED, UNKNOWN>",
  "D7_LIFECYCLE": "<one of: PRODUCTION, DEVELOPMENT, TEST, BUILD, UNKNOWN>",
  "D8_TRUST": "<one of: INTERNAL, EXTERNAL, USER_INPUT, UNKNOWN>",
  "confidence": <0.0-1.0>,
  "reasoning": "<one sentence explaining the classification>"
}}"""


def rate_limit_wait():
    """Ensure we don't exceed rate limits."""
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - elapsed)
    _last_request_time = time.time()


def classify_file_cerebras(file_path: Path, api_key: str, max_retries: int = 5) -> Optional[FileTag]:
    """Classify a single file using Cerebras with retry logic."""
    content = read_file_content(file_path)
    prompt = build_classification_prompt(str(file_path.relative_to(PROJECT_ROOT)), content)

    for attempt in range(max_retries):
        try:
            # Rate limiting
            rate_limit_wait()

            response = requests.post(
                CEREBRAS_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": CEREBRAS_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500,
                    "temperature": 0.1
                },
                timeout=30
            )

            if response.status_code == 429:
                # Rate limited - exponential backoff
                wait = (2 ** attempt) * 2 + 1  # 3s, 5s, 9s, 17s, 33s
                print(f" [429 retry {attempt+1}/{max_retries}, wait {wait}s]", end="", flush=True)
                time.sleep(wait)
                continue

            if response.status_code != 200:
                print(f" [Error {response.status_code}]", end="", flush=True)
                return None

            result = response.json()
            resp_content = result["choices"][0]["message"]["content"]

            # Parse JSON response - handle markdown wrapping
            if "```json" in resp_content:
                resp_content = resp_content.split("```json")[1].split("```")[0]
            elif "```" in resp_content:
                resp_content = resp_content.split("```")[1].split("```")[0]

            data = json.loads(resp_content.strip())

            return FileTag(
                file_path=str(file_path.relative_to(PROJECT_ROOT)),
                D1_WHAT=data.get("D1_WHAT", "UNKNOWN"),
                D2_LAYER=data.get("D2_LAYER", "UNKNOWN"),
                D3_ROLE=data.get("D3_ROLE", "UNKNOWN"),
                D4_BOUNDARY=data.get("D4_BOUNDARY", "UNKNOWN"),
                D5_STATE=data.get("D5_STATE", "UNKNOWN"),
                D6_EFFECT=data.get("D6_EFFECT", "UNKNOWN"),
                D7_LIFECYCLE=data.get("D7_LIFECYCLE", "UNKNOWN"),
                D8_TRUST=data.get("D8_TRUST", "UNKNOWN"),
                confidence=float(data.get("confidence", 0.5)),
                reasoning=data.get("reasoning", ""),
                tagged_at=datetime.now().isoformat(),
                model=CEREBRAS_MODEL
            )

        except json.JSONDecodeError as e:
            print(f" [JSON error: {e}]", end="", flush=True)
            return None
        except requests.exceptions.Timeout:
            print(f" [Timeout, retry {attempt+1}]", end="", flush=True)
            time.sleep(2)
            continue
        except Exception as e:
            print(f" [Error: {e}]", end="", flush=True)
            return None

    print(" [Max retries exceeded]", end="", flush=True)
    return None


def collect_files(pattern: str = "**/*.py", path: Optional[str] = None) -> list[Path]:
    """Collect files to tag."""
    base = PROJECT_ROOT / path if path else PROJECT_ROOT

    # Exclude patterns
    excludes = [".git", "__pycache__", "node_modules", ".venv", ".tools_venv",
                "venv", "dist", "build", ".egg-info", ".collider"]

    files = []
    for f in base.glob(pattern):
        if f.is_file() and not any(ex in str(f) for ex in excludes):
            files.append(f)

    return sorted(files)


def cmd_tag(args):
    """Tag files with Cerebras."""
    api_key = get_cerebras_key()
    files = collect_files(args.pattern, args.path)

    if args.limit:
        files = files[:args.limit]

    print(f"Tagging {len(files)} files with Cerebras ({CEREBRAS_MODEL})...")
    print(f"Estimated cost: ${len(files) * 0.0007:.2f}")
    print(f"Estimated time: {len(files) * 0.5:.0f} seconds (~{len(files) * 0.5 / 60:.1f} min)")
    print(f"Rate limit: ~28 req/sec")
    print()

    tags = []
    failed = []
    start = time.time()

    for i, f in enumerate(files):
        rel_path = f.relative_to(PROJECT_ROOT)
        print(f"[{i+1}/{len(files)}] {rel_path}", end=" ", flush=True)

        tag = classify_file_cerebras(f, api_key)
        if tag:
            tags.append(tag)
            print(f"→ {tag.D1_WHAT}/{tag.D2_LAYER} ({tag.confidence:.0%})")
        else:
            failed.append(str(rel_path))
            print("→ FAILED")

    elapsed = time.time() - start

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = TAGS_DIR / f"tags_{timestamp}.json"

    output = {
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "model": CEREBRAS_MODEL,
            "files_processed": len(files),
            "files_tagged": len(tags),
            "files_failed": len(failed),
            "elapsed_seconds": round(elapsed, 2),
            "pattern": args.pattern,
            "path": args.path
        },
        "tags": [asdict(t) for t in tags],
        "failed": failed
    }

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    # Also save latest
    latest_file = TAGS_DIR / "tags_latest.json"
    with open(latest_file, 'w') as f:
        json.dump(output, f, indent=2)

    print()
    print(f"Done! Tagged {len(tags)}/{len(files)} files in {elapsed:.1f}s ({elapsed/len(files):.2f}s/file)")
    print(f"Output: {output_file}")

    # Summary stats
    if tags:
        print()
        print("D1_WHAT Distribution:")
        d1_counts = {}
        for t in tags:
            d1_counts[t.D1_WHAT] = d1_counts.get(t.D1_WHAT, 0) + 1
        for k, v in sorted(d1_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"  {k}: {v}")

    if failed:
        print()
        print(f"Failed files ({len(failed)}):")
        for f in failed[:10]:
            print(f"  - {f}")
        if len(failed) > 10:
            print(f"  ... and {len(failed) - 10} more")


def cmd_validate(args):
    """Validate tags using Claude (big brain)."""
    latest_file = TAGS_DIR / "tags_latest.json"
    if not latest_file.exists():
        print("No tags found. Run 'tag' first.", file=sys.stderr)
        sys.exit(1)

    with open(latest_file) as f:
        data = json.load(f)

    tags = data["tags"]
    sample_size = int(len(tags) * args.sample)
    sample_size = max(1, min(sample_size, len(tags)))

    import random
    sample = random.sample(tags, sample_size)

    print(f"Validating {sample_size} tags ({args.sample:.0%} sample) with Claude...")
    print()

    validation_items = []
    for t in sample:
        validation_items.append(f"""
File: {t['file_path']}
Cerebras: D1={t['D1_WHAT']}, D2={t['D2_LAYER']}, D3={t['D3_ROLE']}
Reasoning: {t['reasoning']}
""")

    prompt = f"""Review these Cerebras-generated file classifications.
For each, mark as: CORRECT, PARTIAL (some wrong), or WRONG.

{chr(10).join(validation_items)}

Respond with JSON array:
[{{"file": "path", "verdict": "CORRECT|PARTIAL|WRONG", "notes": "if wrong, explain"}}]
"""

    prompt_file = TAGS_DIR / "validation_prompt.txt"
    with open(prompt_file, 'w') as f:
        f.write(prompt)

    print(f"Validation prompt saved: {prompt_file}")
    print()
    print("Run validation with Claude:")
    print(f"  cat {prompt_file} | pbcopy  # Copy to clipboard")
    print("  # Then paste into Claude Code")


def cmd_stats(args):
    """Show statistics for tagged files."""
    latest_file = TAGS_DIR / "tags_latest.json"
    if not latest_file.exists():
        print("No tags found. Run 'tag' first.", file=sys.stderr)
        sys.exit(1)

    with open(latest_file) as f:
        data = json.load(f)

    tags = data["tags"]
    meta = data["metadata"]

    print(f"Tag Statistics")
    print(f"==============")
    print(f"Created: {meta['created_at']}")
    print(f"Model: {meta['model']}")
    print(f"Files: {meta['files_tagged']}/{meta['files_processed']}")
    print(f"Failed: {meta.get('files_failed', 0)}")
    print(f"Time: {meta['elapsed_seconds']}s")
    print()

    for dim in ["D1_WHAT", "D2_LAYER", "D3_ROLE", "D4_BOUNDARY", "D5_STATE", "D6_EFFECT"]:
        print(f"{dim}:")
        counts = {}
        for t in tags:
            v = t.get(dim, "UNKNOWN")
            counts[v] = counts.get(v, 0) + 1
        for k, v in sorted(counts.items(), key=lambda x: -x[1]):
            pct = v / len(tags) * 100
            bar = "█" * int(pct / 5)
            print(f"  {k:20} {v:4} ({pct:5.1f}%) {bar}")
        print()

    confs = [t.get("confidence", 0) for t in tags]
    avg_conf = sum(confs) / len(confs) if confs else 0
    print(f"Avg Confidence: {avg_conf:.1%}")
    low_conf = [t for t in tags if t.get("confidence", 0) < 0.7]
    print(f"Low Confidence (<70%): {len(low_conf)} files")


def main():
    parser = argparse.ArgumentParser(description="Cerebras Batch Tagger")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    tag_parser = subparsers.add_parser("tag", help="Tag files with Cerebras")
    tag_parser.add_argument("--pattern", default="**/*.py", help="Glob pattern")
    tag_parser.add_argument("--path", help="Subdirectory to scan")
    tag_parser.add_argument("--limit", type=int, help="Max files to tag")

    val_parser = subparsers.add_parser("validate", help="Validate with Claude")
    val_parser.add_argument("--sample", type=float, default=0.1, help="Sample ratio")

    stats_parser = subparsers.add_parser("stats", help="Show tag statistics")
    stats_parser.add_argument("--verbose", "-v", action="store_true")

    pipe_parser = subparsers.add_parser("pipeline", help="Tag + validate")
    pipe_parser.add_argument("--pattern", default="**/*.py", help="Glob pattern")
    pipe_parser.add_argument("--path", help="Subdirectory to scan")
    pipe_parser.add_argument("--limit", type=int, help="Max files to tag")
    pipe_parser.add_argument("--sample", type=float, default=0.1, help="Validation sample")

    args = parser.parse_args()

    if args.command == "tag":
        cmd_tag(args)
    elif args.command == "validate":
        cmd_validate(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "pipeline":
        cmd_tag(args)
        print()
        cmd_validate(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
