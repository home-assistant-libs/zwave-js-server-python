"""Test the firmware update helper."""

from unittest.mock import patch

from zwave_js_server.firmware import driver_firmware_update_otw, update_firmware
from zwave_js_server.model.driver.firmware import (
    DriverFirmwareUpdateData,
    DriverFirmwareUpdateStatus,
)
from zwave_js_server.model.node.firmware import (
    NodeFirmwareUpdateData,
    NodeFirmwareUpdateStatus,
)


async def test_update_firmware_guess_format(url, client_session, multisensor_6):
    """Test update_firmware with guessed format."""
    with (
        patch("zwave_js_server.firmware.Client.connect") as connect_mock,
        patch("zwave_js_server.firmware.Client.initialize") as initialize_mock,
        patch("zwave_js_server.firmware.Client.async_send_command") as cmd_mock,
        patch("zwave_js_server.firmware.Client.disconnect") as disconnect_mock,
    ):
        node = multisensor_6
        cmd_mock.return_value = {
            "result": {"status": 255, "success": True, "reInterview": False}
        }
        result = await update_firmware(
            url, node, [NodeFirmwareUpdateData("test", bytes(10))], client_session
        )
        assert result.status == NodeFirmwareUpdateStatus.OK_RESTART_PENDING
        assert result.success
        assert not result.reinterview

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
            require_schema=29,
        )
        disconnect_mock.assert_called_once()


async def test_update_firmware_known_format_and_target(
    url, client_session, multisensor_6
):
    """Test update_firmware with known format."""
    with (
        patch("zwave_js_server.firmware.Client.connect") as connect_mock,
        patch("zwave_js_server.firmware.Client.initialize") as initialize_mock,
        patch("zwave_js_server.firmware.Client.async_send_command") as cmd_mock,
        patch("zwave_js_server.firmware.Client.disconnect") as disconnect_mock,
    ):
        node = multisensor_6
        cmd_mock.return_value = {
            "result": {"status": 255, "success": True, "reInterview": False}
        }
        result = await update_firmware(
            url=url,
            node=node,
            updates=[NodeFirmwareUpdateData("test", bytes(10), "test", 1)],
            session=client_session,
        )
        assert result.status == NodeFirmwareUpdateStatus.OK_RESTART_PENDING
        assert result.success
        assert not result.reinterview

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
                        "firmwareTarget": 1,
                    }
                ],
            },
            require_schema=29,
        )
        disconnect_mock.assert_called_once()


async def test_driver_firmware_update_otw_guess_format(url, client_session):
    """Test driver_firmware_update_otw with guessed format."""
    with (
        patch("zwave_js_server.firmware.Client.connect") as connect_mock,
        patch("zwave_js_server.firmware.Client.initialize") as initialize_mock,
        patch("zwave_js_server.firmware.Client.async_send_command") as cmd_mock,
        patch("zwave_js_server.firmware.Client.disconnect") as disconnect_mock,
    ):
        cmd_mock.return_value = {"result": {"status": 255, "success": True}}
        result = await driver_firmware_update_otw(
            url, DriverFirmwareUpdateData("test", bytes(10)), client_session
        )
        assert result.status == DriverFirmwareUpdateStatus.OK
        assert result.success

        connect_mock.assert_called_once()
        initialize_mock.assert_called_once()
        cmd_mock.assert_called_once_with(
            {
                "command": "driver.firmware_update_otw",
                "filename": "test",
                "file": "AAAAAAAAAAAAAA==",
            },
            require_schema=29,
        )
        disconnect_mock.assert_called_once()


async def test_driver_firmware_update_otw_known_format_and_target(url, client_session):
    """Test driver_firmware_update_otw with known format."""
    with (
        patch("zwave_js_server.firmware.Client.connect") as connect_mock,
        patch("zwave_js_server.firmware.Client.initialize") as initialize_mock,
        patch("zwave_js_server.firmware.Client.async_send_command") as cmd_mock,
        patch("zwave_js_server.firmware.Client.disconnect") as disconnect_mock,
    ):
        cmd_mock.return_value = {"result": {"status": 255, "success": True}}
        result = await driver_firmware_update_otw(
            url=url,
            firmware_file=DriverFirmwareUpdateData("test", bytes(10), "test"),
            session=client_session,
        )
        assert result.status == DriverFirmwareUpdateStatus.OK
        assert result.success

        connect_mock.assert_called_once()
        initialize_mock.assert_called_once()
        cmd_mock.assert_called_once_with(
            {
                "command": "driver.firmware_update_otw",
                "filename": "test",
                "file": "AAAAAAAAAAAAAA==",
                "fileFormat": "test",
            },
            require_schema=29,
        )
        disconnect_mock.assert_called_once()
