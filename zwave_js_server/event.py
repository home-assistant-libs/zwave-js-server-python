"""Provide Event base classes for Z-Wave JS."""


class EventBase:
    """Represent a Z-Wave JS base class for event handling models."""

    def __init__(self):
        """Initialize event base."""
        self._listeners = {}

    def on(self, event_name, callback):  # pylint: disable=invalid-name
        """Register an event callback."""
        listeners: list = self._listeners.setdefault(event_name, [])
        listeners.append(callback)

        def unsubscribe():
            """Unsubscribe listeners."""
            if callback in listeners:
                listeners.remove(callback)

        return unsubscribe

    def emit(self, event_name, data):
        """Run all callbacks for an event."""
        for listener in self._listeners.get(event_name, []):
            listener(data)
