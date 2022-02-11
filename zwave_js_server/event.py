"""Provide Event base classes for Z-Wave JS."""
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Literal, Optional, Type

from pydantic import BaseModel, ValidationError

LOGGER = logging.getLogger(__package__)


def validate_event_data(
    data: Dict[str, Any],
    source: str,
    event_name: str,
    event_name_to_model_map: Dict[str, Type["BaseEventModel"]],
    keys_can_be_missing: bool = False,
) -> Optional[Type["BaseEventModel"]]:
    """
    Validate data with a pydantic model using event name and source.

    Raises an exception if data is invalid.
    keys_can_be_missing allows for required keys to be missing when True.
    """
    return_model = True
    try:
        model = event_name_to_model_map[event_name](**data)
    except ValidationError as exc:
        errors: List[Dict[str, Any]] = []
        for error in exc.errors():
            # Filter out required field errors if keys can be missing
            if error["msg"] == "field required" and keys_can_be_missing:
                continue
            errors.append(error)

        # If there are still errors after filtering, raise an exception
        if errors:
            raise ValueError(errors) from exc

        # We can't return a model when keys are missing
        return_model = False
    except KeyError as exc:
        raise TypeError(
            f"{event_name} is not a valid event name for the given source {source}"
        ) from exc

    if return_model:
        return model
    return None


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
