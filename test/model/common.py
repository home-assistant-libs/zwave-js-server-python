"""Provide common tools for testing Z-Wave JS server models."""

from zwave_js_server.model.firmware import FirmwareUpdateInfoDataType

FIRMWARE_UPDATE_INFO = FirmwareUpdateInfoDataType(
    **{
        "version": "1.0.0",
        "changelog": "changelog",
        "channel": "stable",
        "files": [{"target": 0, "url": "http://example.com", "integrity": "test"}],
        "downgrade": True,
        "normalizedVersion": "1.0.0",
        "device": {
            "manufacturerId": 1,
            "productType": 2,
            "productId": 3,
            "firmwareVersion": "0.4.4",
            "rfRegion": 1,
        },
    }
)
