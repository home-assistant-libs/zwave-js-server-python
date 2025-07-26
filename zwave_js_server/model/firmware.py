"""Provide models for Z-Wave JS firmware."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import IntEnum
from typing import Literal, Required, TypedDict, cast

from zwave_js_server.const import RFRegion
from zwave_js_server.util.helpers import convert_bytes_to_base64


@dataclass
class FirmwareUpdateData:
    """Firmware update data."""

    filename: str
    file: bytes
    file_format: str | None = None

    def to_dict(self) -> FirmwareUpdateDataDataType:
        """Convert firmware update data to dict."""
        data: FirmwareUpdateDataDataType = {
            "filename": self.filename,
            "file": convert_bytes_to_base64(self.file),
        }
        if self.file_format is not None:
            data["fileFormat"] = self.file_format
        return data


class FirmwareUpdateDataDataType(TypedDict, total=False):
    """Represent a firmware update data dict type."""

    filename: Required[str]
    file: Required[str]
    fileFormat: str


@dataclass
class FirmwareUpdateInfo:
    """Represent a firmware update info."""

    version: str
    changelog: str
    channel: Literal["stable", "beta"]
    files: list[FirmwareUpdateFileInfo]
    downgrade: bool
    normalized_version: str
    device: FirmwareUpdateDeviceID

    @classmethod
    def from_dict(cls, data: FirmwareUpdateInfoDataType) -> FirmwareUpdateInfo:
        """Initialize from dict."""
        return cls(
            version=data["version"],
            changelog=data["changelog"],
            channel=data["channel"],
            files=[FirmwareUpdateFileInfo.from_dict(file) for file in data["files"]],
            downgrade=data["downgrade"],
            normalized_version=data["normalizedVersion"],
            device=FirmwareUpdateDeviceID.from_dict(data["device"]),
        )

    def to_dict(self) -> FirmwareUpdateInfoDataType:
        """Return dict representation of the object."""
        return cast(
            FirmwareUpdateInfoDataType,
            {
                "version": self.version,
                "changelog": self.changelog,
                "channel": self.channel,
                "files": [file.to_dict() for file in self.files],
                "downgrade": self.downgrade,
                "normalizedVersion": self.normalized_version,
                "device": self.device.to_dict(),
            },
        )


class FirmwareUpdateInfoDataType(TypedDict, total=False):
    """Represent a firmware update info data dict type."""

    version: str
    changelog: str
    channel: Literal["stable", "beta"]
    files: list[FirmwareUpdateFileInfoDataType]
    downgrade: bool
    normalizedVersion: str
    device: FirmwareUpdateDeviceIDDataType


@dataclass
class FirmwareUpdateDeviceID:
    """Represent a firmware update device ID."""

    manufacturer_id: int
    product_type: int
    product_id: int
    firmware_version: str
    rf_region: RFRegion | None

    @classmethod
    def from_dict(cls, data: FirmwareUpdateDeviceIDDataType) -> FirmwareUpdateDeviceID:
        """Initialize from dict."""
        return cls(
            manufacturer_id=data["manufacturerId"],
            product_type=data["productType"],
            product_id=data["productId"],
            firmware_version=data["firmwareVersion"],
            rf_region=RFRegion(data["rfRegion"]) if "rfRegion" in data else None,
        )

    def to_dict(self) -> FirmwareUpdateDeviceIDDataType:
        """Return dict representation of the object."""
        data = {
            "manufacturerId": self.manufacturer_id,
            "productType": self.product_type,
            "productId": self.product_id,
            "firmwareVersion": self.firmware_version,
        }
        if self.rf_region is not None:
            data["rfRegion"] = self.rf_region
        return cast(FirmwareUpdateDeviceIDDataType, data)


class FirmwareUpdateDeviceIDDataType(TypedDict, total=False):
    """Represent a firmware update device ID dict type."""

    manufacturerId: Required[int]
    productType: Required[int]
    productId: Required[int]
    firmwareVersion: Required[str]
    rfRegion: int


@dataclass
class FirmwareUpdateFileInfo:
    """Represent a firmware update file info."""

    target: int
    url: str
    integrity: str

    @classmethod
    def from_dict(cls, data: FirmwareUpdateFileInfoDataType) -> FirmwareUpdateFileInfo:
        """Initialize from dict."""
        return cls(
            target=data["target"],
            url=data["url"],
            integrity=data["integrity"],
        )

    def to_dict(self) -> FirmwareUpdateFileInfoDataType:
        """Return dict representation of the object."""
        return cast(FirmwareUpdateFileInfoDataType, asdict(self))


class FirmwareUpdateFileInfoDataType(TypedDict):
    """Represent a firmware update file info data dict type."""

    target: int
    url: str
    integrity: str  # sha256


@dataclass
class FirmwareUpdateProgress:
    """Model for a firmware update progress."""

    data: FirmwareUpdateProgressDataType = field(repr=False)
    sent_fragments: int = field(init=False)
    total_fragments: int = field(init=False)
    progress: float = field(init=False)

    def __post_init__(self) -> None:
        """Post initialize."""
        self.sent_fragments = self.data["sentFragments"]
        self.total_fragments = self.data["totalFragments"]
        self.progress = float(self.data["progress"])


class FirmwareUpdateProgressDataType(TypedDict):
    """Represent a firmware update progress dict type."""

    sentFragments: int
    totalFragments: int
    progress: float


@dataclass
class FirmwareUpdateResult:
    """Model for firmware update result data."""

    data: FirmwareUpdateResultDataType = field(repr=False)
    status: IntEnum = field(init=False)
    success: bool = field(init=False)
    _status_class: type[IntEnum] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Post initialize."""
        self.status = self._status_class(self.data["status"])
        self.success = self.data["success"]


class FirmwareUpdateResultDataType(TypedDict):
    """Represent a driver firmware update result dict type."""

    status: int
    success: bool
