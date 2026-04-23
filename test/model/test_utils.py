"""Test general utility functions."""

import pytest

from zwave_js_server.client import Client
from zwave_js_server.const import (
    Protocols,
    ProvisioningEntryStatus,
    QRCodeVersion,
    SecurityClass,
)
from zwave_js_server.model.utils import (
    async_extract_firmware,
    async_guess_firmware_file_format,
    async_parse_qr_code_string,
    async_try_parse_dsk_from_qr_code_string,
    async_try_unzip_firmware_file,
)

from ..common import MockCommandProtocol


async def test_parse_qr_code_string(client, mock_command, uuid4):
    """Test parsing a QR code string."""
    ack_commands = mock_command(
        {"command": "utils.parse_qr_code_string"},
        {
            "qrProvisioningInformation": {
                "version": 0,
                "securityClasses": [0, 1, 2],
                "requestedSecurityClasses": [0],
                "status": 1,
                "dsk": "test",
                "genericDeviceClass": 1,
                "specificDeviceClass": 1,
                "installerIconType": 1,
                "manufacturerId": 1,
                "productType": 1,
                "productId": 1,
                "applicationVersion": "test",
                "maxInclusionRequestInterval": 1,
                "uuid": "test",
                "supportedProtocols": [0],
            }
        },
    )
    qr_provisioning_info = await async_parse_qr_code_string(
        client, "90testtesttesttesttesttesttesttesttesttesttesttesttest"
    )
    assert ack_commands[0] == {
        "command": "utils.parse_qr_code_string",
        "qr": "90testtesttesttesttesttesttesttesttesttesttesttesttest",
        "messageId": uuid4,
    }
    assert qr_provisioning_info.version == QRCodeVersion.S2
    assert set(qr_provisioning_info.security_classes) == {
        SecurityClass.S2_ACCESS_CONTROL,
        SecurityClass.S2_AUTHENTICATED,
        SecurityClass.S2_UNAUTHENTICATED,
    }
    assert qr_provisioning_info.requested_security_classes == [
        SecurityClass.S2_UNAUTHENTICATED
    ]
    assert qr_provisioning_info.status == ProvisioningEntryStatus.INACTIVE
    assert (
        qr_provisioning_info.dsk
        == qr_provisioning_info.application_version
        == qr_provisioning_info.uuid
        == "test"
    )
    assert (
        qr_provisioning_info.generic_device_class
        == qr_provisioning_info.specific_device_class
        == qr_provisioning_info.installer_icon_type
        == qr_provisioning_info.manufacturer_id
        == qr_provisioning_info.product_type
        == qr_provisioning_info.product_id
        == qr_provisioning_info.max_inclusion_request_interval
        == 1
    )
    assert qr_provisioning_info.supported_protocols == [Protocols.ZWAVE]

    # Test invalid QR code length fails
    with pytest.raises(ValueError):
        await async_parse_qr_code_string(client, "test")


async def test_async_try_parse_dsk_from_qr_code_string(client, mock_command, uuid4):
    """Test trying to parse a DSK from a qr code string."""
    ack_commands = mock_command(
        {"command": "utils.try_parse_dsk_from_qr_code_string"}, {"dsk": "abc"}
    )
    dsk = await async_try_parse_dsk_from_qr_code_string(
        client, "90testtesttesttesttesttesttesttesttesttesttesttesttest"
    )
    assert ack_commands[0] == {
        "command": "utils.try_parse_dsk_from_qr_code_string",
        "qr": "90testtesttesttesttesttesttesttesttesttesttesttesttest",
        "messageId": uuid4,
    }
    assert dsk == "abc"


async def test_async_try_parse_dsk_from_qr_code_string_fails(
    client, mock_command, uuid4
):
    """Test trying to parse a DSK from a qr code string fails."""

    ack_commands = mock_command(
        {"command": "utils.try_parse_dsk_from_qr_code_string"}, {}
    )

    dsk = await async_try_parse_dsk_from_qr_code_string(
        client, "90testtesttesttesttesttesttesttesttesttesttesttesttest"
    )
    assert ack_commands[0] == {
        "command": "utils.try_parse_dsk_from_qr_code_string",
        "qr": "90testtesttesttesttesttesttesttesttesttesttesttesttest",
        "messageId": uuid4,
    }
    assert dsk is None


async def test_guess_firmware_file_format(
    client: Client, mock_command: MockCommandProtocol, uuid4: str
) -> None:
    """Test guessing firmware file format."""
    ack_commands = mock_command(
        {"command": "utils.guess_firmware_file_format"}, {"format": "hex"}
    )
    result = await async_guess_firmware_file_format(client, "test.hex", b"\x00\x01")
    assert result == "hex"
    assert ack_commands[0] == {
        "command": "utils.guess_firmware_file_format",
        "filename": "test.hex",
        "file": "AAE=",
        "messageId": uuid4,
    }


async def test_try_unzip_firmware_file(
    client: Client, mock_command: MockCommandProtocol, uuid4: str
) -> None:
    """Test unzipping firmware file — success and None cases."""
    mock_command(
        {"command": "utils.try_unzip_firmware_file"},
        {"file": {"filename": "fw.bin", "format": "bin", "data": "AQID"}},
    )
    result = await async_try_unzip_firmware_file(client, b"\x00")
    assert result is not None
    assert result["filename"] == "fw.bin"
    assert result["format"] == "bin"
    assert result["data"] == b"\x01\x02\x03"


async def test_try_unzip_firmware_file_none(
    client: Client, mock_command: MockCommandProtocol
) -> None:
    """Test unzipping returns None when not a valid ZIP."""
    mock_command({"command": "utils.try_unzip_firmware_file"}, {"file": None})
    assert await async_try_unzip_firmware_file(client, b"\x00") is None


async def test_extract_firmware(
    client: Client, mock_command: MockCommandProtocol
) -> None:
    """Test extracting firmware with firmwareTarget."""
    mock_command(
        {"command": "utils.extract_firmware"},
        {"firmware": {"data": "AQID", "firmwareTarget": 0}},
    )
    result = await async_extract_firmware(client, b"\x00", "hex")
    assert result["data"] == b"\x01\x02\x03"
    assert result["firmware_target"] == 0


async def test_extract_firmware_no_target(
    client: Client, mock_command: MockCommandProtocol
) -> None:
    """Test extracting firmware without firmwareTarget."""
    mock_command(
        {"command": "utils.extract_firmware"},
        {"firmware": {"data": "AQID"}},
    )
    result = await async_extract_firmware(client, b"\x00", "bin")
    assert "firmware_target" not in result
