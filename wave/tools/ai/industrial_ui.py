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
# CONTEXT INJECTION UI - Transparency for AI agents and humans
# ============================================================================

class ContextUI(IndustrialUI):
    """
    Transparent display of what's going INTO the context window.

    This is the key to Stone Tool ergonomics: both AI and human
    can see exactly what the model will "see".
    """

    PRIMARY = Colors.MAGENTA
    ACCENT = Colors.CYAN
    NAME = "CONTEXT"

    def injection_header(self, query: str, tier: str, model: str):
        """Show the query and routing decision."""
        self.header("CONTEXT INJECTION REPORT")

        # Query (truncated)
        q_display = query[:60] + "..." if len(query) > 60 else query
        print(f"  {Colors.DIM}Query:{Colors.RESET} {Colors.BOLD}{q_display}{Colors.RESET}")

        # Tier with color coding
        tier_colors = {
            "instant": Colors.GREEN,
            "rag": Colors.CYAN,
            "long_context": Colors.BLUE,
            "perplexity": Colors.GREEN,
            "flash_deep": Colors.MAGENTA,
            "hybrid": Colors.YELLOW,
        }
        tc = tier_colors.get(tier.lower(), Colors.WHITE)
        print(f"  {Colors.DIM}Tier:{Colors.RESET}  {tc}{Colors.BOLD}{tier.upper()}{Colors.RESET}")
        print(f"  {Colors.DIM}Model:{Colors.RESET} {model}")
        print()

    def sets_used(self, sets: list, merged: bool = False):
        """Show which analysis sets are being used."""
        label = "MERGED SETS" if merged else "SETS"
        self.section(label)
        for s in sets:
            print(f"    {self.ACCENT}◆{Colors.RESET} {s}")
        print()

    def files_included(self, files: list, show_tokens: bool = True, max_show: int = 10):
        """Show files that ARE in context."""
        self.section(f"FILES INCLUDED ({len(files)})")

        total_tokens = 0
        for i, f in enumerate(files[:max_show]):
            if isinstance(f, dict):
                path = f.get('path', str(f))
                tokens = f.get('tokens', 0)
                total_tokens += tokens
                if show_tokens:
                    print(f"    {Colors.GREEN}✓{Colors.RESET} {path} {Colors.DIM}({tokens:,} tok){Colors.RESET}")
                else:
                    print(f"    {Colors.GREEN}✓{Colors.RESET} {path}")
            else:
                print(f"    {Colors.GREEN}✓{Colors.RESET} {f}")

        if len(files) > max_show:
            print(f"    {Colors.DIM}... and {len(files) - max_show} more files{Colors.RESET}")

        if show_tokens and total_tokens > 0:
            print(f"    {Colors.DIM}─────────────────────────{Colors.RESET}")
            print(f"    {Colors.BOLD}Total: {total_tokens:,} tokens{Colors.RESET}")
        print()

    def files_excluded(self, files: list, max_show: int = 5):
        """Show files that were EXCLUDED and why."""
        if not files:
            return

        self.section(f"FILES EXCLUDED ({len(files)})")

        # Group by reason
        by_reason = {}
        for f in files:
            if isinstance(f, dict):
                reason = f.get('reason', 'unknown')
                path = f.get('path', str(f))
            else:
                reason = 'unknown'
                path = str(f)
            by_reason.setdefault(reason, []).append(path)

        for reason, paths in by_reason.items():
            reason_display = reason.replace('_', ' ').title()
            print(f"    {Colors.YELLOW}⚠{Colors.RESET} {reason_display}: {len(paths)} files")
            for p in paths[:2]:
                print(f"      {Colors.DIM}└─ {p}{Colors.RESET}")
            if len(paths) > 2:
                print(f"      {Colors.DIM}└─ ... and {len(paths) - 2} more{Colors.RESET}")
        print()

    def injections(self, injections: list):
        """Show what was injected (critical files, architect docs, etc.)."""
        if not injections:
            return

        self.section("INJECTIONS")

        for inj in injections:
            inj_type = inj.get('type', 'unknown')
            strategy = inj.get('strategy', '')
            files = inj.get('files', [])
            tokens = inj.get('tokens', 0)

            # Icon by type
            icons = {
                'critical_files': '★',
                'architect_docs': '📐',
                'agent_kernel': '🤖',
                'agent_tasks': '📋',
                'deck_snapshot': '🎴',
            }
            icon = icons.get(inj_type, '◆')

            print(f"    {Colors.CYAN}{icon}{Colors.RESET} {inj_type}")
            if strategy:
                print(f"      {Colors.DIM}Strategy: {strategy}{Colors.RESET}")
            if files:
                for f in files[:3]:
                    print(f"      {Colors.DIM}└─ {f}{Colors.RESET}")
            if tokens:
                print(f"      {Colors.DIM}Tokens: {tokens:,}{Colors.RESET}")
        print()

    def limiting_factor(self, files_used: int, files_limit: int, tokens_used: int, tokens_limit: int):
        """
        Show which constraint is actually limiting the context.
        This is CRITICAL for transparency - users need to know WHY truncation happened.
        """
        self.section("LIMITING FACTOR")

        files_pct = files_used / max(files_limit, 1)
        tokens_pct = tokens_used / max(tokens_limit, 1)

        # Determine the bottleneck
        if files_pct >= 1.0 and tokens_pct < 1.0:
            # File count is the bottleneck
            bottleneck = "FILE_COUNT"
            print(f"    {Colors.YELLOW}►{Colors.RESET} {Colors.BOLD}FILE COUNT{Colors.RESET} is the limiting factor")
            print(f"      {Colors.DIM}You hit the max_files limit ({files_limit}) before token budget{Colors.RESET}")
            print(f"      {Colors.DIM}Tokens used: {tokens_used:,} ({tokens_pct:.0%} of {tokens_limit:,}){Colors.RESET}")
            print(f"      {Colors.GREEN}Tip: Increase --max-files to include more context{Colors.RESET}")
        elif tokens_pct >= 0.9:
            # Token budget is the bottleneck
            bottleneck = "TOKEN_BUDGET"
            print(f"    {Colors.RED}►{Colors.RESET} {Colors.BOLD}TOKEN BUDGET{Colors.RESET} is the limiting factor")
            print(f"      {Colors.DIM}You're at {tokens_pct:.0%} of the {tokens_limit:,} token limit{Colors.RESET}")
            print(f"      {Colors.DIM}Files: {files_used}/{files_limit}{Colors.RESET}")
            print(f"      {Colors.YELLOW}Tip: Use a more focused set or reduce max_files{Colors.RESET}")
        else:
            # Neither is limiting - plenty of headroom
            bottleneck = "NONE"
            print(f"    {Colors.GREEN}►{Colors.RESET} {Colors.BOLD}NO LIMITING FACTOR{Colors.RESET} - plenty of headroom")
            print(f"      {Colors.DIM}Files: {files_used}/{files_limit} ({files_pct:.0%}){Colors.RESET}")
            print(f"      {Colors.DIM}Tokens: {tokens_used:,}/{tokens_limit:,} ({tokens_pct:.0%}){Colors.RESET}")

        print()

        # Visual comparison bars
        bar_width = 30

        # Files bar
        files_filled = int(files_pct * bar_width)
        files_color = Colors.RED if files_pct >= 1.0 else Colors.GREEN
        files_bar = f"{files_color}{'█' * min(files_filled, bar_width)}{Colors.DIM}{'░' * (bar_width - min(files_filled, bar_width))}{Colors.RESET}"
        print(f"    Files:  {files_bar} {files_used}/{files_limit}")

        # Tokens bar
        tokens_filled = int(tokens_pct * bar_width)
        tokens_color = Colors.RED if tokens_pct >= 0.9 else Colors.YELLOW if tokens_pct >= 0.7 else Colors.GREEN
        tokens_bar = f"{tokens_color}{'█' * min(tokens_filled, bar_width)}{Colors.DIM}{'░' * (bar_width - min(tokens_filled, bar_width))}{Colors.RESET}"
        print(f"    Tokens: {tokens_bar} {tokens_used:,}/{tokens_limit:,}")

        print()
        return bottleneck

    def budget_bar(self, used: int, limit: int, label: str = "Context Budget"):
        """Show context budget usage with visual bar."""
        pct = min(used / max(limit, 1), 1.0)

        # Color based on usage
        if pct > 0.9:
            color = Colors.RED
        elif pct > 0.7:
            color = Colors.YELLOW
        else:
            color = Colors.GREEN

        bar_width = 40
        filled = int(pct * bar_width)
        bar = f"{color}{'█' * filled}{Colors.DIM}{'░' * (bar_width - filled)}{Colors.RESET}"

        print(f"  {label}")
        print(f"  {bar} {Colors.BOLD}{pct:.0%}{Colors.RESET}")
        print(f"  {Colors.DIM}{used:,} / {limit:,} tokens{Colors.RESET}")

        if pct > 0.9:
            print(f"  {Colors.RED}⚠ Near limit - some content may be truncated{Colors.RESET}")
        print()

    def query_schema(self, config: dict):
        """
        Show the full query schema and defaults.

        config should contain:
        - model: str (actual model being used)
        - model_default: str (default model)
        - tier: str (actual tier)
        - tier_default: str (default tier or "auto")
        - mode: str (actual mode)
        - mode_default: str (default mode)
        - max_files: int (actual limit)
        - max_files_default: int (default limit)
        - max_tokens: int (context budget)
        - line_numbers: bool
        - backend: str (ai_studio, vertex)
        - aci_enabled: bool
        - set_name: str (if using a set)
        - set_config: dict (set metadata if available)
        """
        self.section("QUERY SCHEMA & DEFAULTS")

        # Model
        model = config.get('model', 'unknown')
        model_default = config.get('model_default', 'gemini-3-pro-preview')
        is_model_default = model == model_default
        model_tag = f"{Colors.DIM}(default){Colors.RESET}" if is_model_default else f"{Colors.YELLOW}(override){Colors.RESET}"
        print(f"    {Colors.DIM}model:{Colors.RESET}       {Colors.BOLD}{model}{Colors.RESET} {model_tag}")

        # Tier
        tier = config.get('tier', 'long_context')
        tier_default = config.get('tier_default', 'auto')
        aci_enabled = config.get('aci_enabled', False)
        if aci_enabled:
            tier_tag = f"{Colors.CYAN}(ACI auto-selected){Colors.RESET}"
        elif tier == tier_default:
            tier_tag = f"{Colors.DIM}(default){Colors.RESET}"
        else:
            tier_tag = f"{Colors.YELLOW}(override){Colors.RESET}"
        print(f"    {Colors.DIM}tier:{Colors.RESET}        {Colors.BOLD}{tier.upper()}{Colors.RESET} {tier_tag}")

        # Mode
        mode = config.get('mode', 'standard')
        mode_default = config.get('mode_default', 'standard')
        is_mode_default = mode == mode_default
        mode_tag = f"{Colors.DIM}(default){Colors.RESET}" if is_mode_default else f"{Colors.YELLOW}(override){Colors.RESET}"
        print(f"    {Colors.DIM}mode:{Colors.RESET}        {mode} {mode_tag}")

        # Max files
        max_files = config.get('max_files', 50)
        max_files_default = config.get('max_files_default', 50)
        is_files_default = max_files == max_files_default
        files_tag = f"{Colors.DIM}(default){Colors.RESET}" if is_files_default else f"{Colors.YELLOW}(override){Colors.RESET}"
        print(f"    {Colors.DIM}max_files:{Colors.RESET}   {max_files} {files_tag}")

        # Max tokens (context budget)
        max_tokens = config.get('max_tokens', 1_000_000)
        print(f"    {Colors.DIM}max_tokens:{Colors.RESET}  {max_tokens:,}")

        # Line numbers
        line_numbers = config.get('line_numbers', False)
        ln_status = f"{Colors.GREEN}enabled{Colors.RESET}" if line_numbers else f"{Colors.DIM}disabled{Colors.RESET}"
        print(f"    {Colors.DIM}line_nums:{Colors.RESET}   {ln_status}")

        # Backend
        backend = config.get('backend', 'ai_studio')
        print(f"    {Colors.DIM}backend:{Colors.RESET}     {backend}")

        print()

        # Set-specific config if available
        set_name = config.get('set_name')
        set_config = config.get('set_config', {})
        if set_name:
            self.section(f"SET: {set_name.upper()}")
            desc = set_config.get('description', '(no description)')
            print(f"    {Colors.DIM}description:{Colors.RESET} {desc}")

            # Show set-specific overrides
            set_max_tokens = set_config.get('max_tokens')
            if set_max_tokens:
                print(f"    {Colors.DIM}set_budget:{Colors.RESET}  {set_max_tokens:,} tokens")

            set_auto_interactive = set_config.get('auto_interactive', False)
            if set_auto_interactive:
                print(f"    {Colors.DIM}auto_interactive:{Colors.RESET} {Colors.GREEN}yes{Colors.RESET}")

            critical_files = set_config.get('critical_files', [])
            if critical_files:
                print(f"    {Colors.DIM}critical_files:{Colors.RESET} {len(critical_files)}")

            positional_strategy = set_config.get('positional_strategy')
            if positional_strategy:
                print(f"    {Colors.DIM}strategy:{Colors.RESET}    {positional_strategy}")

            includes = set_config.get('includes', [])
            if includes:
                print(f"    {Colors.DIM}includes:{Colors.RESET}    {', '.join(includes)}")

            patterns = set_config.get('patterns', [])
            if patterns:
                print(f"    {Colors.DIM}patterns:{Colors.RESET}    {len(patterns)} patterns")
                for p in patterns[:3]:
                    print(f"      {Colors.DIM}└─ {p}{Colors.RESET}")
                if len(patterns) > 3:
                    print(f"      {Colors.DIM}└─ ... and {len(patterns) - 3} more{Colors.RESET}")

            print()

        # ACI routing info if enabled
        if aci_enabled:
            self.section("ACI ROUTING")
            aci_confidence = config.get('aci_confidence', 0)
            aci_reason = config.get('aci_reason', '')
            aci_sets = config.get('aci_sets', [])

            print(f"    {Colors.DIM}confidence:{Colors.RESET}  {aci_confidence:.0%}")
            if aci_reason:
                print(f"    {Colors.DIM}reason:{Colors.RESET}      {aci_reason}")
            if aci_sets:
                print(f"    {Colors.DIM}selected_sets:{Colors.RESET} {', '.join(aci_sets)}")
            print()

    def truncation_warning(self, truncated: bool, original_files: int, included_files: int):
        """Show truncation warning if applicable."""
        if not truncated:
            return

        cut = original_files - included_files
        print(f"  {Colors.RED}{'─' * 50}{Colors.RESET}")
        print(f"  {Colors.RED}⚠ TRUNCATION OCCURRED{Colors.RESET}")
        print(f"  {Colors.DIM}Original: {original_files} files → Included: {included_files} files{Colors.RESET}")
        print(f"  {Colors.DIM}{cut} files were cut to fit context window{Colors.RESET}")
        print()


