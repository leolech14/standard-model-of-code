"""
Event Bus - Decoupled Module Communication
============================================
SMoC Role: Infrastructure | Domain: Coordination

Minimal pub/sub event system for cross-module communication.
Enables loose coupling between modules via events instead of direct dependencies.

Usage:
    from src.core.event_bus import EventBus

    bus = EventBus()

    # Subscribe
    bus.on('user:created', lambda data: print(f"User {data['id']} created"))

    # Publish
    bus.emit('user:created', {'id': 123, 'name': 'Alice'})

    # Unsubscribe
    bus.off('user:created', handler)

Part of: Elements Hub Architecture (MODULAR_ARCHITECTURE_SYNTHESIS.md)
"""

from typing import Callable, Dict, List, Optional, Any
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class EventBus:
    """
    Minimal pub/sub event bus for module communication.

    Features:
    - Subscribe to events by name
    - Emit events with optional data payload
    - Unsubscribe specific handlers
    - Wildcard subscriptions (e.g., 'user:*')
    - Handler error isolation (one failing handler doesn't crash others)
    """

    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._wildcard_handlers: List[tuple[str, Callable]] = []
        self._enabled = True

    def on(self, event: str, handler: Callable[[Any], None]) -> None:
        """
        Subscribe to an event.

        Args:
            event: Event name (e.g., 'user:created', 'data:*')
            handler: Callback function receiving event data

        Example:
            bus.on('module:loaded', lambda data: print(f"Loaded {data['name']}"))
        """
        if event.endswith(':*'):
            # Wildcard subscription
            prefix = event[:-2]
            self._wildcard_handlers.append((prefix, handler))
        else:
            self._handlers[event].append(handler)

    def emit(self, event: str, data: Optional[Any] = None) -> int:
        """
        Publish an event to all subscribers.

        Args:
            event: Event name
            data: Optional payload (dict, list, primitive, etc.)

        Returns:
            Number of handlers that successfully executed

        Example:
            bus.emit('task:completed', {'task_id': 'T-001', 'status': 'success'})
        """
        if not self._enabled:
            return 0

        handlers_called = 0

        # Direct handlers
        for handler in self._handlers.get(event, []):
            try:
                handler(data)
                handlers_called += 1
            except Exception as e:
                logger.error(f"Event handler failed for '{event}': {e}", exc_info=True)

        # Wildcard handlers
        for prefix, handler in self._wildcard_handlers:
            if event.startswith(prefix + ':'):
                try:
                    handler(data)
                    handlers_called += 1
                except Exception as e:
                    logger.error(f"Wildcard handler failed for '{event}': {e}", exc_info=True)

        return handlers_called

    def off(self, event: str, handler: Callable) -> bool:
        """
        Unsubscribe a specific handler from an event.

        Args:
            event: Event name
            handler: The exact handler function to remove

        Returns:
            True if handler was found and removed

        Example:
            def my_handler(data): ...
            bus.on('event', my_handler)
            bus.off('event', my_handler)
        """
        if event.endswith(':*'):
            prefix = event[:-2]
            original_len = len(self._wildcard_handlers)
            self._wildcard_handlers = [
                (p, h) for p, h in self._wildcard_handlers
                if not (p == prefix and h == handler)
            ]
            return len(self._wildcard_handlers) < original_len
        else:
            if event in self._handlers:
                try:
                    self._handlers[event].remove(handler)
                    return True
                except ValueError:
                    return False
            return False

    def clear(self, event: Optional[str] = None) -> None:
        """
        Clear all handlers for an event, or all events if None.

        Args:
            event: Event name to clear, or None to clear all

        Example:
            bus.clear('user:*')      # Clear all user events
            bus.clear()              # Clear ALL events
        """
        if event is None:
            self._handlers.clear()
            self._wildcard_handlers.clear()
        elif event.endswith(':*'):
            prefix = event[:-2]
            # Clear exact event handlers starting with prefix
            keys_to_clear = [k for k in self._handlers if k.startswith(prefix + ':')]
            for k in keys_to_clear:
                del self._handlers[k]
            # Clear wildcard handlers
            self._wildcard_handlers = [
                (p, h) for p, h in self._wildcard_handlers if p != prefix
            ]
        else:
            if event in self._handlers:
                del self._handlers[event]

    def once(self, event: str, handler: Callable[[Any], None]) -> None:
        """
        Subscribe to an event, but automatically unsubscribe after first emission.

        Args:
            event: Event name
            handler: Callback function

        Example:
            bus.once('startup:complete', lambda _: print('App started!'))
        """
        def wrapper(data):
            handler(data)
            self.off(event, wrapper)

        self.on(event, wrapper)

    def disable(self) -> None:
        """Temporarily disable all event emission (for testing)."""
        self._enabled = False

    def enable(self) -> None:
        """Re-enable event emission after disable()."""
        self._enabled = True

    def get_events(self) -> List[str]:
        """
        List all registered event names.

        Returns:
            List of event names with active handlers
        """
        events = list(self._handlers.keys())
        events.extend([f"{prefix}:*" for prefix, _ in self._wildcard_handlers])
        return sorted(set(events))

    def get_handler_count(self, event: str) -> int:
        """
        Count handlers registered for an event.

        Args:
            event: Event name

        Returns:
            Number of registered handlers
        """
        count = len(self._handlers.get(event, []))

        # Count wildcard handlers that match
        if ':' in event:
            prefix = event.split(':')[0]
            count += sum(1 for p, _ in self._wildcard_handlers if p == prefix)

        return count


# Global singleton for convenience (optional - can create instances)
_global_bus = None

def get_event_bus() -> EventBus:
    """Get or create global EventBus singleton."""
    global _global_bus
    if _global_bus is None:
        _global_bus = EventBus()
    return _global_bus
