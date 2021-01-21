"""Dump helper."""
import asyncio
from typing import List
import aiohttp


async def dump_msgs(
    url: str, session: aiohttp.ClientSession, timeout: float = None
) -> List[dict]:
    """Dump server state."""
    client = await session.ws_connect(url)
    msgs = []

    version = await client.receive_json()
    msgs.append(version)

    await client.send_json({"command": "start_listening"})
    state = await client.receive_json()
    msgs.append(state)

    if timeout is None:
        await client.close()
        return msgs

    current_task = asyncio.current_task()
    assert current_task is not None
    asyncio.get_running_loop().call_later(timeout, current_task.cancel)

    try:
        event = await client.receive_json()
        msgs.append(event)
    except asyncio.CancelledError:
        pass

    await client.close()
    return msgs
