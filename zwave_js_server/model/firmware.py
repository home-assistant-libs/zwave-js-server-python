"""Provide a model for Z-Wave firmware."""
from enum import IntEnum
from typing import TYPE_CHECKING, Optional, TypedDict

if TYPE_CHECKING:
    from .node import Node


class FirmwareUpdateStatus(IntEnum):
    """Enum with all Firmware update status values.

    https://zwave-js.github.io/node-zwave-js/#/api/node?id=status
    """

    ERROR_TIMEOUT = -1
    ERROR_CHECKSUM = 0
    ERROR_TRANSMISSION_FAILED = 1
    ERROR_INVALID_MANUFACTURER_ID = 2
    ERROR_INVALID_FIRMWARE_ID = 3
    ERROR_INVALID_FIRMWARE_TARGET = 4
    ERROR_INVALID_HEADER_INFORMATION = 5
    ERROR_INVALID_HEADER_FORMAT = 6
    ERROR_INSUFFICIENT_MEMORY = 7
    ERROR_INVALID_HARDWARE_VERSION = 8
    OK_WAITING_FOR_ACTIVATION = 253
    OK_NO_RESTART = 254
    OK_RESTART_PENDING = 255


class FirmwareUpdateProgressDataType(TypedDict):
    """Represent a firmware update progress event dict type."""

    sentFragments: int  # required
    totalFragments: int  # required


class FirmwareUpdateProgress:
    """Model for firmware update progress event."""

    def __init__(self, node: "Node", data: FirmwareUpdateProgressDataType) -> None:
        """Initialize."""
        self.data = data
        self.node = node

    @property
    def sent_fragments(self) -> int:
        """Return the number of fragments sent to the device so far."""
        return self.data["sentFragments"]

    @property
    def total_fragments(self) -> int:
        """Return the total number of fragments that need to be sent to the device."""
        return self.data["totalFragments"]


class FirmwareUpdateFinishedDataType(TypedDict, total=False):
    """Represent a firmware update finished event dict type."""

    status: int  # required
    waitTime: int


class FirmwareUpdateFinished:
    """Model for firmware update finished event."""

    def __init__(self, node: "Node", data: FirmwareUpdateFinishedDataType) -> None:
        """Initialize."""
        self.data = data
        self.node = node

    @property
    def status(self) -> FirmwareUpdateStatus:
        """Return the firmware update status."""
        return FirmwareUpdateStatus(self.data["status"])

    @property
    def wait_time(self) -> Optional[int]:
        """Return the wait time in seconds before the device is functional again."""
        return self.data.get("waitTime")
