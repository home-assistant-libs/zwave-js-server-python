"""
Model for a Zwave Node's device class.

https://zwave-js.github.io/node-zwave-js/#/api/node?id=deviceclass
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict


class DeviceClassItemDataType(TypedDict):
    """Represent a device class data dict type."""

    key: int
    label: str


class DeviceClassDataType(TypedDict):
    """Represent a device class data dict type."""

    basic: DeviceClassItemDataType
    generic: DeviceClassItemDataType
    specific: DeviceClassItemDataType
    mandatorySupportedCCs: list[int]
    mandatoryControlledCCs: list[int]


@dataclass
class DeviceClassItem:
    """Model for a DeviceClass item (e.g. basic or generic)."""

    key: int
    label: str


class DeviceClass:
    """Model for a Zwave Node's device class."""

    def __init__(self, data: DeviceClassDataType | None) -> None:
        """Initialize."""
        self.data = data

    @property
    def basic(self) -> DeviceClassItem | None:
        """Return basic DeviceClass."""
        if self.data and "basic" in self.data:
            return DeviceClassItem(**self.data["basic"])
        return None

    @property
    def generic(self) -> DeviceClassItem | None:
        """Return generic DeviceClass."""
        if self.data and "generic" in self.data:
            return DeviceClassItem(**self.data["generic"])
        return None

    @property
    def specific(self) -> DeviceClassItem | None:
        """Return specific DeviceClass."""
        if self.data and "specific" in self.data:
            return DeviceClassItem(**self.data["specific"])
        return None

    @property
    def mandatory_supported_ccs(self) -> list[int]:
        """Return list of mandatory Supported CC id's."""
        if self.data and "mandatorySupportedCCs" in self.data:
            return self.data["mandatorySupportedCCs"]
        return []

    @property
    def mandatory_controlled_ccs(self) -> list[int]:
        """Return list of mandatory Controlled CC id's."""
        if self.data and "mandatoryControlledCCs" in self.data:
            return self.data["mandatoryControlledCCs"]
        return []
