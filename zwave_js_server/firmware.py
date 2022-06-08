"""Firmware update helper."""
import asyncio
from typing import Optional

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
    file_format: Optional[str] = None,
) -> None:
    """Send beginFirmwareUpdate command to Node."""
    client = Client(url, session)
    await client.connect()
    await client.set_api_schema()

    receive_task = asyncio.get_running_loop().create_task(client.receive_until_closed())

    cmd = {
        "command": "node.begin_firmware_update",
        "nodeId": node.node_id,
        "firmwareFilename": filename,
        "firmwareFile": convert_bytes_to_base64(file),
    }
    if file_format is not None:
        cmd["firmwareFileFormat"] = file_format

    await client.async_send_command(cmd, require_schema=5)
    await client.disconnect()
    if not receive_task.done():
        receive_task.cancel()
