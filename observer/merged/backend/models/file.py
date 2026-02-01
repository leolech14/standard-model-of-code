"""File and Artifact models."""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from .enums import CanonicalStage, PipelineId, TruthStatus, ArtifactStatus


class FileItem(BaseModel):
    """Base file from file system."""
    path: str
    name: str
    size: int
    type: str
    modified: float  # Unix timestamp
    is_directory: bool = False


class Artifact(BaseModel):
    """Artifact from refinery pipeline."""
    id: str
    name: str
    project_id: str
    pipeline_id: PipelineId
    stage: CanonicalStage
    type: str
    size: str
    updated_at: float
    tags: List[str]
    status: ArtifactStatus
    is_vaulted: Optional[bool] = None
    atom_class: str
    truth_status: TruthStatus


class UnifiedFile(Artifact):
    """Bridges Artifact and FileItem."""
    path: str
    modified: float
    is_directory: bool = False


class DirectoryListing(BaseModel):
    """Directory listing response."""
    path: str
    files: List[FileItem]
    total: int


class FilePreview(BaseModel):
    """File preview response."""
    path: str
    preview: Optional[str] = None
    type: str
    language: Optional[str] = None
    line_count: Optional[int] = None


class FileMetadata(BaseModel):
    """File metadata."""
    path: str
    size: int
    created: float
    modified: float
    accessed: float
    permissions: str
    owner: str
    mime_type: str


class PasteRequest(BaseModel):
    """Copy/move request."""
    files: List[str]
    destination: str
    operation: str = 'copy'  # 'copy' or 'move'


class DeleteRequest(BaseModel):
    """Delete request."""
    files: List[str]


class CreateFolderRequest(BaseModel):
    """Create folder request."""
    path: str
    name: str


class RenameRequest(BaseModel):
    """Rename request."""
    path: str
    new_name: str


class OperationResult(BaseModel):
    """Operation result."""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None


class SearchResult(BaseModel):
    """Search result item."""
    path: str
    name: str
    type: str
    match_context: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response."""
    query: str
    results: List[SearchResult]
    total: int
