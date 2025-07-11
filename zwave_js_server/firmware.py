"""Firmware update helper."""

from __future__ import annotations

import asyncio

import aiohttp

from .client import Client
from .model.driver.firmware import DriverFirmwareUpdateData, DriverFirmwareUpdateResult
from .model.node import Node
from .model.node.firmware import NodeFirmwareUpdateData, NodeFirmwareUpdateResult


async def update_firmware(
    url: str,
    node: Node,
    updates: list[NodeFirmwareUpdateData],
    session: aiohttp.ClientSession,
    additional_user_agent_components: dict[str, str] | None = None,
) -> NodeFirmwareUpdateResult:
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

    data = await client.async_send_command(cmd, require_schema=29)
    await client.disconnect()
    if not receive_task.done():
        receive_task.cancel()

    return NodeFirmwareUpdateResult(node, data["result"])


async def driver_firmware_update_otw(
    url: str,
    firmware_file: DriverFirmwareUpdateData,
    session: aiohttp.ClientSession,
    additional_user_agent_components: dict[str, str] | None = None,
) -> DriverFirmwareUpdateResult:
    """
    Send firmwareUpdateOTW command to Driver.

    Sending the wrong firmware to a driver can brick it and make it unrecoverable.
    Consumers of this library should build mechanisms to ensure that users understand
    the risks.
    """
    client = Client(
        url, session, additional_user_agent_components=additional_user_agent_components
    )
    await client.connect()
    await client.initialize()

    receive_task = asyncio.get_running_loop().create_task(client.receive_until_closed())

    data = await client.async_send_command(
        {
            "command": "driver.firmware_update_otw",
            **firmware_file.to_dict(),
        },
        require_schema=29,
    )
    await client.disconnect()
    if not receive_task.done():
        receive_task.cancel()

    return DriverFirmwareUpdateResult(data["result"])
