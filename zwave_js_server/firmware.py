"""Firmware update helper."""
import asyncio
from typing import Dict, List, Optional, cast

import aiohttp

from .client import Client
from .model.node import Node
from .model.node.firmware import FirmwareUpdateData


async def update_firmware(
    url: str,
    node: Node,
    updates: List[FirmwareUpdateData],
    session: aiohttp.ClientSession,
    additional_user_agent_components: Optional[Dict[str, str]] = None,
) -> bool:
    """Send updateFirmware command to Node."""
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


async def update_controller_firmware_otw(
    url: str,
    firmware_file: FirmwareUpdateData,
    session: aiohttp.ClientSession,
    additional_user_agent_components: Optional[Dict[str, str]] = None,
) -> bool:
    """
    Send firmwareUpdateOTW command to Controller.

    Sending the wrong firmware to a controller can brick it and make it unrecoverable.
    Consumers of this library should build mechanisms to ensure that users understand
    the risks.
    """
    client = Client(
        url, session, additional_user_agent_components=additional_user_agent_components
    )
    await client.connect()
    await client.initialize()

    receive_task = asyncio.get_running_loop().create_task(client.receive_until_closed())

    cmd = {
        "command": "controller.firmware_update_otw",
        **firmware_file.to_dict(),
    }

    data = await client.async_send_command(cmd, require_schema=25)
    await client.disconnect()
    if not receive_task.done():
        receive_task.cancel()

    return cast(bool, data["success"])
