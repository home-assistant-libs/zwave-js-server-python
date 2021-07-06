"""
Model for a Zwave Node's endpoints.

https://zwave-js.github.io/node-zwave-js/#/api/endpoint?id=endpoint-properties
"""

from typing import List, TYPE_CHECKING, Optional, TypedDict, Union
from zwave_js_server.model.value import ValueDataType
from zwave_js_server.model.command_class import CommandClassInfoDataType
from zwave_js_server.model.device_config import DeviceConfigDataType

from zwave_js_server.event import EventBase

from .device_class import DeviceClass, DeviceClassDataType

if TYPE_CHECKING:
    from ..client import Client


class EndpointDataType(TypedDict, total=False):
    """Represent an endpoint data dict type."""

    nodeId: int  # required
    index: int  # required
    deviceClass: DeviceClassDataType  # required
    installerIcon: int
    userIcon: int
    name: str
    location: str
    status: int  # 0-4  # required for Nodes
    zwavePlusVersion: int
    zwavePlusNodeType: int
    zwavePlusRoleType: int
    isListening: bool
    isFrequentListening: Union[bool, str]
    isRouting: bool
    maxDataRate: int
    supportedDataRates: List[int]
    isSecure: bool
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
    endpoints: List["EndpointDataType"]  # type: ignore
    endpointCountIsDynamic: bool
    endpointsHaveIdenticalCapabilities: bool
    individualEndpointCount: int
    aggregatedEndpointCount: int
    interviewAttempts: int
    interviewStage: Optional[Union[int, str]]
    commandClasses: List[CommandClassInfoDataType]
    values: List[ValueDataType]


class Endpoint(EventBase):
    """Model for a Zwave Node's endpoint."""

    def __init__(self, client: "Client", data: EndpointDataType) -> None:
        """Initialize."""
        super().__init__()
        self.client = client
        self.data = data

    @property
    def node_id(self) -> int:
        """Return node ID property."""
        return self.data["nodeId"]

    @property
    def index(self) -> int:
        """Return index property."""
        return self.data["index"]

    @property
    def device_class(self) -> DeviceClass:
        """Return the device_class."""
        return DeviceClass(self.data["deviceClass"])

    @property
    def installer_icon(self) -> Optional[int]:
        """Return installer icon property."""
        return self.data.get("installerIcon")

    @property
    def user_icon(self) -> Optional[int]:
        """Return user icon property."""
        return self.data.get("userIcon")
