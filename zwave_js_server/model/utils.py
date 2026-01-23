"""Model for utils commands."""

from __future__ import annotations

import base64
from dataclasses import dataclass

from ..client import Client
from ..const import MINIMUM_QR_STRING_LENGTH, FirmwareFileFormat
from .controller import QRProvisioningInformation


@dataclass
class UnzippedFirmware:
    """Represent firmware extracted from a ZIP file."""

    filename: str
    format: FirmwareFileFormat
    data: bytes


@dataclass
class ExtractedFirmware:
    """Represent extracted firmware data."""

    data: bytes
    firmware_target: int | None = None


async def async_parse_qr_code_string(
    client: Client, qr_code_string: str
) -> QRProvisioningInformation:
    """Parse a QR code string into a QRProvisioningInformation object."""
    if len(qr_code_string) < MINIMUM_QR_STRING_LENGTH or not qr_code_string.startswith(
        "90"
    ):
        raise ValueError(
            f"QR code string must be at least {MINIMUM_QR_STRING_LENGTH} characters "
            "long and start with `90`"
        )
    data = await client.async_send_command(
        {"command": "utils.parse_qr_code_string", "qr": qr_code_string}
    )
    return QRProvisioningInformation.from_dict(data["qrProvisioningInformation"])


async def async_try_parse_dsk_from_qr_code_string(
    client: Client, qr_code_string: str
) -> str | None:
    """Try to get DSK QR code."""
    data = await client.async_send_command(
        {"command": "utils.try_parse_dsk_from_qr_code_string", "qr": qr_code_string}
    )
    return data.get("dsk")


async def async_guess_firmware_file_format(
    client: Client, filename: str, file_data: bytes
) -> FirmwareFileFormat:
    """Guess the firmware file format from filename and file contents.

    Args:
    ----
        client: The Z-Wave JS client.
        filename: The name of the firmware file.
        file_data: The raw firmware file data.

    Returns:
    -------
        The guessed firmware file format.

    """
    data = await client.async_send_command(
        {
            "command": "utils.guess_firmware_file_format",
            "filename": filename,
            "file": base64.b64encode(file_data).decode("ascii"),
        },
        require_schema=45,
    )
    return FirmwareFileFormat(data["format"])


async def async_try_unzip_firmware_file(
    client: Client, file_data: bytes
) -> UnzippedFirmware | None:
    """Extract firmware from a ZIP archive.

    Args:
    ----
        client: The Z-Wave JS client.
        file_data: The raw ZIP file data.

    Returns:
    -------
        The extracted firmware if successful, None if not a valid ZIP or
        no compatible firmware was found.

    """
    data = await client.async_send_command(
        {
            "command": "utils.try_unzip_firmware_file",
            "file": base64.b64encode(file_data).decode("ascii"),
        },
        require_schema=45,
    )
    file_info = data.get("file")
    if file_info is None:
        return None
    return UnzippedFirmware(
        filename=file_info["filename"],
        format=FirmwareFileFormat(file_info["format"]),
        data=base64.b64decode(file_info["data"]),
    )


async def async_extract_firmware(
    client: Client, file_data: bytes, file_format: FirmwareFileFormat
) -> ExtractedFirmware:
    """Extract firmware data from a firmware file given its format.

    Args:
    ----
        client: The Z-Wave JS client.
        file_data: The raw firmware file data.
        file_format: The format of the firmware file.

    Returns:
    -------
        The extracted firmware data.

    """
    data = await client.async_send_command(
        {
            "command": "utils.extract_firmware",
            "file": base64.b64encode(file_data).decode("ascii"),
            "format": file_format.value,
        },
        require_schema=45,
    )
    firmware = data["firmware"]
    return ExtractedFirmware(
        data=base64.b64decode(firmware["data"]),
        firmware_target=firmware.get("firmwareTarget"),
    )
