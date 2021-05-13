"""Test the firmware update helper."""
from unittest.mock import patch

from zwave_js_server.firmware import begin_firmware_update


async def test_begin_firmware_update_guess_format(url, client_session, multisensor_6):
    """Test begin_firmware_update with guessed format."""
    with patch("zwave_js_server.firmware.Client.connect") as connect_mock, patch(
        "zwave_js_server.firmware.Client.set_api_schema"
    ) as set_api_schema_mock, patch(
        "zwave_js_server.firmware.Client.async_send_command"
    ) as cmd_mock, patch(
        "zwave_js_server.firmware.Client.disconnect"
    ) as disconnect_mock:
        node = multisensor_6
        await begin_firmware_update(url, node, "test", bytes(10), client_session)

        connect_mock.assert_called_once()
        set_api_schema_mock.assert_called_once()
        cmd_mock.assert_called_once_with(
            {
                "command": "node.begin_firmware_update",
                "nodeId": node.node_id,
                "firmwareFilename": "test",
                "firmwareFile": "AAAAAAAAAAAAAA==",
            },
            require_schema=5,
        )
        disconnect_mock.assert_called_once()


async def test_begin_firmware_update_known_format(url, client_session, multisensor_6):
    """Test begin_firmware_update with known format."""
    with patch("zwave_js_server.firmware.Client.connect") as connect_mock, patch(
        "zwave_js_server.firmware.Client.set_api_schema"
    ) as set_api_schema_mock, patch(
        "zwave_js_server.firmware.Client.async_send_command"
    ) as cmd_mock, patch(
        "zwave_js_server.firmware.Client.disconnect"
    ) as disconnect_mock:
        node = multisensor_6
        await begin_firmware_update(
            url, node, "test", bytes(10), client_session, "test"
        )

        connect_mock.assert_called_once()
        set_api_schema_mock.assert_called_once()
        cmd_mock.assert_called_once_with(
            {
                "command": "node.begin_firmware_update",
                "nodeId": node.node_id,
                "firmwareFilename": "test",
                "firmwareFile": "AAAAAAAAAAAAAA==",
                "firmwareFileFormat": "test",
            },
            require_schema=5,
        )
        disconnect_mock.assert_called_once()
