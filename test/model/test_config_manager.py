"""Test the config manager."""

from zwave_js_server.client import Client
from zwave_js_server.model.config_manager import ConfigManager
from zwave_js_server.model.device_config import DeviceConfigDataType

from ..common import MockCommandProtocol


async def test_lookup_device(
    client: Client,
    mock_command: MockCommandProtocol,
    device_config: DeviceConfigDataType,
) -> None:
    """Test the lookup_device command."""
    # Test successful lookup
    mock_command(
        {
            "command": "config_manager.lookup_device",
            "manufacturerId": 0x1234,
            "productType": 0x5678,
            "productId": 0x9ABC,
        },
        {"config": device_config},
    )

    config_manager = ConfigManager(client)
    result = await config_manager.lookup_device(0x1234, 0x5678, 0x9ABC)

    assert result is not None
    assert result.manufacturer == "Test Manufacturer"
    assert result.manufacturer_id == "0x1234"
    assert result.label == "Test Device"
    assert result.description == "Test Device Description"
    assert len(result.devices) == 1
    assert result.devices[0].product_type == "0x5678"
    assert result.devices[0].product_id == "0x9ABC"
    assert result.firmware_version.min == "1.0"
    assert result.firmware_version.max == "2.0"

    # Test lookup with firmware version
    mock_command(
        {
            "command": "config_manager.lookup_device",
            "manufacturerId": 0x1234,
            "productType": 0x5678,
            "productId": 0x9ABC,
            "firmwareVersion": "1.5",
        },
        {"config": device_config},
    )

    result = await config_manager.lookup_device(0x1234, 0x5678, 0x9ABC, "1.5")

    assert result is not None
    assert result.manufacturer == "Test Manufacturer"

    assert result.to_dict() == device_config

    # Test device not found
    mock_command(
        {
            "command": "config_manager.lookup_device",
            "manufacturerId": 0x4321,
            "productType": 0x8765,
            "productId": 0xCBA9,
        },
        {"config": None},
    )

    result = await config_manager.lookup_device(0x4321, 0x8765, 0xCBA9)

    assert result is None
