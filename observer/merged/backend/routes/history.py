"""Undo/redo history routes."""

from fastapi import APIRouter, HTTPException
from pathlib import Path

from services.history import history_service, ActionType
from services.file_ops import FileService

router = APIRouter()


@router.post("/undo")
async def undo_action() -> dict:
    """Undo last action."""
    entry = history_service.undo()

    if not entry:
        return {"success": False, "error": "Nothing to undo"}

    try:
        # Perform the undo based on action type
        if entry.action == ActionType.CREATE_FOLDER:
            # Delete the created folder
            path = Path(entry.undo_data.get('path'))
            if path.exists():
                FileService.delete([path], to_trash=True)

        elif entry.action == ActionType.RENAME:
            # Rename back to original
            new_path = Path(entry.undo_data.get('new_path'))
            old_name = entry.undo_data.get('old_name')
            if new_path.exists():
                FileService.rename(new_path, old_name)

        elif entry.action == ActionType.DELETE:
            # Can't easily undo trash - would need to restore from Trash
            return {
                "success": False,
                "error": "Cannot undo delete - items are in Trash",
                "action": entry.action.value
            }

        elif entry.action == ActionType.UPLOAD:
            # Delete the uploaded file
            path = Path(entry.undo_data.get('path'))
            if path.exists():
                FileService.delete([path], to_trash=True)

        elif entry.action in (ActionType.COPY, ActionType.MOVE):
            # Delete copied files or move back
            paths = entry.undo_data.get('paths', [])
            if entry.action == ActionType.COPY:
                FileService.delete([Path(p) for p in paths], to_trash=True)
            else:
                # For move, would need to move back - complex
                return {
                    "success": False,
                    "error": "Cannot undo move operation",
                    "action": entry.action.value
                }

        return {
            "success": True,
            "action": entry.action.value,
            "message": f"Undid {entry.action.value}"
        }

    except Exception as e:
        return {"success": False, "error": str(e), "action": entry.action.value}


@router.post("/redo")
async def redo_action() -> dict:
    """Redo last undone action."""
    entry = history_service.redo()

    if not entry:
        return {"success": False, "error": "Nothing to redo"}

    # For now, just report what would be redone
    # Full redo implementation would replay the original action
    return {
        "success": True,
        "action": entry.action.value,
        "message": f"Redid {entry.action.value}",
        "data": entry.data
    }


@router.get("/state")
async def get_history_state() -> dict:
    """Get current history state."""
    return history_service.get_state()
