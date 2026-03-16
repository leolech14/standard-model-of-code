"""
Stage 23: Atlas Emitter

Transforms Collider pipeline output into Ecosystem Atlas component candidates.
Produces `.collider/atlas_candidates.yaml` — a review-ready file of auto-detected
components with P0-minimum fields matching the atlas schema.

The emitter OBSERVES. The atlas GOVERNS. Candidates require human review
before merging into atlas/ATLAS.yaml.

Detection patterns:
  - CLI tools: `if __name__ == "__main__"` + argparse/click
  - MCP servers: FastMCP imports or @mcp.tool decorators
  - API endpoints: FastAPI @app.get/@app.post/@router
  - Library modules: __all__ exports or imported by 3+ files
  - Scheduled jobs: cron/schedule patterns
  - Webhook handlers: webhook in function/route names
"""

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


# Env var → atlas connection ID mapping.
# Small, stable table. Grows only when new connections are registered in atlas.
ENV_TO_CONNECTION: Dict[str, str] = {
    "CEREBRAS_API_KEY": "CON-001",
    "ANTHROPIC_API_KEY": "CON-002",
    "PERPLEXITY_API_KEY": "CON-007",
    "GEMINI_API_KEY": "CON-008",
    "HF_TOKEN": "CON-009",
    "NOTION_API_KEY": "CON-010",
    "GITHUB_TOKEN": "CON-006",
}

# Env var → Doppler ref mapping.
ENV_TO_DOPPLER: Dict[str, str] = {
    "CEREBRAS_API_KEY": "doppler:ai-tools/prd/CEREBRAS_API_KEY",
    "ANTHROPIC_API_KEY": "doppler:ai-tools/prd/ANTHROPIC_API_KEY",
    "PERPLEXITY_API_KEY": "doppler:ai-tools/dev/PERPLEXITY_API_KEY",
    "GEMINI_API_KEY": "doppler:ai-tools/prd/GEMINI_API_KEY",
    "HF_TOKEN": "doppler:ai-tools/dev/HF_TOKEN",
    "NOTION_API_KEY": "doppler:ai-tools/prd/NOTION_API_KEY",
    "GITHUB_TOKEN": "doppler:ai-tools/prd/GITHUB_TOKEN",
}

# D-dimension → atlas category mapping.
DIMENSION_TO_CATEGORY: Dict[str, str] = {
    "D1": "analysis",          # Structure
    "D2": "analysis",          # Complexity
    "D3": "transformation",    # Behavior
    "D4": "analysis",          # Quality
    "D5": "integration",       # Interface
    "D6": "generation",        # Generation
    "D7": "orchestration",     # Orchestration
    "D8": "monitoring",        # Observability
}

# Patterns for boundary detection.
_RE_GETENV = re.compile(r"""os\.(?:getenv|environ)\s*[\[(]\s*['"]([A-Z_]+)['"]""")
_RE_MAIN = re.compile(r"""if\s+__name__\s*==\s*['"]__main__['"]""")
_RE_ARGPARSE = re.compile(r"""argparse\.ArgumentParser|click\.command|@click\.""")
_RE_FASTMCP = re.compile(r"""from\s+mcp\.server\.fastmcp\s+import|FastMCP\(""")
_RE_MCP_TOOL = re.compile(r"""@\w+\.tool\b""")
_RE_FASTAPI = re.compile(r"""@(?:app|router)\.\s*(?:get|post|put|delete|patch)\b""")
_RE_WEBHOOK = re.compile(r"""webhook""", re.IGNORECASE)
_RE_SCHEDULE = re.compile(r"""schedule\.|cron|@periodic_task""")
_RE_ALL_EXPORT = re.compile(r"""^__all__\s*=""", re.MULTILINE)


