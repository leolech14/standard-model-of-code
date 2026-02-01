#!/usr/bin/env python3
"""
Cerebras Zoo Compare - Compare external knowledge to CODE_ZOO taxonomy
=====================================================================
Uses Cerebras 3000 t/s to rapidly compare documents against CODE_ZOO.

Usage:
    # Compare SWEBOK to CODE_ZOO
    python cerebras_zoo_compare.py swebok

    # Compare any text file
    python cerebras_zoo_compare.py compare path/to/document.txt

    # Interactive mode
    python cerebras_zoo_compare.py interactive

Output:
    wave/data/intel/zoo_comparisons/
    - swebok_comparison.json (structured differences)
    - swebok_comparison.yaml (human-readable)
"""

import os
import sys
import json
import yaml
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any

# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
THEORY_DIR = PROJECT_ROOT / "particle" / "docs" / "theory"
CODE_ZOO_PATH = THEORY_DIR / "CODE_ZOO.md"
SWEBOK_PATH = PROJECT_ROOT / "wave" / "archive" / "references" / "swebok" / "swebok-v4-clean.txt"
OUTPUT_DIR = PROJECT_ROOT / "wave" / "data" / "intel" / "zoo_comparisons"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CEREBRAS_API_URL = "https://api.cerebras.ai/v1/chat/completions"
CEREBRAS_MODEL = os.getenv("CEREBRAS_MODEL", "llama-3.3-70b")

# Rate limiting
MIN_REQUEST_INTERVAL = 0.15
_last_request_time = 0.0

# Chunk size for processing
CHUNK_SIZE = 2000  # words per chunk


# =============================================================================
# CODE_ZOO SYSTEM CONTEXT
# =============================================================================

def load_code_zoo() -> str:
    """Load CODE_ZOO.md as system context."""
    if CODE_ZOO_PATH.exists():
        return CODE_ZOO_PATH.read_text()
    raise FileNotFoundError(f"CODE_ZOO not found at {CODE_ZOO_PATH}")


CODE_ZOO_SYSTEM_PROMPT = """You are an expert in the Standard Model of Code taxonomy (CODE_ZOO).

CODE_ZOO defines:
- 167 ATOMS (structural types): Functions, Classes, Handlers, etc.
- 33 ROLES (functional purposes): Query, Command, Validator, Factory, etc.
- 16 LEVELS (scale): L-3 (Bit) to L12 (Universe)
- 5 RINGS (dependency depth): R0 (Core) to R4 (Framework)
- LOCUS formula: ⟨λ, Ω, τ, α, R⟩ (Level, Ring, Tier, Role, RPBL)
- RPBL metrics: Responsibility, Purity, Boundary, Lifecycle (1-9 each)

Your task: Compare external text to CODE_ZOO concepts and identify:
1. MATCHES - Concepts that align with CODE_ZOO atoms/roles
2. GAPS - Concepts in the external text that CODE_ZOO doesn't cover
3. ENHANCEMENTS - Ways CODE_ZOO could be improved based on this text
4. CONFLICTS - Where the external text contradicts CODE_ZOO

Output structured YAML."""


# =============================================================================
# CEREBRAS CLIENT
# =============================================================================

def cerebras_complete(system: str, user: str, max_tokens: int = 2000) -> str:
    """Call Cerebras API with rate limiting."""
    global _last_request_time

    # Rate limit
    elapsed = time.time() - _last_request_time
    if elapsed < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - elapsed)

    api_key = os.getenv("CEREBRAS_API_KEY")
    if not api_key:
        raise ValueError("CEREBRAS_API_KEY not set")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": CEREBRAS_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.3
    }

    _last_request_time = time.time()
    response = requests.post(CEREBRAS_API_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]


# =============================================================================
# TEXT CHUNKING
# =============================================================================

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> List[Dict[str, Any]]:
    """Split text into chunks by chapter/section."""
    chunks = []
    current_chapter = "Unknown"
    current_text = []
    word_count = 0

    for line in text.split('\n'):
        # Detect chapter headers
        if line.startswith('CHAPTER:') or line.startswith('====='):
            # Save previous chunk
            if current_text:
                chunks.append({
                    "chapter": current_chapter,
                    "text": '\n'.join(current_text),
                    "word_count": word_count
                })

            if 'CHAPTER:' in line:
                current_chapter = line.replace('CHAPTER:', '').strip()
            current_text = []
            word_count = 0
            continue

        words = len(line.split())

        # If adding this line exceeds chunk size, save and start new
        if word_count + words > chunk_size and current_text:
            chunks.append({
                "chapter": current_chapter,
                "text": '\n'.join(current_text),
                "word_count": word_count
            })
            current_text = [line]
            word_count = words
        else:
            current_text.append(line)
            word_count += words

    # Don't forget the last chunk
    if current_text:
        chunks.append({
            "chapter": current_chapter,
            "text": '\n'.join(current_text),
            "word_count": word_count
        })

    return chunks


