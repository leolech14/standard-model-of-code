#!/usr/bin/env python3
"""
Cerebras Enricher - Semantic layer on top of Collider output.

Collider gives us STRUCTURE (nodes, edges, atoms, dimensions).
Cerebras adds MEANING (purpose, summary, intent, relationships).

Usage:
    # First run Collider
    ./collider full /path/to/repo --output .collider

    # Then enrich with Cerebras
    python cerebras_enricher.py enrich .collider/unified_analysis.json

    # Or enrich specific files
    python cerebras_enricher.py enrich-file src/core/atom_registry.py

Output:
    - enriched_analysis.json (Collider + semantic layer)
    - Per-file summaries
    - Cross-file semantic relationships
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "wave" / "data" / "enriched"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CEREBRAS_API_URL = "https://api.cerebras.ai/v1/chat/completions"

# Available models (different rate limits)
MODELS = {
    "llama-3.3-70b": {"rpm": 3000, "quality": "high"},
    "llama3.1-8b": {"rpm": 2000, "quality": "fast"},
    "qwen-3-32b": {"rpm": 1000, "quality": "good"},
    "gpt-oss-120b": {"rpm": 1000, "quality": "high"},
    "zai-glm-4.7": {"rpm": 500, "quality": "preview"},
    "qwen-3-235b-a22b-instruct-2507": {"rpm": 1000, "quality": "preview"}
}

# Default model - can be overridden via --model flag
CEREBRAS_MODEL = os.getenv("CEREBRAS_MODEL", "llama-3.3-70b")

# Rate limiting - Cerebras enforces per-SECOND burst limits
# 3000 RPM = 50/sec max, but burst limit is stricter
# Use 150ms interval = ~7 req/sec to avoid 429s
MIN_REQUEST_INTERVAL = 0.15
_last_request_time = 0.0


def get_cerebras_key() -> str:
    """Get Cerebras API key."""
    key = os.getenv("CEREBRAS_API_KEY")
    if not key:
        try:
            import subprocess
            result = subprocess.run(
                ["doppler", "secrets", "get", "CEREBRAS_API_KEY", "--plain"],
                capture_output=True, text=True
            )
            key = result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            pass
    if not key:
        print("Error: CEREBRAS_API_KEY not found", file=sys.stderr)
        sys.exit(1)
    return key


def rate_limit_wait():
    """Ensure we don't exceed rate limits."""
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - elapsed)
    _last_request_time = time.time()


def call_cerebras(prompt: str, api_key: str, max_tokens: int = 300, model: str = None) -> Optional[str]:
    """Call Cerebras API with rate limiting and retries."""
    use_model = model or CEREBRAS_MODEL
    for attempt in range(5):
        try:
            rate_limit_wait()

            response = requests.post(
                CEREBRAS_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": use_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.1
                },
                timeout=30
            )

            if response.status_code == 429:
                wait = (2 ** attempt) * 2 + 1
                print(f" [429, wait {wait}s]", end="", flush=True)
                time.sleep(wait)
                continue

            if response.status_code != 200:
                return None

            result = response.json()
            return result["choices"][0]["message"]["content"]

        except Exception as e:
            if attempt < 4:
                time.sleep(2)
                continue
            return None

    return None


# ============================================================================
# ENRICHMENT PROMPTS - What Collider CAN'T do
# ============================================================================

def prompt_file_purpose(file_path: str, collider_data: dict) -> str:
    """Generate purpose/intent summary for a file."""
    # Extract what Collider knows
    atoms = collider_data.get("atoms", [])
    imports = collider_data.get("imports", [])
    exports = collider_data.get("exports", [])

    return f"""You are analyzing a code file. Collider (AST parser) extracted:
- File: {file_path}
- Atoms detected: {', '.join(atoms[:5]) if atoms else 'none'}
- Imports: {len(imports)} modules
- Exports: {len(exports)} symbols

In ONE sentence (max 20 words), answer: What is the PURPOSE of this file?
Focus on INTENT, not structure. Example: "Handles user authentication via JWT tokens"

Purpose:"""


