"""Dump helper."""
from __future__ import annotations

import asyncio

import aiohttp

from .client import INITIALIZE_MESSAGE_ID
from .const import MAX_SERVER_SCHEMA_VERSION, PACKAGE_NAME, __version__


async def dump_msgs(
    url: str,
    session: aiohttp.ClientSession,
    additional_user_agent_components: dict[str, str] | None = None,
    timeout: float | None = None,
) -> list[dict]:
    """Dump server state."""
    client = await session.ws_connect(url, compress=15, max_msg_size=0)
    msgs = []

    version = await client.receive_json()
    msgs.append(version)

    for to_send in (
        {
            "command": "initialize",
            "messageId": INITIALIZE_MESSAGE_ID,
            "schemaVersion": MAX_SERVER_SCHEMA_VERSION,
            "additionalUserAgentComponents": {
                PACKAGE_NAME: __version__,
                **(additional_user_agent_components or {}),
            },
        },
        {"command": "start_listening", "messageId": "start-listening"},
    ):
        await client.send_json(to_send)
        msgs.append(await client.receive_json())

    if timeout is None:
        await client.close()
        return msgs

    current_task = asyncio.current_task()
    assert current_task is not None
    asyncio.get_running_loop().call_later(timeout, current_task.cancel)

    while True:
        try:
            msg = await client.receive_json()
            msgs.append(msg)
        except asyncio.CancelledError:
            break

    await client.close()
    return msgs
