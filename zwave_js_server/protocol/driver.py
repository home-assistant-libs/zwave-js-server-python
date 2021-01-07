"""Provide a protocol for the driver model."""
from enum import Enum
from typing import TYPE_CHECKING

from ..event import Event

if TYPE_CHECKING:
    from ..model.driver import Driver


class Type(Enum):
    """Represent a driver event type."""

    ERROR = "error"
    DRIVER_READY = "driver ready"
    ALL_NODES_READY = "all nodes ready"


class Handler:
    """Represent an event handler for the driver."""

    @classmethod
    def handle_error(cls, driver: "Driver", event: Event) -> None:
        """Process a driver error event."""

    @classmethod
    def handle_driver_ready(cls, driver: "Driver", event: Event) -> None:
        """Process a driver ready event."""

    @classmethod
    def handle_all_nodes_ready(cls, driver: "Driver", event: Event) -> None:
        """Process a driver all nodes ready event."""
