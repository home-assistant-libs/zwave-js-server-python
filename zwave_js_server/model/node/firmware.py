"""Provide a model for Z-Wave firmware."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import TYPE_CHECKING, Required, TypedDict, cast

from zwave_js_server.model.firmware import (
    FirmwareUpdateData,
    FirmwareUpdateDataDataType,
    FirmwareUpdateDeviceID,
    FirmwareUpdateDeviceIDDataType,
    FirmwareUpdateFileInfo,
    FirmwareUpdateFileInfoDataType,
    FirmwareUpdateInfo,
    FirmwareUpdateInfoDataType,
    FirmwareUpdateProgress,
    FirmwareUpdateProgressDataType,
    FirmwareUpdateResult,
    FirmwareUpdateResultDataType,
)

from ...const import VALUE_UNKNOWN

if TYPE_CHECKING:
    from . import Node


class NodeFirmwareUpdateDataDataType(FirmwareUpdateDataDataType):
    """Represent a firmware update data dict type."""

    firmwareTarget: int


@dataclass
class NodeFirmwareUpdateData(FirmwareUpdateData):
    """Firmware update data."""

    firmware_target: int | None = None

    def to_dict(self) -> NodeFirmwareUpdateDataDataType:
        """Convert firmware update data to dict."""
        data = super().to_dict()
        node_data = cast(NodeFirmwareUpdateDataDataType, data)
        if self.firmware_target is not None:
            node_data["firmwareTarget"] = self.firmware_target
        return node_data


class NodeFirmwareUpdateCapabilitiesDataType(TypedDict, total=False):
    """Represent a firmware update capabilities dict type."""

    firmwareUpgradable: Required[bool]
    firmwareTargets: list[int]
    continuesToFunction: bool | str
    supportsActivation: bool | str


class NodeFirmwareUpdateCapabilitiesDict(TypedDict, total=False):
    """Represent a dict from FirmwareUpdateCapabilities."""

    firmware_upgradable: Required[bool]
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


class NodeFirmwareUpdateProgressDataType(FirmwareUpdateProgressDataType):
    """Represent a node firmware update progress dict type."""

    currentFile: int
    totalFiles: int


@dataclass
class NodeFirmwareUpdateProgress(FirmwareUpdateProgress):
    """Model for a node firmware update progress data."""

    node: Node
    data: NodeFirmwareUpdateProgressDataType = field(repr=False)
    current_file: int = field(init=False)
    total_files: int = field(init=False)

    def __init__(self, node: Node, data: NodeFirmwareUpdateProgressDataType) -> None:
        """Initialize the node firmware update progress.

        Explicit init method to retain backwards compatibility
        that requires the node as first parameter.
        """
        super().__init__(data)
        self.node = node

    def __post_init__(self) -> None:
        """Post initialize."""
        super().__post_init__()
        self.current_file = self.data["currentFile"]
        self.total_files = self.data["totalFiles"]


class NodeFirmwareUpdateResultDataType(FirmwareUpdateResultDataType, total=False):
    """Represent a node firmware update result dict type."""

    waitTime: int
    reInterview: Required[bool]


@dataclass
class NodeFirmwareUpdateResult(FirmwareUpdateResult):
    """Model for node firmware update result data."""

    node: Node
    data: NodeFirmwareUpdateResultDataType = field(repr=False)
    status: NodeFirmwareUpdateStatus = field(init=False)
    wait_time: int | None = field(init=False)
    reinterview: bool = field(init=False)
    _status_class = NodeFirmwareUpdateStatus

    def __init__(self, node: Node, data: NodeFirmwareUpdateResultDataType) -> None:
        """Initialize the node firmware update result.

        Explicit init method to retain backwards compatibility
        that requires the node as first parameter.
        """
        super().__init__(data)
        self.node = node

    def __post_init__(self) -> None:
        """Post initialize."""
        super().__post_init__()
        self.wait_time = self.data.get("waitTime")
        self.reinterview = self.data["reInterview"]


class NodeFirmwareUpdateFileInfoDataType(FirmwareUpdateFileInfoDataType):
    """Represent a node firmware update file info data dict type."""


@dataclass
class NodeFirmwareUpdateFileInfo(FirmwareUpdateFileInfo):
    """Represent a firmware update file info."""

    @classmethod
    def from_dict(
        cls, data: NodeFirmwareUpdateFileInfoDataType
    ) -> NodeFirmwareUpdateFileInfo:
        """Initialize from dict."""
        return cast(NodeFirmwareUpdateFileInfo, super().from_dict(data))

    def to_dict(self) -> NodeFirmwareUpdateFileInfoDataType:
        """Return dict representation of the object."""
        return super().to_dict()


class NodeFirmwareUpdateDeviceIDDataType(FirmwareUpdateDeviceIDDataType):
    """Represent a node firmware update device ID data dict type."""


@dataclass
class NodeFirmwareUpdateDeviceID(FirmwareUpdateDeviceID):
    """Represent a firmware update device ID."""

    @classmethod
    def from_dict(
        cls, data: NodeFirmwareUpdateDeviceIDDataType
    ) -> NodeFirmwareUpdateDeviceID:
        """Initialize from dict."""
        return cast(NodeFirmwareUpdateDeviceID, super().from_dict(data))

    def to_dict(self) -> NodeFirmwareUpdateDeviceIDDataType:
        """Return dict representation of the object."""
        return super().to_dict()


class NodeFirmwareUpdateInfoDataType(FirmwareUpdateInfoDataType):
    """Represent a node firmware update info data dict type."""


@dataclass
class NodeFirmwareUpdateInfo(FirmwareUpdateInfo):
    """Represent a firmware update info."""

    @classmethod
    def from_dict(cls, data: NodeFirmwareUpdateInfoDataType) -> NodeFirmwareUpdateInfo:
        """Initialize from dict."""
        return cast(NodeFirmwareUpdateInfo, super().from_dict(data))

    def to_dict(self) -> NodeFirmwareUpdateInfoDataType:
        """Return dict representation of the object."""
        return super().to_dict()
