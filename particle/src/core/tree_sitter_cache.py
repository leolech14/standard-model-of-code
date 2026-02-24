"""Shared Tree-sitter parser and AST cache for the Collider pipeline.

Addresses the redundant-parsing hotspot in Stages 2.8-2.11 of full_analysis.py:
each stage previously created its own parsers and re-parsed the same source
bodies independently.  This module provides a single shared cache so that a
given (language, source) pair is parsed at most once per pipeline run.

Design:
- Parsers are initialized lazily on first use (avoids import cost when tree-sitter
  is not installed or a language is never requested).
- Parsed ASTs are memoised with an LRU policy (default 500 entries) keyed by a
  (language, SHA-256 hash of source) tuple.  Memory per cached tree is typically
  1-10 KB for production-sized functions/classes, so 500 entries ≈ 1-5 MB.
- Graceful degradation: if tree-sitter or a language grammar is unavailable, the
  ``parse`` method raises ``ImportError`` / ``ValueError`` and the caller's
  existing try/except block handles it exactly as before.
"""

import hashlib
from collections import OrderedDict

__all__ = ["TreeSitterCache"]


class TreeSitterCache:
    """Lazy-initialising, LRU-limited tree-sitter parser pool + AST cache.

    Usage::

        cache = TreeSitterCache(max_size=500)
        tree = cache.parse(body_source, lang="python")   # 'python' or 'javascript'
        # tree is a tree_sitter.Tree object

    The ``lang`` argument accepts:
    - ``"python"``      for ``.py`` files
    - ``"javascript"``  for ``.js / .jsx / .ts / .tsx`` files
    """

    # Maps canonical lang name -> callable that returns the grammar language object
    _LANG_LOADERS = {
        "python": lambda: _load_python_lang(),
        "javascript": lambda: _load_js_lang(),
    }

    def __init__(self, max_size: int = 500) -> None:
        self._max_size = max_size
        # Lazily initialised parsers: lang -> tree_sitter.Parser
        self._parsers: dict = {}
        # LRU cache: OrderedDict[(lang, content_hash)] -> tree_sitter.Tree
        self._cache: OrderedDict = OrderedDict()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse(self, body_source: str, lang: str):
        """Return the parsed tree for *body_source* in *lang*.

        Args:
            body_source: Raw source text to parse.
            lang: Language key – ``"python"`` or ``"javascript"``.

        Returns:
            A ``tree_sitter.Tree`` object.

        Raises:
            ImportError: If tree-sitter or the required grammar is not installed.
            ValueError:  If *lang* is not supported.
        """
        if lang not in self._LANG_LOADERS:
            raise ValueError(f"TreeSitterCache: unsupported language '{lang}'")

        content_hash = hashlib.sha256(body_source.encode("utf-8")).hexdigest()
        cache_key = (lang, content_hash)

        # Cache hit – move to end (most-recently-used) and return
        if cache_key in self._cache:
            self._cache.move_to_end(cache_key)
            return self._cache[cache_key]

        # Ensure parser exists
        parser = self._get_parser(lang)

        # Parse and store
        tree = parser.parse(bytes(body_source, "utf-8"))
        self._store(cache_key, tree)
        return tree

    def get_parser(self, lang: str):
        """Return the raw ``tree_sitter.Parser`` for *lang* (initialises lazily).

        Callers that need the parser directly (e.g. to pass to an existing
        analyser function) can use this instead of ``parse()``.
        """
        return self._get_parser(lang)

    def cache_size(self) -> int:
        """Return the number of cached ASTs."""
        return len(self._cache)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_parser(self, lang: str):
        if lang not in self._parsers:
            import tree_sitter  # noqa: deferred import for graceful degradation

            loader = self._LANG_LOADERS[lang]
            lang_obj = loader()
            parser = tree_sitter.Parser()
            parser.language = tree_sitter.Language(lang_obj)
            self._parsers[lang] = parser
        return self._parsers[lang]

    def _store(self, key: tuple, tree) -> None:
        """Add *tree* to the LRU cache, evicting oldest entry if needed."""
        if len(self._cache) >= self._max_size:
            self._cache.popitem(last=False)  # Remove least-recently-used (front)
        self._cache[key] = tree


# ---------------------------------------------------------------------------
# Language grammar loaders (kept isolated so ImportError messages are clear)
# ---------------------------------------------------------------------------

def _load_python_lang():
    try:
        import tree_sitter_python  # type: ignore
        return tree_sitter_python.language()
    except ImportError as exc:
        raise ImportError(
            "tree-sitter-python is required for Python parsing. "
            "Install it with: pip install tree-sitter-python"
        ) from exc


def _load_js_lang():
    try:
        import tree_sitter_javascript  # type: ignore
        return tree_sitter_javascript.language()
    except ImportError as exc:
        raise ImportError(
            "tree-sitter-javascript is required for JavaScript/TypeScript parsing. "
            "Install it with: pip install tree-sitter-javascript"
        ) from exc
