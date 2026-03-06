#!/usr/bin/env python3
"""
Sonar Deep — Deep Research Tool for Standard Model of Code
===========================================================

Dedicated deep-research tool using Perplexity's sonar-deep-research model.
Unlike the generic perplexity_research.py, this tool is purpose-built for
long-form, multi-step research with optional Collider context injection.

Modes:
    research   Single deep research query (default)
    plan       Multi-query research plan — executes N sub-queries, synthesizes
    context    Inject Collider insights into the research prompt automatically

AUTO-SAVES all research to: particle/docs/research/sonar-deep/

Usage:
    python sonar_deep.py "your deep research question"
    python sonar_deep.py plan "topic" --queries 3
    python sonar_deep.py context "question about this codebase"
    python sonar_deep.py --file query.txt
    python sonar_deep.py --no-save "quick deep query"
"""

import argparse
import json
import os
import subprocess
import sys
import textwrap
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Check for Industrial UI
try:
    import industrial_ui  # noqa: F401
    HAS_INDUSTRIAL_UI = True
except ImportError:
    HAS_INDUSTRIAL_UI = False

# Paths
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
RESEARCH_DIR = PROJECT_ROOT / "particle" / "docs" / "research" / "sonar-deep"

# Model config
MODEL = "sonar-deep-research"
DEFAULT_TIMEOUT = 600  # Deep research needs more time
MAX_RETRIES = 2


def get_api_key() -> str:
    """Get Perplexity API key from Doppler or environment."""
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

    key = os.environ.get("PERPLEXITY_API_KEY")
    if key:
        return key

    raise ValueError("No PERPLEXITY_API_KEY found in Doppler or environment")


def _load_collider_context() -> Optional[str]:
    """Load Collider insights as context string for injection."""
    try:
        from collider_bridge import load_insights, insights_summary, insights_age_days
    except ImportError:
        # Try relative import path
        sys.path.insert(0, str(SCRIPT_DIR))
        try:
            from collider_bridge import load_insights, insights_summary, insights_age_days
        except ImportError:
            return None

    insights = load_insights(PROJECT_ROOT)
    if insights is None:
        return None

    age = insights_age_days(PROJECT_ROOT)
    if age is not None and age > 7:
        print(f"[sonar-deep] Warning: Collider insights are {age:.1f} days old", file=sys.stderr)

    summary = insights_summary(insights)

    # Build context block from findings
    lines = [f"## Project Context (Collider Analysis)", f"Summary: {summary}", ""]

    for finding in insights.get("findings", [])[:10]:
        cat = finding.get("category", "unknown")
        sev = finding.get("severity", "?")
        msg = finding.get("message", "")
        lines.append(f"- [{sev}] {cat}: {msg}")

    # Include top-level metrics
    metrics = insights.get("metrics", {})
    if metrics:
        lines.append("")
        lines.append("Metrics:")
        for k, v in list(metrics.items())[:8]:
            lines.append(f"  {k}: {v}")

    return "\n".join(lines)


def deep_research(query: str, timeout: int = DEFAULT_TIMEOUT,
                  system_context: Optional[str] = None) -> Dict:
    """
    Execute a deep research query using Perplexity sonar-deep-research.

    Args:
        query: The research question
        timeout: Request timeout in seconds (default 600)
        system_context: Optional system message for context injection

    Returns:
        dict with 'content', 'citations', 'usage', 'model', 'elapsed_seconds'
    """
    import httpx

    api_key = get_api_key()

    print(f"[sonar-deep] Model: {MODEL}", file=sys.stderr)
    print(f"[sonar-deep] Query: {len(query)} chars | Timeout: {timeout}s", file=sys.stderr)
    if system_context:
        print(f"[sonar-deep] Context injected: {len(system_context)} chars", file=sys.stderr)

    messages = []
    if system_context:
        messages.append({"role": "system", "content": system_context})
    messages.append({"role": "user", "content": query})

    start = time.time()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = httpx.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": MODEL,
                    "messages": messages,
                    "return_citations": True
                },
                timeout=float(timeout)
            )
            response.raise_for_status()
            data = response.json()
            elapsed = time.time() - start

            print(f"[sonar-deep] Completed in {elapsed:.1f}s", file=sys.stderr)

            return {
                "content": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                "citations": data.get("citations", []),
                "usage": data.get("usage", {}),
                "model": MODEL,
                "elapsed_seconds": round(elapsed, 1)
            }

        except httpx.TimeoutException:
            if attempt < MAX_RETRIES:
                print(f"[sonar-deep] Timeout on attempt {attempt}, retrying...", file=sys.stderr)
                continue
            print(f"[sonar-deep] Timeout after {timeout}s x {MAX_RETRIES} attempts", file=sys.stderr)
            raise
        except httpx.HTTPStatusError as e:
            print(f"[sonar-deep] HTTP {e.response.status_code}: {e.response.text}", file=sys.stderr)
            raise

    # Should not reach here
    raise RuntimeError("Exhausted retries")


