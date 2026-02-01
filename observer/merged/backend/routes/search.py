"""Search and recent files routes."""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import List
from pathlib import Path
import os
import fnmatch

from middleware.path_validator import validate_path, get_sandbox_root

router = APIRouter()


class SearchResult(BaseModel):
    path: str
    name: str
    type: str
    match_context: str | None = None


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total: int


@router.get("/search")
async def search_files(
    q: str = Query(..., min_length=1),
    path: str = Query(default=None),
    max_results: int = Query(default=100, le=500)
) -> SearchResponse:
    """Search files by name.

    Args:
        q: Search query (supports * and ? wildcards)
        path: Optional path to search within
        max_results: Maximum results to return
    """
    try:
        search_root = validate_path(path) if path else get_sandbox_root()

        # Convert query to glob pattern
        pattern = f"*{q}*" if not any(c in q for c in '*?[]') else q

        results = []
        for root, dirs, files in os.walk(search_root):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for name in files + dirs:
                if fnmatch.fnmatch(name.lower(), pattern.lower()):
                    full_path = Path(root) / name
                    results.append(SearchResult(
                        path=str(full_path),
                        name=name,
                        type='directory' if full_path.is_dir() else full_path.suffix.lstrip('.') or 'file'
                    ))

                    if len(results) >= max_results:
                        break

            if len(results) >= max_results:
                break

        return SearchResponse(
            query=q,
            results=results,
            total=len(results)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent")
async def get_recent_files(limit: int = Query(default=20, le=100)) -> List[dict]:
    """Get recently modified files.

    Returns files sorted by modification time, most recent first.
    """
    try:
        root = get_sandbox_root()
        files = []

        for path in root.rglob('*'):
            if path.is_file() and not any(part.startswith('.') for part in path.parts):
                try:
                    stat = path.stat()
                    files.append({
                        'path': str(path),
                        'name': path.name,
                        'modified': stat.st_mtime,
                        'size': stat.st_size,
                        'type': path.suffix.lstrip('.') or 'file'
                    })
                except (PermissionError, OSError):
                    continue

        # Sort by modification time, most recent first
        files.sort(key=lambda x: x['modified'], reverse=True)

        return files[:limit]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
