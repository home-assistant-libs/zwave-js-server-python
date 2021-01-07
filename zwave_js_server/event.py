"""Provide Event base classes for Z-Wave JS."""


from typing import Callable, Dict, List


class EventBase:
    """Represent a Z-Wave JS base class for event handling models."""

    def __init__(self) -> None:
        """Initialize event base."""
        self._listeners: Dict[str, List[Callable]] = {}

    def on(  # pylint: disable=invalid-name
        self, event_name: str, callback: Callable
    ) -> Callable:
        """Register an event callback."""
        listeners: list = self._listeners.setdefault(event_name, [])
        listeners.append(callback)

        def unsubscribe() -> None:
            """Unsubscribe listeners."""
            if callback in listeners:
                listeners.remove(callback)

        return unsubscribe

    def emit(self, event_name: str, data: dict) -> None:
        """Run all callbacks for an event."""
        for listener in self._listeners.get(event_name, []):
            listener(data)