# =============================================================================
# COMPARISON ENGINE
# =============================================================================

@dataclass
class ComparisonResult:
    chunk_id: int
    chapter: str
    matches: List[Dict[str, str]] = field(default_factory=list)
    gaps: List[Dict[str, str]] = field(default_factory=list)
    enhancements: List[Dict[str, str]] = field(default_factory=list)
    conflicts: List[Dict[str, str]] = field(default_factory=list)
    raw_response: str = ""


def compare_chunk_to_zoo(chunk: Dict[str, Any], chunk_id: int, code_zoo: str) -> ComparisonResult:
    """Compare a single chunk against CODE_ZOO."""

    system = CODE_ZOO_SYSTEM_PROMPT + "\n\nHere is the CODE_ZOO taxonomy:\n\n" + code_zoo

    user = f"""Analyze this text from SWEBOK (IEEE Software Engineering Body of Knowledge) chapter "{chunk['chapter']}":

---
{chunk['text'][:3000]}
---

Identify and output in YAML format:

```yaml
matches:
  - swebok_concept: "name of SWEBOK concept"
    code_zoo_atom: "matching atom (e.g., LOG.FNC.Function)"
    code_zoo_role: "matching role (e.g., Validator)"
    confidence: high/medium/low
    notes: "explanation"

gaps:
  - swebok_concept: "concept not in CODE_ZOO"
    description: "what it means"
    suggested_atom: "proposed atom name if we should add it"
    suggested_phase: "DAT/LOG/ORG/EXE"

enhancements:
  - code_zoo_concept: "existing concept"
    enhancement: "how to improve it based on SWEBOK"
    source: "SWEBOK section/concept"

conflicts:
  - swebok_says: "SWEBOK definition"
    code_zoo_says: "CODE_ZOO definition"
    resolution: "which is better and why"
```

Be specific and cite exact atoms/roles from CODE_ZOO."""

    try:
        response = cerebras_complete(system, user)

        # Parse YAML from response
        result = ComparisonResult(chunk_id=chunk_id, chapter=chunk['chapter'], raw_response=response)

        # Extract YAML block
        if '```yaml' in response:
            yaml_text = response.split('```yaml')[1].split('```')[0]
        elif '```' in response:
            yaml_text = response.split('```')[1].split('```')[0]
        else:
            yaml_text = response

        try:
            parsed = yaml.safe_load(yaml_text)
            if parsed:
                result.matches = parsed.get('matches', []) or []
                result.gaps = parsed.get('gaps', []) or []
                result.enhancements = parsed.get('enhancements', []) or []
                result.conflicts = parsed.get('conflicts', []) or []
        except yaml.YAMLError:
            pass  # Keep raw response

        return result

    except Exception as e:
        return ComparisonResult(
            chunk_id=chunk_id,
            chapter=chunk['chapter'],
            raw_response=f"ERROR: {e}"
        )


def run_comparison(source_path: Path, source_name: str = "document") -> Dict[str, Any]:
    """Run full comparison of a document against CODE_ZOO."""

    print(f"Loading CODE_ZOO... ", end="", flush=True)
    code_zoo = load_code_zoo()
    print(f"({len(code_zoo.split())} words)")

    print(f"Loading {source_name}... ", end="", flush=True)
    text = source_path.read_text()
    print(f"({len(text.split())} words)")

    print(f"Chunking... ", end="", flush=True)
    chunks = chunk_text(text)
    print(f"({len(chunks)} chunks)")

    results = []
    total_matches = 0
    total_gaps = 0
    total_enhancements = 0
    total_conflicts = 0

    print(f"\nProcessing chunks with Cerebras ({CEREBRAS_MODEL})...")
    print("=" * 60)

    for i, chunk in enumerate(chunks):
        print(f"[{i+1}/{len(chunks)}] {chunk['chapter'][:40]}... ", end="", flush=True)

        result = compare_chunk_to_zoo(chunk, i, code_zoo)
        results.append(asdict(result))

        total_matches += len(result.matches)
        total_gaps += len(result.gaps)
        total_enhancements += len(result.enhancements)
        total_conflicts += len(result.conflicts)

        print(f"M:{len(result.matches)} G:{len(result.gaps)} E:{len(result.enhancements)} C:{len(result.conflicts)}")

        # Small delay to be nice to API
        time.sleep(0.2)

    # Aggregate results
    all_matches = []
    all_gaps = []
    all_enhancements = []
    all_conflicts = []

    for r in results:
        all_matches.extend(r.get('matches', []))
        all_gaps.extend(r.get('gaps', []))
        all_enhancements.extend(r.get('enhancements', []))
        all_conflicts.extend(r.get('conflicts', []))

    report = {
        "metadata": {
            "source": str(source_path),
            "source_name": source_name,
            "timestamp": datetime.now().isoformat(),
            "model": CEREBRAS_MODEL,
            "chunks_processed": len(chunks),
            "code_zoo_version": "2026-01-31"
        },
        "summary": {
            "total_matches": total_matches,
            "total_gaps": total_gaps,
            "total_enhancements": total_enhancements,
            "total_conflicts": total_conflicts
        },
        "aggregated": {
            "matches": all_matches,
            "gaps": all_gaps,
            "enhancements": all_enhancements,
            "conflicts": all_conflicts
        },
        "by_chunk": results
    }

    return report


