"""Model for utils commands."""

from __future__ import annotations

from ..client import Client
from ..const import MINIMUM_QR_STRING_LENGTH
from ..util.helpers import convert_base64_to_bytes, convert_bytes_to_base64
from .controller import QRProvisioningInformation


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
    client: Client, filename: str, file: bytes
) -> str:
    """Guess the firmware file format from filename and file contents."""
    data = await client.async_send_command(
        {
            "command": "utils.guess_firmware_file_format",
            "filename": filename,
            "file": convert_bytes_to_base64(file),
        },
        require_schema=47,
    )
    return data["format"]


async def async_try_unzip_firmware_file(client: Client, file: bytes) -> dict | None:
    """Try to unzip a firmware file.

    Returns a dict with `filename`, `format`, and `data` (bytes) if successful,
    or None if the file is not a valid ZIP or contains no compatible firmware.
    """
    data = await client.async_send_command(
        {
            "command": "utils.try_unzip_firmware_file",
            "file": convert_bytes_to_base64(file),
        },
        require_schema=47,
    )
    result = data.get("file")
    if result is None:
        return None
    return {
        "filename": result["filename"],
        "format": result["format"],
        "data": convert_base64_to_bytes(result["data"]),
    }


async def async_extract_firmware(client: Client, file: bytes, format_: str) -> dict:
    """Extract firmware from a file with a known format.

    Returns a dict with `data` (bytes) and optionally `firmware_target` (int).
    """
    data = await client.async_send_command(
        {
            "command": "utils.extract_firmware",
            "file": convert_bytes_to_base64(file),
            "format": format_,
        },
        require_schema=47,
    )
    firmware = data["firmware"]
    result: dict = {"data": convert_base64_to_bytes(firmware["data"])}
    if "firmwareTarget" in firmware:
        result["firmware_target"] = firmware["firmwareTarget"]
    return result
