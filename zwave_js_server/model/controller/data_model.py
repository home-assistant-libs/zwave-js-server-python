"""Data model for a Z-Wave JS controller."""
from typing import List

from ...const import TYPING_EXTENSION_FOR_TYPEDDICT_REQUIRED
from .statistics import ControllerStatisticsDataType

if TYPING_EXTENSION_FOR_TYPEDDICT_REQUIRED:
    from typing_extensions import TypedDict
else:
    from typing import TypedDict


class ControllerDataType(TypedDict, total=False):
    """Represent a controller data dict type."""

    sdkVersion: str
    type: int
    homeId: int
    ownNodeId: int
    isPrimary: bool
    isSUC: bool
    nodeType: int
    isUsingHomeIdFromOtherNetwork: bool  # TODO: The following items are missing in the docs.
    isSISPresent: bool
    wasRealPrimary: bool
    firmwareVersion: str
    manufacturerId: int
    productType: int
    productId: int
    supportedFunctionTypes: List[int]
    sucNodeId: int
    supportsTimers: bool
    isHealNetworkActive: bool
    statistics: ControllerStatisticsDataType
    inclusionState: int
    rfRegion: int
