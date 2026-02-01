"""Authentication models."""

from pydantic import BaseModel
from typing import Optional, Literal


class AuthState(BaseModel):
    """Authentication state."""
    is_authenticated: bool
    token: Optional[str] = None
    error: Optional[str] = None
    loading: bool = False


class AuthResponse(BaseModel):
    """Authentication response."""
    authenticated: bool
    token: Optional[str] = None
    error: Optional[str] = None


class AppSettings(BaseModel):
    """Application settings."""
    poll_interval: int = 5000
    show_notifications: bool = True
    auto_pin: bool = False
    api_base_url: str = 'http://localhost:8000'


class AppState(BaseModel):
    """Application state."""
    last_visit: float
    theme: Literal['dark'] = 'dark'
    settings: AppSettings


# WebSocket message types
class WSMessage(BaseModel):
    """WebSocket message."""
    type: str
    event: str
    data: Optional[dict] = None
    room: Optional[str] = None
    timestamp: Optional[float] = None


class FileChangeEvent(BaseModel):
    """File change WebSocket event."""
    type: Literal['file_change'] = 'file_change'
    event: Literal['created', 'modified', 'deleted']
    path: str
    name: str


class PipelineProgressEvent(BaseModel):
    """Pipeline progress WebSocket event."""
    type: Literal['pipeline_progress'] = 'pipeline_progress'
    pipeline_id: str
    stage: str
    status: Literal['in_progress', 'completed', 'failed']


class AlertBroadcastEvent(BaseModel):
    """Alert broadcast WebSocket event."""
    type: Literal['alert_broadcast'] = 'alert_broadcast'
    alert_id: str
    message: str
    severity: Literal['info', 'warning', 'error']
