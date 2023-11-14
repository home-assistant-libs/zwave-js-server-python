"""Provide Event base classes for Z-Wave JS."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
import logging
from typing import Literal

try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel

LOGGER = logging.getLogger(__package__)


class BaseEventModel(BaseModel):
    """Base model for an event."""

    source: Literal["controller", "driver", "node"]
    event: str


@dataclass
class Event:
    """Represent an event."""

    type: str
    data: dict = field(default_factory=dict)


class EventBase:
    """Represent a Z-Wave JS base class for event handling models."""

    def __init__(self) -> None:
        """Initialize event base."""
        self._listeners: dict[str, list[Callable]] = {}

    def on(self, event_name: str, callback: Callable) -> Callable:
        """Register an event callback."""
        listeners: list = self._listeners.setdefault(event_name, [])
        listeners.append(callback)

        def unsubscribe() -> None:
            """Unsubscribe listeners."""
            if callback in listeners:
                listeners.remove(callback)

        return unsubscribe

    def once(self, event_name: str, callback: Callable) -> Callable:
        """Listen for an event exactly once."""

        def event_listener(data: dict) -> None:
            unsub()
            callback(data)

        unsub = self.on(event_name, event_listener)

        return unsub

    def emit(self, event_name: str, data: dict) -> None:
        """Run all callbacks for an event."""
        for listener in self._listeners.get(event_name, []).copy():
            listener(data)

    def _handle_event_protocol(self, event: Event) -> None:
        """Process an event based on event protocol."""
        handler = getattr(self, f"handle_{event.type.replace(' ', '_')}", None)
        if handler is None:
            LOGGER.debug("Received unknown event: %s", event)
            return
        handler(event)
