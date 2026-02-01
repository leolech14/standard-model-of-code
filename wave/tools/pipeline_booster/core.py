"""
Pipeline Booster Core - The boost() decorator and configuration.
"""

import functools
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional, List, Dict, TypeVar, ParamSpec

logger = logging.getLogger(__name__)

P = ParamSpec('P')
T = TypeVar('T')


class ComputeBackend(Enum):
    """Available compute backends."""
    LOCAL = "local"           # Local CPU/GPU
    MODAL = "modal"           # Modal.com (easiest)
    RUNPOD = "runpod"         # RunPod (cheapest)
    GCP = "gcp"               # Google Cloud
    AWS = "aws"               # AWS
    AUTO = "auto"             # Auto-select best


@dataclass
class BoostConfig:
    """Configuration for pipeline boosting."""

    # Compute settings
    backend: ComputeBackend = ComputeBackend.AUTO
    gpu: bool = True
    gpu_type: str = "any"     # "any", "a100", "t4", "rtx4090"
    memory_gb: int = 16
    timeout_seconds: int = 3600

    # Cost controls
    max_cost_per_run: float = 1.0   # USD
    prefer_spot: bool = True         # Use spot/preemptible

    # Fallback behavior
    fallback_to_local: bool = True
    local_if_small: bool = True      # Use local for small jobs
    small_threshold: int = 10        # Items below this = "small"

    # Caching
    cache_results: bool = True
    cache_dir: str = ".boost_cache"

    # Provider-specific
    modal_app_name: str = "pipeline-booster"
    gcp_project: Optional[str] = None
    gcp_region: str = "us-central1"

    @classmethod
    def fast(cls) -> "BoostConfig":
        """Preset: Fastest execution, higher cost."""
        return cls(
            gpu=True,
            gpu_type="a100",
            memory_gb=32,
            prefer_spot=False,
            max_cost_per_run=5.0,
        )

    @classmethod
    def cheap(cls) -> "BoostConfig":
        """Preset: Lowest cost, may be slower."""
        return cls(
            gpu=True,
            gpu_type="t4",
            memory_gb=8,
            prefer_spot=True,
            max_cost_per_run=0.50,
        )

    @classmethod
    def local_only(cls) -> "BoostConfig":
        """Preset: Never use cloud."""
        return cls(
            backend=ComputeBackend.LOCAL,
            gpu=True,
            fallback_to_local=True,
        )


class BoostContext:
    """Runtime context for boosted functions."""

    def __init__(self, config: BoostConfig):
        self.config = config
        self.backend_used: Optional[str] = None
        self.execution_time: float = 0
        self.cost_estimate: float = 0
        self.gpu_used: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "backend_used": self.backend_used,
            "execution_time": self.execution_time,
            "cost_estimate": self.cost_estimate,
            "gpu_used": self.gpu_used,
        }


def _detect_best_backend(config: BoostConfig) -> ComputeBackend:
    """Auto-detect the best available backend."""

    # Check for local GPU first
    try:
        import torch
        if torch.cuda.is_available():
            logger.info("Local CUDA GPU detected")
            return ComputeBackend.LOCAL
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            logger.info("Local MPS (Apple Silicon) detected")
            return ComputeBackend.LOCAL
    except ImportError:
        pass

    # Check for Modal (easiest cloud option)
    if os.environ.get("MODAL_TOKEN_ID"):
        logger.info("Modal credentials detected")
        return ComputeBackend.MODAL

    # Check for GCP
    if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or config.gcp_project:
        logger.info("GCP credentials detected")
        return ComputeBackend.GCP

    # Check for RunPod
    if os.environ.get("RUNPOD_API_KEY"):
        logger.info("RunPod credentials detected")
        return ComputeBackend.RUNPOD

    # Default to local
    logger.info("No cloud credentials, using local compute")
    return ComputeBackend.LOCAL


def _should_use_local(config: BoostConfig, *args, **kwargs) -> bool:
    """Determine if job is small enough for local execution."""
    if not config.local_if_small:
        return False

    # Try to estimate job size from arguments
    for arg in args:
        if hasattr(arg, '__len__'):
            if len(arg) <= config.small_threshold:
                return True

    for v in kwargs.values():
        if hasattr(v, '__len__'):
            if len(v) <= config.small_threshold:
                return True

    return False


