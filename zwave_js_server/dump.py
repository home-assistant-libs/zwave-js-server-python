"""Dump helper."""
import asyncio
from typing import Dict, List, Optional, Union

import aiohttp

from .client import INITIALIZE_MESSAGE_ID
from .const import MAX_SERVER_SCHEMA_VERSION


async def dump_msgs(
    url: str,
    session: aiohttp.ClientSession,
    additional_user_agent_components: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None,
) -> List[dict]:
    """Dump server state."""
    client = await session.ws_connect(url, compress=15, max_msg_size=0)
    msgs = []

    version = await client.receive_json()
    msgs.append(version)

    initialize_payload: Dict[str, Union[int, str, Dict[str, str]]] = {
        "command": "initialize",
        "messageId": INITIALIZE_MESSAGE_ID,
        "schemaVersion": MAX_SERVER_SCHEMA_VERSION,
    }
    if additional_user_agent_components:
        initialize_payload[
            "additionalUserAgentComponents"
        ] = additional_user_agent_components

    for to_send in (
        initialize_payload,
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
