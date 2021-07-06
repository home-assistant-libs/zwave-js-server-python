"""
Model for a Zwave Node's endpoints.

https://zwave-js.github.io/node-zwave-js/#/api/endpoint?id=endpoint-properties
"""

from typing import Dict, List, TYPE_CHECKING, Optional, TypedDict, Union

from .command_class import CommandClassInfoDataType
from .device_class import DeviceClass, DeviceClassDataType
from .device_config import DeviceConfigDataType
from ..event import EventBase
from .value import ConfigurationValue, Value, ValueDataType

if TYPE_CHECKING:
    from ..client import Client


class EndpointDataType(TypedDict, total=False):
    """Represent an endpoint data dict type."""

    # Endpoint data
    nodeId: int  # required
    index: int  # required
    deviceClass: DeviceClassDataType  # required
    installerIcon: int
    userIcon: int

    # Node data
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

    def __init__(
        self,
        client: "Client",
        data: EndpointDataType,
        values: Dict[str, Union[ConfigurationValue, Value]] = None,
    ) -> None:
        """Initialize."""
        super().__init__()
        self.client = client
        self.data = data
        if values is not None:
            self.values = values

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
