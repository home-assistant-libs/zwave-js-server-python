"""
Model for a Zwave Node's device class.

https://zwave-js.github.io/node-zwave-js/#/api/node?id=deviceclass
"""

from dataclasses import dataclass
from typing import List, TypedDict


class DeviceClassItemDataType(TypedDict):
    """Represent a device class data dict type."""

    key: int
    label: str


class DeviceClassDataType(TypedDict):
    """Represent a device class data dict type."""

    basic: DeviceClassItemDataType
    generic: DeviceClassItemDataType
    specific: DeviceClassItemDataType
    mandatorySupportedCCs: List[int]
    mandatoryControlledCCs: List[int]


@dataclass
class DeviceClassItem:
    """Model for a DeviceClass item (e.g. basic or generic)."""

    key: int
    label: str


class DeviceClass:
    """Model for a Zwave Node's device class."""

    def __init__(self, data: DeviceClassDataType) -> None:
        """Initialize."""
        self.data = data

    @property
    def basic(self) -> DeviceClassItem:
        """Return basic DeviceClass."""
        return DeviceClassItem(**self.data["basic"])

    @property
    def generic(self) -> DeviceClassItem:
        """Return generic DeviceClass."""
        return DeviceClassItem(**self.data["generic"])

    @property
    def specific(self) -> DeviceClassItem:
        """Return specific DeviceClass."""
        return DeviceClassItem(**self.data["specific"])

    @property
    def mandatory_supported_ccs(self) -> List[int]:
        """Return list of mandatory Supported CC id's."""
        return self.data["mandatorySupportedCCs"]

    @property
    def mandatory_controlled_ccs(self) -> List[int]:
        """Return list of mandatory Controlled CC id's."""
        return self.data["mandatoryControlledCCs"]
