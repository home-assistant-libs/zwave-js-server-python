"""Provide a protocol for the websocket message model."""
from enum import Enum
from typing import TYPE_CHECKING

from ..model.driver import Driver, DriverEvent
from ..model.message import Message

if TYPE_CHECKING:
    from ..new_client import Client


class Type(Enum):
    """Represent a websocket message type."""

    EVENT = "event"
    STATE = "state"


class Handler:
    """Represent a message handler."""

    @classmethod
    def handle_event(cls, client: "Client", message: Message) -> None:
        """Process an event message."""
        driver_event = DriverEvent(type=message.data["event"], data=message.data)
        assert client.driver
        client.driver.handle_event(driver_event)

    @classmethod
    def handle_state(cls, client: "Client", message: Message) -> None:
        """Process a state message."""
        client.driver = Driver(message.data)
