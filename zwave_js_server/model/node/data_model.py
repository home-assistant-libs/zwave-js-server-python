"""Data model for a Z-Wave JS node."""
from typing import List, Literal, Optional, Union

from ...const import TYPING_EXTENSION_FOR_TYPEDDICT_REQUIRED
from ..device_class import DeviceClassDataType
from ..device_config import DeviceConfigDataType
from ..endpoint import EndpointDataType
from ..value import ValueDataType
from .statistics import NodeStatisticsDataType

if TYPING_EXTENSION_FOR_TYPEDDICT_REQUIRED:
    from typing_extensions import TypedDict
else:
    from typing import TypedDict


class FoundNodeDataType(TypedDict, total=False):
    """Represent a found node data dict type."""

    nodeId: int
    deviceClass: DeviceClassDataType
    supportedCCs: List[int]
    controlledCCs: List[int]


class NodeDataType(TypedDict, total=False):
    """Represent a node data dict type."""

    nodeId: int  # required
    index: int  # required
    deviceClass: DeviceClassDataType  # required
    installerIcon: int
    userIcon: int
    name: str
    location: str
    status: int  # 0-4  # required
    zwavePlusVersion: int
    zwavePlusNodeType: int
    zwavePlusRoleType: int
    isListening: bool
    isFrequentListening: Union[bool, str]
    isRouting: bool
    maxDataRate: int
    supportedDataRates: List[int]
    isSecure: Union[bool, Literal["unknown"]]
    supportsBeaming: bool
    supportsSecurity: bool
    protocolVersion: int
    firmwareVersion: str
    manufacturerId: int
    productId: int
    productType: int
    deviceConfig: DeviceConfigDataType
    deviceDatabaseUrl: str
    keepAwake: bool
    ready: bool
    label: str
    endpoints: List[EndpointDataType]
    endpointCountIsDynamic: bool
    endpointsHaveIdenticalCapabilities: bool
    individualEndpointCount: int
    aggregatedEndpointCount: int
    interviewAttempts: int
    interviewStage: Optional[Union[int, str]]
    values: List[ValueDataType]
    statistics: NodeStatisticsDataType
    highestSecurityClass: int
    isControllerNode: bool
