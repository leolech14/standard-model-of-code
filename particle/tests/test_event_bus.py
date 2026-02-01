"""
Tests for EventBus - Module Communication System
"""

import pytest
from src.core.event_bus import EventBus


class TestEventBusBasics:
    """Test basic pub/sub functionality."""

    def test_subscribe_and_emit(self):
        """Handler receives emitted events."""
        bus = EventBus()
        received = []

        bus.on('test:event', lambda data: received.append(data))
        bus.emit('test:event', {'value': 42})

        assert len(received) == 1
        assert received[0] == {'value': 42}

    def test_multiple_handlers(self):
        """Multiple handlers can subscribe to same event."""
        bus = EventBus()
        calls = []

        bus.on('event', lambda d: calls.append('handler1'))
        bus.on('event', lambda d: calls.append('handler2'))
        bus.on('event', lambda d: calls.append('handler3'))

        bus.emit('event', None)

        assert len(calls) == 3
        assert 'handler1' in calls
        assert 'handler2' in calls
        assert 'handler3' in calls

    def test_unsubscribe(self):
        """Handler can be removed with off()."""
        bus = EventBus()
        received = []

        def handler(data):
            received.append(data)

        bus.on('event', handler)
        bus.emit('event', 1)

        bus.off('event', handler)
        bus.emit('event', 2)

        assert received == [1]  # Only first emission received

    def test_emit_returns_handler_count(self):
        """emit() returns number of handlers called."""
        bus = EventBus()

        bus.on('event', lambda d: None)
        bus.on('event', lambda d: None)

        count = bus.emit('event', None)
        assert count == 2


class TestWildcardSubscriptions:
    """Test wildcard event patterns."""

    def test_wildcard_subscription(self):
        """Wildcard subscriptions match all events with prefix."""
        bus = EventBus()
        received = []

        bus.on('user:*', lambda data: received.append(data))

        bus.emit('user:created', {'id': 1})
        bus.emit('user:updated', {'id': 2})
        bus.emit('user:deleted', {'id': 3})
        bus.emit('other:event', {'id': 4})

        assert len(received) == 3
        assert received[0] == {'id': 1}
        assert received[1] == {'id': 2}
        assert received[2] == {'id': 3}

    def test_wildcard_and_exact_both_fire(self):
        """Both wildcard and exact handlers receive events."""
        bus = EventBus()
        exact_calls = []
        wildcard_calls = []

        bus.on('user:created', lambda d: exact_calls.append(d))
        bus.on('user:*', lambda d: wildcard_calls.append(d))

        bus.emit('user:created', {'id': 1})

        assert len(exact_calls) == 1
        assert len(wildcard_calls) == 1

    def test_wildcard_unsubscribe(self):
        """Can unsubscribe from wildcard patterns."""
        bus = EventBus()
        received = []

        def handler(data):
            received.append(data)

        bus.on('user:*', handler)
        bus.emit('user:created', 1)

        bus.off('user:*', handler)
        bus.emit('user:updated', 2)

        assert received == [1]


class TestErrorIsolation:
    """Test that handler errors don't crash other handlers."""

    def test_failing_handler_isolated(self):
        """One failing handler doesn't prevent others from running."""
        bus = EventBus()
        calls = []

        def failing_handler(data):
            raise ValueError("Handler failed")

        def working_handler(data):
            calls.append(data)

        bus.on('event', failing_handler)
        bus.on('event', working_handler)

        count = bus.emit('event', 'test')

        # Working handler should have executed despite failing handler
        assert 'test' in calls
        # Only one handler succeeded
        assert count == 1

    def test_wildcard_handler_error_isolation(self):
        """Wildcard handler errors don't prevent other handlers."""
        bus = EventBus()
        calls = []

        def failing_wildcard(data):
            raise RuntimeError("Wildcard failed")

        def working_handler(data):
            calls.append(data)

        bus.on('test:*', failing_wildcard)
        bus.on('test:event', working_handler)

        count = bus.emit('test:event', 'data')

        assert 'data' in calls
        assert count == 1


