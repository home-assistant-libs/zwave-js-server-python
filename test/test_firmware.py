"""Test the firmware update helper."""
from unittest.mock import patch

from zwave_js_server.firmware import controller_firmware_update_otw, update_firmware
from zwave_js_server.model.firmware import FirmwareUpdateData


async def test_update_firmware_guess_format(url, client_session, multisensor_6):
    """Test update_firmware with guessed format."""
    with patch("zwave_js_server.firmware.Client.connect") as connect_mock, patch(
        "zwave_js_server.firmware.Client.initialize"
    ) as initialize_mock, patch(
        "zwave_js_server.firmware.Client.async_send_command"
    ) as cmd_mock, patch(
        "zwave_js_server.firmware.Client.disconnect"
    ) as disconnect_mock:
        node = multisensor_6
        cmd_mock.return_value = {"success": True}
        assert await update_firmware(
            url, node, [FirmwareUpdateData("test", bytes(10))], client_session
        )

        connect_mock.assert_called_once()
        initialize_mock.assert_called_once()
        cmd_mock.assert_called_once_with(
            {
                "command": "node.update_firmware",
                "nodeId": node.node_id,
                "updates": [
                    {
                        "filename": "test",
                        "file": "AAAAAAAAAAAAAA==",
                    }
                ],
            },
            require_schema=24,
        )
        disconnect_mock.assert_called_once()


async def test_update_firmware_known_format_and_target(
    url, client_session, multisensor_6
):
    """Test update_firmware with known format."""
    with patch("zwave_js_server.firmware.Client.connect") as connect_mock, patch(
        "zwave_js_server.firmware.Client.initialize"
    ) as initialize_mock, patch(
        "zwave_js_server.firmware.Client.async_send_command"
    ) as cmd_mock, patch(
        "zwave_js_server.firmware.Client.disconnect"
    ) as disconnect_mock:
        node = multisensor_6
        cmd_mock.return_value = {"success": True}
        assert await update_firmware(
            url=url,
            node=node,
            updates=[FirmwareUpdateData("test", bytes(10), "test")],
            session=client_session,
        )

        connect_mock.assert_called_once()
        initialize_mock.assert_called_once()
        cmd_mock.assert_called_once_with(
            {
                "command": "node.update_firmware",
                "nodeId": node.node_id,
                "updates": [
                    {
                        "filename": "test",
                        "file": "AAAAAAAAAAAAAA==",
                        "fileFormat": "test",
                    }
                ],
            },
            require_schema=24,
        )
        disconnect_mock.assert_called_once()


async def test_controller_firmware_update_otw_guess_format(url, client_session):
    """Test controller_firmware_update_otw with guessed format."""
    with patch("zwave_js_server.firmware.Client.connect") as connect_mock, patch(
        "zwave_js_server.firmware.Client.initialize"
    ) as initialize_mock, patch(
        "zwave_js_server.firmware.Client.async_send_command"
    ) as cmd_mock, patch(
        "zwave_js_server.firmware.Client.disconnect"
    ) as disconnect_mock:
        cmd_mock.return_value = {"success": True}
        assert await controller_firmware_update_otw(
            url, FirmwareUpdateData("test", bytes(10)), client_session
        )

        connect_mock.assert_called_once()
        initialize_mock.assert_called_once()
        cmd_mock.assert_called_once_with(
            {
                "command": "controller.firmware_update_otw",
                "filename": "test",
                "file": "AAAAAAAAAAAAAA==",
            },
            require_schema=25,
        )
        disconnect_mock.assert_called_once()


async def test_controller_firmware_update_otw_known_format_and_target(
    url, client_session
):
    """Test controller_firmware_update_otw with known format."""
    with patch("zwave_js_server.firmware.Client.connect") as connect_mock, patch(
        "zwave_js_server.firmware.Client.initialize"
    ) as initialize_mock, patch(
        "zwave_js_server.firmware.Client.async_send_command"
    ) as cmd_mock, patch(
        "zwave_js_server.firmware.Client.disconnect"
    ) as disconnect_mock:
        cmd_mock.return_value = {"success": True}
        assert await controller_firmware_update_otw(
            url=url,
            firmware_file=FirmwareUpdateData("test", bytes(10), "test"),
            session=client_session,
        )

        connect_mock.assert_called_once()
        initialize_mock.assert_called_once()
        cmd_mock.assert_called_once_with(
            {
                "command": "controller.firmware_update_otw",
                "filename": "test",
                "file": "AAAAAAAAAAAAAA==",
                "fileFormat": "test",
            },
            require_schema=25,
        )
        disconnect_mock.assert_called_once()
