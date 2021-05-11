"""Test the firmware update helper."""
from unittest.mock import call

from zwave_js_server.firmware import (
    begin_firmware_update_guess_format,
    begin_firmware_update_known_format,
)


async def test_begin_firmware_update_guess_format(
    url, firmware_client_session, firmware_ws_client, multisensor_6
):
    """Test begin_firmware_update_guess_format."""
    node = multisensor_6
    assert (
        await begin_firmware_update_guess_format(
            url, node, "test", bytes(10), firmware_client_session
        )
        == {}
    )

    assert firmware_ws_client.receive_json.call_count == 3
    assert firmware_ws_client.send_json.call_count == 2
    assert firmware_ws_client.send_json.call_args == call(
        {
            "command": "node.begin_firmware_update_guess_format",
            "messageId": "begin-firmware-update-guess-format",
            "nodeId": node.node_id,
            "firmwareFile": "AAAAAAAAAAAAAA==",
            "firmwareFilename": "test",
        }
    )
    assert firmware_ws_client.close.call_count == 1


async def test_begin_firmware_update_known_format(
    url, firmware_client_session, firmware_ws_client, multisensor_6
):
    """Test begin_firmware_update_known_format."""
    node = multisensor_6
    assert (
        await begin_firmware_update_known_format(
            url, node, "test", bytes(10), firmware_client_session
        )
        == {}
    )

    assert firmware_ws_client.receive_json.call_count == 3
    assert firmware_ws_client.send_json.call_count == 2
    assert firmware_ws_client.send_json.call_args == call(
        {
            "command": "node.begin_firmware_update_known_format",
            "messageId": "begin-firmware-update-known-format",
            "nodeId": node.node_id,
            "firmwareFile": "AAAAAAAAAAAAAA==",
            "firmwareFileFormat": "test",
        }
    )
    assert firmware_ws_client.close.call_count == 1
