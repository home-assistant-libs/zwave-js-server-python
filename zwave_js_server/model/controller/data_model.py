"""Provide a model for the Z-Wave JS controller."""
from typing import List, TypedDict

from .statistics import ControllerStatisticsDataType


class ControllerDataType(TypedDict, total=False):
    """Represent a controller data dict type."""

    libraryVersion: str
    type: int
    homeId: int
    ownNodeId: int
    isSecondary: bool  # TODO: The following items are missing in the docs.
    isUsingHomeIdFromOtherNetwork: bool
    isSISPresent: bool
    wasRealPrimary: bool
    isStaticUpdateController: bool
    isSlave: bool
    serialApiVersion: str
    manufacturerId: int
    productType: int
    productId: int
    supportedFunctionTypes: List[int]
    sucNodeId: int
    supportsTimers: bool
    isHealNetworkActive: bool
    statistics: ControllerStatisticsDataType
    inclusionState: int
