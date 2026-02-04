"""Semantic Pipeline API Routes."""

from fastapi import APIRouter, HTTPException
from typing import List, Dict
import time
import random

from models.pipeline import (
    PipelineStageConfig,
    Run,
    Alert,
    Artifact
)
from models.enums import (
    CanonicalStage,
    PipelineId,
    RunStatus,
    StageStatus,
    AlertSeverity,
    TruthStatus
)

# Initialize router
router = APIRouter()

# --- Semantic Data Source (Replaces Mock Data) ---

PROJECTS = ['Project_Helios', 'Project_Aether', 'Project_Nyx', 'Internal_Ops']

def generate_id():
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=8))

# Static Pipeline Definitions (Backend Source of Truth)
PIPELINES: Dict[PipelineId, List[PipelineStageConfig]] = {
    PipelineId.Refinery: [
        PipelineStageConfig(
            name=CanonicalStage.Capture,
            description="Ingests raw telemetry from edge nodes.",
            status=StageStatus.success,
            queue_depth=12,
            last_updated=time.time() - 7200
        ),
        PipelineStageConfig(
            name=CanonicalStage.Separate,
            description="Splits streams into audio, video, and metadata.",
            status=StageStatus.running,
            queue_depth=450,
            last_updated=time.time()
        ),
        PipelineStageConfig(
            name=CanonicalStage.Clean,
            description="Normalizes audio gain and removes video artifacts.",
            status=StageStatus.idle,
            queue_depth=0,
            last_updated=time.time() - 18000
        ),
        PipelineStageConfig(
            name=CanonicalStage.Enrich,
            description="Adds AI-generated tags and transcription.",
            status=StageStatus.success,
            queue_depth=5,
            last_updated=time.time() - 3600,
            is_loop_start=True
        ),
        PipelineStageConfig(
            name=CanonicalStage.Mix,
            description="Combines enriched streams for preview.",
            status=StageStatus.failed,
            queue_depth=2,
            last_updated=time.time() - 1800,
            is_loop_end=True,
            loop_target=CanonicalStage.Enrich
        ),
        PipelineStageConfig(
            name=CanonicalStage.Publish,
            description="Pushes to CDN and archives to cold storage.",
            status=StageStatus.idle,
            queue_depth=0,
            last_updated=time.time() - 43200
        )
    ],
    PipelineId.Factory: [
        PipelineStageConfig(
            name=CanonicalStage.Capture,
            description="Polls external partner APIs for new assets.",
            status=StageStatus.success,
            queue_depth=0,
            last_updated=time.time() - 14400
        ),
        PipelineStageConfig(
            name=CanonicalStage.Clean,
            description="Standardizes metadata formats.",
            status=StageStatus.success,
            queue_depth=0,
            last_updated=time.time() - 14400
        ),
        PipelineStageConfig(
            name=CanonicalStage.Distill,
            description="Generates summary reports and thumbnails.",
            status=StageStatus.running,
            queue_depth=89,
            last_updated=time.time()
        ),
        PipelineStageConfig(
            name=CanonicalStage.Publish,
            description="Updates internal registries.",
            status=StageStatus.idle,
            queue_depth=0,
            last_updated=time.time() - 86400
        )
    ]
}


@router.get("/pipelines", response_model=Dict[PipelineId, List[PipelineStageConfig]])
async def get_pipelines():
    """Get all pipeline configurations."""
    return PIPELINES


@router.get("/runs", response_model=List[Run])
async def get_runs():
    """Get recent pipeline runs."""
    # TODO: Connect to actual run history DB
    return []


@router.get("/artifacts", response_model=List[Artifact])
async def get_artifacts():
    """Get all enriched artifacts."""
    # This replaces the client-side 'enrichFile' logic
    # TODO: Fetch real files from FileService and enrich here
    return []
