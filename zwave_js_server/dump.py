"""Dump helper."""
import asyncio
import aiohttp


async def dump_msgs(url: str, session: aiohttp.ClientSession, timeout=None, node=None):
    """Dump server state."""
    client = await session.ws_connect(url)
    msgs = []

    version = await client.receive_json()
    msgs.append(version)

    await client.send_json({"command": "start_listening"})
    state = await client.receive_str()
    msgs.append(state)

    if timeout is None:
        await client.close()
        return msgs

    asyncio.get_running_loop().call_later(timeout, asyncio.current_task().cancel)

    try:
        event = await client.receive_str()
        msgs.append(event)
    except asyncio.CancelledError:
        pass

    await client.close()
    return msgs
