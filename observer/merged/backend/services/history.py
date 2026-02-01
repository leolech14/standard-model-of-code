"""Undo/redo history service."""

import time
import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class ActionType(str, Enum):
    """Types of actions that can be undone/redone."""
    CREATE_FOLDER = 'create_folder'
    RENAME = 'rename'
    DELETE = 'delete'
    COPY = 'copy'
    MOVE = 'move'
    UPLOAD = 'upload'


@dataclass
class HistoryEntry:
    """A single history entry."""
    id: str
    action: ActionType
    timestamp: float
    data: Dict[str, Any]
    # For undo - stores info needed to reverse the action
    undo_data: Dict[str, Any] = field(default_factory=dict)


class HistoryService:
    """Service for tracking and undoing file operations.

    Maintains a stack of operations that can be undone/redone.
    """

    MAX_HISTORY = 50  # Maximum entries to keep

    def __init__(self):
        self._undo_stack: List[HistoryEntry] = []
        self._redo_stack: List[HistoryEntry] = []

    def record(self, action: ActionType, data: Dict[str, Any], undo_data: Dict[str, Any] = None) -> str:
        """Record an action for potential undo.

        Args:
            action: Type of action performed
            data: Data about the action (paths, names, etc.)
            undo_data: Data needed to undo the action

        Returns:
            Entry ID
        """
        entry = HistoryEntry(
            id=str(uuid.uuid4()),
            action=action,
            timestamp=time.time(),
            data=data,
            undo_data=undo_data or {}
        )

        self._undo_stack.append(entry)

        # Clear redo stack when new action is performed
        self._redo_stack.clear()

        # Limit history size
        if len(self._undo_stack) > self.MAX_HISTORY:
            self._undo_stack.pop(0)

        return entry.id

    def undo(self) -> Optional[HistoryEntry]:
        """Get the last action to undo.

        Returns:
            HistoryEntry to undo, or None if nothing to undo
        """
        if not self._undo_stack:
            return None

        entry = self._undo_stack.pop()
        self._redo_stack.append(entry)
        return entry

    def redo(self) -> Optional[HistoryEntry]:
        """Get the last undone action to redo.

        Returns:
            HistoryEntry to redo, or None if nothing to redo
        """
        if not self._redo_stack:
            return None

        entry = self._redo_stack.pop()
        self._undo_stack.append(entry)
        return entry

    @property
    def can_undo(self) -> bool:
        """Check if there's anything to undo."""
        return len(self._undo_stack) > 0

    @property
    def can_redo(self) -> bool:
        """Check if there's anything to redo."""
        return len(self._redo_stack) > 0

    def get_state(self) -> Dict[str, Any]:
        """Get current history state."""
        return {
            'can_undo': self.can_undo,
            'can_redo': self.can_redo,
            'undo_stack': [
                {
                    'id': e.id,
                    'action': e.action.value,
                    'timestamp': e.timestamp,
                    'data': e.data
                }
                for e in self._undo_stack[-10:]  # Last 10 only
            ],
            'redo_stack': [
                {
                    'id': e.id,
                    'action': e.action.value,
                    'timestamp': e.timestamp,
                    'data': e.data
                }
                for e in self._redo_stack[-10:]
            ]
        }

    def clear(self) -> None:
        """Clear all history."""
        self._undo_stack.clear()
        self._redo_stack.clear()


# Global history service instance
history_service = HistoryService()
