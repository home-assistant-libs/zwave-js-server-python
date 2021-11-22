"""Test general utility functions."""
import pytest

from zwave_js_server.const import Protocols, QRCodeVersion, SecurityClass
from zwave_js_server.model.utils import async_parse_qr_code_string


async def test_parse_qr_code_string(client, mock_command, uuid4):
    """Test parsing a QR code string."""
    ack_commands = mock_command(
        {"command": "utils.parse_qr_code_string"},
        {
            "qrProvisioningInformation": {
                "version": 0,
                "securityClasses": [0, 1, 2],
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
