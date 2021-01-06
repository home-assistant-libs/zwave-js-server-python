"""Provide a client for zwave-js-server."""
from dataclasses import dataclass
from typing import Optional

from .model.gateway import Gateway
from .model.message import Message
from .protocol import get_handler, message as protocol


@dataclass
class Client:
    """Represent a zwave-js-server client."""

    gateway: Optional[Gateway] = None

    async def handle_message(self, message: Message) -> None:
        """Handle a message."""
        message_handler = get_handler(protocol, message)

        await message_handler(self, message)
