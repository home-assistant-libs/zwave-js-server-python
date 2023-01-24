"""Provide a model for Z-Wave controller firmware."""
from enum import IntEnum
from typing import TypedDict


class FirmwareUpdateStatus(IntEnum):
    """Enum with all controller firmware update status values.

    https://zwave-js.github.io/node-zwave-js/#/api/node?id=status
    """

    ERROR_TIMEOUT = 0
    # The maximum number of retry attempts for a firmware fragments were reached
    ERROR_RETRY_LIMIT_REACHED = 1
    # The update was aborted by the bootloader
    ERROR_ABORTED = 2
    OK = 255


class FirmwareUpdateProgressDataType(TypedDict):
    """Represent a controller firmware update progress dict type."""

    sentFragments: int
    totalFragments: int
    progress: float


class FirmwareUpdateProgress:
    """Model for a controller firmware update progress data."""

    def __init__(self, data: FirmwareUpdateProgressDataType) -> None:
        """Initialize."""
        self.data = data

    @property
    def sent_fragments(self) -> int:
        """Return the number of fragments sent to the device so far."""
        return self.data["sentFragments"]

    @property
    def total_fragments(self) -> int:
        """Return the total number of fragments that need to be sent to the device."""
        return self.data["totalFragments"]

    @property
    def progress(self) -> float:
        """Return progress."""
        return float(self.data["progress"])


class FirmwareUpdateResultDataType(TypedDict):
    """Represent a controller firmware update result dict type."""

    status: int
    success: bool


class FirmwareUpdateResult:
    """Model for controller firmware update result data."""

    def __init__(self, data: FirmwareUpdateResultDataType) -> None:
        """Initialize."""
        self.data = data

    @property
    def status(self) -> FirmwareUpdateStatus:
        """Return the firmware update status."""
        return FirmwareUpdateStatus(self.data["status"])

    @property
    def success(self) -> bool:
        """Return whether the firmware update was successful."""
        return self.data["success"]
