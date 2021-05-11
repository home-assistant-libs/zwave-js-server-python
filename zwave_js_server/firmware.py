"""Firmware update helper."""
from typing import Any

import aiohttp

from .const import MAX_SERVER_SCHEMA_VERSION
from .model.node import Node
from .util.helpers import convert_bytes_to_base64


async def begin_firmware_update_guess_format(
    url: str, node: Node, filename: str, file: bytes, session: aiohttp.ClientSession
) -> Any:
    """Send beginFirmwareUpdate command to Node (file format to be guessed)."""
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

    await client.send_json(
        {
            "command": "node.begin_firmware_update_guess_format",
            "nodeId": node.node_id,
            "firmwareFilename": filename,
            "firmwareFile": convert_bytes_to_base64(file),
            "messageId": "begin-firmware-update-guess-format",
        }
    )
    resp = await client.receive_json()
    await client.close()
    return resp


async def begin_firmware_update_known_format(
    url: str, node: Node, file_format: str, file: bytes, session: aiohttp.ClientSession
) -> Any:
    """Send beginFirmwareUpdate command to Node (file format is known)."""
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

    await client.send_json(
        {
            "command": "node.begin_firmware_update_known_format",
            "nodeId": node.node_id,
            "firmwareFileFormat": file_format,
            "firmwareFile": convert_bytes_to_base64(file),
            "messageId": "begin-firmware-update-known-format",
        }
    )
    resp = await client.receive_json()
    await client.close()
    return resp
