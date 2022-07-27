"""Provide a model for Z-Wave firmware."""
from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING, List, Optional, Union

from ..const import TYPING_EXTENSION_FOR_TYPEDDICT_REQUIRED, VALUE_UNKNOWN

if TYPING_EXTENSION_FOR_TYPEDDICT_REQUIRED:
    from typing_extensions import TypedDict
else:
    from typing import TypedDict

if TYPE_CHECKING:
    from .node import Node


class FirmwareUpdateCapabilitiesDataType(TypedDict, total=False):
    """Represent a firmware update capabilities dict type."""

    firmwareUpgradable: bool  # required
    firmwareTargets: List[int]
    continuesToFunction: Union[bool, str]
    supportsActivation: Union[bool, str]


class FirmwareUpdateCapabilitiesDict(TypedDict, total=False):
    """Represent a dict from FirmwareUpdateCapabilities."""

    firmware_upgradable: bool  # required
    firmware_targets: List[int]
    continues_to_function: Optional[bool]
    supports_activation: Optional[bool]


class FirmwareUpdateCapabilities:
    """Model for firmware update capabilities."""

    def __init__(self, data: FirmwareUpdateCapabilitiesDataType) -> None:
        """Initialize class."""
        self.data = data

    @property
    def firmware_upgradable(self) -> bool:
        """Return whether firmware is upgradable."""
        return self.data["firmwareUpgradable"]

    @property
    def firmware_targets(self) -> List[int]:
        """Return firmware targets."""
        if not self.firmware_upgradable:
            raise TypeError("Firmware is not upgradeable.")
        return self.data["firmwareTargets"]

    @property
    def continues_to_function(self) -> Optional[bool]:
        """Return whether node continues to function during update."""
        if not self.firmware_upgradable:
            raise TypeError("Firmware is not upgradeable.")
        if (val := self.data["continuesToFunction"]) == VALUE_UNKNOWN:
            return None
        assert isinstance(val, bool)
        return val

    @property
    def supports_activation(self) -> Optional[bool]:
        """Return whether node supports delayed activation of the new firmware."""
        if not self.firmware_upgradable:
            raise TypeError("Firmware is not upgradeable.")
        if (val := self.data["supportsActivation"]) == VALUE_UNKNOWN:
            return None
        assert isinstance(val, bool)
        return val

    def to_dict(self) -> FirmwareUpdateCapabilitiesDict:
        """Return dict representation of the object."""
        if not self.firmware_upgradable:
            return {"firmware_upgradable": self.firmware_upgradable}
        return {
            "firmware_upgradable": self.firmware_upgradable,
            "firmware_targets": self.firmware_targets,
            "continues_to_function": self.continues_to_function,
            "supports_activation": self.supports_activation,
        }


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


class FirmwareUpdateFileInfoDataType(TypedDict):
    """Represent a firmware update file info data dict type."""

    target: int
    url: str
    integrity: str  # sha256


@dataclass
class FirmwareUpdateFileInfo:
    """Represent a firmware update file info."""

    target: int
    url: str
    integrity: str


class FirmwareUpdateInfoDataType(TypedDict):
    """Represent a firmware update info data dict type."""

    version: str
    changelog: str
    files: List[FirmwareUpdateFileInfoDataType]


@dataclass
class FirmwareUpdateInfo:
    """Represent a firmware update info."""

    version: str
    changelog: str
    files: List[FirmwareUpdateFileInfo]

    @classmethod
    def from_dict(cls, data: FirmwareUpdateInfoDataType) -> "FirmwareUpdateInfo":
        """Initialize from dict."""
        return cls(
            version=data["version"],
            changelog=data["changelog"],
            files=[FirmwareUpdateFileInfo(**file) for file in data["files"]],
        )
