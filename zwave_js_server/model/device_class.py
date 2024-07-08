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


@dataclass
class DeviceClassItem:
    """Model for a DeviceClass item (e.g. basic or generic)."""

    key: int
    label: str


class DeviceClass:
    """Model for a Zwave Node's device class."""

    def __init__(self, data: DeviceClassDataType) -> None:
        """Initialize."""
        self._basic = DeviceClassItem(
            key=data["basic"]["key"],
            label=data["basic"]["label"],
        )
        self._generic = DeviceClassItem(
            key=data["generic"]["key"],
            label=data["generic"]["label"],
        )
        self._specific = DeviceClassItem(
            key=data["specific"]["key"],
            label=data["specific"]["label"],
        )

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
