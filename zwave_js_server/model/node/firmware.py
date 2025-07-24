"""Provide a model for Z-Wave firmware."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import TYPE_CHECKING, TypedDict

from ...const import VALUE_UNKNOWN
from ...util.helpers import convert_bytes_to_base64

if TYPE_CHECKING:
    from . import Node


class NodeFirmwareUpdateDataDataType(TypedDict, total=False):
    """Represent a firmware update data dict type."""

    filename: str  # required
    file: str  # required
    fileFormat: str
    firmwareTarget: int


@dataclass
class NodeFirmwareUpdateData:
    """Firmware update data."""

    filename: str
    file: bytes
    file_format: str | None = None
    firmware_target: int | None = None

    def to_dict(self) -> NodeFirmwareUpdateDataDataType:
        """Convert firmware update data to dict."""
        data: NodeFirmwareUpdateDataDataType = {
            "filename": self.filename,
            "file": convert_bytes_to_base64(self.file),
        }
        if self.file_format is not None:
            data["fileFormat"] = self.file_format
        if self.firmware_target is not None:
            data["firmwareTarget"] = self.firmware_target
        return data


class NodeFirmwareUpdateCapabilitiesDataType(TypedDict, total=False):
    """Represent a firmware update capabilities dict type."""

    firmwareUpgradable: bool  # required
    firmwareTargets: list[int]
    continuesToFunction: bool | str
    supportsActivation: bool | str


class NodeFirmwareUpdateCapabilitiesDict(TypedDict, total=False):
    """Represent a dict from FirmwareUpdateCapabilities."""

    firmware_upgradable: bool  # required
    firmware_targets: list[int]
    continues_to_function: bool | None
    supports_activation: bool | None


@dataclass
class NodeFirmwareUpdateCapabilities:
    """Model for firmware update capabilities."""

    data: NodeFirmwareUpdateCapabilitiesDataType = field(repr=False)
    firmware_upgradable: bool = field(init=False)

    def __post_init__(self) -> None:
        """Post initialize."""
        self.firmware_upgradable = self.data["firmwareUpgradable"]

    @property
    def firmware_targets(self) -> list[int]:
        """Return firmware targets."""
        if not self.firmware_upgradable:
            raise TypeError("Firmware is not upgradeable.")
        return self.data["firmwareTargets"]

    @property
    def continues_to_function(self) -> bool | None:
        """Return whether node continues to function during update."""
        if not self.firmware_upgradable:
            raise TypeError("Firmware is not upgradeable.")
        if (val := self.data["continuesToFunction"]) == VALUE_UNKNOWN:
            return None
        assert isinstance(val, bool)
        return val

    @property
    def supports_activation(self) -> bool | None:
        """Return whether node supports delayed activation of the new firmware."""
        if not self.firmware_upgradable:
            raise TypeError("Firmware is not upgradeable.")
        if (val := self.data["supportsActivation"]) == VALUE_UNKNOWN:
            return None
        assert isinstance(val, bool)
        return val

    def to_dict(self) -> NodeFirmwareUpdateCapabilitiesDict:
        """Return dict representation of the object."""
        if not self.firmware_upgradable:
            return {"firmware_upgradable": self.firmware_upgradable}
        return {
            "firmware_upgradable": self.firmware_upgradable,
            "firmware_targets": self.firmware_targets,
            "continues_to_function": self.continues_to_function,
            "supports_activation": self.supports_activation,
        }


class NodeFirmwareUpdateStatus(IntEnum):
    """Enum with all node firmware update status values.

    https://zwave-js.github.io/node-zwave-js/#/api/node?id=quotfirmware-update-finishedquot
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


class NodeFirmwareUpdateProgressDataType(TypedDict):
    """Represent a node firmware update progress dict type."""

    currentFile: int
    totalFiles: int
    sentFragments: int
    totalFragments: int
    progress: float


@dataclass
class NodeFirmwareUpdateProgress:
    """Model for a node firmware update progress data."""

    node: Node
    data: NodeFirmwareUpdateProgressDataType = field(repr=False)
    current_file: int = field(init=False)
    total_files: int = field(init=False)
    sent_fragments: int = field(init=False)
    total_fragments: int = field(init=False)
    progress: float = field(init=False)

    def __post_init__(self) -> None:
        """Post initialize."""
        self.current_file = self.data["currentFile"]
        self.total_files = self.data["totalFiles"]
        self.sent_fragments = self.data["sentFragments"]
        self.total_fragments = self.data["totalFragments"]
        self.progress = float(self.data["progress"])


class NodeFirmwareUpdateResultDataType(TypedDict, total=False):
    """Represent a node firmware update result dict type."""

    status: int  # required
    success: bool  # required
    waitTime: int
    reInterview: bool  # required


@dataclass
class NodeFirmwareUpdateResult:
    """Model for node firmware update result data."""

    node: Node
    data: NodeFirmwareUpdateResultDataType = field(repr=False)
    status: NodeFirmwareUpdateStatus = field(init=False)
    success: bool = field(init=False)
    wait_time: int | None = field(init=False)
    reinterview: bool = field(init=False)

    def __post_init__(self) -> None:
        """Post initialize."""
        self.status = NodeFirmwareUpdateStatus(self.data["status"])
        self.success = self.data["success"]
        self.wait_time = self.data.get("waitTime")
        self.reinterview = self.data["reInterview"]
