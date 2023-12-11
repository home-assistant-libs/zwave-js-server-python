"""Data model for a Z-Wave JS controller."""
from __future__ import annotations

from typing import TypedDict

from .statistics import ControllerStatisticsDataType


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
