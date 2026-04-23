"""Data model for a Z-Wave JS controller."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, TypedDict

from .statistics import ControllerStatisticsDataType

if TYPE_CHECKING:
    from ..node import Node


class ZWaveApiVersionDataType(TypedDict):
    """Represent a Z-Wave API version (schema 47+)."""

    kind: Literal["official", "legacy"]
    version: int


class UnknownZWaveChipTypeDataType(TypedDict):
    """Represent an unknown Z-Wave chip type descriptor (schema 47+)."""

    type: int
    version: int


@dataclass(frozen=True)
class ZWaveChipType:
    """Z-Wave chip type descriptor (schema 47+).

    For known chips, `name` is set (e.g. ``"ZW0700"``).
    For unknown chips, `type` and `version` are set instead.
    """

    name: str | None = None
    type: int | None = None
    version: int | None = None

    @classmethod
    def from_dict(cls, data: str | UnknownZWaveChipTypeDataType) -> ZWaveChipType:
        """Initialize from dict."""
        if isinstance(data, str):
            return cls(name=data)
        return cls(type=data["type"], version=data["version"])


@dataclass(frozen=True)
class Route:
    """A Z-Wave routing instruction specifying repeaters and speed."""

    repeaters: list[Node]
    route_speed: int

    def to_dict(self) -> dict[str, Any]:
        """Return wire-format dict."""
        return {
            "repeaters": [n.node_id for n in self.repeaters],
            "routeSpeed": self.route_speed,
        }

    @classmethod
    def from_dict(cls, data: dict, nodes: dict[int, Node]) -> Route:
        """Initialize from wire-format dict."""
        return cls(
            repeaters=[nodes[nid] for nid in data["repeaters"]],
            route_speed=data["routeSpeed"],
        )


@dataclass(frozen=True)
class BackgroundRSSI:
    """Background RSSI noise levels for all channels."""

    channel_0: int
    channel_1: int
    channel_2: int | None = None
    channel_3: int | None = None


@dataclass(frozen=True)
class RFRegionInfo:
    """Information about an RF region."""

    region: int
    supports_zwave: bool
    supports_long_range: bool
    includes_region: int | None = None


@dataclass(frozen=True)
class NVMReadResult:
    """Result of an NVM buffer read operation."""

    buffer: bytes
    end_of_file: bool


@dataclass(frozen=True)
class NVMOpenExtResult:
    """Result of an extended NVM open operation."""

    size: int
    supported_operations: list


@dataclass
class NVMProgress:
    """Class to represent an NVM backup/restore progress event."""

    bytes_read_or_written: int
    total_bytes: int


class ControllerDataType(TypedDict, total=False):
    """Represent a controller data dict type."""

    sdkVersion: str
    type: int
    homeId: int
    ownNodeId: int
    isPrimary: bool
    isSUC: bool
    nodeType: int
    isUsingHomeIdFromOtherNetwork: bool
    isSISPresent: bool
    wasRealPrimary: bool
    firmwareVersion: str
    manufacturerId: int
    productType: int
    productId: int
    supportedFunctionTypes: list[int]
    sucNodeId: int
    supportsTimers: bool
    isRebuildingRoutes: bool
    statistics: ControllerStatisticsDataType
    inclusionState: int
    rfRegion: int
    status: int
    rebuildRoutesProgress: dict[str, str]
    supportsLongRange: bool
    # Schema 47+ properties
    isSIS: bool
    maxPayloadSize: int
    maxPayloadSizeLR: int
    zwaveApiVersion: ZWaveApiVersionDataType
    zwaveChipType: str | UnknownZWaveChipTypeDataType
