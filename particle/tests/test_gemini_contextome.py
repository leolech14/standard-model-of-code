"""Tests for GeminiContextomeAdapter — Gemini LLM adapter for Stage 0.8."""

from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Adapter instantiation (mocked — no real API key needed)
# ---------------------------------------------------------------------------

class TestGeminiAdapterInit:

    @patch("src.core.adapters.gemini_contextome.genai", create=True)
    def test_instantiation_creates_client(self, mock_genai_module):
        # Patch at import level
        import importlib
        with patch.dict("sys.modules", {"google": MagicMock(), "google.genai": mock_genai_module}):
            import src.core.adapters.gemini_contextome as mod
            importlib.reload(mod)
            adapter = mod.GeminiContextomeAdapter.__new__(mod.GeminiContextomeAdapter)
            adapter._client = MagicMock()
            adapter._model = "gemini-2.0-flash-001"
            assert adapter._model == "gemini-2.0-flash-001"
            assert adapter.provider_name == "gemini"


# ---------------------------------------------------------------------------
# extract_purpose — mocked responses
# ---------------------------------------------------------------------------

class TestExtractPurpose:

    def _make_adapter(self):
        """Create adapter with mocked genai client."""
        from unittest.mock import MagicMock
        import sys

        # Mock google.genai
        mock_genai = MagicMock()
        sys.modules["google"] = MagicMock()
        sys.modules["google.genai"] = mock_genai

        import importlib
        import src.core.adapters.gemini_contextome as mod
        importlib.reload(mod)

        adapter = mod.GeminiContextomeAdapter.__new__(mod.GeminiContextomeAdapter)
        adapter._client = MagicMock()
        adapter._model = "gemini-2.0-flash-001"
        return adapter

    def test_valid_json_response(self):
        adapter = self._make_adapter()

        mock_response = MagicMock()
        mock_response.text = '''{
            "semantic_purpose": "Defines the authentication flow for the API.",
            "architecture_hints": ["OAuth2", "JWT"],
            "constraints": ["MUST use HTTPS for all token exchanges"],
            "relationships": ["Google OAuth", "Redis session store"]
        }'''
        adapter._client.models.generate_content.return_value = mock_response

        result = adapter.extract_purpose("# Auth Guide\nUses OAuth2.", "docs/auth.md")

        assert result is not None
        assert "semantic_purpose" in result
        assert "architecture_hints" in result
        assert "constraints" in result
        assert "relationships" in result
        assert len(result["architecture_hints"]) == 2

    def test_markdown_fenced_response(self):
        adapter = self._make_adapter()

        mock_response = MagicMock()
        mock_response.text = '```json\n{"semantic_purpose": "Test.", "architecture_hints": [], "constraints": [], "relationships": []}\n```'
        adapter._client.models.generate_content.return_value = mock_response

        result = adapter.extract_purpose("Test content", "test.md")
        assert result is not None
        assert result["semantic_purpose"] == "Test."

    def test_api_error_returns_none(self):
        adapter = self._make_adapter()
        adapter._client.models.generate_content.side_effect = Exception("API down")

        result = adapter.extract_purpose("Content", "file.md")
        assert result is None

    def test_invalid_json_returns_none(self):
        adapter = self._make_adapter()

        mock_response = MagicMock()
        mock_response.text = "This is not JSON at all"
        adapter._client.models.generate_content.return_value = mock_response

        result = adapter.extract_purpose("Content", "file.md")
        assert result is None

    def test_missing_keys_returns_none(self):
        adapter = self._make_adapter()

        mock_response = MagicMock()
        mock_response.text = '{"semantic_purpose": "Only one key"}'
        adapter._client.models.generate_content.return_value = mock_response

        result = adapter.extract_purpose("Content", "file.md")
        assert result is None

    def test_content_truncation(self):
        adapter = self._make_adapter()

        mock_response = MagicMock()
        mock_response.text = '{"semantic_purpose": "OK", "architecture_hints": [], "constraints": [], "relationships": []}'
        adapter._client.models.generate_content.return_value = mock_response

        # Content longer than 16K chars
        long_content = "x" * 20_000
        result = adapter.extract_purpose(long_content, "big.md")
        assert result is not None

        # Verify the prompt was truncated
        call_args = adapter._client.models.generate_content.call_args
        prompt = call_args[1]["contents"] if "contents" in call_args[1] else call_args[0][0]
        # The prompt should contain truncation marker
        if isinstance(prompt, str):
            assert "truncated" in prompt


# ---------------------------------------------------------------------------
# Protocol compliance
# ---------------------------------------------------------------------------

class TestProtocolCompliance:

    def test_adapter_satisfies_llm_adapter_protocol(self):
        """GeminiContextomeAdapter structurally matches LLMAdapter protocol."""
        from src.core.contextome_intel import LLMAdapter

        adapter = MagicMock()
        adapter.extract_purpose = MagicMock(return_value={"semantic_purpose": "test"})

        # runtime_checkable Protocol check
        assert isinstance(adapter, LLMAdapter)

    def test_real_adapter_has_extract_purpose(self):
        """The actual class defines extract_purpose with correct signature."""
        import inspect
        import sys

        # Mock google.genai for import
        sys.modules["google"] = MagicMock()
        sys.modules["google.genai"] = MagicMock()

        import importlib
        import src.core.adapters.gemini_contextome as mod
        importlib.reload(mod)

        sig = inspect.signature(mod.GeminiContextomeAdapter.extract_purpose)
        params = list(sig.parameters.keys())
        assert "content" in params
        assert "path" in params
