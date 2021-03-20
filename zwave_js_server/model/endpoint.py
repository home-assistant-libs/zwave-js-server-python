"""
Model for a Zwave Node's endpoints.

https://zwave-js.github.io/node-zwave-js/#/api/endpoint?id=endpoint-properties
"""

from typing import Optional, TypedDict

from .device_class import DeviceClass, DeviceClassDataType


class EndpointDataType(TypedDict, total=False):
    """Represent an endpoint data dict type."""

    nodeId: int  # required
    index: int  # required
    deviceClass: DeviceClassDataType  # required
    installerIcon: int
    userIcon: int


class Endpoint:
    """Model for a Zwave Node's endpoint."""

    def __init__(self, data: EndpointDataType) -> None:
        """Initialize."""
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
