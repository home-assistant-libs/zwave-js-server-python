"""Provide a model for Z-Wave controller firmware."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import TypedDict

from ...util.helpers import convert_bytes_to_base64


class ControllerFirmwareUpdateDataDataType(TypedDict, total=False):
    """Represent a controller firmware update data dict type."""

    filename: str  # required
    file: str  # required
    fileFormat: str


@dataclass
class ControllerFirmwareUpdateData:
    """Controller firmware update data."""

    filename: str
    file: bytes
    file_format: str | None = None

    def to_dict(self) -> ControllerFirmwareUpdateDataDataType:
        """Convert firmware update data to dict."""
        data: ControllerFirmwareUpdateDataDataType = {
            "filename": self.filename,
            "file": convert_bytes_to_base64(self.file),
        }
        if self.file_format is not None:
            data["fileFormat"] = self.file_format
        return data


class ControllerFirmwareUpdateStatus(IntEnum):
    """Enum with all controller firmware update status values.

    https://zwave-js.github.io/node-zwave-js/#/api/controller?id=quotfirmware-update-finishedquot
    """

    ERROR_TIMEOUT = 0
    # The maximum number of retry attempts for a firmware fragments were reached
    ERROR_RETRY_LIMIT_REACHED = 1
    # The update was aborted by the bootloader
    ERROR_ABORTED = 2
    # This controller does not support firmware updates
    ERROR_NOT_SUPPORTED = 3
    OK = 255


class ControllerFirmwareUpdateProgressDataType(TypedDict):
    """Represent a controller firmware update progress dict type."""

    sentFragments: int
    totalFragments: int
    progress: float


@dataclass
class ControllerFirmwareUpdateProgress:
    """Model for a controller firmware update progress data."""

    data: ControllerFirmwareUpdateProgressDataType = field(repr=False)
    sent_fragments: int = field(init=False)
    total_fragments: int = field(init=False)
    progress: float = field(init=False)

    def __post_init__(self) -> None:
        """Post initialize."""
        self.sent_fragments = self.data["sentFragments"]
        self.total_fragments = self.data["totalFragments"]
        self.progress = float(self.data["progress"])


class ControllerFirmwareUpdateResultDataType(TypedDict):
    """Represent a controller firmware update result dict type."""

    status: int
    success: bool


@dataclass
class ControllerFirmwareUpdateResult:
    """Model for controller firmware update result data."""

    data: ControllerFirmwareUpdateResultDataType = field(repr=False)
    status: ControllerFirmwareUpdateStatus = field(init=False)
    success: bool = field(init=False)

    def __post_init__(self) -> None:
        """Post initialize."""
        self.status = ControllerFirmwareUpdateStatus(self.data["status"])
        self.success = self.data["success"]