def boost(
    gpu: bool = True,
    backend: str = "auto",
    config: Optional[BoostConfig] = None,
    **config_kwargs
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to boost a function with GPU/cloud compute.

    Args:
        gpu: Whether to use GPU acceleration
        backend: Compute backend ("auto", "local", "modal", "runpod", "gcp")
        config: Full BoostConfig object
        **config_kwargs: Additional config options

    Returns:
        Decorated function that auto-routes to best compute

    Examples:
        # Simple usage - auto-detect best compute
        @boost()
        def process(data):
            return heavy_computation(data)

        # Force Modal
        @boost(backend="modal")
        def process(data):
            return heavy_computation(data)

        # Custom config
        @boost(config=BoostConfig.fast())
        def process(data):
            return heavy_computation(data)
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        # Build config
        if config is not None:
            cfg = config
        else:
            try:
                backend_enum = ComputeBackend(backend.lower())
            except ValueError:
                backend_enum = ComputeBackend.AUTO
            cfg = BoostConfig(backend=backend_enum, gpu=gpu, **config_kwargs)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            ctx = BoostContext(cfg)
            start_time = time.time()

            # Determine backend
            if cfg.backend == ComputeBackend.AUTO:
                selected_backend = _detect_best_backend(cfg)
            else:
                selected_backend = cfg.backend

            # Check if small enough for local
            if selected_backend != ComputeBackend.LOCAL and _should_use_local(cfg, *args, **kwargs):
                logger.info(f"Job small enough, using local compute")
                selected_backend = ComputeBackend.LOCAL

            ctx.backend_used = selected_backend.value

            try:
                # Route to appropriate backend
                if selected_backend == ComputeBackend.LOCAL:
                    result = _run_local(func, cfg, *args, **kwargs)
                elif selected_backend == ComputeBackend.MODAL:
                    result = _run_modal(func, cfg, *args, **kwargs)
                elif selected_backend == ComputeBackend.RUNPOD:
                    result = _run_runpod(func, cfg, *args, **kwargs)
                elif selected_backend == ComputeBackend.GCP:
                    result = _run_gcp(func, cfg, *args, **kwargs)
                else:
                    result = _run_local(func, cfg, *args, **kwargs)

                ctx.execution_time = time.time() - start_time
                logger.info(
                    f"Boosted {func.__name__} completed in {ctx.execution_time:.2f}s "
                    f"using {ctx.backend_used}"
                )
                return result

            except Exception as e:
                if cfg.fallback_to_local and selected_backend != ComputeBackend.LOCAL:
                    logger.warning(f"Cloud failed, falling back to local: {e}")
                    ctx.backend_used = "local_fallback"
                    result = _run_local(func, cfg, *args, **kwargs)
                    ctx.execution_time = time.time() - start_time
                    return result
                raise

        # Attach config for inspection
        wrapper._boost_config = cfg
        wrapper._boost_original = func

        return wrapper

    return decorator


def _run_local(func: Callable, config: BoostConfig, *args, **kwargs) -> Any:
    """Run function locally."""
    logger.debug(f"Running {func.__name__} locally")
    return func(*args, **kwargs)


def _run_modal(func: Callable, config: BoostConfig, *args, **kwargs) -> Any:
    """Run function on Modal."""
    try:
        import modal
    except ImportError:
        raise ImportError(
            "Modal not installed. Run: pip install modal && modal setup"
        )

    # Create Modal stub dynamically
    app = modal.App(config.modal_app_name)

    # Configure GPU
    if config.gpu:
        if config.gpu_type == "a100":
            gpu_config = modal.gpu.A100()
        elif config.gpu_type == "t4":
            gpu_config = modal.gpu.T4()
        else:
            gpu_config = modal.gpu.Any()
    else:
        gpu_config = None

    # Create remote function
    image = modal.Image.debian_slim().pip_install("docling", "torch")

    @app.function(gpu=gpu_config, image=image, timeout=config.timeout_seconds)
    def remote_func(*args, **kwargs):
        return func(*args, **kwargs)

    # Run remotely
    with app.run():
        return remote_func.remote(*args, **kwargs)


def _run_runpod(func: Callable, config: BoostConfig, *args, **kwargs) -> Any:
    """Run function on RunPod."""
    try:
        import runpod
    except ImportError:
        raise ImportError(
            "RunPod not installed. Run: pip install runpod"
        )

    # RunPod requires serverless endpoint setup
    # For now, fall back to local with warning
    logger.warning("RunPod integration requires endpoint setup. Using local.")
    return _run_local(func, config, *args, **kwargs)


def _run_gcp(func: Callable, config: BoostConfig, *args, **kwargs) -> Any:
    """Run function on GCP."""
    # GCP requires more setup (Vertex AI or Compute Engine)
    # For now, fall back to local with warning
    logger.warning("GCP integration not yet implemented. Using local.")
    return _run_local(func, config, *args, **kwargs)
