"""
Model for a Zwave Node's Notification Event.

https://zwave-js.github.io/node-zwave-js/#/api/node?id=quotnotificationquot
"""

from typing import Literal, TYPE_CHECKING, Any, Dict, TypedDict

if TYPE_CHECKING:
    from .node import Node


class NotificationDataType(TypedDict, total=False):
    """Represent a notification event data dict type."""

    source: Literal["node"]  # required
    event: Literal["notification"]  # required
    nodeId: int  # required
    notificationLabel: str  # required
    parameters: Dict[str, Any]


class Notification:
    """Model for a Zwave Node's notification event."""

    def __init__(self, node: "Node", data: NotificationDataType) -> None:
        """Initialize."""
        self.node = node
        self.data = data

    @property
    def node_id(self) -> int:
        """Return node ID property."""
        return self.data["nodeId"]

    @property
    def notification_label(self) -> str:
        """Return notification label property."""
        return self.data["notificationLabel"]

    @property
    def parameters(self) -> Dict[str, Any]:
        """Return installer icon property."""
        return self.data.get("parameters", {})
