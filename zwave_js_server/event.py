"""Provide Event base classes for Z-Wave JS."""
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


@dataclass
class Event:
    """Represent an event."""

    type: str
    data: dict = field(default_factory=dict)


class EventBase:
    """Represent a Z-Wave JS base class for event handling models."""

    def __init__(self, protocol: Any) -> None:
        """Initialize event base."""
        self.protocol = protocol
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

    def _handle_event_protocol(self, event: Event) -> None:
        """Process an event based on event protocol."""
    handler = getattr(self, f"handle_{event.type.replace(' ', '_')}", None)
    if handler is None:
        LOGGER.debug("Received unknown event")
        return
    handler(event)
