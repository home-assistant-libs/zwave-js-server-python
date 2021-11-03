"""Model for utils commands."""
from ..client import Client
from .controller import QRProvisioningInformation


async def async_parse_qr_code_string(
    client: Client, qr_code_string: str
) -> QRProvisioningInformation:
    """Parse a QR code string into a QRProvisioningInformation object."""
    data = await client.async_send_command(
        {"command": "utils.parse_qr_code_string", "qr": qr_code_string}
    )
    return QRProvisioningInformation.from_dict(data["qrProvisioningInformation"])
