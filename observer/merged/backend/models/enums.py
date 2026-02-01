"""Canonical enums - shared between frontend and backend."""

from enum import Enum


class CanonicalStage(str, Enum):
    """Pipeline processing stages."""
    Capture = 'Capture'
    Separate = 'Separate'
    Clean = 'Clean'
    Enrich = 'Enrich'
    Mix = 'Mix'
    Distill = 'Distill'
    Publish = 'Publish'


class PipelineId(str, Enum):
    """Pipeline identifiers."""
    Refinery = 'Cloud Refinery Pipeline'
    Factory = 'Canonical Factory Pipeline'


class TruthStatus(str, Enum):
    """Artifact truth verification status."""
    VERIFIED = 'VERIFIED'
    SUPPORTED = 'SUPPORTED'
    CONFLICTING = 'CONFLICTING'
    STALE = 'STALE'
    UNVERIFIED = 'UNVERIFIED'


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    critical = 'critical'
    warning = 'warning'
    info = 'info'


class RunStatus(str, Enum):
    """Pipeline run status."""
    success = 'success'
    failed = 'failed'
    running = 'running'


class ArtifactStatus(str, Enum):
    """Artifact lifecycle status."""
    live = 'live'
    archived = 'archived'
    failed = 'failed'


class StageStatus(str, Enum):
    """Pipeline stage status."""
    idle = 'idle'
    running = 'running'
    success = 'success'
    failed = 'failed'


class ObserverType(str, Enum):
    """SMC Observer types."""
    structural = 'structural'
    operational = 'operational'
    generative = 'generative'
