"""Data model for a Z-Wave JS node."""
from typing import Literal, Optional, TypedDict, Union

from ..device_class import DeviceClassDataType
from ..device_config import DeviceConfigDataType
from ..endpoint import EndpointDataType
from ..value import ValueDataType
from .statistics import NodeStatisticsDataType


class FoundNodeDataType(TypedDict, total=False):
    """Represent a found node data dict type."""

    nodeId: int
    deviceClass: DeviceClassDataType
    supportedCCs: list[int]
    controlledCCs: list[int]


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
    supportedDataRates: list[int]
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
    endpoints: list[EndpointDataType]
    endpointCountIsDynamic: bool
    endpointsHaveIdenticalCapabilities: bool
    individualEndpointCount: int
    aggregatedEndpointCount: int
    interviewAttempts: int
    interviewStage: Optional[Union[int, str]]
    values: list[ValueDataType]
    statistics: NodeStatisticsDataType
    highestSecurityClass: int
    isControllerNode: bool
