"""Pipeline and monitoring models."""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from .enums import (
    CanonicalStage,
    PipelineId,
    RunStatus,
    StageStatus,
    AlertSeverity,
    ObserverType
)


class PipelineStageConfig(BaseModel):
    """Pipeline stage configuration."""
    name: CanonicalStage
    description: str
    is_loop_start: Optional[bool] = None
    is_loop_end: Optional[bool] = None
    loop_target: Optional[CanonicalStage] = None
    status: StageStatus
    queue_depth: int
    last_updated: float


class Run(BaseModel):
    """Pipeline run."""
    id: str
    project_id: str
    pipeline_id: PipelineId
    status: RunStatus
    start_time: float
    duration: str
    triggered_by: str


class Alert(BaseModel):
    """System alert."""
    id: str
    severity: AlertSeverity
    message: str
    timestamp: float
    acknowledged: bool
    source: str


class ObserverStatus(BaseModel):
    """SMC Observer status."""
    type: ObserverType
    active: bool
    last_update: float
    metrics: Dict[str, float]


class HistoryEntry(BaseModel):
    """Undo/redo history entry."""
    id: str
    action: str
    timestamp: float
    data: Dict[str, Any]


class HistoryState(BaseModel):
    """History state for undo/redo."""
    can_undo: bool
    can_redo: bool
    undo_stack: List[HistoryEntry]
    redo_stack: List[HistoryEntry]
