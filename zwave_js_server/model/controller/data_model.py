"""Data model for a Z-Wave JS controller."""

from __future__ import annotations

from typing import Literal, TypedDict

from .statistics import ControllerStatisticsDataType


class ZWaveApiVersionDataType(TypedDict):
    """Represent a Z-Wave API version (schema 47+)."""

    kind: Literal["official", "legacy"]
    version: int


class UnknownZWaveChipTypeDataType(TypedDict):
    """Represent an unknown Z-Wave chip type descriptor (schema 47+)."""

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
    # Schema 47+ properties
    isSIS: bool
    maxPayloadSize: int
    maxPayloadSizeLR: int
    zwaveApiVersion: ZWaveApiVersionDataType
    zwaveChipType: str | UnknownZWaveChipTypeDataType
