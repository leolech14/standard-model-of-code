#!/usr/bin/env python3
"""
INDUSTRIAL UI - Shared Terminal Output Styling

Consistent ANSI-styled terminal output for AI tools.
Each tool gets its own primary color:

| Tool           | Primary | Accent  |
|----------------|---------|---------|
| Gemini         | BLUE    | CYAN    |
| Perplexity     | GREEN   | CYAN    |
| Industrial     | YELLOW  | MAGENTA |

Usage:
    from industrial_ui import GeminiUI, PerplexityUI

    # Gemini
    ui = GeminiUI()
    ui.header("GEMINI ANALYSIS")
    ui.section("CONTEXT")
    ui.item("brain.yaml", "loaded")
    ui.progress_bar("Processing", 0.75)
    ui.footer()

    # Perplexity
    ui = PerplexityUI()
    ui.header("PERPLEXITY RESEARCH")
    ui.citation(1, "https://example.com", "Example Source")
    ui.footer()
"""

from abc import ABC
from typing import Optional

# ============================================================================
# ANSI COLOR CODES
# ============================================================================

class Colors:
    """ANSI escape codes for terminal colors."""
    # Primary colors
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    # Modifiers
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    # Reset
    RESET = "\033[0m"

    # Background (optional)
    BG_BLUE = "\033[44m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"


# ============================================================================
# BASE INDUSTRIAL UI
# ============================================================================

class IndustrialUI(ABC):
    """Base class for industrial-style terminal output."""

    # Override in subclasses
    PRIMARY = Colors.WHITE
    ACCENT = Colors.CYAN
    NAME = "INDUSTRIAL"

    def __init__(self, width: int = 70):
        self.width = width

    def header(self, title: str):
        """Print industrial header with double-line border."""
        bar = "═" * self.width
        print()
        print(f"{self.PRIMARY}{bar}{Colors.RESET}")
        print(f"{self.PRIMARY}  {title}{Colors.RESET}")
        print(f"{self.PRIMARY}{bar}{Colors.RESET}")
        print()

    def footer(self):
        """Print industrial footer."""
        bar = "═" * self.width
        print()
        print(f"{self.PRIMARY}{bar}{Colors.RESET}")
        print()

    def section(self, title: str):
        """Print section header with thin line."""
        print(f"  {self.ACCENT}{title}{Colors.RESET}")
        print(f"  {Colors.DIM}{'─' * 50}{Colors.RESET}")

    def item(self, label: str, value: str, color: Optional[str] = None):
        """Print a labeled item."""
        c = color or Colors.RESET
        print(f"    {Colors.DIM}{label}:{Colors.RESET} {c}{value}{Colors.RESET}")

    def bullet(self, text: str, symbol: str = "▸"):
        """Print a bullet point."""
        print(f"    {self.ACCENT}{symbol}{Colors.RESET} {text}")

    def success(self, text: str):
        """Print success message."""
        print(f"    {Colors.GREEN}✓{Colors.RESET} {text}")

    def error(self, text: str):
        """Print error message."""
        print(f"    {Colors.RED}✗{Colors.RESET} {text}")

    def warning(self, text: str):
        """Print warning message."""
        print(f"    {Colors.YELLOW}⚠{Colors.RESET} {text}")

    def info(self, text: str):
        """Print info message (dim)."""
        print(f"  {Colors.DIM}{text}{Colors.RESET}")

    def progress_bar(self, label: str, fraction: float, width: int = 30):
        """Print a progress bar."""
        filled = int(fraction * width)
        bar = "█" * filled + "░" * (width - filled)
        pct = fraction * 100
        print(f"  {label} {bar} {Colors.BOLD}{pct:5.1f}%{Colors.RESET}")

    def stats_row(self, label: str, count: int, total: int, color: Optional[str] = None):
        """Print a stats row with bar chart."""
        c = color or self.PRIMARY
        pct = count / max(total, 1) * 100
        bar_len = int((count / max(total, 1)) * 30)
        bar = "█" * bar_len + "░" * (30 - bar_len)
        print(f"  {c}{label:3}{Colors.RESET} {bar} {Colors.BOLD}{count:3}{Colors.RESET} ({pct:5.1f}%)")

    def divider(self):
        """Print thin divider."""
        print(f"  {Colors.DIM}{'─' * 50}{Colors.RESET}")

    def blank(self):
        """Print blank line."""
        print()


