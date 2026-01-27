"""
Configuration Module
====================

Standard Model Classification:
-----------------------------
D1_KIND:     ORG.MOD.O (Organizational Module)
D2_LAYER:    Core (foundational, no external dependencies)
D3_ROLE:     Loader (loads configuration from files)
D4_BOUNDARY: Input (reads from disk, no writes)
D5_STATE:    Stateless (functions are pure)
D6_EFFECT:   Pure (deterministic given same files)
D7_LIFECYCLE: Create (initialization-time module)
D8_TRUST:    95 (well-tested, simple logic)

RPBL: (2, 1, 2, 5)
    R=2: Two responsibilities (load sets, load prompts) - could split further
    P=1: Pure - only reads files, no mutations
    B=2: Internal boundary with file I/O
    L=5: Module-lifetime singleton pattern

Communication Theory:
    Source:   YAML files on disk
    Channel:  File I/O (read-only)
    Message:  AnalyzeConfig dataclass
    Receiver: All other analyze modules
    Noise:    Missing files (handled with defaults)

Tool Theory:
    Universe: TOOLOME (shapes analysis behavior)
    Role:     T-Supplier (provides configuration, doesn't mutate)
    Stone Tool Test: PASS (human can read YAML directly)
"""

import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


# Path Resolution (relative to this file)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent  # tools/ai/analyze -> PROJECT_ROOT

# Configuration file paths
SETS_CONFIG_PATH = PROJECT_ROOT / "context-management/config/analysis_sets.yaml"
PROMPTS_CONFIG_PATH = PROJECT_ROOT / "context-management/config/prompts.yaml"
SEMANTIC_MODELS_PATH = PROJECT_ROOT / "context-management/config/semantic_models.yaml"

# Token limits per tier (Shannon capacity)
MAX_CONTEXT_TOKENS = 1_000_000       # Gemini 3 Pro (Long Context tier)
MAX_FLASH_DEEP_TOKENS = 2_000_000    # Gemini 2.0 Flash (Flash Deep tier)
INTERACTIVE_THRESHOLD = 50_000       # Auto-interactive above this

# File Search configuration
FILE_SEARCH_MODEL = "gemini-3-pro-preview"
FILE_SEARCH_CHUNK_SIZE = 512
FILE_SEARCH_CHUNK_OVERLAP = 50

# Environment variable names
GEMINI_API_KEY_ENV = "GEMINI_API_KEY"
GEMINI_BACKEND_ENV = "GEMINI_BACKEND"

# Research output paths
GEMINI_RESEARCH_PATH = PROJECT_ROOT / "standard-model-of-code/docs/research/gemini"

# Architect mode auto-injection
ARCHITECT_DOCS = [
    "context-management/docs/COLLIDER_ARCHITECTURE.md",
    "standard-model-of-code/docs/MODEL.md",
]


@dataclass
class ModelConfig:
    """Model configuration with fallbacks."""
    default_model: str = "gemini-3-pro-preview"
    fast_model: str = "gemini-2.0-flash-001"
    fallback_models: List[str] = field(default_factory=lambda: ["gemini-2.5-pro", "gemini-2.0-flash-001"])
    pricing: Dict[str, Dict[str, float]] = field(default_factory=dict)


@dataclass
class BackendConfig:
    """Backend configuration (Vertex vs AI Studio)."""
    backend: str = "vertex"
    vertex_project: Optional[str] = None
    vertex_location: str = "us-central1"


@dataclass
class AnalyzeConfig:
    """
    Complete analysis configuration.

    Aggregates all configuration sources into a single coherent structure.
    This is the "state vector" for the analysis system.
    """
    # Sets
    analysis_sets: Dict[str, Any] = field(default_factory=dict)
    recommendations: Dict[str, List[str]] = field(default_factory=dict)

    # Models
    models: ModelConfig = field(default_factory=ModelConfig)

    # Backend
    backend: BackendConfig = field(default_factory=BackendConfig)

    # Prompts/Modes
    modes: Dict[str, Dict[str, str]] = field(default_factory=dict)
    insights_prompt: Optional[str] = None
    role_validation_prompt: Optional[str] = None
    plan_validation_prompt: Optional[str] = None

    # Runtime
    auto_save_enabled: bool = True
    is_interactive_env: bool = True


def load_sets_config() -> Dict[str, Any]:
    """Load analysis sets configuration."""
    if not SETS_CONFIG_PATH.exists():
        return {}
    with open(SETS_CONFIG_PATH) as f:
        return yaml.safe_load(f) or {}


def load_prompts_config() -> Dict[str, Any]:
    """Load prompts and modes configuration."""
    if not PROMPTS_CONFIG_PATH.exists():
        return {}
    with open(PROMPTS_CONFIG_PATH) as f:
        return yaml.safe_load(f) or {}


def load_semantic_models() -> Dict[str, Any]:
    """Load semantic models (HSL) configuration."""
    if not SEMANTIC_MODELS_PATH.exists():
        return {}
    with open(SEMANTIC_MODELS_PATH) as f:
        return yaml.safe_load(f) or {}


