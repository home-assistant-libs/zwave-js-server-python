"""
Model for a Zwave Node's Notification Event.

https://zwave-js.github.io/node-zwave-js/#/api/node?id=quotnotificationquot
"""

from typing import Literal, TYPE_CHECKING, Any, Dict, TypedDict, Union

from ..const import CommandClass, EntryControlDataType, EntryControlEventType

if TYPE_CHECKING:
    from .node import Node


class NotificationDataType(TypedDict, total=False):
    """Represent a base notification event data dict type."""

    source: Literal["node"]  # required
    event: Literal["notification"]  # required
    nodeId: int  # required
    ccId: Union[
        Literal[CommandClass.NOTIFICATION], Literal[CommandClass.ENTRY_CONTROL]
    ]  # required


class EntryControlNotificationArgsDataType(TypedDict, total=False):
    """Represent args for a Entry Control CC notification event data dict type."""

    eventType: EntryControlEventType  # required
    dataType: EntryControlDataType  # required
    eventData: str  # required


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


class Notification:
    """Model for a Zwave Node's Notification CC notification event."""

    def __init__(self, node: "Node", data: NotificationDataType) -> None:
        """Initialize."""
        self.node = node
        self.data = data

    @property
    def node_id(self) -> int:
        """Return node ID property."""
        return self.data["nodeId"]

    @property
    def command_class(self) -> CommandClass:
        """Return command class."""
        return self.data["ccId"]


class NotificationNotification(Notification):
    """Model for a Zwave Node's Notification CC notification event."""

    def __init__(self, node: "Node", data: NotificationNotificationDataType) -> None:
        """Initialize."""
        super().__init__(node, data)

    @property
    def type_(self) -> int:
        """Return type property."""
        return self.data["args"]["type"]

    @property
    def label(self) -> int:
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


class EntryControlNotification(Notification):
    """Model for a Zwave Node's Entry Control CC notification event."""

    def __init__(self, node: "Node", data: EntryControlNotificationDataType) -> None:
        """Initialize."""
        super().__init__(node, data)

    @property
    def event_type(self) -> EntryControlEventType:
        """Return event type property."""
        return self.data["args"]["eventType"]

    @property
    def data_type(self) -> EntryControlDataType:
        """Return data type property."""
        return self.data["args"]["dataType"]

    @property
    def event_data(self) -> str:
        """Return event data property."""
        return self.data["args"]["eventData"]