# ============================================================================
# GEMINI UI (BLUE)
# ============================================================================

class GeminiUI(IndustrialUI):
    """Blue-themed UI for Gemini/analyze.py outputs."""

    PRIMARY = Colors.BLUE
    ACCENT = Colors.CYAN
    NAME = "GEMINI"

    def model_info(self, model: str, backend: str = "AI Studio"):
        """Print model information box."""
        print(f"  {Colors.DIM}Model:{Colors.RESET} {Colors.BOLD}{model}{Colors.RESET}")
        print(f"  {Colors.DIM}Backend:{Colors.RESET} {backend}")

    def token_stats(self, input_tokens: int, output_tokens: int,
                    cost: Optional[float] = None):
        """Print token usage statistics."""
        self.section("TOKEN USAGE")
        print(f"    {Colors.DIM}Input:{Colors.RESET}  {input_tokens:,} tokens")
        print(f"    {Colors.DIM}Output:{Colors.RESET} {output_tokens:,} tokens")
        if cost is not None:
            print(f"    {Colors.DIM}Cost:{Colors.RESET}   ${cost:.4f}")

    def aci_routing(self, tier: str, confidence: float, reason: str):
        """Print ACI routing decision."""
        tier_colors = {
            "INSTANT": Colors.GREEN,
            "RAG": Colors.CYAN,
            "LONG_CONTEXT": Colors.BLUE,
            "PERPLEXITY": Colors.MAGENTA,
        }
        color = tier_colors.get(tier.upper(), Colors.WHITE)

        self.section("ACI ROUTING")
        print(f"    {Colors.DIM}Tier:{Colors.RESET}       {color}{Colors.BOLD}{tier}{Colors.RESET}")
        print(f"    {Colors.DIM}Confidence:{Colors.RESET} {confidence:.0%}")
        print(f"    {Colors.DIM}Reason:{Colors.RESET}     {reason}")

    def context_summary(self, file_count: int, total_tokens: int,
                       set_name: Optional[str] = None):
        """Print context loading summary."""
        self.section("CONTEXT")
        if set_name:
            print(f"    {Colors.DIM}Set:{Colors.RESET}    {set_name}")
        print(f"    {Colors.DIM}Files:{Colors.RESET}  {file_count}")
        print(f"    {Colors.DIM}Tokens:{Colors.RESET} {total_tokens:,}")


# ============================================================================
# PERPLEXITY UI (GREEN)
# ============================================================================

class PerplexityUI(IndustrialUI):
    """Green-themed UI for Perplexity research outputs."""

    PRIMARY = Colors.GREEN
    ACCENT = Colors.CYAN
    NAME = "PERPLEXITY"

    def model_info(self, model: str):
        """Print model information."""
        print(f"  {Colors.DIM}Model:{Colors.RESET} {Colors.BOLD}{model}{Colors.RESET}")

    def citation(self, index: int, url: str, title: Optional[str] = None):
        """Print a single citation."""
        if title:
            print(f"    {self.ACCENT}[{index}]{Colors.RESET} {title}")
            print(f"        {Colors.DIM}{url}{Colors.RESET}")
        else:
            print(f"    {self.ACCENT}[{index}]{Colors.RESET} {url}")

    def citations_section(self, citations: list):
        """Print all citations in a section."""
        self.section(f"CITATIONS ({len(citations)})")
        for i, citation in enumerate(citations, 1):
            if isinstance(citation, dict):
                self.citation(i, citation.get('url', ''), citation.get('title'))
            else:
                self.citation(i, str(citation))

    def query_info(self, query: str, char_count: Optional[int] = None):
        """Print query information."""
        self.section("QUERY")
        # Truncate long queries
        if len(query) > 100:
            display = query[:97] + "..."
        else:
            display = query
        print(f"    {display}")
        if char_count:
            print(f"    {Colors.DIM}({char_count} chars){Colors.RESET}")

    def save_location(self, path: str):
        """Print save location."""
        print(f"  {Colors.DIM}Saved:{Colors.RESET} {path}")


