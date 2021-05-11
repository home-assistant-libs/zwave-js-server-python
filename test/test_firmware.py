"""Test the firmware update helper."""
from unittest.mock import call

from zwave_js_server.firmware import begin_firmware_update


async def test_begin_firmware_update_guess_format(
    url, firmware_client_session, firmware_ws_client, multisensor_6
):
    """Test begin_firmware_update with guessed format."""
    node = multisensor_6
    assert (
        await begin_firmware_update(
            url, node, "test", bytes(10), firmware_client_session
        )
        == {}
    )

    assert firmware_ws_client.receive_json.call_count == 3
    assert firmware_ws_client.send_json.call_count == 2
    assert firmware_ws_client.send_json.call_args == call(
        {
            "command": "node.begin_firmware_update",
            "messageId": "begin-firmware-update",
            "nodeId": node.node_id,
            "firmwareFile": "AAAAAAAAAAAAAA==",
            "firmwareFilename": "test",
        }
    )
    assert firmware_ws_client.close.call_count == 1


async def test_begin_firmware_update_known_format(
    url, firmware_client_session, firmware_ws_client, multisensor_6
):
    """Test begin_firmware_update with known format."""
    node = multisensor_6
    assert (
        await begin_firmware_update(
            url, node, "test", bytes(10), firmware_client_session, "test"
        )
        == {}
    )

    assert firmware_ws_client.receive_json.call_count == 3
    assert firmware_ws_client.send_json.call_count == 2
    assert firmware_ws_client.send_json.call_args == call(
        {
            "command": "node.begin_firmware_update",
            "messageId": "begin-firmware-update",
            "nodeId": node.node_id,
            "firmwareFilename": "test",
            "firmwareFile": "AAAAAAAAAAAAAA==",
            "firmwareFileFormat": "test",
        }
    )
    assert firmware_ws_client.close.call_count == 1
