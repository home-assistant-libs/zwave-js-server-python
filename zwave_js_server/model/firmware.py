"""Provide a model for Z-Wave firmware."""
from dataclasses import asdict, dataclass
from typing import List, Optional, Union, cast

from ..const import TYPING_EXTENSION_FOR_TYPEDDICT_REQUIRED, VALUE_UNKNOWN
from ..util.helpers import convert_bytes_to_base64

if TYPING_EXTENSION_FOR_TYPEDDICT_REQUIRED:
    from typing_extensions import TypedDict
else:
    from typing import TypedDict


class FirmwareUpdateDataDataType(TypedDict, total=False):
    """Represent a firmware update data dict type."""

    filename: str  # required
    file: str  # required
    fileFormat: str


@dataclass
class FirmwareUpdateData:
    """Firmware update data."""

    filename: str
    file: bytes
    file_format: Optional[str] = None

    def to_dict(self) -> FirmwareUpdateDataDataType:
        """Convert firmware update data to dict."""
        data: FirmwareUpdateDataDataType = {
            "filename": self.filename,
            "file": convert_bytes_to_base64(self.file),
        }
        if self.file_format is not None:
            data["fileFormat"] = self.file_format
        return data


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

    def to_dict(self) -> FirmwareUpdateFileInfoDataType:
        """Return dict representation of the object."""
        return cast(FirmwareUpdateFileInfoDataType, asdict(self))


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
