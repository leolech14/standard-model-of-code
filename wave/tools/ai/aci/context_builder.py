"""
Context Builder
===============
SMoC Role: Builder | Domain: Context

Builds optimized context for AI queries:
- Automatic injection of .agent/ context when needed
- Strategic positioning of critical files (sandwich/front-load)
- Context budget management (from aci_config.yaml)
- Truths integration for instant queries

Part of S3 (ACI subsystem).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path
import json
import yaml

# =============================================================================
# CONFIGURATION
# =============================================================================
# Load from aci_config.yaml via the module's config loader.
# Defaults are provided as fallback if config is unavailable.

_DEFAULT_TOKEN_BUDGETS = {
    "guru": 50_000,        # Focused analysis
    "architect": 150_000,  # Multi-file reasoning
    "archeologist": 200_000,  # Deep exploration
    "perilous": 200_001,   # Avoid - lost-in-middle effects
}

_DEFAULT_HARD_CAP = 200_000  # Maximum recommended tokens

def _get_config():
    """Get ACI config, with lazy import to avoid circular dependency."""
    try:
        # Import here to avoid circular import at module load time
        from . import ACI_CONFIG
        return ACI_CONFIG
    except ImportError:
        return {}

def get_token_budgets() -> Dict[str, int]:
    """Get token budgets from config or defaults."""
    config = _get_config()
    config_budgets = config.get("token_budgets", {})
    # Merge config over defaults
    budgets = _DEFAULT_TOKEN_BUDGETS.copy()
    budgets.update(config_budgets)
    return budgets

def get_hard_cap() -> int:
    """Get hard cap from config or default."""
    config = _get_config()
    return config.get("token_budgets", {}).get("hard_cap", _DEFAULT_HARD_CAP)

# Note: Use get_token_budgets() and get_hard_cap() functions directly.
# Module-level constants removed to ensure config is always read.


@dataclass
class OptimizedContext:
    """Result of context optimization."""
    sets: List[str]              # Final list of sets to use
    truths: Optional[Dict]       # Repo truths if loaded
    positioning: str             # "sandwich" or "front-load"
    critical_files: List[str]    # Files to position strategically
    estimated_tokens: int        # Estimated total token count
    budget_warning: bool         # True if exceeding recommended budget
    collider_health: Optional[Dict] = None  # Collider insights if loaded


def load_repo_truths(project_root: Path) -> Optional[Dict]:
    """Load cached truths from BARE TruthValidator."""
    truths_path = project_root / ".agent/intelligence/truths/repo_truths.yaml"
    if not truths_path.exists():
        return None

    try:
        with open(truths_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def _find_insights_json(project_root: Path) -> Optional[Path]:
    """Find collider_insights.json in .collider/ or /tmp/ fallback."""
    primary = project_root / ".collider" / "collider_insights.json"
    if primary.exists():
        return primary

    tmp = Path("/tmp")
    if tmp.exists():
        candidates = sorted(
            tmp.glob("**/collider_insights.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if candidates:
            return candidates[0]
    return None


def load_collider_insights(project_root: Path) -> Optional[Dict]:
    """Load Collider architectural insights.

    Returns a summary dict with grade, health_score, findings_count,
    top_finding, topology_shape, and a staleness warning if > 7 days old.
    Searches .collider/ first, then /tmp/ for recent outputs.
    """
    found = _find_insights_json(project_root)
    if found is None:
        return None

    try:
        with open(found, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    # Build compact summary for context injection
    import time
    age_days = (time.time() - found.stat().st_mtime) / 86400

    # Extract topology shape from findings
    topo = "unknown"
    top_finding = None
    for finding in data.get("findings", []):
        if finding.get("category") == "topology":
            topo = finding.get("evidence", {}).get("shape", topo)
        if top_finding is None and finding.get("severity") in ("critical", "high"):
            top_finding = finding.get("title")

    if top_finding is None and data.get("findings"):
        top_finding = data["findings"][0].get("title", "None")

    result = {
        "grade": data.get("grade", "?"),
        "health_score": data.get("health_score", 0),
        "findings_count": data.get("findings_count", 0),
        "top_finding": top_finding or "None",
        "topology_shape": topo,
        "executive_summary": data.get("executive_summary", ""),
    }

    if age_days > 7:
        result["_stale"] = f"Insights are {age_days:.0f} days old. Re-run Collider."

    return result


def answer_from_truths(query: str, truths: Dict) -> Optional[str]:
    """Try to answer a query using cached truths."""
    query_lower = query.lower()

    # Pattern: "how many X files"
    if "how many" in query_lower:
        counts = truths.get("counts", {})
        files = counts.get("files", {})

        # Check for specific file type
        for ext, count in files.items():
            if ext in query_lower:
                return f"There are {count} {ext} files in the repository."

        # General file count
        if "files" in query_lower and files:
            total = sum(files.values())
            breakdown = ", ".join(f"{c} {e}" for e, c in files.items())
            return f"Total files: {total} ({breakdown})"

        # Lines of code
        if "lines" in query_lower or "loc" in query_lower:
            loc = counts.get("lines_of_code")
            if loc:
                return f"The repository contains approximately {loc:,} lines of code."

        # Functions
        if "function" in query_lower:
            funcs = counts.get("functions")
            if funcs:
                return f"There are approximately {funcs} functions in the repository."

        # Classes
        if "class" in query_lower:
            classes = counts.get("classes")
            if classes:
                return f"There are approximately {classes} classes in the repository."

    # Pattern: "what is the pipeline" - check for known facts
    if "pipeline" in query_lower and "stages" in query_lower:
        pipeline = truths.get("pipeline", {})
        stages = pipeline.get("stages")
        if stages:
            return f"The analysis pipeline has {stages} stages."

    # Collider health queries (from collider_health section in truths)
    ch = truths.get("collider_health", {})
    if ch:
        if any(w in query_lower for w in ["grade", "health score", "what's the grade"]):
            return (
                f"Collider Grade: {ch.get('grade', '?')} "
                f"(health score: {ch.get('health_score', '?')}/10, "
                f"{ch.get('findings_count', '?')} findings). "
                f"Topology: {ch.get('topology_shape', 'unknown')}."
            )
        if any(w in query_lower for w in ["how many findings", "any critical", "issues"]):
            return (
                f"The Collider found {ch.get('findings_count', '?')} findings. "
                f"Top finding: {ch.get('top_finding', 'None')}."
            )
        if any(w in query_lower for w in ["topology", "architecture shape"]):
            return f"The codebase topology is {ch.get('topology_shape', 'unknown')}."

    return None


def get_critical_files_for_sets(
    sets: List[str],
    sets_config: Dict
) -> List[str]:
    """Extract critical files from set configurations."""
    critical = []
    seen = set()

    for set_name in sets:
        set_def = sets_config.get(set_name, {})
        files = set_def.get("critical_files", [])
        for f in files:
            if f not in seen:
                critical.append(f)
                seen.add(f)

    return critical


def get_positional_strategy(
    sets: List[str],
    sets_config: Dict
) -> str:
    """Determine positioning strategy from sets."""
    # Priority: sandwich > front-load > none
    strategies = []

    for set_name in sets:
        set_def = sets_config.get(set_name, {})
        strategy = set_def.get("positional_strategy")
        if strategy:
            strategies.append(strategy)

    if "sandwich" in strategies:
        return "sandwich"
    elif "front-load" in strategies:
        return "front-load"
    else:
        return "none"


def estimate_tokens_for_sets(
    sets: List[str],
    sets_config: Dict
) -> int:
    """Estimate total token count for given sets."""
    total = 0
    seen_sets = set()

    def _estimate_recursive(set_name: str) -> int:
        if set_name in seen_sets:
            return 0
        seen_sets.add(set_name)

        set_def = sets_config.get(set_name, {})
        tokens = set_def.get("max_tokens", 50_000)

        # Handle includes
        for included in set_def.get("includes", []):
            tokens = max(tokens, _estimate_recursive(included))

        return tokens

    for s in sets:
        total += _estimate_recursive(s)

    return total


def inject_agent_context(
    sets: List[str],
    inject_level: str = "minimal"
) -> List[str]:
    """Inject appropriate agent context sets.

    Args:
        sets: Current list of sets
        inject_level: "minimal" (kernel only), "standard" (kernel+tasks),
                      "full" (all agent sets)
    """
    injection_map = {
        "minimal": ["agent_kernel"],
        "standard": ["agent_kernel", "agent_tasks", "deck_state"],
        "full": ["agent_full", "deck"],
    }

    to_inject = injection_map.get(inject_level, ["agent_kernel"])

    # Inject at beginning (high attention position)
    result = []
    for s in to_inject:
        if s not in sets:
            result.append(s)

    result.extend(s for s in sets if s not in to_inject)
    return result


def optimize_context(
    sets: List[str],
    sets_config: Dict,
    project_root: Path,
    use_truths: bool = True,
    inject_agent: bool = False,
    inject_level: str = "standard",
    intent: Optional[str] = None
) -> OptimizedContext:
    """
    Optimize context for a query.

    Args:
        sets: Initial list of analysis sets
        sets_config: Full sets configuration
        project_root: Path to project root
        use_truths: Whether to load repo_truths.yaml
        inject_agent: Whether to inject agent context
        inject_level: Level of agent context injection
        intent: Query intent (e.g. "architecture", "debug", "validate")

    Returns:
        OptimizedContext with optimized sets and metadata
    """
    # Inject agent context if requested
    if inject_agent:
        sets = inject_agent_context(sets, inject_level)

    # Load truths if requested
    truths = load_repo_truths(project_root) if use_truths else None

    # Load collider insights
    collider_health = load_collider_insights(project_root)

    # Auto-inject collider_insights set for architecture/debug/validate intents
    if collider_health and intent in ("architecture", "debug", "validate"):
        if "collider_insights" not in sets:
            sets.insert(0, "collider_insights")

    # Merge collider health into truths for instant answers
    if collider_health and truths is not None:
        truths["collider_health"] = collider_health

    # Get critical files and positioning
    critical_files = get_critical_files_for_sets(sets, sets_config)
    positioning = get_positional_strategy(sets, sets_config)

    # Estimate tokens and check against config-driven hard cap
    estimated_tokens = estimate_tokens_for_sets(sets, sets_config)
    hard_cap = get_hard_cap()
    budget_warning = estimated_tokens > hard_cap

    return OptimizedContext(
        sets=sets,
        truths=truths,
        positioning=positioning,
        critical_files=critical_files,
        estimated_tokens=estimated_tokens,
        budget_warning=budget_warning,
        collider_health=collider_health
    )


def format_context_summary(ctx: OptimizedContext) -> str:
    """Format context optimization summary for display."""
    lines = [
        f"Sets: {', '.join(ctx.sets)}",
        f"Estimated tokens: {ctx.estimated_tokens:,}",
        f"Positioning: {ctx.positioning}",
    ]

    if ctx.critical_files:
        lines.append(f"Critical files: {len(ctx.critical_files)}")

    if ctx.truths:
        lines.append("Truths: loaded")

    if ctx.budget_warning:
        lines.append(f"WARNING: Exceeds {get_hard_cap():,} token budget!")

    return "\n".join(lines)
