"""Provide a model for Z-Wave driver firmware."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import TypedDict

from ...util.helpers import convert_bytes_to_base64


class DriverFirmwareUpdateDataDataType(TypedDict, total=False):
    """Represent a driver firmware update data dict type."""

    filename: str  # required
    file: str  # required
    fileFormat: str


@dataclass
class DriverFirmwareUpdateData:
    """Driver firmware update data."""

    filename: str
    file: bytes
    file_format: str | None = None

    def to_dict(self) -> DriverFirmwareUpdateDataDataType:
        """Convert firmware update data to dict."""
        data: DriverFirmwareUpdateDataDataType = {
            "filename": self.filename,
            "file": convert_bytes_to_base64(self.file),
        }
        if self.file_format is not None:
            data["fileFormat"] = self.file_format
        return data


class DriverFirmwareUpdateStatus(IntEnum):
    """Enum with all driver firmware update status values.

    https://zwave-js.github.io/node-zwave-js/#/api/driver?id=quotfirmware-update-finishedquot
    """

    ERROR_TIMEOUT = 0
    # The maximum number of retry attempts for a firmware fragments were reached
    ERROR_RETRY_LIMIT_REACHED = 1
    # The update was aborted by the bootloader
    ERROR_ABORTED = 2
    # This driver does not support firmware updates
    ERROR_NOT_SUPPORTED = 3
    OK = 255


class DriverFirmwareUpdateProgressDataType(TypedDict):
    """Represent a driver firmware update progress dict type."""

    sentFragments: int
    totalFragments: int
    progress: float


@dataclass
class DriverFirmwareUpdateProgress:
    """Model for a driver firmware update progress data."""

    data: DriverFirmwareUpdateProgressDataType = field(repr=False)
    sent_fragments: int = field(init=False)
    total_fragments: int = field(init=False)
    progress: float = field(init=False)

    def __post_init__(self) -> None:
        """Post initialize."""
        self.sent_fragments = self.data["sentFragments"]
        self.total_fragments = self.data["totalFragments"]
        self.progress = float(self.data["progress"])


class DriverFirmwareUpdateResultDataType(TypedDict):
    """Represent a driver firmware update result dict type."""

    status: int
    success: bool


@dataclass
class DriverFirmwareUpdateResult:
    """Model for driver firmware update result data."""

    data: DriverFirmwareUpdateResultDataType = field(repr=False)
    status: DriverFirmwareUpdateStatus = field(init=False)
    success: bool = field(init=False)

    def __post_init__(self) -> None:
        """Post initialize."""
        self.status = DriverFirmwareUpdateStatus(self.data["status"])
        self.success = self.data["success"]
