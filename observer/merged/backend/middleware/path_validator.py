"""Path validation middleware - prevents directory traversal attacks."""

import os
from pathlib import Path
from typing import Optional
from fastapi import HTTPException


# Configurable sandbox root - default to user's home directory
SANDBOX_ROOT = Path(os.environ.get('CONTROL_ROOM_ROOT', Path.home())).resolve()


def validate_path(path: str) -> Path:
    """Validate that a path is within the sandbox.

    Args:
        path: The path to validate (absolute or relative)

    Returns:
        Resolved absolute path

    Raises:
        HTTPException: If path is outside sandbox or invalid
    """
    if not path:
        raise HTTPException(status_code=400, detail="Path is required")

    try:
        # Handle both absolute and relative paths
        if Path(path).is_absolute():
            resolved = Path(path).resolve()
        else:
            resolved = (SANDBOX_ROOT / path).resolve()

        # Check if path is within sandbox
        try:
            resolved.relative_to(SANDBOX_ROOT)
        except ValueError:
            raise HTTPException(
                status_code=403,
                detail="Access denied: path is outside allowed directory"
            )

        return resolved

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid path: {str(e)}")


def validate_paths(paths: list[str]) -> list[Path]:
    """Validate multiple paths."""
    return [validate_path(p) for p in paths]


def get_sandbox_root() -> Path:
    """Get the sandbox root directory."""
    return SANDBOX_ROOT


def set_sandbox_root(path: str) -> None:
    """Set the sandbox root directory (for testing)."""
    global SANDBOX_ROOT
    SANDBOX_ROOT = Path(path).resolve()
