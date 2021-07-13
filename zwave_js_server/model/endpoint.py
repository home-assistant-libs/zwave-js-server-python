"""
Model for a Zwave Node's endpoints.

https://zwave-js.github.io/node-zwave-js/#/api/endpoint?id=endpoint-properties
"""

from typing import TYPE_CHECKING, Dict, Optional, TypedDict, Union

from ..event import EventBase
from .device_class import DeviceClass, DeviceClassDataType
from .value import ConfigurationValue, Value

if TYPE_CHECKING:
    from ..client import Client


class EndpointDataType(TypedDict, total=False):
    """Represent an endpoint data dict type."""

    nodeId: int  # required
    index: int  # required
    deviceClass: DeviceClassDataType  # required
    installerIcon: int
    userIcon: int


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