def prompt_file_summary(file_path: str, content_preview: str) -> str:
    """Generate human-readable summary."""
    return f"""Summarize this code file in 2-3 sentences. Focus on WHAT it does and WHY it exists.

File: {file_path}
Preview (first 100 lines):
{content_preview}

Summary:"""


def prompt_semantic_tags(file_path: str, content_preview: str) -> str:
    """Generate semantic tags beyond D1-D8."""
    return f"""Assign 3-5 semantic tags to this file. Tags should describe WHAT it's about, not structure.
Examples: "authentication", "database-migration", "api-endpoint", "unit-tests", "configuration"

File: {file_path}
Preview:
{content_preview[:2000]}

Tags (comma-separated):"""


def prompt_relationship_hint(file_a: str, file_b: str, shared_context: str) -> str:
    """Detect semantic relationship between files."""
    return f"""These two files share some dependencies. Is there a SEMANTIC relationship?

File A: {file_a}
File B: {file_b}
Shared: {shared_context}

If related, describe the relationship in 10 words or less.
If not meaningfully related, respond: "NO_RELATIONSHIP"

Relationship:"""


# ============================================================================
# ENRICHMENT FUNCTIONS
# ============================================================================

@dataclass
class EnrichedNode:
    """A node enriched with comprehensive semantic understanding."""
    id: str
    file_path: str
    # From Collider (structure)
    atom: str
    layer: str
    role: str
    # From Cerebras (semantics)
    purpose: str                    # One-line intent
    semantic_tags: list[str]        # Human-meaningful tags
    key_exports: list[str]          # Main functions/classes provided
    dependencies: str               # What it needs to work
    complexity: str                 # LOW|MEDIUM|HIGH
    quality_hints: str              # Potential issues
    related_to: list[str]           # Suggested related files
    enriched_at: str
    model: str                      # Which model was used


def build_combined_prompt(file_path: str, node: dict, content_preview: str) -> str:
    """Comprehensive analysis prompt - extracts maximum value per request."""
    atoms = node.get("atoms", [])
    imports = node.get("imports", [])
    exports = node.get("exports", [])

    return f"""Analyze this code file comprehensively. Respond in EXACTLY this format:

PURPOSE: <one sentence, max 20 words, what this file does and why it exists>
TAGS: <5 semantic tags, comma-separated: e.g., authentication, api-endpoint, data-validation>
KEY_EXPORTS: <main functions/classes this file provides, comma-separated, max 5>
DEPENDENCIES: <what this file needs to work: libraries, services, other modules>
COMPLEXITY: <LOW|MEDIUM|HIGH> - based on logic complexity, not length
QUALITY_HINTS: <potential issues: missing tests, tight coupling, magic numbers, etc. or "none">
RELATED_TO: <suggest 2-3 files that likely interact with this, based on purpose>

File: {file_path}
Collider detected:
- Atoms: {', '.join(atoms[:5]) if atoms else 'none'}
- Imports: {len(imports)} modules
- Exports: {len(exports)} symbols

Code preview:
```
{content_preview[:2000]}
```

Respond now (start with PURPOSE:):"""