class ThreadUI(IndustrialUI):
    """
    Quick reference for conversation threads / session history.
    """

    PRIMARY = Colors.CYAN
    ACCENT = Colors.BLUE
    NAME = "THREAD"

    def thread_header(self, session_id: str, turn_count: int):
        """Show thread header."""
        self.header(f"THREAD: {session_id[:20]}...")
        print(f"  {Colors.DIM}Turns:{Colors.RESET} {turn_count}")
        print()

    def turn(self, index: int, role: str, content: str, tokens: int = 0):
        """Show a single turn in the thread."""
        role_colors = {
            'user': Colors.GREEN,
            'assistant': Colors.BLUE,
            'system': Colors.YELLOW,
        }
        color = role_colors.get(role.lower(), Colors.WHITE)

        # Truncate content
        preview = content[:80].replace('\n', ' ')
        if len(content) > 80:
            preview += "..."

        print(f"  {Colors.DIM}[{index}]{Colors.RESET} {color}{role.upper()}{Colors.RESET}")
        print(f"      {preview}")
        if tokens:
            print(f"      {Colors.DIM}({tokens:,} tokens){Colors.RESET}")

    def turns_summary(self, turns: list, max_show: int = 5):
        """Show recent turns summary."""
        self.section(f"RECENT TURNS ({len(turns)} total)")

        # Show last N turns
        for turn in turns[-max_show:]:
            idx = turn.get('index', 0)
            role = turn.get('role', 'unknown')
            content = turn.get('content', '')
            tokens = turn.get('tokens', 0)
            self.turn(idx, role, content, tokens)

        if len(turns) > max_show:
            print(f"  {Colors.DIM}... {len(turns) - max_show} earlier turns{Colors.RESET}")
        print()