def plan_research(topic: str, num_queries: int = 3,
                  timeout: int = DEFAULT_TIMEOUT) -> Dict:
    """
    Multi-query research plan: generate sub-questions, research each, synthesize.

    Args:
        topic: The broad research topic
        num_queries: Number of sub-queries to generate and research
        timeout: Timeout per query

    Returns:
        dict with 'topic', 'sub_queries', 'results', 'synthesis', 'total_elapsed'
    """
    print(f"[sonar-deep] Plan mode: {num_queries} sub-queries for '{topic[:60]}'", file=sys.stderr)

    # Step 1: Generate sub-queries
    planner_prompt = textwrap.dedent(f"""\
        I need to deeply research this topic: {topic}

        Generate exactly {num_queries} specific, non-overlapping research sub-questions
        that together would provide comprehensive coverage of this topic.

        Return ONLY the questions, one per line, numbered 1-{num_queries}.
        No preamble, no explanations — just the questions.
    """)

    plan_result = deep_research(planner_prompt, timeout=min(timeout, 120))
    sub_queries = _parse_numbered_lines(plan_result["content"], num_queries)

    if not sub_queries:
        print("[sonar-deep] Warning: Could not parse sub-queries, using topic directly", file=sys.stderr)
        sub_queries = [topic]

    print(f"[sonar-deep] Generated {len(sub_queries)} sub-queries:", file=sys.stderr)
    for i, q in enumerate(sub_queries, 1):
        print(f"  {i}. {q[:80]}", file=sys.stderr)

    # Step 2: Research each sub-query
    results = []
    total_start = time.time()

    for i, sq in enumerate(sub_queries, 1):
        print(f"\n[sonar-deep] Researching {i}/{len(sub_queries)}...", file=sys.stderr)
        try:
            r = deep_research(sq, timeout=timeout)
            results.append({"query": sq, "result": r})
        except Exception as e:
            print(f"[sonar-deep] Sub-query {i} failed: {e}", file=sys.stderr)
            results.append({"query": sq, "error": str(e)})

    # Step 3: Synthesize
    print(f"\n[sonar-deep] Synthesizing {len(results)} results...", file=sys.stderr)
    synthesis_parts = []
    all_citations = []

    for i, item in enumerate(results, 1):
        if "error" in item:
            synthesis_parts.append(f"## Sub-query {i}: {item['query']}\n\n*Failed: {item['error']}*")
        else:
            synthesis_parts.append(
                f"## Sub-query {i}: {item['query']}\n\n{item['result']['content']}"
            )
            all_citations.extend(item["result"].get("citations", []))

    synthesis_body = "\n\n---\n\n".join(synthesis_parts)

    # Deduplicate citations
    seen = set()
    unique_citations = []
    for c in all_citations:
        if c not in seen:
            seen.add(c)
            unique_citations.append(c)

    total_elapsed = time.time() - total_start

    return {
        "topic": topic,
        "sub_queries": sub_queries,
        "results": results,
        "synthesis": synthesis_body,
        "citations": unique_citations,
        "model": MODEL,
        "total_elapsed": round(total_elapsed, 1)
    }


