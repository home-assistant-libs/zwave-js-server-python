"""Provide a protocol for zwave-js-server."""
from typing import Any, Callable, Protocol


class ModelType(Protocol):
    """Represent a model message or event type."""

    type: Any
    data: Any


class ProtocolType(Protocol):
    """Represent a protocol module type."""

    Type: Any
    Handler: Any


def get_handler(protocol: ProtocolType, data: ModelType) -> Callable:
    """Return a handler based on protocol."""
    protocol_type = protocol.Type(data.type)
    protocol_handler: Callable = getattr(
        protocol.Handler, f"handle_{protocol_type.value}"
    )
    return protocol_handler
