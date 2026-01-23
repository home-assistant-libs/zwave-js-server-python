"""Test general utility functions."""

import base64

import pytest

from zwave_js_server.const import (
    FirmwareFileFormat,
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


# Schema 45+ tests


async def test_guess_firmware_file_format(client, mock_command, uuid4):
    """Test guessing firmware file format."""
    ack_commands = mock_command(
        {"command": "utils.guess_firmware_file_format"},
        {"format": "hex"},
    )

    file_data = b"test firmware data"
    result = await async_guess_firmware_file_format(client, "firmware.hex", file_data)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "utils.guess_firmware_file_format",
        "filename": "firmware.hex",
        "file": base64.b64encode(file_data).decode("ascii"),
        "messageId": uuid4,
    }
    assert result == FirmwareFileFormat.HEX


async def test_try_unzip_firmware_file(client, mock_command, uuid4):
    """Test extracting firmware from a ZIP file."""
    firmware_data = b"extracted firmware"
    ack_commands = mock_command(
        {"command": "utils.try_unzip_firmware_file"},
        {
            "file": {
                "filename": "firmware.hex",
                "format": "hex",
                "data": base64.b64encode(firmware_data).decode("ascii"),
            }
        },
    )

    zip_data = b"fake zip data"
    result = await async_try_unzip_firmware_file(client, zip_data)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "utils.try_unzip_firmware_file",
        "file": base64.b64encode(zip_data).decode("ascii"),
        "messageId": uuid4,
    }
    assert result is not None
    assert result.filename == "firmware.hex"
    assert result.format == FirmwareFileFormat.HEX
    assert result.data == firmware_data


async def test_try_unzip_firmware_file_not_found(client, mock_command, uuid4):
    """Test extracting firmware from an invalid ZIP file returns None."""
    ack_commands = mock_command(
        {"command": "utils.try_unzip_firmware_file"},
        {"file": None},
    )

    zip_data = b"not a valid zip"
    result = await async_try_unzip_firmware_file(client, zip_data)

    assert len(ack_commands) == 1
    assert result is None


async def test_extract_firmware(client, mock_command, uuid4):
    """Test extracting firmware data from a file."""
    extracted_data = b"extracted firmware bytes"
    ack_commands = mock_command(
        {"command": "utils.extract_firmware"},
        {
            "firmware": {
                "data": base64.b64encode(extracted_data).decode("ascii"),
                "firmwareTarget": 0,
            }
        },
    )

    file_data = b"raw firmware file"
    result = await async_extract_firmware(client, file_data, FirmwareFileFormat.HEX)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "utils.extract_firmware",
        "file": base64.b64encode(file_data).decode("ascii"),
        "format": "hex",
        "messageId": uuid4,
    }
    assert result.data == extracted_data
    assert result.firmware_target == 0


async def test_extract_firmware_no_target(client, mock_command, uuid4):
    """Test extracting firmware data without firmware target."""
    extracted_data = b"extracted firmware bytes"
    ack_commands = mock_command(
        {"command": "utils.extract_firmware"},
        {
            "firmware": {
                "data": base64.b64encode(extracted_data).decode("ascii"),
            }
        },
    )

    file_data = b"raw firmware file"
    result = await async_extract_firmware(client, file_data, FirmwareFileFormat.BIN)

    assert len(ack_commands) == 1
    assert result.data == extracted_data
    assert result.firmware_target is None