def _parse_numbered_lines(text: str, expected: int) -> List[str]:
    """Parse numbered lines (1. ..., 2. ...) from text."""
    lines = []
    for line in text.strip().splitlines():
        line = line.strip()
        # Match patterns like "1. question" or "1) question"
        for prefix_len in range(1, 4):
            prefix_num = line[:prefix_len]
            if prefix_num.isdigit():
                rest = line[prefix_len:].lstrip(".)")
                rest = rest.strip()
                if rest:
                    lines.append(rest)
                    break
    return lines[:expected]


def auto_save(query: str, result: Dict, mode: str) -> Path:
    """
    Auto-save research output to particle/docs/research/sonar-deep/.

    Returns:
        Path to saved file
    """
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = "".join(c if c.isalnum() else "_" for c in query[:50]).strip("_").lower()
    filename = f"{timestamp}_{mode}_{slug}.md"

    # Build markdown
    elapsed = result.get("elapsed_seconds") or result.get("total_elapsed", "?")
    content = f"""# Sonar Deep Research: {query[:100]}{'...' if len(query) > 100 else ''}

> **Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
> **Model:** {MODEL}
> **Mode:** {mode}
> **Elapsed:** {elapsed}s
> **Query Length:** {len(query)} chars

---

## Query

{query}

---

"""

    if mode == "plan":
        content += f"## Research Plan\n\n"
        for i, sq in enumerate(result.get("sub_queries", []), 1):
            content += f"{i}. {sq}\n"
        content += f"\n---\n\n{result.get('synthesis', 'No synthesis')}\n"
    else:
        content += f"## Response\n\n{result.get('content', 'No content')}\n"

    # Citations
    citations = result.get("citations", [])
    content += "\n---\n\n## Citations\n\n"
    if citations:
        for i, c in enumerate(citations, 1):
            content += f"{i}. {c}\n"
    else:
        content += "_No citations provided_\n"

    # Usage stats
    usage = result.get("usage", {})
    if usage:
        content += f"""
---

## Usage Stats

- Input tokens: {usage.get('prompt_tokens', 'N/A')}
- Output tokens: {usage.get('completion_tokens', 'N/A')}
"""

    filepath = RESEARCH_DIR / filename
    filepath.write_text(content)
    return filepath


def _print_styled(result: Dict, query: str, mode: str, saved_path: Optional[Path]):
    """Industrial UI styled output."""
    from industrial_ui import PerplexityUI as PUI, Colors as C
    ui = PUI()
    ui.header("SONAR DEEP RESEARCH")
    print(f"    {C.DIM}Model:{C.RESET}  {MODEL}")
    print(f"    {C.DIM}Mode:{C.RESET}   {mode}")
    elapsed = result.get("elapsed_seconds") or result.get("total_elapsed", "?")
    print(f"    {C.DIM}Time:{C.RESET}   {elapsed}s")
    ui.blank()
    ui.query_info(query, len(query))
    ui.blank()

    if mode == "plan":
        ui.section("RESEARCH PLAN")
        for i, sq in enumerate(result.get("sub_queries", []), 1):
            print(f"    {C.DIM}{i}.{C.RESET} {sq}")
        ui.blank()
        ui.section("SYNTHESIS")
        print()
        print(result.get("synthesis", "No synthesis"))
    else:
        ui.section("RESPONSE")
        print()
        print(result.get("content", "No content"))

    print()

    citations = result.get("citations", [])
    if citations:
        ui.citations_section(citations)
        ui.blank()

    usage = result.get("usage", {})
    if usage:
        ui.section("USAGE")
        print(f"    {C.DIM}Input:{C.RESET}  {usage.get('prompt_tokens', '?'):,} tokens")
        print(f"    {C.DIM}Output:{C.RESET} {usage.get('completion_tokens', '?'):,} tokens")
        ui.blank()

    if saved_path:
        ui.info(f"Saved: {saved_path}")

    ui.footer()


