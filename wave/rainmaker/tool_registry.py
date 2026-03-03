"""
Unified Tool Registry for Rainmaker Console.

Single source of truth for all tool definitions, format converters,
and execution. Replaces the fragmented voice_tools + voice_tools_elevenlabs
+ voice_tool_exec triad.

Spec: .agent/specs/RAINMAKER_TOOL_REGISTRY.md
Macro: .agent/macros/library/MACRO-003-tool-registry-sync.yaml
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# ToolSpec -- one tool = one HTTP call
# ---------------------------------------------------------------------------

@dataclass
class ToolSpec:
    """A single tool available across all channels."""

    # Identity
    name: str
    description: str
    parameters: dict          # JSON Schema for arguments

    # Execution
    method: str               # "GET" or "POST"
    path: str                 # "/api/trading/current"
    arg_transform: Callable[[dict], dict] | None = None
    timeout: int = 15
    max_chars: int = 2000

    # Lifecycle
    enabled: bool = True
    source: str = "builtin"   # "builtin" | "elevenlabs" | "runtime"
    tags: list[str] = field(default_factory=list)

    # --- Format converters ---

    def _base_schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters or {"type": "object", "properties": {}},
        }

    def to_openai(self) -> dict:
        """OpenAI Realtime / xAI Grok format (flat)."""
        return {"type": "function", **self._base_schema()}

    def to_chat_completions(self) -> dict:
        """OpenAI Chat Completions format (nested)."""
        return {"type": "function", "function": self._base_schema()}

    def to_gemini(self) -> dict:
        """Gemini Live format (simple)."""
        return self._base_schema()

    def to_dict(self) -> dict:
        """Serialize for JSON persistence (runtime tools)."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "method": self.method,
            "path": self.path,
            "timeout": self.timeout,
            "max_chars": self.max_chars,
            "enabled": self.enabled,
            "source": self.source,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, d: dict) -> ToolSpec:
        """Deserialize from JSON."""
        return cls(
            name=d["name"],
            description=d["description"],
            parameters=d.get("parameters", {}),
            method=d.get("method", "GET"),
            path=d.get("path", ""),
            timeout=d.get("timeout", 15),
            max_chars=d.get("max_chars", 2000),
            enabled=d.get("enabled", True),
            source=d.get("source", "runtime"),
            tags=d.get("tags", []),
        )


# ---------------------------------------------------------------------------
# ToolRegistry -- singleton holding all ToolSpecs
# ---------------------------------------------------------------------------

