"""Dump helper."""
import asyncio
from typing import List, Optional

import aiohttp

from .const import MAX_SERVER_SCHEMA_VERSION


async def dump_msgs(
    url: str,
    session: aiohttp.ClientSession,
    timeout: Optional[float] = None,
) -> List[dict]:
    """Dump server state."""
    client = await session.ws_connect(url)
    msgs = []

    version = await client.receive_json()
    msgs.append(version)

    for to_send in (
        {
            "command": "set_api_schema",
            "messageId": "api-schema-id",
            "schemaVersion": MAX_SERVER_SCHEMA_VERSION,
        },
        {"command": "start_listening", "messageId": "listen-id"},
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
