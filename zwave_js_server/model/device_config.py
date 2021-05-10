"""
Model for a Zwave Node's device config.

https://zwave-js.github.io/node-zwave-js/#/api/node?id=deviceconfig
"""
from typing import Dict, List, Optional, TypedDict


class DeviceDeviceDataType(TypedDict, total=False):
    """Represent a device device data dict type."""

    productType: int
    productId: int


class DeviceDevice:
    """Model for a Zwave Node's device config's device."""

    def __init__(self, data: DeviceDeviceDataType) -> None:
        """Initialize."""
        self.data = data

    @property
    def product_type(self) -> Optional[int]:
        """Return product type."""
        return self.data.get("productType")

    @property
    def product_id(self) -> Optional[int]:
        """Return product id."""
        return self.data.get("productId")


class DeviceFirmwareVersionRangeDataType(TypedDict, total=False):
    """Represent a device firmware version range data dict type."""

    min: str
    max: str


class DeviceFirmwareVersionRange:
    """Model for a Zwave Node's device config's firmware version range."""

    def __init__(self, data: DeviceFirmwareVersionRangeDataType) -> None:
        """Initialize."""
        self.data = data

    @property
    def min(self) -> Optional[str]:
        """Return min version."""
        return self.data.get("min")

    @property
    def max(self) -> Optional[str]:
        """Return max version."""
        return self.data.get("max")


class DeviceMetadataDataType(TypedDict, total=False):
    """Represent a device metadata data dict type."""

    wakeup: str
    inclusion: str
    exclusion: str
    reset: str
    manual: str


class DeviceMetadata:
    """Model for a Zwave Node's device config's metadata."""

    def __init__(self, data: DeviceMetadataDataType) -> None:
        """Initialize."""
        self.data = data

    @property
    def wakeup(self) -> Optional[str]:
        """Return wakeup instructions."""
        return self.data.get("wakeup")

    @property
    def inclusion(self) -> Optional[str]:
        """Return inclusion instructions."""
        return self.data.get("inclusion")

    @property
    def exclusion(self) -> Optional[str]:
        """Return exclusion instructions."""
        return self.data.get("exclusion")

    @property
    def reset(self) -> Optional[str]:
        """Return reset instructions."""
        return self.data.get("reset")

    @property
    def manual(self) -> Optional[str]:
        """Return manual instructions."""
        return self.data.get("manual")


class DeviceConfigDataType(TypedDict, total=False):
    """Represent a device config data dict type."""

    filename: str
    manufacturer: str
    manufacturerId: str
    label: str
    description: str
    devices: List[DeviceDeviceDataType]
    firmwareVersion: DeviceFirmwareVersionRange
    associations: Dict[str, dict]
    paramInformation: Dict[str, dict]
    supportsZWavePlus: bool
    proprietary: dict
    compat: Dict[str, dict]
    metadata: DeviceMetadataDataType
    isEmbedded: bool


class DeviceConfig:
    """Model for a Zwave Node's device config."""

    def __init__(self, data: DeviceConfigDataType) -> None:
        """Initialize."""
        self.data = data
        self._devices = [
            DeviceDevice(device) for device in self.data.get("devices", [])
        ]
        self._firmware_version = DeviceFirmwareVersionRange(
            self.data.get("firmwareVersion", {})  # type: ignore
        )
        self._metadata = DeviceMetadata(self.data.get("metadata", {}))

    @property
    def filename(self) -> Optional[str]:
        """Return config filename."""
        return self.data.get("filename")

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
    def devices(self) -> List[DeviceDevice]:
        """Return list of product type and product ID combinations."""
        return self._devices

    @property
    def firmware_version(self) -> DeviceFirmwareVersionRange:
        """Return firmware version range this config is valid for."""
        return self._firmware_version

    @property
    def associations(self) -> Dict[str, dict]:
        """Return dict of association groups the device supports."""
        return self.data.get("associations", {})

    @property
    def param_information(self) -> Dict[str, dict]:
        """Return dictionary of configuration parameters the device supports."""
        return self.data.get("paramInformation", {})

    @property
    def supports_zwave_plus(self) -> Optional[bool]:
        """Return if the device complies with the Z-Wave+ standard."""
        return self.data.get("supportsZWavePlus")

    @property
    def proprietary(self) -> dict:
        """Return dictionary of settings for the proprietary CC."""
        return self.data.get("proprietary", {})

    @property
    def compat(self) -> Dict[str, dict]:
        """Return compatibility flags."""
        return self.data.get("compat", {})

    @property
    def metadata(self) -> DeviceMetadata:
        """Return metadata."""
        return self._metadata

    @property
    def is_embedded(self) -> Optional[bool]:
        """Return whether device config is embedded in zwave-js-server."""
        return self.data.get("isEmbedded")