def _print_plain(result: Dict, query: str, mode: str, saved_path: Optional[Path]):
    """Plain text fallback output."""
    elapsed = result.get("elapsed_seconds") or result.get("total_elapsed", "?")
    print(f"=== Sonar Deep Research ({mode}) ===")
    print(f"Model: {MODEL} | Elapsed: {elapsed}s\n")

    if mode == "plan":
        print("--- Research Plan ---")
        for i, sq in enumerate(result.get("sub_queries", []), 1):
            print(f"  {i}. {sq}")
        print(f"\n--- Synthesis ---\n")
        print(result.get("synthesis", "No synthesis"))
    else:
        print(result.get("content", "No content"))

    citations = result.get("citations", [])
    if citations:
        print("\n--- Citations ---")
        for i, c in enumerate(citations, 1):
            print(f"  {i}. {c}")

    usage = result.get("usage", {})
    if usage:
        print(f"\n[Usage] Input: {usage.get('prompt_tokens', '?')} tokens, "
              f"Output: {usage.get('completion_tokens', '?')} tokens", file=sys.stderr)

    if saved_path:
        print(f"\n[Saved] {saved_path}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Sonar Deep — Deep Research Tool (Perplexity sonar-deep-research)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Modes:
              research   Single deep research query (default)
              plan       Multi-query research plan with synthesis
              context    Inject Collider project insights into query

            Examples:
              %(prog)s "What are the latest advances in code analysis?"
              %(prog)s plan "static analysis techniques" --queries 4
              %(prog)s context "How does this project compare to industry standards?"
              %(prog)s --file research_question.txt
        """)
    )

    parser.add_argument("mode", nargs="?", default="research",
                        choices=["research", "plan", "context"],
                        help="Research mode (default: research)")
    parser.add_argument("query", nargs="?", help="Research query")
    parser.add_argument("--file", "-f", help="Read query from file")
    parser.add_argument("--queries", "-q", type=int, default=3,
                        help="Number of sub-queries for plan mode (default: 3)")
    parser.add_argument("--timeout", "-t", type=int, default=DEFAULT_TIMEOUT,
                        help=f"Timeout per query in seconds (default: {DEFAULT_TIMEOUT})")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--no-save", action="store_true",
                        help="Skip auto-save to research directory")

    args = parser.parse_args()

    # Resolve query
    if args.file:
        query = Path(args.file).read_text().strip()
    elif args.query:
        query = args.query
    elif not sys.stdin.isatty():
        print("Reading query from stdin...", file=sys.stderr)
        query = sys.stdin.read().strip()
    else:
        parser.print_help()
        sys.exit(1)

    if not query:
        print("Error: Empty query", file=sys.stderr)
        sys.exit(1)

    # Execute
    try:
        if args.mode == "plan":
            result = plan_research(query, num_queries=args.queries, timeout=args.timeout)
        elif args.mode == "context":
            ctx = _load_collider_context()
            if ctx:
                print(f"[sonar-deep] Collider context loaded ({len(ctx)} chars)", file=sys.stderr)
            else:
                print("[sonar-deep] No Collider context available, proceeding without", file=sys.stderr)
            result = deep_research(query, timeout=args.timeout, system_context=ctx)
        else:
            result = deep_research(query, timeout=args.timeout)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Auto-save
    saved_path = None
    if not args.no_save:
        try:
            saved_path = auto_save(query, result, args.mode)
            print(f"[Auto-saved] {saved_path}", file=sys.stderr)
        except Exception as e:
            print(f"[Auto-save failed] {e}", file=sys.stderr)

    # Output
    if args.json:
        output = json.dumps(result, indent=2, default=str)
        if args.output:
            Path(args.output).write_text(output)
            print(f"Output written to {args.output}", file=sys.stderr)
        else:
            print(output)
    elif args.output:
        # File output — plain text
        if args.mode == "plan":
            text = result.get("synthesis", "")
        else:
            text = result.get("content", "")
        Path(args.output).write_text(text)
        print(f"Output written to {args.output}", file=sys.stderr)
    elif HAS_INDUSTRIAL_UI:
        _print_styled(result, query, args.mode, saved_path)
    else:
        _print_plain(result, query, args.mode, saved_path)


if __name__ == "__main__":
    main()
