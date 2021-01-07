"""Provide a client for zwave-js-server."""
from dataclasses import dataclass
from typing import Optional, cast

from .model.driver import Driver
from .model.message import Message
from .protocol import ProtocolType, get_handler, message as protocol


@dataclass
class Client:
    """Represent a zwave-js-server client."""

    driver: Optional[Driver] = None

    async def handle_message(self, message: Message) -> None:
        """Handle a message."""
        protocol_ = cast(ProtocolType, protocol)
        message_handler = get_handler(protocol_, message)

        message_handler(self, message)
