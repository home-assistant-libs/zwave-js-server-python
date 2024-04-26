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

    def __init__(self, data: DeviceClassDataType) -> None:
        """Initialize."""
        self._basic = DeviceClassItem(**data["basic"])
        self._generic = DeviceClassItem(**data["generic"])
        self._specific = DeviceClassItem(**data["specific"])
        self._mandatory_supported_ccs: list[int] = data["mandatorySupportedCCs"]
        self._mandatory_controlled_ccs: list[int] = data["mandatoryControlledCCs"]

    @property
    def basic(self) -> DeviceClassItem:
        """Return basic DeviceClass."""
        return self._basic

    @property
    def generic(self) -> DeviceClassItem:
        """Return generic DeviceClass."""
        return self._generic

    @property
    def specific(self) -> DeviceClassItem:
        """Return specific DeviceClass."""
        return self._specific

    @property
    def mandatory_supported_ccs(self) -> list[int]:
        """Return list of mandatory Supported CC id's."""
        return self._mandatory_supported_ccs

    @property
    def mandatory_controlled_ccs(self) -> list[int]:
        """Return list of mandatory Controlled CC id's."""
        return self._mandatory_controlled_ccs
