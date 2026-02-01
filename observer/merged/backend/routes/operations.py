"""File operation routes - CRUD, compress, extract."""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Literal
from pathlib import Path
import aiofiles
import shutil

from middleware.path_validator import validate_path, validate_paths
from services.file_ops import FileService
from services.history import history_service, ActionType

router = APIRouter()


class PasteRequest(BaseModel):
    files: List[str]
    destination: str
    operation: Literal["copy", "move"] = "copy"


class DeleteRequest(BaseModel):
    files: List[str]


class CreateFolderRequest(BaseModel):
    path: str
    name: str


class RenameRequest(BaseModel):
    path: str
    new_name: str


class OperationResult(BaseModel):
    success: bool
    message: str | None = None
    error: str | None = None
    paths: List[str] | None = None


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    path: str = ""
) -> OperationResult:
    """Upload a file."""
    try:
        dest_dir = validate_path(path) if path else validate_path(".")
        dest_path = dest_dir / file.filename

        # Write file
        async with aiofiles.open(dest_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        # Record for undo
        history_service.record(
            ActionType.UPLOAD,
            {'path': str(dest_path)},
            {'path': str(dest_path)}  # For undo: delete the file
        )

        return OperationResult(success=True, message=f"Uploaded {file.filename}", paths=[str(dest_path)])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paste")
async def paste_files(request: PasteRequest) -> OperationResult:
    """Copy or move files."""
    try:
        sources = validate_paths(request.files)
        destination = validate_path(request.destination)

        if request.operation == "copy":
            result_paths = FileService.copy(sources, destination)
            action = ActionType.COPY
        else:
            result_paths = FileService.move(sources, destination)
            action = ActionType.MOVE

        # Record for undo
        history_service.record(
            action,
            {'sources': request.files, 'destination': request.destination, 'operation': request.operation},
            {'paths': result_paths, 'original_sources': request.files}
        )

        return OperationResult(
            success=True,
            message=f"{request.operation.capitalize()}d {len(result_paths)} items",
            paths=result_paths
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/delete")
async def delete_files(request: DeleteRequest) -> OperationResult:
    """Delete files (move to trash)."""
    try:
        paths = validate_paths(request.files)
        deleted = FileService.delete(paths, to_trash=True)

        # Record for undo (restore from trash)
        history_service.record(
            ActionType.DELETE,
            {'files': request.files},
            {'deleted_paths': deleted}
        )

        return OperationResult(
            success=True,
            message=f"Deleted {len(deleted)} items",
            paths=deleted
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-folder")
async def create_folder(request: CreateFolderRequest) -> OperationResult:
    """Create a new folder."""
    try:
        parent = validate_path(request.path)
        new_folder = FileService.create_folder(parent, request.name)

        history_service.record(
            ActionType.CREATE_FOLDER,
            {'path': str(new_folder)},
            {'path': str(new_folder)}  # For undo: delete the folder
        )

        return OperationResult(
            success=True,
            message=f"Created folder {request.name}",
            paths=[str(new_folder)]
        )
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rename")
async def rename_file(request: RenameRequest) -> OperationResult:
    """Rename a file or folder."""
    try:
        path = validate_path(request.path)
        old_name = path.name
        new_path = FileService.rename(path, request.new_name)

        history_service.record(
            ActionType.RENAME,
            {'old_path': request.path, 'new_name': request.new_name},
            {'new_path': str(new_path), 'old_name': old_name}
        )

        return OperationResult(
            success=True,
            message=f"Renamed to {request.new_name}",
            paths=[str(new_path)]
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compress")
async def compress_files(files: List[str], archive_name: str = "archive.zip") -> OperationResult:
    """Create zip archive."""
    try:
        paths = validate_paths(files)

        if not paths:
            raise HTTPException(status_code=400, detail="No files to compress")

        # Create archive in same directory as first file
        archive_path = paths[0].parent / archive_name

        shutil.make_archive(
            str(archive_path.with_suffix('')),
            'zip',
            paths[0].parent,
            paths[0].name if len(paths) == 1 else None
        )

        return OperationResult(
            success=True,
            message=f"Created archive {archive_name}",
            paths=[str(archive_path)]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract")
async def extract_archive(path: str, destination: str = None) -> OperationResult:
    """Extract archive."""
    try:
        archive_path = validate_path(path)
        dest_path = validate_path(destination) if destination else archive_path.parent

        shutil.unpack_archive(str(archive_path), str(dest_path))

        return OperationResult(
            success=True,
            message=f"Extracted to {dest_path}",
            paths=[str(dest_path)]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
