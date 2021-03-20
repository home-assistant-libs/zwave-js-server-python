"""
Model for a Zwave Node's Notification Event.

https://zwave-js.github.io/node-zwave-js/#/api/node?id=quotnotificationquot
"""

from typing import TYPE_CHECKING, Any, Dict, Literal, Optional, TypedDict, Union

from zwave_js_server.util.helpers import parse_buffer

if TYPE_CHECKING:
    from .node import Node


class NotificationDataType(TypedDict):
    """Represent a generic notification event data dict type."""

    source: Literal["node"]  # required
    event: Literal["notification"]  # required
    nodeId: int  # required
    ccId: int  # required


class EntryControlNotificationArgsDataType(TypedDict, total=False):
    """Represent args for a Entry Control CC notification event data dict type."""

    eventType: int  # required
    dataType: int  # required
    eventData: Union[str, Dict[str, Any]]


class EntryControlNotificationDataType(NotificationDataType):
    """Represent an Entry Control CC notification event data dict type."""

    args: EntryControlNotificationArgsDataType  # required


class NotificationNotificationArgsDataType(TypedDict, total=False):
    """Represent args for a Notification CC notification event data dict type."""

    type: int  # required
    label: str  # required
    event: int  # required
    eventLabel: str  # required
    parameters: Dict[str, Any]


class NotificationNotificationDataType(NotificationDataType):
    """Represent a Notification CC notification event data dict type."""

    args: NotificationNotificationArgsDataType  # required


class NotificationNotification:
    """Model for a Zwave Node's Notification CC notification event."""

    def __init__(self, node: "Node", data: NotificationNotificationDataType) -> None:
        """Initialize."""
        self.node = node
        self.data = data

    @property
    def node_id(self) -> int:
        """Return node ID property."""
        return self.data["nodeId"]

    @property
    def command_class(self) -> int:
        """Return command class."""
        return self.data["ccId"]

    @property
    def type_(self) -> int:
        """Return type property."""
        return self.data["args"]["type"]

    @property
    def label(self) -> str:
        """Return label property."""
        return self.data["args"]["label"]

    @property
    def event(self) -> int:
        """Return event property."""
        return self.data["args"]["event"]

    @property
    def event_label(self) -> str:
        """Return notification label property."""
        return self.data["args"]["eventLabel"]

    @property
    def parameters(self) -> Dict[str, Any]:
        """Return installer icon property."""
        return self.data["args"].get("parameters", {})


class EntryControlNotification:
    """Model for a Zwave Node's Entry Control CC notification event."""

    def __init__(self, node: "Node", data: EntryControlNotificationDataType) -> None:
        """Initialize."""
        self.node = node
        self.data = data

    @property
    def node_id(self) -> int:
        """Return node ID property."""
        return self.data["nodeId"]

    @property
    def command_class(self) -> int:
        """Return command class."""
        return self.data["ccId"]

    @property
    def event_type(self) -> int:
        """Return event type property."""
        return self.data["args"]["eventType"]

    @property
    def data_type(self) -> int:
        """Return data type property."""
        return self.data["args"]["dataType"]

    @property
    def event_data(self) -> Optional[str]:
        """Return event data property."""
        if event_data := self.data["args"].get("eventData"):
            return parse_buffer(event_data)
        return None
