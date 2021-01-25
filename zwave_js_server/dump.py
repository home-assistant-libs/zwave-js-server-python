"""Dump helper."""
import asyncio
from typing import List, Optional

import aiohttp


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
