"""Firmware update helper."""
from typing import Any

import aiohttp

from .const import MAX_SERVER_SCHEMA_VERSION
from .model.node import Node
from .util.helpers import convert_bytes_to_base64


async def begin_firmware_update(
    url: str,
    node: Node,
    filename: str,
    file: bytes,
    session: aiohttp.ClientSession,
    file_format: str = None,
) -> Any:
    """Send beginFirmwareUpdate command to Node."""
    client = await session.ws_connect(url)
    # Version info
    await client.receive_json()
    await client.send_json(
        {
            "command": "set_api_schema",
            "messageId": "api-schema-id",
            "schemaVersion": MAX_SERVER_SCHEMA_VERSION,
        }
    )
    # set_api_schema response
    await client.receive_json()

    cmd = {
        "command": "node.begin_firmware_update",
        "nodeId": node.node_id,
        "firmwareFilename": filename,
        "firmwareFile": convert_bytes_to_base64(file),
        "messageId": "begin-firmware-update",
    }
    if file_format is not None:
        cmd["firmwareFileFormat"] = file_format

    await client.send_json(cmd)
    resp = await client.receive_json()
    await client.close()
    return resp
