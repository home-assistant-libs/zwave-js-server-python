"""Common methods for tests."""

import asyncio
from typing import Protocol
from unittest.mock import AsyncMock


class MockCommandProtocol(Protocol):
    """Represent the function signature of mock_the mock_command callable."""

    def __call__(
        self, command: dict, response: dict, success: bool = True
    ) -> list[dict]:
        """Represent the signature of the mock_command callable."""


def update_ws_client_msg_queue(fixture, new_messages):
    """Update a ws client fixture with a new message queue."""
    to_receive = asyncio.Queue()
    for message in new_messages:
        to_receive.put_nowait(message)

    async def receive_json():
        return await to_receive.get()

    fixture.receive_json = AsyncMock(side_effect=receive_json)
