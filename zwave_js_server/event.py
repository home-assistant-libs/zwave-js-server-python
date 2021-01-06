"""Event base classes for Z-Wave JS."""


class EventBase:
    def __init__(self):
        """Initialize event base."""
        self._listeners = {}

    def on(self, event_name, callback):
        listeners: list = self._listeners.setdefault(event_name, [])
        listeners.append(callback)

        def unsub():
            if callback in listeners:
                listeners.remove(callback)

        return unsub

    def emit(self, event_name, data):
        for listener in self._listeners.get(event_name, []):
            listener(data)
