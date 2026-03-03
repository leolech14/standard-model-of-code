"""Tools Registry API — serves tool inventory from live Python registry."""

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Lazy-load registry to avoid import-time side effects
_registry = None


def _get_registry():
    global _registry
    if _registry is None:
        from tool_registry import registry
        import tools  # noqa: F401 -- triggers registration
        _registry = registry
    return _registry


@router.get("/tools", response_class=HTMLResponse)
def page_tools(request: Request):
    return templates.TemplateResponse("tools.html", {
        "request": request,
        "page": "tools",
    })


@router.get("/api/tools")
def api_tools(
    tag: str = Query(None, description="Filter by tag"),
    include_disabled: bool = Query(False, description="Include disabled tools"),
):
    """Return live tool registry."""
    reg = _get_registry()

    if tag:
        specs = reg.by_tag(tag)
    elif include_disabled:
        specs = list(reg._tools.values())
    else:
        specs = reg.all()

    tool_list = []
    for spec in specs:
        tool_list.append({
            "name": spec.name,
            "description": spec.description,
            "method": spec.method,
            "path": spec.path,
            "parameters": spec.parameters,
            "timeout": spec.timeout,
            "max_chars": spec.max_chars,
            "enabled": spec.enabled,
            "source": spec.source,
            "tags": spec.tags,
        })

    enabled_count = sum(1 for s in reg._tools.values() if s.enabled)
    disabled_count = sum(1 for s in reg._tools.values() if not s.enabled)

    return JSONResponse({
        "tools": tool_list,
        "summary": {
            "total": len(reg._tools),
            "enabled": enabled_count,
            "disabled": disabled_count,
            "returned": len(tool_list),
        },
    })


@router.get("/api/tools/{tool_name}")
def api_tool_detail(tool_name: str):
    """Return details for a single tool."""
    reg = _get_registry()
    spec = reg.get(tool_name)
    if not spec:
        return JSONResponse({"error": f"Tool {tool_name!r} not found"}, status_code=404)
    return JSONResponse({
        "name": spec.name,
        "description": spec.description,
        "method": spec.method,
        "path": spec.path,
        "parameters": spec.parameters,
        "timeout": spec.timeout,
        "max_chars": spec.max_chars,
        "enabled": spec.enabled,
        "source": spec.source,
        "tags": spec.tags,
    })


@router.get("/api/tools/tags/list")
def api_tool_tags():
    """Return all unique tags with tool counts."""
    reg = _get_registry()
    tag_counts = {}
    for spec in reg._tools.values():
        for t in spec.tags:
            tag_counts[t] = tag_counts.get(t, 0) + 1
    return JSONResponse({
        "tags": [{"tag": t, "count": c} for t, c in sorted(tag_counts.items())],
    })
