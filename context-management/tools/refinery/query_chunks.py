#!/usr/bin/env python3
"""
Chunk Query Interface - Search consolidated knowledge
======================================================

Simple text search over refinery chunks with relevance ranking.

Usage:
    python query_chunks.py "search term"
    python query_chunks.py "purpose field" --limit 5
    python query_chunks.py "cloud deployment" --context

Examples:
    ./pe refinery search "Communication Fabric"
    ./pe refinery search "pipeline stages" --limit 3
"""

import json
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Paths
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
CHUNKS_DIR = PROJECT_ROOT / ".agent" / "intelligence" / "chunks"


def search_chunks(query: str, limit: int = 10, show_context: bool = False) -> List[Dict[str, Any]]:
    """
    Search chunks by text match with relevance ranking.

    Args:
        query: Search term or phrase
        limit: Maximum results to return
        show_context: If True, return full chunk content

    Returns:
        List of matching chunks sorted by relevance
    """
    results = []
    query_lower = query.lower()

    # Search all chunk files
    for chunk_file in sorted(CHUNKS_DIR.glob("*_chunks.json")):
        try:
            with open(chunk_file) as f:
                data = json.load(f)

            for node in data.get("nodes", []):
                content = node.get("content", "")
                content_lower = content.lower()

                # Check if query appears in chunk
                if query_lower in content_lower:
                    # Calculate match score
                    match_count = content_lower.count(query_lower)
                    base_relevance = node.get("relevance_score", 0.5)

                    # Boost score based on match count and position
                    match_score = base_relevance + (match_count * 0.1)

                    # Extract preview (100 chars around first match)
                    match_index = content_lower.index(query_lower)
                    preview_start = max(0, match_index - 50)
                    preview_end = min(len(content), match_index + 150)
                    preview = content[preview_start:preview_end]

                    # Get source file name without full path
                    source_path = Path(node.get("source_file", ""))
                    source_name = str(source_path.relative_to(PROJECT_ROOT)) if source_path.is_absolute() else str(source_path)

                    result = {
                        "chunk_file": chunk_file.stem,
                        "chunk_type": node.get("chunk_type", "unknown"),
                        "source": source_name,
                        "line": node.get("start_line", 0),
                        "relevance": node.get("relevance_score", 0.0),
                        "match_score": match_score,
                        "match_count": match_count,
                        "preview": preview.strip(),
                        "full_content": content if show_context else None,
                    }
                    results.append(result)

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Failed to process {chunk_file}: {e}", file=sys.stderr)
            continue

    # Sort by match score (relevance + match frequency)
    results.sort(key=lambda x: x["match_score"], reverse=True)

    return results[:limit]


def print_results(results: List[Dict[str, Any]], query: str, show_context: bool = False):
    """Pretty print search results."""
    if not results:
        print(f"\nNo matches found for: '{query}'\n")
        return

    print(f"\n{'='*60}")
    print(f"Found {len(results)} matches for: '{query}'")
    print(f"{'='*60}\n")

    for i, r in enumerate(results, 1):
        # Header
        print(f"{i}. [{r['source']}:{r['line']}]")
        print(f"   Type: {r['chunk_type']}")
        print(f"   Relevance: {r['relevance']:.2f} | Matches: {r['match_count']}")

        # Preview or full content
        if show_context and r['full_content']:
            print(f"\n   Content:")
            for line in r['full_content'].split('\n')[:20]:  # First 20 lines
                print(f"   │ {line}")
            if r['full_content'].count('\n') > 20:
                print(f"   │ ... ({r['full_content'].count(chr(10)) - 20} more lines)")
        else:
            print(f"   Preview: ...{r['preview']}...")

        print()


def main():
    parser = argparse.ArgumentParser(
        description="Query consolidated knowledge chunks",
        epilog="""
Examples:
  query_chunks.py "purpose field"
  query_chunks.py "cloud deployment" --limit 5
  query_chunks.py "Communication Fabric" --context
        """
    )
    parser.add_argument("query", nargs="+", help="Search query")
    parser.add_argument("--limit", "-n", type=int, default=10,
                       help="Maximum results to return (default: 10)")
    parser.add_argument("--context", "-c", action="store_true",
                       help="Show full chunk content (not just preview)")
    parser.add_argument("--json", action="store_true",
                       help="Output as JSON")

    args = parser.parse_args()

    # Join query parts
    query = " ".join(args.query)

    # Check if chunks exist
    if not CHUNKS_DIR.exists():
        print(f"Error: Chunks directory not found: {CHUNKS_DIR}", file=sys.stderr)
        print("Run: ./pe wire   (to generate chunks)", file=sys.stderr)
        return 1

    chunk_files = list(CHUNKS_DIR.glob("*_chunks.json"))
    if not chunk_files:
        print(f"Error: No chunk files found in {CHUNKS_DIR}", file=sys.stderr)
        print("Run: ./pe wire   (to generate chunks)", file=sys.stderr)
        return 1

    # Search
    results = search_chunks(query, limit=args.limit, show_context=args.context)

    # Output
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_results(results, query, show_context=args.context)

    return 0


if __name__ == "__main__":
    sys.exit(main())
