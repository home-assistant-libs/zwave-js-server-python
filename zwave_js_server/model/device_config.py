"""
Model for a Zwave Node's device config.

https://zwave-js.github.io/node-zwave-js/#/api/node?id=deviceconfig
"""
from __future__ import annotations

from typing import Any, Literal, TypedDict


class DeviceDeviceDataType(TypedDict, total=False):
    """Represent a device device data dict type."""

    productType: str
    productId: str


class DeviceDevice:
    """Model for a Zwave Node's device config's device."""

    def __init__(self, data: DeviceDeviceDataType) -> None:
        """Initialize."""
        self.data = data

    @property
    def product_type(self) -> str | None:
        """Return product type."""
        return self.data.get("productType")

    @property
    def product_id(self) -> str | None:
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
    def min(self) -> str | None:
        """Return min version."""
        return self.data.get("min")

    @property
    def max(self) -> str | None:
        """Return max version."""
        return self.data.get("max")


class CommentDataType(TypedDict):
    """Represent a device config's comment data dict type."""

    # See PR for suggested meanings of each level:
    # https://github.com/zwave-js/node-zwave-js/pull/3947
    level: Literal["info", "warning", "error"]
    text: str


class DeviceMetadataDataType(TypedDict, total=False):
    """Represent a device metadata data dict type."""

    wakeup: str
    inclusion: str
    exclusion: str
    reset: str
    manual: str
    comments: CommentDataType | list[CommentDataType]


class DeviceMetadata:
    """Model for a Zwave Node's device config's metadata."""

    def __init__(self, data: DeviceMetadataDataType) -> None:
        """Initialize."""
        self.data = data

    @property
    def wakeup(self) -> str | None:
        """Return wakeup instructions."""
        return self.data.get("wakeup")

    @property
    def inclusion(self) -> str | None:
        """Return inclusion instructions."""
        return self.data.get("inclusion")

    @property
    def exclusion(self) -> str | None:
        """Return exclusion instructions."""
        return self.data.get("exclusion")

    @property
    def reset(self) -> str | None:
        """Return reset instructions."""
        return self.data.get("reset")

    @property
    def manual(self) -> str | None:
        """Return manual instructions."""
        return self.data.get("manual")

    @property
    def comments(self) -> list[CommentDataType]:
        """Return list of comments about device."""
        comments = self.data.get("comments", [])
        if isinstance(comments, dict):
            return [comments]
        return comments


class DeviceConfigDataType(TypedDict, total=False):
    """Represent a device config data dict type."""

    filename: str
    manufacturer: str
    manufacturerId: str
    label: str
    description: str
    devices: list[DeviceDeviceDataType]
    firmwareVersion: DeviceFirmwareVersionRangeDataType
    associations: dict[str, dict]
    paramInformation: dict[str, dict]
    supportsZWavePlus: bool
    proprietary: dict
    compat: dict[str, Any]
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
            self.data.get("firmwareVersion", {})
        )
        self._metadata = DeviceMetadata(self.data.get("metadata", {}))

    @property
    def filename(self) -> str | None:
        """Return config filename."""
        return self.data.get("filename")

    @property
    def manufacturer(self) -> str | None:
        """Return name of the manufacturer."""
        return self.data.get("manufacturer")

    @property
    def manufacturer_id(self) -> str | None:  # TODO: In the dump this is an int.
        """Return manufacturer id (as defined in specs) as a 4-digit hex string."""
        return self.data.get("manufacturerId")

    @property
    def label(self) -> str | None:
        """Return short label for the device."""
        return self.data.get("label")

    @property
    def description(self) -> str | None:
        """Return longer description of the device, usually the full name."""
        return self.data.get("description")

    @property
    def devices(self) -> list[DeviceDevice]:
        """Return list of product type and product ID combinations."""
        return self._devices

    @property
    def firmware_version(self) -> DeviceFirmwareVersionRange:
        """Return firmware version range this config is valid for."""
        return self._firmware_version

    @property
    def associations(self) -> dict[str, dict]:
        """Return dict of association groups the device supports."""
        return self.data.get("associations", {})

    @property
    def param_information(self) -> dict[str, dict]:
        """Return dictionary of configuration parameters the device supports."""
        return self.data.get("paramInformation", {})

    @property
    def supports_zwave_plus(self) -> bool | None:
        """Return if the device complies with the Z-Wave+ standard."""
        return self.data.get("supportsZWavePlus")

    @property
    def proprietary(self) -> dict:
        """Return dictionary of settings for the proprietary CC."""
        return self.data.get("proprietary", {})

    @property
    def compat(self) -> dict[str, dict]:
        """Return compatibility flags."""
        return self.data.get("compat", {})

    @property
    def metadata(self) -> DeviceMetadata:
        """Return metadata."""
        return self._metadata

    @property
    def is_embedded(self) -> bool | None:
        """Return whether device config is embedded in zwave-js-server."""
        return self.data.get("isEmbedded")
