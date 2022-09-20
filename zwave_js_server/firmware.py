"""Firmware update helper."""
import asyncio
from typing import Dict, Optional

import aiohttp

from .client import Client
from .model.node import Node
from .util.helpers import convert_bytes_to_base64


async def begin_firmware_update(
    url: str,
    node: Node,
    filename: str,
    file: bytes,
    session: aiohttp.ClientSession,
    additional_user_agent_components: Optional[Dict[str, str]] = None,
    file_format: Optional[str] = None,
    target: Optional[int] = None,
) -> None:
    """Send beginFirmwareUpdate command to Node."""
    client = Client(
        url, session, additional_user_agent_components=additional_user_agent_components
    )
    await client.connect()
    await client.initialize()

    receive_task = asyncio.get_running_loop().create_task(client.receive_until_closed())

    cmd = {
        "command": "node.begin_firmware_update",
        "nodeId": node.node_id,
        "firmwareFilename": filename,
        "firmwareFile": convert_bytes_to_base64(file),
    }
    if file_format is not None:
        cmd["firmwareFileFormat"] = file_format

    if target is not None:
        cmd["target"] = target

    await client.async_send_command(cmd, require_schema=18)
    await client.disconnect()
    if not receive_task.done():
        receive_task.cancel()
