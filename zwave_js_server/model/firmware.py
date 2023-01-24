"""Provide a model for Z-Wave firmware."""
from dataclasses import dataclass
from typing import Optional

from ..const import TYPING_EXTENSION_FOR_TYPEDDICT_REQUIRED
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
