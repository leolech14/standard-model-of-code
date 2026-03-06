"""Gemini adapter for Contextome Intelligence (Stage 0.8, Layer 2).

Implements the LLMAdapter protocol from contextome_intel.py using
Google's genai SDK with Gemini 2.0 Flash.

Usage:
    from src.core.adapters.gemini_contextome import GeminiContextomeAdapter
    adapter = GeminiContextomeAdapter()
    result = adapter.extract_purpose(content, path)
"""

from __future__ import annotations

import json
import re
from typing import Any


# Max content length (~4K tokens ≈ 16K chars conservatively)
_MAX_CONTENT_CHARS = 16_000

_EXTRACTION_PROMPT = """\
You are a code architecture analyst. Given the content of a documentation file, \
extract structured metadata about the system it describes.

File path: {path}

Content:
```
{content}
```

Return ONLY a JSON object with exactly these 4 keys:
- "semantic_purpose": A single sentence describing what this document declares about the system's purpose.
- "architecture_hints": A list of architectural patterns or structures mentioned (e.g., "microservices", "event-driven", "layered architecture"). Empty list if none.
- "constraints": A list of MUST/MUST NOT declarations or rules stated in the document. Empty list if none.
- "relationships": A list of external systems, APIs, or services referenced (e.g., "PostgreSQL", "GitHub API", "Redis"). Empty list if none.

Return ONLY valid JSON. No markdown, no explanation.
"""


class GeminiContextomeAdapter:
    """Wraps Google genai SDK to implement LLMAdapter protocol.

    Satisfies contextome_intel.LLMAdapter via structural subtyping:
    must implement extract_purpose(content: str, path: str) -> dict | None.
    """

    provider_name = "gemini"

    def __init__(self, model: str = "gemini-2.0-flash-001"):
        from google import genai

        self._client = genai.Client()
        self._model = model

    def extract_purpose(self, content: str, path: str) -> dict[str, Any] | None:
        """Extract semantic purpose from document content via Gemini.

        Args:
            content: Document text (will be truncated to ~4K tokens).
            path: Relative file path for context.

        Returns:
            Dict with keys: semantic_purpose, architecture_hints,
            constraints, relationships. None on failure.
        """
        truncated = content[:_MAX_CONTENT_CHARS]
        if len(content) > _MAX_CONTENT_CHARS:
            truncated += "\n... [truncated]"

        prompt = _EXTRACTION_PROMPT.format(path=path, content=truncated)

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
            )
            raw = response.text.strip()

            # Strip markdown fences if present
            if raw.startswith("```"):
                raw = re.sub(r"^```(?:json)?\s*\n?", "", raw)
                raw = re.sub(r"\n?```\s*$", "", raw)

            result = json.loads(raw)

            # Validate expected shape
            expected_keys = {"semantic_purpose", "architecture_hints", "constraints", "relationships"}
            if not expected_keys.issubset(result.keys()):
                return None

            return result

        except Exception:
            return None
