"""Firmware update helper."""
import asyncio
from typing import Dict, List, Optional, cast

import aiohttp

from .client import Client
from .model.firmware import FirmwareUpdateData
from .model.node import Node


async def update_firmware(
    url: str,
    node: Node,
    updates: List[FirmwareUpdateData],
    session: aiohttp.ClientSession,
    additional_user_agent_components: Optional[Dict[str, str]] = None,
) -> bool:
    """Send beginFirmwareUpdate command to Node."""
    client = Client(
        url, session, additional_user_agent_components=additional_user_agent_components
    )
    await client.connect()
    await client.initialize()

    receive_task = asyncio.get_running_loop().create_task(client.receive_until_closed())

    cmd = {
        "command": "node.update_firmware",
        "nodeId": node.node_id,
        "updates": [update.to_dict() for update in updates],
    }

    data = await client.async_send_command(cmd, require_schema=24)
    await client.disconnect()
    if not receive_task.done():
        receive_task.cancel()

    return cast(bool, data["success"])
