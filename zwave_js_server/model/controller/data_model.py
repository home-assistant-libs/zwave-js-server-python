"""Data model for a Z-Wave JS controller."""

from __future__ import annotations

from typing import TypedDict

from .statistics import ControllerStatisticsDataType


class ZWaveApiVersionDataType(TypedDict, total=False):
    """Represent the Z-Wave API version info."""

    kind: int
    version: str


class ZWaveChipTypeDataType(TypedDict, total=False):
    """Represent the Z-Wave chip type info."""

    type: int
    version: int


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
    # Schema 45+ properties
    isSIS: bool
    maxPayloadSize: int
    maxPayloadSizeLR: int
    zwaveApiVersion: ZWaveApiVersionDataType
    zwaveChipType: ZWaveChipTypeDataType