def enrich_node(node: dict, api_key: str, source_dir: Path, model: str = None) -> Optional[EnrichedNode]:
    """Enrich a single node with semantic understanding (1 API call)."""
    file_path = node.get("file_path") or node.get("id", "").split("::")[0]

    if not file_path:
        return None

    # Read file content for context
    full_path = source_dir / file_path
    content_preview = ""
    if full_path.exists():
        try:
            with open(full_path, 'r', errors='ignore') as f:
                lines = f.readlines()[:100]
                content_preview = ''.join(lines)
        except Exception:
            pass

    # Comprehensive single request
    prompt = build_combined_prompt(file_path, node, content_preview)
    response = call_cerebras(prompt, api_key, max_tokens=300, model=model)

    # Parse structured response
    parsed = {
        "purpose": "",
        "tags": [],
        "key_exports": [],
        "dependencies": "",
        "complexity": "MEDIUM",
        "quality_hints": "",
        "related_to": []
    }

    if response:
        for line in response.strip().split('\n'):
            line = line.strip()
            if line.startswith("PURPOSE:"):
                parsed["purpose"] = line.replace("PURPOSE:", "").strip()
            elif line.startswith("TAGS:"):
                parsed["tags"] = [t.strip() for t in line.replace("TAGS:", "").split(",") if t.strip()]
            elif line.startswith("KEY_EXPORTS:"):
                parsed["key_exports"] = [e.strip() for e in line.replace("KEY_EXPORTS:", "").split(",") if e.strip()]
            elif line.startswith("DEPENDENCIES:"):
                parsed["dependencies"] = line.replace("DEPENDENCIES:", "").strip()
            elif line.startswith("COMPLEXITY:"):
                parsed["complexity"] = line.replace("COMPLEXITY:", "").strip().upper()
            elif line.startswith("QUALITY_HINTS:"):
                parsed["quality_hints"] = line.replace("QUALITY_HINTS:", "").strip()
            elif line.startswith("RELATED_TO:"):
                parsed["related_to"] = [r.strip() for r in line.replace("RELATED_TO:", "").split(",") if r.strip()]

    return EnrichedNode(
        id=node.get("id", file_path),
        file_path=file_path,
        atom=node.get("atom", "UNKNOWN"),
        layer=node.get("layer", "UNKNOWN"),
        role=node.get("role", "UNKNOWN"),
        purpose=parsed["purpose"],
        semantic_tags=parsed["tags"][:5],
        key_exports=parsed["key_exports"][:5],
        dependencies=parsed["dependencies"],
        complexity=parsed["complexity"] if parsed["complexity"] in ["LOW", "MEDIUM", "HIGH"] else "MEDIUM",
        quality_hints=parsed["quality_hints"],
        related_to=parsed["related_to"][:3],
        enriched_at=datetime.now().isoformat(),
        model=model or CEREBRAS_MODEL
    )


def load_collider_output(path: Path) -> dict:
    """Load Collider's unified_analysis.json."""
    with open(path) as f:
        return json.load(f)


def get_file_nodes(collider_data: dict) -> list[dict]:
    """Extract file-level nodes from Collider output."""
    nodes = collider_data.get("nodes", [])

    # Filter to file-level nodes (not function/class level)
    file_nodes = []
    seen_files = set()

    for node in nodes:
        node_id = node.get("id", "")
        # File-level nodes have format "path/file.py" or "path/file.py::module"
        if "::" in node_id:
            file_path = node_id.split("::")[0]
        else:
            file_path = node_id

        if file_path and file_path not in seen_files and file_path.endswith(".py"):
            seen_files.add(file_path)
            file_nodes.append({
                "id": node_id,
                "file_path": file_path,
                "atom": node.get("atom", ""),
                "layer": node.get("layer", ""),
                "role": node.get("role", ""),
                "imports": node.get("imports", []),
                "exports": node.get("exports", [])
            })

    return file_nodes


