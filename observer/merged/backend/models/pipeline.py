"""Pipeline and monitoring models."""

from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any

from .enums import (
    CanonicalStage,
    PipelineId,
    RunStatus,
    StageStatus,
    AlertSeverity,
    ObserverType,
    TruthStatus
)


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase."""
    words = string.split('_')
    return words[0] + ''.join(word.capitalize() for word in words[1:])


class BaseSchema(BaseModel):
    """Base schema with camelCase aliasing."""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )


class PipelineStageConfig(BaseSchema):
    """Pipeline stage configuration."""
    name: CanonicalStage
    description: str
    is_loop_start: Optional[bool] = None
    is_loop_end: Optional[bool] = None
    loop_target: Optional[CanonicalStage] = None
    status: StageStatus
    queue_depth: int
    last_updated: float


class Run(BaseSchema):
    """Pipeline run."""
    id: str
    project_id: str
    pipeline_id: PipelineId
    status: RunStatus
    start_time: float
    duration: str
    triggered_by: str


class Alert(BaseSchema):
    """System alert."""
    id: str
    severity: AlertSeverity
    message: str
    timestamp: float
    acknowledged: bool
    source: str


class ObserverStatus(BaseSchema):
    """SMC Observer status."""
    type: ObserverType
    active: bool
    last_update: float
    metrics: Dict[str, float]


class HistoryEntry(BaseSchema):
    """Undo/redo history entry."""
    id: str
    action: str
    timestamp: float
    data: Dict[str, Any]


class HistoryState(BaseSchema):
    """History state for undo/redo."""
    can_undo: bool
    can_redo: bool
    undo_stack: List[HistoryEntry]
    redo_stack: List[HistoryEntry]


class Artifact(BaseSchema):
    """Enriched file artifact."""
    id: str
    name: str
    project_id: str
    pipeline_id: PipelineId
    stage: CanonicalStage
    type: str
    size: str
    updated_at: float
    tags: List[str]
    status: str
    is_vaulted: bool = False
    atom_class: str
    truth_status: TruthStatus
