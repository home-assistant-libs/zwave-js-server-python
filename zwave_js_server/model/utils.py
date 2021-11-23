"""Model for utils commands."""
from zwave_js_server.const import MINIMUM_QR_STRING_LENGTH
from ..client import Client
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
