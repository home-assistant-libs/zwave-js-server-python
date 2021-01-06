"""Provide a protocol for the gateway."""
from enum import Enum
from typing import TYPE_CHECKING

from ..exceptions import MissingNodeError

if TYPE_CHECKING:
    from ..model.gateway import Gateway


class Type(Enum):
    """Represent a gateway event type."""

    CONTROLLER = "controller"
    DRIVER = "driver"
    NODE = "node"


class Handler:
    """Represent an event handler for the gateway."""

    @classmethod
    def handle_controller(cls, gateway: "Gateway", event: dict) -> None:
        """Process a controller event."""
        gateway.controller.handle_event(event)

    @classmethod
    def handle_driver(cls, gateway: "Gateway", event: dict) -> None:
        """Process a driver event."""

    @classmethod
    def handle_node(cls, gateway: "Gateway", event: dict) -> None:
        """Process a node event."""
        node = gateway.nodes.get(event["nodeId"])

        if node is None:
            raise MissingNodeError

        node.handle_event(event)
