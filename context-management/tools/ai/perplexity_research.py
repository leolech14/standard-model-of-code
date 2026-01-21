#!/usr/bin/env python3
"""
Perplexity Research Tool for Standard Model of Code

Uses Perplexity's Sonar API for deep research queries.
Integrates with Doppler for secrets management.

Usage:
    python perplexity_research.py "your research query"
    python perplexity_research.py --model sonar-deep-research "complex query"
    python perplexity_research.py --file query.txt
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def get_api_key():
    """Get Perplexity API key from Doppler or environment."""
    # Try Doppler first
    try:
        result = subprocess.run(
            ["doppler", "secrets", "get", "PERPLEXITY_API_KEY", "--plain",
             "--project", "ai-tools", "--config", "dev"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass

    # Fall back to environment
    key = os.environ.get("PERPLEXITY_API_KEY")
    if key:
        return key

    raise ValueError("No PERPLEXITY_API_KEY found in Doppler or environment")


def research(query: str, model: str = "sonar-pro", timeout: int = 300) -> dict:
    """
    Execute a research query using Perplexity API.

    Args:
        query: The research question
        model: sonar, sonar-pro, sonar-reasoning, or sonar-deep-research
        timeout: Request timeout in seconds

    Returns:
        dict with 'content', 'citations', and 'usage'
    """
    import httpx

    api_key = get_api_key()

    print(f"[Perplexity] Using model: {model}", file=sys.stderr)
    print(f"[Perplexity] Query length: {len(query)} chars", file=sys.stderr)

    try:
        response = httpx.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": query}],
                "return_citations": True
            },
            timeout=float(timeout)
        )

        response.raise_for_status()
        data = response.json()

        result = {
            "content": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
            "citations": data.get("citations", []),
            "usage": data.get("usage", {}),
            "model": model
        }

        return result

    except httpx.TimeoutException:
        print(f"[Perplexity] Timeout after {timeout}s - try a simpler model or shorter query", file=sys.stderr)
        raise
    except httpx.HTTPStatusError as e:
        print(f"[Perplexity] HTTP Error: {e.response.status_code}", file=sys.stderr)
        print(f"[Perplexity] Response: {e.response.text}", file=sys.stderr)
        raise


def main():
    parser = argparse.ArgumentParser(description="Perplexity Research Tool")
    parser.add_argument("query", nargs="?", help="Research query")
    parser.add_argument("--model", "-m", default="sonar-pro",
                        choices=["sonar", "sonar-pro", "sonar-reasoning", "sonar-deep-research"],
                        help="Model to use (default: sonar-pro)")
    parser.add_argument("--file", "-f", help="Read query from file")
    parser.add_argument("--timeout", "-t", type=int, default=300,
                        help="Timeout in seconds (default: 300)")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Get query
    if args.file:
        query = Path(args.file).read_text()
    elif args.query:
        query = args.query
    else:
        print("Reading query from stdin...", file=sys.stderr)
        query = sys.stdin.read()

    if not query.strip():
        print("Error: No query provided", file=sys.stderr)
        sys.exit(1)

    # Execute research
    try:
        result = research(query, model=args.model, timeout=args.timeout)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Output
    if args.json:
        output = json.dumps(result, indent=2)
    else:
        output = result["content"]
        if result.get("citations"):
            output += "\n\n---\nSources:\n"
            for i, citation in enumerate(result["citations"], 1):
                output += f"{i}. {citation}\n"

    if args.output:
        Path(args.output).write_text(output)
        print(f"Output written to {args.output}", file=sys.stderr)
    else:
        print(output)

    # Print usage stats
    usage = result.get("usage", {})
    if usage:
        print(f"\n[Usage] Input: {usage.get('prompt_tokens', '?')} tokens, "
              f"Output: {usage.get('completion_tokens', '?')} tokens", file=sys.stderr)


if __name__ == "__main__":
    main()
