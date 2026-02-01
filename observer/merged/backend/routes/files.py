"""File listing and preview routes."""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import List
from pathlib import Path

from middleware.path_validator import validate_path
from services.file_ops import FileService
from services.preview import PreviewService

router = APIRouter()


class FileItem(BaseModel):
    path: str
    name: str
    size: int
    type: str
    modified: float
    is_directory: bool = False


class DirectoryListing(BaseModel):
    path: str
    files: List[FileItem]
    total: int


@router.get("/list")
async def list_directory(path: str = Query(...)) -> DirectoryListing:
    """List directory contents."""
    try:
        validated_path = validate_path(path)
        items = FileService.list_directory(validated_path)
        return DirectoryListing(
            path=str(validated_path),
            files=[FileItem(**item) for item in items],
            total=len(items)
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/preview")
async def preview_file(path: str = Query(...)) -> dict:
    """Get file preview (first N lines or thumbnail)."""
    try:
        validated_path = validate_path(path)
        return PreviewService.get_preview(validated_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/content")
async def get_content(path: str = Query(...)) -> dict:
    """Get full file content."""
    try:
        validated_path = validate_path(path)
        content = PreviewService.get_full_content(validated_path)
        return {"path": str(validated_path), "content": content}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IsADirectoryError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/metadata")
async def get_metadata(path: str = Query(...)) -> dict:
    """Get file metadata."""
    try:
        validated_path = validate_path(path)
        return FileService.get_metadata(validated_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