class TestUtilityMethods:
    """Test utility and introspection methods."""

    def test_once(self):
        """once() subscription fires only on first emission."""
        bus = EventBus()
        calls = []

        bus.once('event', lambda d: calls.append(d))

        bus.emit('event', 1)
        bus.emit('event', 2)
        bus.emit('event', 3)

        assert calls == [1]

    def test_clear_specific_event(self):
        """clear(event) removes all handlers for that event."""
        bus = EventBus()

        bus.on('event1', lambda d: None)
        bus.on('event1', lambda d: None)
        bus.on('event2', lambda d: None)

        bus.clear('event1')

        assert bus.get_handler_count('event1') == 0
        assert bus.get_handler_count('event2') == 1

    def test_clear_all_events(self):
        """clear() with no args removes all handlers."""
        bus = EventBus()

        bus.on('event1', lambda d: None)
        bus.on('event2', lambda d: None)
        bus.on('event3:*', lambda d: None)

        bus.clear()

        assert bus.get_handler_count('event1') == 0
        assert bus.get_handler_count('event2') == 0
        assert len(bus.get_events()) == 0

    def test_get_events(self):
        """get_events() lists all registered event names."""
        bus = EventBus()

        bus.on('alpha', lambda d: None)
        bus.on('beta', lambda d: None)
        bus.on('gamma:*', lambda d: None)

        events = bus.get_events()

        assert 'alpha' in events
        assert 'beta' in events
        assert 'gamma:*' in events

    def test_disable_enable(self):
        """disable() stops event emission, enable() resumes."""
        bus = EventBus()
        calls = []

        bus.on('event', lambda d: calls.append(d))

        bus.emit('event', 1)
        bus.disable()
        bus.emit('event', 2)
        bus.enable()
        bus.emit('event', 3)

        assert calls == [1, 3]  # 2 was emitted while disabled

    def test_handler_count(self):
        """get_handler_count() returns correct count."""
        bus = EventBus()

        bus.on('event', lambda d: None)
        bus.on('event', lambda d: None)
        bus.on('other:*', lambda d: None)

        assert bus.get_handler_count('event') == 2
        assert bus.get_handler_count('other:created') == 1  # Matches wildcard


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_emit_without_handlers(self):
        """Emitting to event with no handlers is safe."""
        bus = EventBus()
        count = bus.emit('nonexistent', 'data')
        assert count == 0

    def test_off_nonexistent_handler(self):
        """Removing nonexistent handler returns False."""
        bus = EventBus()
        result = bus.off('event', lambda d: None)
        assert result is False

    def test_none_data_payload(self):
        """None is a valid data payload."""
        bus = EventBus()
        received = []

        bus.on('event', lambda d: received.append(d))
        bus.emit('event', None)

        assert received == [None]

    def test_complex_data_payload(self):
        """Complex nested data structures work."""
        bus = EventBus()
        received = []

        bus.on('event', lambda d: received.append(d))

        payload = {
            'nested': {
                'list': [1, 2, 3],
                'dict': {'a': 'b'}
            },
            'value': 42
        }

        bus.emit('event', payload)

        assert received[0] == payload
        assert received[0]['nested']['list'] == [1, 2, 3]


class TestGlobalSingleton:
    """Test global singleton accessor."""

    def test_get_event_bus_singleton(self):
        """get_event_bus() returns same instance."""
        from src.core.event_bus import get_event_bus

        bus1 = get_event_bus()
        bus2 = get_event_bus()

        assert bus1 is bus2

    def test_singleton_retains_state(self):
        """Global bus retains registered handlers."""
        from src.core.event_bus import get_event_bus

        bus = get_event_bus()
        received = []

        bus.on('test:global', lambda d: received.append(d))

        # Get bus again and emit
        bus2 = get_event_bus()
        bus2.emit('test:global', 'data')

        assert received == ['data']