# ============================================================================
# TRIAGE UI (YELLOW) - For industrial_triage.py
# ============================================================================

class TriageUI(IndustrialUI):
    """Yellow-themed UI for inbox triage."""

    PRIMARY = Colors.YELLOW
    ACCENT = Colors.MAGENTA
    NAME = "TRIAGE"

    GRADE_COLORS = {
        "A+": Colors.GREEN,
        "A": Colors.GREEN,
        "B": Colors.YELLOW,
        "C": Colors.YELLOW,
        "F": Colors.RED,
    }

    def grade_distribution(self, distribution: dict, total: int):
        """Print grade distribution chart."""
        self.section("GRADE DISTRIBUTION")
        for grade in ["A+", "A", "B", "C", "F"]:
            count = distribution.get(grade, 0)
            color = self.GRADE_COLORS.get(grade, Colors.WHITE)
            self.stats_row(grade, count, total, color)

    def promotable_items(self, items: list, max_show: int = 10):
        """Print promotable items list."""
        self.section(f"READY TO PROMOTE ({len(items)})")
        for item in items[:max_show]:
            id_ = item.get('id', '?')
            conf = item.get('confidence', item.get('_overall', 0))
            title = item.get('title', '?')[:40]
            print(f"    {Colors.GREEN}✓{Colors.RESET} {id_:10} {conf:3}% {title}")
        if len(items) > max_show:
            print(f"    {Colors.DIM}... and {len(items) - max_show} more{Colors.RESET}")

    def needs_research(self, items: list, max_show: int = 10):
        """Print items needing research."""
        self.section(f"NEEDS RESEARCH ({len(items)})")
        for item in items[:max_show]:
            id_ = item.get('id', '?')
            overall = item.get('overall', 50)
            gap = item.get('gap_to_A', 85 - overall)
            weak = item.get('weakest_dimension', '?')[:3]
            title = item.get('title', '?')[:30]
            print(f"    {Colors.YELLOW}?{Colors.RESET} {id_:10} {overall:3}% (+{gap} needed) [{weak}] {title}")
        if len(items) > max_show:
            print(f"    {Colors.DIM}... and {len(items) - max_show} more{Colors.RESET}")


# ============================================================================
# CONVENIENCE EXPORTS
# ============================================================================

# Pre-instantiated UIs for quick use
gemini_ui = GeminiUI()
perplexity_ui = PerplexityUI()
triage_ui = TriageUI()


if __name__ == "__main__":
    # Demo all three styles
    print("\n" + "=" * 70)
    print("INDUSTRIAL UI DEMO")
    print("=" * 70)

    # Gemini demo
    ui = GeminiUI()
    ui.header("GEMINI ANALYSIS")
    ui.model_info("gemini-3-pro-preview", "AI Studio")
    ui.blank()
    ui.context_summary(12, 45000, "pipeline")
    ui.blank()
    ui.aci_routing("LONG_CONTEXT", 0.92, "Complex reasoning query")
    ui.blank()
    ui.token_stats(45000, 2500, 0.0234)
    ui.footer()

    # Perplexity demo
    ui = PerplexityUI()
    ui.header("PERPLEXITY RESEARCH")
    ui.model_info("sonar-pro")
    ui.blank()
    ui.query_info("What are the best practices for OKLCH color spaces in data visualization?", 78)
    ui.blank()
    ui.citations_section([
        "https://oklch.com/",
        "https://css-tricks.com/oklch-in-css/",
        "https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/oklch",
    ])
    ui.blank()
    ui.save_location("docs/research/perplexity/20260123_171500_oklch.md")
    ui.footer()

    # Triage demo
    ui = TriageUI()
    ui.header("INDUSTRIAL TRIAGE REPORT")
    ui.info("Generated: 2026-01-23 17:15:00")
    ui.info("Total Inbox: 33 opportunities")
    ui.blank()
    ui.grade_distribution({"A+": 1, "A": 4, "B": 24, "C": 3, "F": 1}, 33)
    ui.footer()