class AtlasEmitterStage(BaseStage):
    """
    Stage 23: Atlas Emitter.

    Input: CodebaseState with all analysis results from prior stages.
    Output: CodebaseState + `.collider/atlas_candidates.yaml`

    Detects component boundaries in the analyzed codebase and emits
    atlas-compatible candidate entries for human review.
    """

    def __init__(self, output_dir: Optional[str] = None):
        self._output_dir = output_dir

    @property
    def name(self) -> str:
        return "atlas_emitter"

    @property
    def stage_number(self) -> Optional[int]:
        return 23

    def validate_input(self, state: "CodebaseState") -> bool:
        return len(state.nodes) > 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """Detect component boundaries and emit atlas candidates."""
        # Group nodes by file to detect file-level components.
        files: Dict[str, List[Dict[str, Any]]] = {}
        for _node_id, node in state.nodes.items():
            fpath = node.get("file_path", node.get("file", ""))
            # Skip __init__.py and test files.
            basename = Path(fpath).name if fpath else ""
            if basename in ("__init__.py", "conftest.py") or basename.startswith("test_"):
                continue
            if fpath:
                files.setdefault(fpath, []).append(node)

        candidates: List[Dict[str, Any]] = []
        seen_files: set = set()

        for fpath, nodes in files.items():
            if fpath in seen_files:
                continue

            # Aggregate source from all nodes in this file.
            source = "\n".join(n.get("body_source", "") for n in nodes if n.get("body_source"))
            docstring = self._get_module_docstring(nodes)
            imports = set()
            for n in nodes:
                imports.update(n.get("imports", []))

            boundary = self._detect_boundary(source, imports, fpath)
            if not boundary:
                continue

            seen_files.add(fpath)
            entry = self._build_entry(fpath, nodes, source, docstring, imports, boundary, state)
            candidates.append(entry)

        # Sort by confidence descending.
        candidates.sort(key=lambda c: c.get("confidence", 0), reverse=True)

        # Write output.
        output_path = self._resolve_output(state)
        self._write_candidates(output_path, candidates, state)

        # Store in state metadata.
        state.metadata["atlas_candidates_count"] = len(candidates)
        state.metadata["atlas_candidates_path"] = str(output_path)
        return state

    def _detect_boundary(
        self, source: str, imports: set, fpath: str
    ) -> Optional[str]:
        """Detect if a file is a component boundary. Returns delivery type or None."""
        imports_str = " ".join(str(i) for i in imports).lower()

        # MCP server (check first — most specific).
        # Module-level FastMCP imports don't appear in function body_source,
        # so also detect by file path convention (mcp_servers/ or *_mcp.py).
        if _RE_FASTMCP.search(source) or "fastmcp" in imports_str or "mcp.server" in imports_str:
            return "mcp_tool"
        if _RE_MCP_TOOL.search(source):
            return "mcp_tool"
        if "mcp_servers/" in fpath or fpath.endswith("_mcp.py") or "_mcp_server" in fpath:
            return "mcp_tool"

        # API endpoint.
        if _RE_FASTAPI.search(source):
            return "api_endpoint"

        # CLI tool — argparse/click is the primary signal.
        # __main__ may not be in node body_source (it's module-level).
        if _RE_ARGPARSE.search(source):
            return "cli_tool"
        if _RE_MAIN.search(source):
            return "cli_tool"

        # Webhook handler.
        if _RE_WEBHOOK.search(fpath) or (_RE_WEBHOOK.search(source) and _RE_FASTAPI.search(source)):
            return "webhook_handler"

        # Scheduled job.
        if _RE_SCHEDULE.search(source):
            return "scheduled_job"

        # Library module (has __all__ or is widely imported).
        if _RE_ALL_EXPORT.search(source):
            return "library"

        # Files with os.getenv calls are likely tool entry points.
        if _RE_GETENV.search(source) and fpath.endswith(".py"):
            return "cli_tool"

        return None

    def _build_entry(
        self,
        fpath: str,
        nodes: List[Dict[str, Any]],
        source: str,
        docstring: str,
        imports: set,
        boundary: str,
        state: "CodebaseState",
    ) -> Dict[str, Any]:
        """Build a P0-minimum atlas candidate entry."""
        rel_path = self._relative_path(fpath, state.target_path)
        stem = Path(fpath).stem.replace("_", "-")

        # Extract env vars.
        env_vars = sorted(set(_RE_GETENV.findall(source)))
        connections = [ENV_TO_CONNECTION[v] for v in env_vars if v in ENV_TO_CONNECTION]
        doppler_refs = [ENV_TO_DOPPLER[v] for v in env_vars if v in ENV_TO_DOPPLER]

        # Purpose from docstring.
        purpose = self._extract_purpose(docstring)

        # Category from D-dimensions if available.
        category = self._infer_category(nodes)

        # Confidence score.
        confidence = self._compute_confidence(docstring, env_vars, boundary)

        entry: Dict[str, Any] = {
            "name": stem,
            "suggested_id": None,
            "confidence": round(confidence, 2),
            "boundary_type": boundary,
            "purpose": purpose,
            "category": category,
            "delivery": boundary,
            "source_file": rel_path,
            "invoke": {
                "method": f"python {rel_path}",
                "environment": doppler_refs if doppler_refs else [],
            },
            "requires_connections": connections,
            "feeds_into": [],
            "fed_by": [],
            "detection_evidence": {
                "has_main": bool(_RE_MAIN.search(source)),
                "has_argparse": bool(_RE_ARGPARSE.search(source)),
                "env_vars_found": env_vars,
                "docstring_length": len(docstring),
                "import_count": len(imports),
            },
        }
        return entry

    def _extract_purpose(self, docstring: str) -> str:
        """Extract first sentence from docstring as purpose."""
        if not docstring:
            return "Purpose not documented."
        # Take first sentence (up to period, question mark, or newline).
        for sep in [".\n", ". ", ".\t", "\n\n"]:
            if sep in docstring:
                first = docstring[: docstring.index(sep)].strip()
                if len(first) > 10:
                    return first + ("." if not first.endswith(".") else "")
        # Fallback: first 150 chars.
        return docstring[:150].strip().split("\n")[0]

    def _infer_category(self, nodes: List[Dict[str, Any]]) -> str:
        """Infer atlas category from D-dimension classifications."""
        for node in nodes:
            dims = node.get("dimensions", {})
            if isinstance(dims, dict):
                primary = dims.get("primary_dimension", "")
                if primary in DIMENSION_TO_CATEGORY:
                    return DIMENSION_TO_CATEGORY[primary]
        return "analysis"  # Default.

    def _compute_confidence(
        self, docstring: str, env_vars: List[str], boundary: str
    ) -> float:
        """Compute confidence score (0.0-1.0) for this detection."""
        score = 0.5  # Base.
        if docstring and len(docstring) > 20:
            score += 0.15
        if env_vars:
            score += 0.1
        if boundary in ("mcp_tool", "api_endpoint"):
            score += 0.15  # High-confidence patterns.
        elif boundary == "cli_tool":
            score += 0.1
        elif boundary == "library":
            score += 0.05
        return min(score, 1.0)

    def _get_module_docstring(self, nodes: List[Dict[str, Any]]) -> str:
        """Get the module-level docstring from nodes."""
        for node in nodes:
            if node.get("kind") == "module" and node.get("docstring"):
                return node["docstring"]
        # Fallback: first node with a docstring.
        for node in nodes:
            if node.get("docstring"):
                return node["docstring"]
        return ""

    def _relative_path(self, fpath: str, target_path: str) -> str:
        """Convert absolute path to relative path from target."""
        try:
            return str(Path(fpath).relative_to(target_path))
        except ValueError:
            return fpath

    def _resolve_output(self, state: "CodebaseState") -> Path:
        """Determine output path for candidates file."""
        if self._output_dir:
            out = Path(self._output_dir)
        else:
            out = Path(state.target_path) / ".collider"
        out.mkdir(parents=True, exist_ok=True)
        return out / "atlas_candidates.yaml"

    def _write_candidates(
        self, output_path: Path, candidates: List[Dict[str, Any]], state: "CodebaseState"
    ) -> None:
        """Write candidates to YAML file."""
        import yaml

        header = (
            f"# Atlas Component Candidates\n"
            f"# Auto-generated by Collider Stage 23 (atlas_emitter)\n"
            f"# Date: {datetime.now(timezone.utc).isoformat()}\n"
            f"# Analyzed: {state.target_path}\n"
            f"# Candidates: {len(candidates)} components detected\n"
            f"#\n"
            f"# REVIEW BEFORE MERGING INTO atlas/ATLAS.yaml\n"
            f"# These are CANDIDATES, not final entries.\n"
            f"# Assign CMP-IDs and verify before adding.\n\n"
        )

        content = {"candidates": candidates}
        yaml_str = yaml.dump(content, default_flow_style=False, sort_keys=False, allow_unicode=True)

        output_path.write_text(header + yaml_str, encoding="utf-8")
