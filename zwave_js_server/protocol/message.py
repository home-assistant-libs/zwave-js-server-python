"""Provide a protocol for the websocket message."""
from enum import Enum
from typing import TYPE_CHECKING

from ..model.gateway import Gateway
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
    async def handle_event(cls, client: "Client", message: Message) -> None:
        """Process an event message."""
        client.gateway.handle_event(message.data)

    @classmethod
    async def handle_state(cls, client: "Client", message: Message) -> None:
        """Process a state message."""
        client.gateway = Gateway(message.data)