def detect_environment() -> bool:
    """
    Detect if running in an interactive terminal.

    Returns False for:
    - CI environments (CI=true)
    - Agent environments (ANTIGRAVITY_AGENT=1)
    - Explicitly non-interactive (NONINTERACTIVE=true)
    - Non-TTY stdin
    """
    import sys
    return sys.stdin.isatty() and not (
        os.environ.get('ANTIGRAVITY_AGENT') == '1' or
        os.environ.get('CI') == 'true' or
        os.environ.get('NONINTERACTIVE') == 'true'
    )


def load_config() -> AnalyzeConfig:
    """
    Load complete configuration from all sources.

    This is the single entry point for configuration loading.
    All configuration is assembled here, making the system state explicit.

    Returns:
        AnalyzeConfig with all configuration loaded
    """
    # Load raw configs
    sets_data = load_sets_config()
    prompts_data = load_prompts_config()

    # Build model config
    models = ModelConfig(
        default_model=prompts_data.get("default_model", "gemini-3-pro-preview"),
        fast_model=prompts_data.get("fast_model", "gemini-2.0-flash-001"),
        fallback_models=prompts_data.get("fallback_models", ["gemini-2.5-pro", "gemini-2.0-flash-001"]),
        pricing=prompts_data.get("pricing", {}),
    )

    # Build backend config (env override)
    configured_backend = prompts_data.get("backend", "vertex")
    backend = BackendConfig(
        backend=os.environ.get(GEMINI_BACKEND_ENV, configured_backend).lower(),
        vertex_project=prompts_data.get("vertex_project"),
        vertex_location=prompts_data.get("vertex_location", "us-central1"),
    )

    # Extract prompts
    analysis_prompts = prompts_data.get("analysis_prompts", {})

    return AnalyzeConfig(
        analysis_sets=sets_data.get("analysis_sets", {}),
        recommendations=sets_data.get("recommendations", {}),
        models=models,
        backend=backend,
        modes=analysis_prompts.get("modes", {}),
        insights_prompt=analysis_prompts.get("insights_source") or analysis_prompts.get("insights"),
        role_validation_prompt=analysis_prompts.get("role_validation"),
        plan_validation_prompt=analysis_prompts.get("plan_validation"),
        auto_save_enabled=True,
        is_interactive_env=detect_environment(),
    )


def resolve_set(set_name: str, analysis_sets: Dict[str, Any], resolved: Optional[set] = None) -> Dict[str, Any]:
    """
    Resolve a set definition, expanding any 'includes' recursively.

    This is a pure function - no side effects, deterministic output.

    Args:
        set_name: Name of the set to resolve
        analysis_sets: All available set definitions
        resolved: Already resolved sets (for cycle detection)

    Returns:
        Dict with patterns, max_tokens, auto_interactive, description,
        critical_files, positional_strategy
    """
    if resolved is None:
        resolved = set()

    # Cycle detection
    if set_name in resolved:
        return {
            'patterns': [],
            'max_tokens': 0,
            'auto_interactive': False,
            'description': '',
            'critical_files': [],
            'positional_strategy': None
        }

    resolved.add(set_name)

    # Unknown set
    if set_name not in analysis_sets:
        return {
            'patterns': [],
            'max_tokens': 0,
            'auto_interactive': False,
            'description': f'Unknown set: {set_name}',
            'critical_files': [],
            'positional_strategy': None
        }

    set_def = analysis_sets[set_name]
    patterns = list(set_def.get('patterns', []))
    max_tokens = set_def.get('max_tokens', 100_000)
    auto_interactive = set_def.get('auto_interactive', False)
    description = set_def.get('description', '')
    critical_files = list(set_def.get('critical_files', []))
    positional_strategy = set_def.get('positional_strategy', None)

    # Resolve includes
    for included_set in set_def.get('includes', []):
        included = resolve_set(included_set, analysis_sets, resolved)
        patterns.extend(included['patterns'])
        max_tokens = max(max_tokens, included['max_tokens'])
        auto_interactive = auto_interactive or included['auto_interactive']
        for cf in included.get('critical_files', []):
            if cf not in critical_files:
                critical_files.append(cf)
        if not positional_strategy and included.get('positional_strategy'):
            positional_strategy = included['positional_strategy']

    # Deduplicate patterns while preserving order
    seen = set()
    unique_patterns = []
    for p in patterns:
        if p not in seen:
            seen.add(p)
            unique_patterns.append(p)

    return {
        'patterns': unique_patterns,
        'max_tokens': max_tokens,
        'auto_interactive': auto_interactive,
        'description': description,
        'critical_files': critical_files,
        'positional_strategy': positional_strategy
    }


def recommend_sets(query: str, recommendations: Dict[str, List[str]]) -> List[str]:
    """
    Match a query against recommendation patterns.

    Uses simple pattern matching where * matches any words.

    Args:
        query: User's query string
        recommendations: Pattern -> set list mapping

    Returns:
        List of recommended set names
    """
    query_lower = query.lower()
    matches = []

    for pattern, sets in recommendations.items():
        pattern_lower = pattern.lower()
        parts = pattern_lower.split('*')

        pos = 0
        matched = True
        for part in parts:
            part = part.strip()
            if not part:
                continue
            idx = query_lower.find(part, pos)
            if idx == -1:
                matched = False
                break
            pos = idx + len(part)

        if matched:
            for s in sets:
                if s not in matches:
                    matches.append(s)

    return matches
