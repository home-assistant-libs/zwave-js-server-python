"""Test the firmware update helper."""
import pytest

from zwave_js_server.exceptions import FailedCommand, FailedZWaveCommand, InvalidMessage
from zwave_js_server.firmware import begin_firmware_update

from .common import update_ws_client_fixture
from .const import (
    FAILED_COMMAND_MSG,
    FAILED_ZWAVE_COMMAND_MSG,
    INVALID_MESSAGE_MSG,
    SUCCESS_MSG,
)


async def test_begin_firmware_update_guess_format(
    client_session,
    multisensor_6,
    url,
    version_data,
    set_api_schema_data,
    ws_client,
):
    """Test begin_firmware_update with guessed format."""
    update_ws_client_fixture(
        ws_client, (version_data, set_api_schema_data, SUCCESS_MSG)
    )

    await begin_firmware_update(url, multisensor_6, "test", bytes(10), client_session)

    assert ws_client.receive_json.call_count == 3
    assert ws_client.send_json.call_count == 2
    command = ws_client.send_json.call_args[0][0]
    command.pop("messageId")
    assert command == {
        "command": "node.begin_firmware_update",
        "nodeId": multisensor_6.node_id,
        "firmwareFilename": "test",
        "firmwareFile": "AAAAAAAAAAAAAA==",
    }
    assert ws_client.close.call_count == 1


async def test_begin_firmware_update_known_format(
    client_session,
    multisensor_6,
    url,
    version_data,
    set_api_schema_data,
    ws_client,
):
    """Test begin_firmware_update with known format."""
    update_ws_client_fixture(
        ws_client, (version_data, set_api_schema_data, SUCCESS_MSG)
    )

    await begin_firmware_update(
        url,
        multisensor_6,
        "test",
        bytes(10),
        client_session,
        "format",
    )

    assert ws_client.receive_json.call_count == 3
    assert ws_client.send_json.call_count == 2
    command = ws_client.send_json.call_args[0][0]
    command.pop("messageId")
    assert command == {
        "command": "node.begin_firmware_update",
        "nodeId": multisensor_6.node_id,
        "firmwareFilename": "test",
        "firmwareFile": "AAAAAAAAAAAAAA==",
        "firmwareFileFormat": "format",
    }
    assert ws_client.close.call_count == 1


@pytest.mark.parametrize(
    "error_message, exception",
    [
        (INVALID_MESSAGE_MSG, InvalidMessage),
        (FAILED_COMMAND_MSG, FailedCommand),
        (FAILED_ZWAVE_COMMAND_MSG, FailedZWaveCommand),
    ],
)
async def test_begin_firmware_update_failures(
    client_session,
    multisensor_6,
    url,
    version_data,
    set_api_schema_data,
    ws_client,
    error_message,
    exception,
):
    """Test begin_firmware_update failures."""
    update_ws_client_fixture(
        ws_client, (version_data, set_api_schema_data, error_message)
    )

    with pytest.raises(exception):
        await begin_firmware_update(
            url, multisensor_6, "test", bytes(10), client_session, "format"
        )
