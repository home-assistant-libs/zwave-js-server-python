"""
Model for a Zwave Node's device config.

https://zwave-js.github.io/node-zwave-js/#/api/node?id=deviceconfig
"""

from typing import Dict, List, Optional, TypedDict


class DeviceConfigDataType(TypedDict, total=False):
    """Represent a device config data dict type."""

    manufacturer: str
    manufacturerId: str
    label: str
    description: str
    devices: List[Dict[str, str]]
    firmwareVersion: Dict[str, str]
    associations: Dict[str, dict]
    supportsZWavePlus: bool
    proprietary: dict
    paramInformation: Dict[str, dict]
    compat: Dict[str, dict]


class DeviceConfig:
    """Model for a Zwave Node's device config."""

    def __init__(self, data: DeviceConfigDataType) -> None:
        """Initialize."""
        self.data = data

    @property
    def manufacturer(self) -> Optional[str]:
        """Return name of the manufacturer."""
        return self.data.get("manufacturer")

    @property
    def manufacturer_id(self) -> Optional[str]:  # TODO: In the dump this is an int.
        """Return manufacturer id (as defined in the specs) as a 4-digit hexadecimal string."""
        return self.data.get("manufacturerId")

    @property
    def label(self) -> Optional[str]:
        """Return short label for the device."""
        return self.data.get("label")

    @property
    def description(self) -> Optional[str]:
        """Return longer description of the device, usually the full name."""
        return self.data.get("description")

    @property
    def devices(self) -> List[Dict[str, str]]:
        """Return list of product type and product ID combinations."""
        return self.data.get("devices", [])

    @property
    def firmware_version(self) -> Optional[Dict[str, str]]:
        """Return firmware version range this config is valid for."""
        return self.data.get("firmwareVersion")

    @property
    def associations(self) -> Optional[Dict[str, dict]]:
        """Return association groups the device supports."""
        return self.data.get("associations")

    @property
    def supports_zwave_plus(self) -> Optional[bool]:
        """Return if the device complies with the Z-Wave+ standard."""
        return self.data.get("supportsZWavePlus")

    @property
    def proprietary(self) -> Optional[dict]:
        """Return dictionary of settings for the proprietary CC."""
        return self.data.get("proprietary")

    @property
    def param_information(self) -> Optional[Dict[str, dict]]:
        """Return dictionary of the configuration parameters the device supports."""
        return self.data.get("paramInformation")

    @property
    def compat(self) -> Optional[Dict[str, dict]]:
        """Return compatibility flags."""
        return self.data.get("compat")