# ============================================================================
# CONVENIENCE EXPORTS
# ============================================================================

# Pre-instantiated UIs for quick use
gemini_ui = GeminiUI()
perplexity_ui = PerplexityUI()
triage_ui = TriageUI()
context_ui = ContextUI()
thread_ui = ThreadUI()


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

    # Context Injection demo (NEW - Stone Tool transparency)
    ui = ContextUI()
    ui.injection_header(
        query="How does atom classification work in the pipeline?",
        tier="long_context",
        model="gemini-3-pro-preview"
    )
    ui.sets_used(["theory", "pipeline", "classifiers"], merged=True)
    ui.files_included([
        {"path": "src/core/full_analysis.py", "tokens": 12500},
        {"path": "src/patterns/atom_classifier.py", "tokens": 8200},
        {"path": "docs/MODEL.md", "tokens": 15000},
        {"path": "schema/atoms.yaml", "tokens": 3400},
    ])
    ui.files_excluded([
        {"path": "archive/old_classifier.py", "reason": "exclude_pattern"},
        {"path": "tests/test_classifier.py", "reason": "max_files_cutoff"},
        {"path": "output/unified_analysis.json", "reason": "too_large"},
    ])
    ui.injections([
        {"type": "critical_files", "strategy": "sandwich", "files": ["docs/MODEL.md", "docs/COLLIDER.md"], "tokens": 18000},
        {"type": "agent_kernel", "files": [".agent/AGENT_KERNEL.md"], "tokens": 5200},
    ])
    ui.budget_bar(used=185000, limit=200000)
    ui.truncation_warning(truncated=True, original_files=67, included_files=50)
    ui.footer()

    # Thread demo (conversation history)
    ui = ThreadUI()
    ui.thread_header("session_20260127_123456", turn_count=8)
    ui.turns_summary([
        {"index": 1, "role": "user", "content": "What is the Stone Tool principle?", "tokens": 120},
        {"index": 2, "role": "assistant", "content": "The Stone Tool principle states that tools MAY be designed...", "tokens": 850},
        {"index": 3, "role": "user", "content": "How does it integrate with TOOLOME?", "tokens": 95},
        {"index": 4, "role": "assistant", "content": "TOOLOME and STONE_TOOLS form a partition of the tool universe...", "tokens": 1200},
    ])
    ui.footer()