def cmd_enrich(args):
    """Enrich Collider output with semantic layer."""
    collider_path = Path(args.collider_output)
    if not collider_path.exists():
        print(f"Error: {collider_path} not found", file=sys.stderr)
        sys.exit(1)

    # Determine source directory
    source_dir = collider_path.parent.parent  # .collider is usually inside repo
    if args.source:
        source_dir = Path(args.source)

    print(f"Loading Collider output: {collider_path}")
    collider_data = load_collider_output(collider_path)

    print(f"Source directory: {source_dir}")

    # Get file nodes
    file_nodes = get_file_nodes(collider_data)

    if args.limit:
        file_nodes = file_nodes[:args.limit]

    # Get model from args or env
    model = getattr(args, 'model', None) or CEREBRAS_MODEL

    print(f"Enriching {len(file_nodes)} files with Cerebras ({model})...")
    print(f"Estimated cost: ${len(file_nodes) * 0.0003:.2f}")
    print(f"Estimated time: {len(file_nodes) * 0.05:.0f} seconds")  # 1 request per file now
    print()

    api_key = get_cerebras_key()
    enriched = []
    start = time.time()

    for i, node in enumerate(file_nodes):
        file_start = time.time()
        elapsed_total = time.time() - start

        # Progress with ETA
        if i > 0:
            avg_per_file = elapsed_total / i
            remaining = (len(file_nodes) - i) * avg_per_file
            eta = f"ETA {remaining:.0f}s"
        else:
            eta = ""

        print(f"[{i+1}/{len(file_nodes)}] {node['file_path']}", end=" ", flush=True)

        result = enrich_node(node, api_key, source_dir, model=model)
        file_time = time.time() - file_start

        if result:
            enriched.append(result)
            purpose_preview = result.purpose[:40] + "..." if len(result.purpose) > 40 else result.purpose
            print(f"→ {purpose_preview} ({file_time:.1f}s) {eta}")
        else:
            print(f"→ FAILED ({file_time:.1f}s)")

    elapsed = time.time() - start

    # Save enriched output
    output = {
        "meta": {
            "created_at": datetime.now().isoformat(),
            "collider_source": str(collider_path),
            "model": model,
            "files_enriched": len(enriched),
            "elapsed_seconds": round(elapsed, 2)
        },
        "enriched_nodes": [asdict(e) for e in enriched]
    }

    output_file = OUTPUT_DIR / f"enriched_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    latest_file = OUTPUT_DIR / "enriched_latest.json"

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    with open(latest_file, 'w') as f:
        json.dump(output, f, indent=2)

    print()
    print("=" * 60)
    print(f"COMPLETE: {len(enriched)}/{len(file_nodes)} files enriched")
    print(f"Time: {elapsed:.1f}s ({elapsed/len(file_nodes):.2f}s/file)")
    print(f"Model: {model}")
    print(f"Output: {output_file}")
    print("=" * 60)

    # Show sample
    if enriched:
        print()
        print("Sample enrichments:")
        for e in enriched[:3]:
            print(f"\n  {e.file_path}")
            print(f"    Purpose: {e.purpose}")
            print(f"    Tags: {', '.join(e.semantic_tags)}")
            print(f"    Exports: {', '.join(e.key_exports) if e.key_exports else 'none'}")
            print(f"    Complexity: {e.complexity}")
            if e.quality_hints and e.quality_hints.lower() != "none":
                print(f"    Quality: {e.quality_hints}")


def cmd_quick(args):
    """Quick enrichment of a single file or directory."""
    target = Path(args.path)
    api_key = get_cerebras_key()

    if target.is_file():
        files = [target]
    else:
        files = list(target.rglob("*.py"))[:args.limit or 10]

    print(f"Quick enrichment: {len(files)} files")
    print()

    for f in files:
        # Read content
        with open(f, 'r', errors='ignore') as fp:
            content = fp.read()[:3000]

        # Get purpose
        prompt = f"""In ONE sentence (max 20 words), what is the PURPOSE of this code?

File: {f.name}
```
{content}
```

Purpose:"""

        print(f"{f.relative_to(PROJECT_ROOT)}")
        result = call_cerebras(prompt, api_key, max_tokens=50)
        print(f"  → {result}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Cerebras Enricher - Semantic layer on Collider")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Enrich command
    enrich_parser = subparsers.add_parser("enrich", help="Enrich Collider output")
    enrich_parser.add_argument("collider_output", help="Path to unified_analysis.json")
    enrich_parser.add_argument("--source", help="Source directory (if different from Collider location)")
    enrich_parser.add_argument("--limit", type=int, help="Limit files to process")
    enrich_parser.add_argument("--model", default="llama-3.3-70b", choices=list(MODELS.keys()), help="Cerebras model to use")

    # Quick command
    quick_parser = subparsers.add_parser("quick", help="Quick enrichment of file/directory")
    quick_parser.add_argument("path", help="File or directory to enrich")
    quick_parser.add_argument("--limit", type=int, default=10, help="Max files")

    args = parser.parse_args()

    if args.command == "enrich":
        cmd_enrich(args)
    elif args.command == "quick":
        cmd_quick(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