# =============================================================================
# CLI COMMANDS
# =============================================================================

def cmd_swebok(args):
    """Compare SWEBOK to CODE_ZOO."""
    if not SWEBOK_PATH.exists():
        print(f"SWEBOK not found at {SWEBOK_PATH}")
        print("Run docling first to extract SWEBOK text.")
        return 1

    report = run_comparison(SWEBOK_PATH, "SWEBOK V4")

    # Save JSON
    json_path = OUTPUT_DIR / "swebok_comparison.json"
    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\nJSON saved: {json_path}")

    # Save human-readable YAML summary
    yaml_path = OUTPUT_DIR / "swebok_comparison.yaml"
    summary = {
        "metadata": report["metadata"],
        "summary": report["summary"],
        "top_matches": report["aggregated"]["matches"][:20],
        "top_gaps": report["aggregated"]["gaps"][:20],
        "top_enhancements": report["aggregated"]["enhancements"][:10],
        "conflicts": report["aggregated"]["conflicts"]
    }
    with open(yaml_path, 'w') as f:
        yaml.dump(summary, f, default_flow_style=False, allow_unicode=True)
    print(f"YAML saved: {yaml_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)
    print(f"Matches:      {report['summary']['total_matches']}")
    print(f"Gaps:         {report['summary']['total_gaps']}")
    print(f"Enhancements: {report['summary']['total_enhancements']}")
    print(f"Conflicts:    {report['summary']['total_conflicts']}")

    return 0


def cmd_compare(args):
    """Compare any document to CODE_ZOO."""
    source_path = Path(args.file)
    if not source_path.exists():
        print(f"File not found: {source_path}")
        return 1

    report = run_comparison(source_path, source_path.stem)

    output_name = source_path.stem + "_comparison"
    json_path = OUTPUT_DIR / f"{output_name}.json"
    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\nSaved: {json_path}")

    return 0


def cmd_interactive(args):
    """Interactive comparison mode."""
    print("Loading CODE_ZOO...")
    code_zoo = load_code_zoo()
    print(f"CODE_ZOO loaded ({len(code_zoo.split())} words)")
    print()
    print("Enter text to compare (Ctrl+D to submit, 'quit' to exit):")
    print("-" * 40)

    while True:
        try:
            lines = []
            while True:
                line = input()
                if line.lower() == 'quit':
                    return 0
                lines.append(line)
        except EOFError:
            pass

        text = '\n'.join(lines)
        if not text.strip():
            continue

        print("\nAnalyzing...")
        chunk = {"chapter": "Interactive", "text": text, "word_count": len(text.split())}
        result = compare_chunk_to_zoo(chunk, 0, code_zoo)

        print("\n" + "=" * 40)
        print("RESULT:")
        print("=" * 40)
        print(result.raw_response)
        print("\n" + "-" * 40)
        print("Enter more text (or 'quit'):")


def main():
    parser = argparse.ArgumentParser(description="Compare documents to CODE_ZOO taxonomy")
    subparsers = parser.add_subparsers(dest='command')

    # swebok
    swebok_parser = subparsers.add_parser('swebok', help='Compare SWEBOK to CODE_ZOO')

    # compare
    compare_parser = subparsers.add_parser('compare', help='Compare any file to CODE_ZOO')
    compare_parser.add_argument('file', help='Path to text file')

    # interactive
    interactive_parser = subparsers.add_parser('interactive', help='Interactive mode')

    args = parser.parse_args()

    if args.command == 'swebok':
        return cmd_swebok(args)
    elif args.command == 'compare':
        return cmd_compare(args)
    elif args.command == 'interactive':
        return cmd_interactive(args)
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
