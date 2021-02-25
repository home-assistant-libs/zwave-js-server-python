"""Dump helper."""
import asyncio
from typing import List, Optional

import aiohttp

from .const import MAX_SERVER_SCHEMA_VERSION
from .exceptions import FailedCommand


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

    # set preferred schema version on the server
    # note: we already check for (in)compatible schemas in the connect call
    await client.send_json(
        {
            "command": "set_api_schema",
            "messageId": "api-schema-id",
            "schemaVersion": MAX_SERVER_SCHEMA_VERSION,
        }
    )
    state_msg = await client.receive_json()

    if not state_msg["success"]:
        # this should not happen, but just in case
        await client.disconnect()
        raise FailedCommand(state_msg["messageId"], state_msg["errorCode"])

    await client.send_json({"command": "start_listening"})
    msg = await client.receive_json()
    msgs.append(msg)

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
