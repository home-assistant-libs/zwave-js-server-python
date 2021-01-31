"""
Model for a Zwave Node's endpoints.

https://zwave-js.github.io/node-zwave-js/#/api/endpoint?id=endpoint-properties
"""

from typing import Optional, TypedDict


class EndpointDataType(TypedDict, total=False):
    """Represent an endpoint data dict type."""

    nodeId: int
    index: int
    installerIcon: Optional[int]
    userIcon: Optional[int]


class Endpoint:
    """Model for a Zwave Node's endpoint."""

    def __init__(self, data: EndpointDataType) -> None:
        """Initialize."""
        self.data = data

    @property
    def nodeId(self) -> int:
        """Return node ID property."""
        return self.data["nodeId"]

    @property
    def index(self) -> int:
        """Return index property."""
        return self.data["index"]

    @property
    def installerIcon(self) -> Optional[int]:
        """Return installer icon property."""
        return self.data.get("installerIcon")

    @property
    def userIcon(self) -> Optional[int]:
        """Return user icon property."""
        return self.data.get("userIcon")
