"""Firmware update helper."""
from typing import Optional
import uuid

import aiohttp

from .const import MAX_SERVER_SCHEMA_VERSION
from .exceptions import FailedCommand, FailedZWaveCommand, InvalidMessage
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
    client = await session.ws_connect(url, compress=15, max_msg_size=0)

    # version info
    await client.receive_json()

    await client.send_json(
        {
            "command": "set_api_schema",
            "messageId": "api-schema-id",
            "schemaVersion": MAX_SERVER_SCHEMA_VERSION,
        }
    )
    # schema response
    await client.receive_json()

    cmd = {
        "command": "node.begin_firmware_update",
        "nodeId": node.node_id,
        "firmwareFilename": filename,
        "firmwareFile": convert_bytes_to_base64(file),
        "messageId": uuid.uuid4().hex,
    }
    if file_format is not None:
        cmd["firmwareFileFormat"] = file_format

    await client.send_json(cmd)
    msg = await client.receive_json()
    await client.close()

    if msg.get("type") != "result":
        raise InvalidMessage(
            "Received invalid message when attempting to begin firmware update"
        )

    if msg["success"]:
        return

    if msg["errorCode"] == "zwave_error":
        raise FailedZWaveCommand(
            msg["messageId"], msg["zwaveErrorCode"], msg["zwaveErrorMessage"]
        )

    raise FailedCommand(msg["messageId"], msg["errorCode"])
