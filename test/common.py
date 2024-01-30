"""Common methods for tests."""

import asyncio
from unittest.mock import AsyncMock


def update_ws_client_msg_queue(fixture, new_messages):
    """Update a ws client fixture with a new message queue."""
    to_receive = asyncio.Queue()
    for message in new_messages:
        to_receive.put_nowait(message)

    async def receive_json():
        return await to_receive.get()

    fixture.receive_json = AsyncMock(side_effect=receive_json)
