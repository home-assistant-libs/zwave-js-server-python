"""Provide Event base classes for Z-Wave JS."""
import logging
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Literal, TypedDict, TypeVar

from pydantic import BaseModel, create_model, create_model_from_typeddict

LOGGER = logging.getLogger(__package__)


class BaseEventModel(BaseModel):
    """Base model for an event."""

    source: Literal["controller", "driver", "node"]
    event: str


EventNameType = TypeVar("EventNameType")


def _event_model_factory(
    base_model: BaseEventModel, model_name: str, event_name: EventNameType
) -> BaseEventModel:
    """
    Factory for new event models from a BaseEventModel.

    Adds the event_name Literal to the model.
    """
    return create_model(
        f"{model_name}EventModel", __base__=base_model, event=(event_name, ...)
    )


def _event_model_from_typeddict_factory(
    base_model: BaseEventModel, typed_dict: TypedDict, event_name: EventNameType
) -> BaseEventModel:
    """
    Factory for event models created from a TypedDict.

    Adds the event_name Literal to the model.
    """
    return create_model_from_typeddict(
        typed_dict, __base__=base_model, event=(event_name, ...)
    )


@dataclass
class Event:
    """Represent an event."""

    type: str
    data: dict = field(default_factory=dict)


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

    def once(self, event_name: str, callback: Callable) -> Callable:
        """Listen for an event exactly once."""

        def event_listener(data: dict) -> None:
            unsub()
            callback(data)

        unsub = self.on(event_name, event_listener)

        return unsub

    def emit(self, event_name: str, data: dict) -> None:
        """Run all callbacks for an event."""
        for listener in self._listeners.get(event_name, []):
            listener(data)

    def _handle_event_protocol(self, event: Event) -> None:
        """Process an event based on event protocol."""
        handler = getattr(self, f"handle_{event.type.replace(' ', '_')}", None)
        if handler is None:
            LOGGER.debug("Received unknown event: %s", event)
            return
        handler(event)
