"""
Long Context Tier - Full Context Gemini Reasoning
==================================================

Standard Model Classification:
-----------------------------
D1_KIND:     LOG.FNC.M (Logic Function Module)
D2_LAYER:    Application (tier implementation)
D3_ROLE:     Service (executes analysis)
D4_BOUNDARY: I-O (API calls)
D5_STATE:    Stateless (each call is independent)
D6_EFFECT:   Impure (network I/O)
D7_LIFECYCLE: Use (called during analysis)
D8_TRUST:    85 (network dependencies)

ACI Tier: 2 (LONG_CONTEXT)
Latency: ~60 seconds
Cost: ~$0.01-0.05 per query
Context: Up to 1M tokens

Purpose: pi3 Organelle
    This tier is a complete, self-contained analysis unit.
    It receives context, queries the model, and returns results.

Communication Theory:
    Channel: HTTPS to Gemini API
    Message: Full codebase context + query
    Noise: Rate limits, network errors (handled by retry)
    Redundancy: Retry with backoff
"""

import sys
import time
from typing import Any, Dict, Optional

from .base import BaseTierExecutor, TierRequest, TierResponse, create_response_from_error
from ..clients import create_client, retry_with_backoff
from ..output import estimate_cost


class LongContextExecutor(BaseTierExecutor):
    """
    Executes analysis using full codebase context.

    This is the "standard" tier - sends all context to the model
    and asks it to reason over the full picture.

    Best for:
    - Architecture questions
    - Code understanding
    - Pattern analysis
    - Comprehensive reviews
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self._client = None
        self._project_id = None

    def _ensure_client(self) -> bool:
        """Ensure API client is initialized."""
        if self._client is not None:
            return True

        try:
            backend = self.config.get("backend", {})
            backend_type = backend.get("backend", "vertex") if isinstance(backend, dict) else "vertex"
            project = backend.get("vertex_project") if isinstance(backend, dict) else None
            location = backend.get("vertex_location", "us-central1") if isinstance(backend, dict) else "us-central1"

            self._client, self._project_id = create_client(
                backend=backend_type,
                project=project,
                location=location
            )
            return True
        except Exception as e:
            self.log(f"Failed to create client: {e}", level="error")
            return False

    def execute(self, request: TierRequest) -> TierResponse:
        """
        Execute long context analysis.

        Args:
            request: TierRequest with query and context

        Returns:
            TierResponse with analysis results
        """
        if not self._ensure_client():
            return create_response_from_error(
                RuntimeError("Failed to initialize API client"),
                tier="LONG_CONTEXT",
                request=request
            )

        # Build the full prompt
        system_prompt = request.system_prompt or self._get_mode_prompt(request.mode)
        full_context = request.context
        if request.extra_context:
            full_context = f"{request.context}\n\n{request.extra_context}"

        full_prompt = f"{system_prompt}\n\nCODEBASE CONTEXT:\n{full_context}\n\nUSER QUERY: {request.query}"

        self.log(f"Analyzing with {request.model or 'default model'}...")

        # Execute with retry
        start_time = time.time()
        try:
            from google.genai.types import Part

            model = request.model or self.config.get("models", {}).get("default_model", "gemini-3-pro-preview")

            def make_request():
                return self._client.models.generate_content(
                    model=model,
                    contents=[Part.from_text(text=full_prompt)]
                )

            response = retry_with_backoff(make_request)
            response_text = response.text or ""
            duration_ms = int((time.time() - start_time) * 1000)

            # Extract usage
            usage = None
            if response.usage_metadata:
                usage = {
                    'input_tokens': response.usage_metadata.prompt_token_count,
                    'output_tokens': response.usage_metadata.candidates_token_count,
                }
                self._log_usage(usage, model, duration_ms)

            # Auto-save if enabled
            saved_path = ""
            if self.config.get("auto_save_enabled", True):
                saved_path = self._auto_save(request.query, response_text, model, request.mode)

            return TierResponse(
                text=response_text,
                usage=usage,
                model=model,
                mode=request.mode,
                tier="LONG_CONTEXT",
                saved_path=saved_path,
                success=True,
            )

        except Exception as e:
            self.log(f"Error during generation: {e}", level="error")
            return create_response_from_error(e, tier="LONG_CONTEXT", request=request)

    def can_handle(self, request: TierRequest) -> bool:
        """
        Check if this tier can handle the request.

        Long context can handle most requests, but may fail if:
        - Context is too large (>1M tokens)
        - No API client available
        """
        # Check context size
        context_tokens = len(request.context) // 4  # Estimate
        max_tokens = self.config.get("max_context_tokens", 1_000_000)

        if context_tokens > max_tokens:
            return False

        return True

    def get_info(self) -> Dict[str, Any]:
        """Get tier metadata."""
        return {
            "name": "LongContextExecutor",
            "tier": "LONG_CONTEXT",
            "description": "Full context Gemini reasoning (~60s)",
            "max_tokens": 1_000_000,
            "latency_ms": 60000,
            "cost_factor": 1.0,
        }

    def _get_mode_prompt(self, mode: str) -> str:
        """Get system prompt for analysis mode."""
        modes = self.config.get("modes", {})
        mode_config = modes.get(mode, {})
        return mode_config.get("prompt", "") if isinstance(mode_config, dict) else ""

    def _log_usage(self, usage: Dict[str, int], model: str, duration_ms: int) -> None:
        """Log token usage and cost."""
        input_tokens = usage.get('input_tokens', 0)
        output_tokens = usage.get('output_tokens', 0)

        print("\n-----------------", file=sys.stderr)
        print(f"Tokens Used: {input_tokens:,} Input, {output_tokens:,} Output", file=sys.stderr)

        pricing = self.config.get("models", {}).get("pricing", {})
        cost = estimate_cost(input_tokens, output_tokens, model, pricing)
        print(f"Estimated Cost: ${cost:.4f}", file=sys.stderr)
        print(f"Duration: {duration_ms/1000:.1f}s", file=sys.stderr)

    def _auto_save(self, query: str, response_text: str, model: str, mode: str) -> str:
        """Auto-save response to research directory."""
        try:
            # Import here to avoid circular dependency
            from pathlib import Path
            from ..config import PROJECT_ROOT, GEMINI_RESEARCH_PATH

            # Try to use DualFormatSaver if available
            try:
                import sys as sys_module
                sys_module.path.insert(0, str(Path(__file__).parent.parent.parent))
                from utils.output_formatters import DualFormatSaver

                saver = DualFormatSaver(base_path=GEMINI_RESEARCH_PATH)
                result = saver.save(
                    query=query,
                    response={"content": response_text, "mode": mode},
                    source="gemini",
                    model=model
                )
                print(f"  [Auto-saved: {result.md_path.name}]", file=sys.stderr)
                return str(result.md_path)
            except ImportError:
                pass

            return ""
        except Exception as e:
            print(f"  [Auto-save failed: {e}]", file=sys.stderr)
            return ""
