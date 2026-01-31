"""
Pipeline Booster Toggle

ONE LINE to enable GPU acceleration on any pipeline.

Usage in your pipeline config:
    boost_mode: true   # Toggle ON = cloud GPU
    boost_mode: false  # Toggle OFF = local CPU

Usage in code:
    from pipeline_booster import toggle

    # Check toggle
    if toggle.is_enabled():
        results = toggle.run(my_function, data)
    else:
        results = my_function(data)

    # Or simpler - auto-routes based on toggle
    results = toggle.auto(my_function)(data)
"""

import os
import functools
from typing import Any, Callable, TypeVar, Optional
from pathlib import Path
import yaml
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

# Global toggle state
_BOOST_ENABLED: Optional[bool] = None
_BOOST_PROVIDER: str = "modal"


def is_enabled() -> bool:
    """Check if boost mode is enabled."""
    global _BOOST_ENABLED

    if _BOOST_ENABLED is not None:
        return _BOOST_ENABLED

    # Check environment variable
    env_val = os.environ.get("PIPELINE_BOOST", "").lower()
    if env_val in ("1", "true", "on", "yes"):
        _BOOST_ENABLED = True
        return True
    if env_val in ("0", "false", "off", "no"):
        _BOOST_ENABLED = False
        return False

    # Check config file
    config_paths = [
        Path("pipeline_config.yaml"),
        Path("config/pipeline.yaml"),
        Path(".boost"),
    ]

    for config_path in config_paths:
        if config_path.exists():
            try:
                if config_path.suffix in ('.yaml', '.yml'):
                    data = yaml.safe_load(config_path.read_text())
                    if data and data.get("boost_mode"):
                        _BOOST_ENABLED = True
                        return True
                else:
                    # .boost file exists = enabled
                    _BOOST_ENABLED = True
                    return True
            except Exception:
                pass

    _BOOST_ENABLED = False
    return False


def enable():
    """Enable boost mode."""
    global _BOOST_ENABLED
    _BOOST_ENABLED = True
    os.environ["PIPELINE_BOOST"] = "1"
    logger.info("Pipeline Boost ENABLED")


def disable():
    """Disable boost mode."""
    global _BOOST_ENABLED
    _BOOST_ENABLED = False
    os.environ["PIPELINE_BOOST"] = "0"
    logger.info("Pipeline Boost DISABLED")


def set_provider(provider: str):
    """Set the boost provider (modal, runpod, gcp)."""
    global _BOOST_PROVIDER
    _BOOST_PROVIDER = provider.lower()


def run(func: Callable[..., T], *args, **kwargs) -> T:
    """
    Run a function with boost if enabled.

    Args:
        func: Function to run
        *args, **kwargs: Arguments to pass

    Returns:
        Function result
    """
    if not is_enabled():
        return func(*args, **kwargs)

    # Import and use boost
    from .core import boost, BoostConfig, ComputeBackend

    try:
        provider = ComputeBackend(_BOOST_PROVIDER)
    except ValueError:
        provider = ComputeBackend.MODAL

    config = BoostConfig(backend=provider, gpu=True)
    boosted = boost(config=config)(func)
    return boosted(*args, **kwargs)


def auto(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator that auto-routes based on toggle.

    Example:
        @toggle.auto
        def process(data):
            return heavy_work(data)

        # Runs on GPU if PIPELINE_BOOST=1, else local
        result = process(data)
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return run(func, *args, **kwargs)

    return wrapper


# Convenience class for pipeline integration
class BoostToggle:
    """
    Boost toggle for pipeline integration.

    Example in pipeline config (YAML):
        pipeline:
          name: my-pipeline
          boost:
            enabled: true
            provider: modal
            gpu: a100

    Example in code:
        boost = BoostToggle.from_config("pipeline.yaml")

        if boost.enabled:
            results = boost.run(process_fn, data)
        else:
            results = process_fn(data)
    """

    def __init__(
        self,
        enabled: bool = False,
        provider: str = "modal",
        gpu: str = "a100",
    ):
        self.enabled = enabled
        self.provider = provider
        self.gpu = gpu

    @classmethod
    def from_config(cls, config_path: str) -> "BoostToggle":
        """Load toggle from config file."""
        path = Path(config_path)
        if not path.exists():
            return cls(enabled=False)

        try:
            data = yaml.safe_load(path.read_text())
            boost_config = data.get("boost", data.get("pipeline", {}).get("boost", {}))

            return cls(
                enabled=boost_config.get("enabled", False),
                provider=boost_config.get("provider", "modal"),
                gpu=boost_config.get("gpu", "a100"),
            )
        except Exception as e:
            logger.warning(f"Could not load boost config: {e}")
            return cls(enabled=False)

    @classmethod
    def from_env(cls) -> "BoostToggle":
        """Load toggle from environment variables."""
        return cls(
            enabled=os.environ.get("PIPELINE_BOOST", "").lower() in ("1", "true", "on"),
            provider=os.environ.get("BOOST_PROVIDER", "modal"),
            gpu=os.environ.get("BOOST_GPU", "a100"),
        )

    def run(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Run function with boost if enabled."""
        if not self.enabled:
            return func(*args, **kwargs)

        from .modal_boost import modal_boost

        boosted = modal_boost(gpu=self.gpu)(func)
        return boosted(*args, **kwargs)

    def __bool__(self) -> bool:
        return self.enabled


# Quick CLI status
def status():
    """Print current boost status."""
    enabled = is_enabled()
    provider = _BOOST_PROVIDER

    print(f"""
╔═══════════════════════════════════════╗
║       PIPELINE BOOST STATUS           ║
╠═══════════════════════════════════════╣
║  Enabled:  {'YES ✓' if enabled else 'NO ✗'}                       ║
║  Provider: {provider.upper():30} ║
╠═══════════════════════════════════════╣
║  Toggle ON:   export PIPELINE_BOOST=1 ║
║  Toggle OFF:  export PIPELINE_BOOST=0 ║
╚═══════════════════════════════════════╝
""")


if __name__ == "__main__":
    status()
