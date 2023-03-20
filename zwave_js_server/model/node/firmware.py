"""Provide a model for Z-Wave firmware."""
from dataclasses import asdict, dataclass
from enum import IntEnum
from typing import TYPE_CHECKING, Optional, TypedDict, Union, cast

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
    file_format: Optional[str] = None
    firmware_target: Optional[int] = None

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
    continuesToFunction: Union[bool, str]
    supportsActivation: Union[bool, str]


class NodeFirmwareUpdateCapabilitiesDict(TypedDict, total=False):
    """Represent a dict from FirmwareUpdateCapabilities."""

    firmware_upgradable: bool  # required
    firmware_targets: list[int]
    continues_to_function: Optional[bool]
    supports_activation: Optional[bool]


class NodeFirmwareUpdateCapabilities:
    """Model for firmware update capabilities."""

    def __init__(self, data: NodeFirmwareUpdateCapabilitiesDataType) -> None:
        """Initialize class."""
        self.data = data

    @property
    def firmware_upgradable(self) -> bool:
        """Return whether firmware is upgradable."""
        return self.data["firmwareUpgradable"]

    @property
    def firmware_targets(self) -> list[int]:
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


class NodeFirmwareUpdateProgress:
    """Model for a node firmware update progress data."""

    def __init__(self, node: "Node", data: NodeFirmwareUpdateProgressDataType) -> None:
        """Initialize."""
        self.data = data
        self.node = node

    @property
    def current_file(self) -> int:
        """Return current file."""
        return self.data["currentFile"]

    @property
    def total_files(self) -> int:
        """Return total files."""
        return self.data["totalFiles"]

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


class NodeFirmwareUpdateResultDataType(TypedDict, total=False):
    """Represent a node firmware update result dict type."""

    status: int  # required
    success: bool  # required
    waitTime: int
    reInterview: bool  # required


class NodeFirmwareUpdateResult:
    """Model for node firmware update result data."""

    def __init__(self, node: "Node", data: NodeFirmwareUpdateResultDataType) -> None:
        """Initialize."""
        self.data = data
        self.node = node

    @property
    def status(self) -> NodeFirmwareUpdateStatus:
        """Return the firmware update status."""
        return NodeFirmwareUpdateStatus(self.data["status"])

    @property
    def success(self) -> bool:
        """Return whether the firmware update was successful."""
        return self.data["success"]

    @property
    def wait_time(self) -> Optional[int]:
        """Return the wait time in seconds before the device is functional again."""
        return self.data.get("waitTime")

    @property
    def reinterview(self) -> bool:
        """Return whether the node will be re-interviewed."""
        return self.data["reInterview"]


class NodeFirmwareUpdateFileInfoDataType(TypedDict):
    """Represent a firmware update file info data dict type."""

    target: int
    url: str
    integrity: str  # sha256


@dataclass
class NodeFirmwareUpdateFileInfo:
    """Represent a firmware update file info."""

    target: int
    url: str
    integrity: str

    @classmethod
    def from_dict(
        cls, data: NodeFirmwareUpdateFileInfoDataType
    ) -> "NodeFirmwareUpdateFileInfo":
        """Initialize from dict."""
        return cls(**data)

    def to_dict(self) -> NodeFirmwareUpdateFileInfoDataType:
        """Return dict representation of the object."""
        return cast(NodeFirmwareUpdateFileInfoDataType, asdict(self))


class NodeFirmwareUpdateInfoDataType(TypedDict):
    """Represent a firmware update info data dict type."""

    version: str
    changelog: str
    files: list[NodeFirmwareUpdateFileInfoDataType]


@dataclass
class NodeFirmwareUpdateInfo:
    """Represent a firmware update info."""

    version: str
    changelog: str
    files: list[NodeFirmwareUpdateFileInfo]

    @classmethod
    def from_dict(
        cls, data: NodeFirmwareUpdateInfoDataType
    ) -> "NodeFirmwareUpdateInfo":
        """Initialize from dict."""
        return cls(
            version=data["version"],
            changelog=data["changelog"],
            files=[
                NodeFirmwareUpdateFileInfo.from_dict(file) for file in data["files"]
            ],
        )

    def to_dict(self) -> NodeFirmwareUpdateInfoDataType:
        """Return dict representation of the object."""
        return cast(
            NodeFirmwareUpdateInfoDataType,
            {
                "version": self.version,
                "changelog": self.changelog,
                "files": [file.to_dict() for file in self.files],
            },
        )
