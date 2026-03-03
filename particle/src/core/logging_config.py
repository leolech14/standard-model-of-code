"""
Centralized logging configuration for Collider pipeline.

Controls log verbosity across all modules. Key design decisions:
- Tree-sitter query warnings (scope_analyzer, dimension_classifier, symbol_indexer)
  are demoted to DEBUG by default since they fire per-language and are non-fatal.
- Pipeline stage output uses print() directly (not logging) for emoji headers.
- This module is imported once at CLI entry and configures the root logger.

Usage:
    from src.core.logging_config import configure_logging
    configure_logging(level='WARNING')  # default: suppress INFO noise
    configure_logging(level='DEBUG')    # verbose: show everything
    configure_logging(quiet=True)       # quiet: only ERROR and above
"""

import logging
import sys


# Modules known to produce high-volume, non-fatal warnings
NOISY_MODULES = [
    'src.core.scope_analyzer',
    'src.core.dimension_classifier',
    'src.core.symbol_indexer',
    'core.scope_analyzer',
    'core.dimension_classifier',
    'core.symbol_indexer',
]


def configure_logging(
    level: str = 'WARNING',
    quiet: bool = False,
    verbose: bool = False,
    format_str: str = None,
):
    """
    Configure Collider logging.

    Args:
        level: Root log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        quiet: If True, suppress everything below ERROR.
        verbose: If True, set level to DEBUG for all modules.
        format_str: Custom format string. Default is compact.
    """
    if quiet:
        effective_level = logging.ERROR
    elif verbose:
        effective_level = logging.DEBUG
    else:
        effective_level = getattr(logging, level.upper(), logging.WARNING)

    if format_str is None:
        if effective_level <= logging.DEBUG:
            format_str = '%(name)s:%(lineno)d %(levelname)s: %(message)s'
        else:
            format_str = '%(levelname)s: %(message)s'

    # Configure root logger
    root = logging.getLogger()
    root.setLevel(effective_level)

    # Remove existing handlers to avoid duplicates on re-configure
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(effective_level)
    handler.setFormatter(logging.Formatter(format_str))
    root.addHandler(handler)

    # When not in verbose mode, silence noisy tree-sitter modules
    # even if root level is below ERROR (e.g., INFO)
    if not verbose:
        for module_name in NOISY_MODULES:
            logging.getLogger(module_name).setLevel(logging.ERROR)
