"""Test the firmware update helper."""
import asyncio
from unittest.mock import AsyncMock

import pytest

from zwave_js_server.exceptions import FailedCommand, FailedZWaveCommand, InvalidMessage
from zwave_js_server.firmware import begin_firmware_update

from .const import FAILED_COMMAND_MSG, FAILED_ZWAVE_COMMAND_MSG, INVALID_MESSAGE_MSG


async def test_begin_firmware_update_guess_format(
    no_get_log_config_client_session,
    multisensor_6,
    url,
    version_data,
    set_api_schema_data,
    no_get_log_config_ws_client,
):
    """Test begin_firmware_update with guessed format."""
    to_receive = asyncio.Queue()
    for message in (
        version_data,
        set_api_schema_data,
        {"type": "result", "success": True},
    ):
        to_receive.put_nowait(message)

    async def receive_json():
        return await to_receive.get()

    no_get_log_config_ws_client.receive_json = AsyncMock(side_effect=receive_json)
    await begin_firmware_update(
        url, multisensor_6, "test", bytes(10), no_get_log_config_client_session
    )

    assert no_get_log_config_ws_client.receive_json.call_count == 3
    assert no_get_log_config_ws_client.send_json.call_count == 2
    command = no_get_log_config_ws_client.send_json.call_args[0][0]
    command.pop("messageId")
    assert command == {
        "command": "node.begin_firmware_update",
        "nodeId": multisensor_6.node_id,
        "firmwareFilename": "test",
        "firmwareFile": "AAAAAAAAAAAAAA==",
    }
    assert no_get_log_config_ws_client.close.call_count == 1


async def test_begin_firmware_update_known_format(
    no_get_log_config_client_session,
    multisensor_6,
    url,
    version_data,
    set_api_schema_data,
    no_get_log_config_ws_client,
):
    """Test begin_firmware_update with known format."""
    to_receive = asyncio.Queue()
    for message in (
        version_data,
        set_api_schema_data,
        {"type": "result", "success": True},
    ):
        to_receive.put_nowait(message)

    async def receive_json():
        return await to_receive.get()

    no_get_log_config_ws_client.receive_json = AsyncMock(side_effect=receive_json)
    await begin_firmware_update(
        url,
        multisensor_6,
        "test",
        bytes(10),
        no_get_log_config_client_session,
        "format",
    )

    assert no_get_log_config_ws_client.receive_json.call_count == 3
    assert no_get_log_config_ws_client.send_json.call_count == 2
    command = no_get_log_config_ws_client.send_json.call_args[0][0]
    command.pop("messageId")
    assert command == {
        "command": "node.begin_firmware_update",
        "nodeId": multisensor_6.node_id,
        "firmwareFilename": "test",
        "firmwareFile": "AAAAAAAAAAAAAA==",
        "firmwareFileFormat": "format",
    }
    assert no_get_log_config_ws_client.close.call_count == 1


@pytest.mark.parametrize(
    "error_message, exception",
    [
        (INVALID_MESSAGE_MSG, InvalidMessage),
        (FAILED_COMMAND_MSG, FailedCommand),
        (FAILED_ZWAVE_COMMAND_MSG, FailedZWaveCommand),
    ],
)
async def test_begin_firmware_update_failures(
    no_get_log_config_client_session,
    multisensor_6,
    url,
    version_data,
    set_api_schema_data,
    no_get_log_config_ws_client,
    error_message,
    exception,
):
    """Test begin_firmware_update failures."""
    to_receive = asyncio.Queue()
    for message in (
        version_data,
        set_api_schema_data,
        error_message,
    ):
        to_receive.put_nowait(message)

    async def receive_json():
        return await to_receive.get()

    no_get_log_config_ws_client.receive_json = AsyncMock(side_effect=receive_json)
    with pytest.raises(exception):
        await begin_firmware_update(
            url,
            multisensor_6,
            "test",
            bytes(10),
            no_get_log_config_client_session,
            "format",
        )