class ToolRegistry:
    """Central registry for all Rainmaker tools."""

    def __init__(self, runtime_path: str | Path | None = None):
        self._tools: dict[str, ToolSpec] = {}
        self._runtime_path = Path(runtime_path) if runtime_path else None
        self._loaded_runtime = False

    # --- Registration ---

    def register(self, spec: ToolSpec) -> None:
        """Register a tool. Last-write wins."""
        self._tools[spec.name] = spec

    def register_many(self, specs: list[ToolSpec]) -> None:
        for spec in specs:
            self.register(spec)

    # --- Queries ---

    def get(self, name: str) -> ToolSpec | None:
        self._ensure_runtime_loaded()
        return self._tools.get(name)

    def all(self, include_disabled: bool = False) -> list[ToolSpec]:
        self._ensure_runtime_loaded()
        if include_disabled:
            return list(self._tools.values())
        return [t for t in self._tools.values() if t.enabled]

    def by_tag(self, tag: str) -> list[ToolSpec]:
        return [t for t in self.all() if tag in t.tags]

    def names(self) -> list[str]:
        return [t.name for t in self.all()]

    # --- Lifecycle ---

    def enable(self, name: str) -> bool:
        """Enable a tool. Only persists for runtime-source tools.
        Builtin/elevenlabs tools reset to enabled on restart."""
        spec = self._tools.get(name)
        if spec:
            spec.enabled = True
            self._persist_runtime(name)
            return True
        return False

    def disable(self, name: str) -> bool:
        """Disable a tool. Only persists for runtime-source tools.
        Builtin/elevenlabs tools reset to enabled on restart."""
        spec = self._tools.get(name)
        if spec:
            spec.enabled = False
            self._persist_runtime(name)
            return True
        return False

    # --- Batch format converters ---

    def for_openai(self) -> list[dict]:
        return [t.to_openai() for t in self.all()]

    def for_chat_completions(self) -> list[dict]:
        return [t.to_chat_completions() for t in self.all()]

    def for_gemini(self) -> list[dict]:
        return [t.to_gemini() for t in self.all()]

    # --- Generic executor ---

    async def execute(
        self,
        name: str,
        arguments: dict[str, Any],
        *,
        base_url: str = "http://127.0.0.1:8100",
        auth_token: str | None = None,
    ) -> str:
        """Execute a tool by name. Returns response text."""
        spec = self.get(name)
        if not spec:
            return json.dumps({"error": f"Unknown tool: {name}"})
        if not spec.enabled:
            return json.dumps({"error": f"Tool disabled: {name}"})

        # Native tools (registry management) -- no HTTP call
        if spec.path.startswith("__native__:"):
            return self._execute_native(spec.path, arguments)

        # Dynamic-path tool (rainmaker_api) -- method and path come from arguments
        if spec.path == "__dynamic__":
            method = arguments.get("method", "GET").upper()
            path = arguments.get("path", "/")
            args = arguments.get("body", {})
        else:
            method = spec.method.upper()
            path = spec.path
            args = spec.arg_transform(arguments) if spec.arg_transform else arguments

        import httpx

        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        url = f"{base_url}{path}"

        try:
            async with httpx.AsyncClient(timeout=spec.timeout) as client:
                if method == "GET":
                    params = {k: str(v) for k, v in args.items()} if args else None
                    resp = await client.get(url, params=params, headers=headers)
                else:
                    resp = await client.post(url, json=args, headers=headers)

                text = resp.text
                if len(text) > spec.max_chars:
                    text = text[:spec.max_chars] + f"\n... (truncated at {spec.max_chars} chars)"
                return text

        except httpx.TimeoutException:
            return json.dumps({"error": f"Timeout after {spec.timeout}s calling {path}"})
        except Exception as e:
            return json.dumps({"error": f"Tool {name} failed: {str(e)}"})

    def _execute_native(self, path: str, arguments: dict[str, Any]) -> str:
        """Handle Python-native tools (registry management)."""
        action = path.split(":")[-1]

        if action == "register":
            spec = ToolSpec(
                name=arguments["name"],
                description=arguments["description"],
                parameters=arguments.get("parameters", {}),
                method=arguments.get("method", "GET"),
                path=arguments.get("handler_path", ""),
                source="runtime",
            )
            self.register_runtime(spec)
            return json.dumps({"ok": True, "registered": spec.name})

        elif action == "disable":
            name = arguments.get("name", "")
            ok = self.disable(name)
            return json.dumps({"ok": ok, "disabled": name})

        elif action == "enable":
            name = arguments.get("name", "")
            ok = self.enable(name)
            return json.dumps({"ok": ok, "enabled": name})

        elif action == "list":
            tools = [
                {"name": t.name, "source": t.source, "enabled": t.enabled, "tags": t.tags}
                for t in self.all(include_disabled=True)
            ]
            return json.dumps({"tools": tools, "total": len(tools)})

        return json.dumps({"error": f"Unknown native action: {action}"})

    def execute_sync(
        self,
        name: str,
        arguments: dict[str, Any],
        *,
        base_url: str = "http://127.0.0.1:8100",
        auth_token: str | None = None,
    ) -> str:
        """Synchronous wrapper for execute()."""
        import asyncio

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Already in async context -- create task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(
                    asyncio.run,
                    self.execute(name, arguments, base_url=base_url, auth_token=auth_token),
                )
                return future.result()
        else:
            return asyncio.run(
                self.execute(name, arguments, base_url=base_url, auth_token=auth_token)
            )

    # --- Runtime tool persistence ---

    def register_runtime(self, spec: ToolSpec) -> None:
        """Register a runtime tool and persist to JSON.

        Note: arg_transform (lambdas) cannot be serialized. Runtime tools
        that need argument reshaping should handle it server-side instead.
        """
        spec.source = "runtime"
        self.register(spec)
        self._persist_runtime(spec.name)

    def _ensure_runtime_loaded(self) -> None:
        if self._loaded_runtime or not self._runtime_path:
            return
        self._loaded_runtime = True
        if self._runtime_path.exists():
            try:
                data = json.loads(self._runtime_path.read_text())
                for name, entry in data.items():
                    if isinstance(entry, dict):
                        # Don't overwrite builtin tools
                        if name not in self._tools:
                            self.register(ToolSpec.from_dict(entry))
            except Exception as e:
                logger.warning(f"Failed to load runtime tools: {e}")

    def _persist_runtime(self, name: str) -> None:
        """Persist runtime tool state to JSON."""
        if not self._runtime_path:
            return
        spec = self._tools.get(name)
        if not spec or spec.source != "runtime":
            return
        try:
            data = {}
            if self._runtime_path.exists():
                data = json.loads(self._runtime_path.read_text())
            data[name] = spec.to_dict()
            self._runtime_path.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.warning(f"Failed to persist runtime tool {name}: {e}")

    # --- Introspection ---

    def summary(self) -> dict:
        all_tools = self.all(include_disabled=True)
        enabled = [t for t in all_tools if t.enabled]
        by_source = {}
        by_tag = {}
        for t in enabled:
            by_source[t.source] = by_source.get(t.source, 0) + 1
            for tag in t.tags:
                by_tag[tag] = by_tag.get(tag, 0) + 1
        return {
            "total": len(all_tools),
            "enabled": len(enabled),
            "disabled": len(all_tools) - len(enabled),
            "by_source": by_source,
            "by_tag": by_tag,
        }


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

registry = ToolRegistry()
