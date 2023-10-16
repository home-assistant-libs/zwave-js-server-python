"""
Model for a Zwave Node's Notification Event.

https://zwave-js.github.io/node-zwave-js/#/api/node?id=quotnotificationquot
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal, TypedDict

from ..const.command_class.multilevel_switch import MultilevelSwitchCommand
from ..const.command_class.power_level import PowerLevelTestStatus
from ..util.helpers import parse_buffer

if TYPE_CHECKING:
    from .node import Node


class BaseNotificationDataType(TypedDict):
    """Represent a base notification event data dict type."""

    source: Literal["node"]  # required
    event: Literal["notification"]  # required
    nodeId: int  # required
    endpointIndex: int  # required
    ccId: int  # required


@dataclass
class BaseNotification:
    """Model for a Zwave Node's notification event."""

    node: Node
    data: BaseNotificationDataType = field(repr=False)
    node_id: int = field(init=False, repr=False)
    endpoint_idx: int = field(init=False)
    command_class: int = field(init=False)

    def __post_init__(self) -> None:
        """Post initialization."""
        self.node_id = self.data["nodeId"]
        self.endpoint_idx = self.data["endpointIndex"]
        self.command_class = self.data["ccId"]


class EntryControlNotificationArgsDataType(TypedDict, total=False):
    """Represent args for a Entry Control CC notification event data dict type."""

    eventType: int  # required
    eventTypeLabel: str  # required
    dataType: int  # required
    dataTypeLabel: str  # required
    eventData: str | dict[str, Any]


class EntryControlNotificationDataType(BaseNotificationDataType):
    """Represent an Entry Control CC notification event data dict type."""

    args: EntryControlNotificationArgsDataType  # required


@dataclass
class EntryControlNotification(BaseNotification):
    """Model for a Zwave Node's Entry Control CC notification event."""

    data: EntryControlNotificationDataType = field(repr=False)
    event_type: int = field(init=False)
    event_type_label: str = field(init=False)
    data_type: int = field(init=False)
    data_type_label: str = field(init=False)
    event_data: str | dict[str, Any] | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        """Post initialize."""
        super().__post_init__()
        self.event_type = self.data["args"]["eventType"]
        self.event_type_label = self.data["args"]["eventTypeLabel"]
        self.data_type = self.data["args"]["dataType"]
        self.data_type_label = self.data["args"]["dataTypeLabel"]
        if event_data := self.data["args"].get("eventData"):
            self.event_data = parse_buffer(event_data)


class NotificationNotificationArgsDataType(TypedDict, total=False):
    """Represent args for a Notification CC notification event data dict type."""

    type: int  # required
    label: str  # required
    event: int  # required
    eventLabel: str  # required
    parameters: dict[str, Any]


class NotificationNotificationDataType(BaseNotificationDataType):
    """Represent a Notification CC notification event data dict type."""

    args: NotificationNotificationArgsDataType  # required


@dataclass
class NotificationNotification(BaseNotification):
    """Model for a Zwave Node's Notification CC notification event."""

    data: NotificationNotificationDataType = field(repr=False)
    type_: int = field(init=False)
    label: str = field(init=False)
    event: int = field(init=False)
    event_label: str = field(init=False)
    parameters: dict[str, Any] = field(init=False)

    def __post_init__(self) -> None:
        """Post initialize."""
        super().__post_init__()
        self.type_ = self.data["args"]["type"]
        self.label = self.data["args"]["label"]
        self.event = self.data["args"]["event"]
        self.event_label = self.data["args"]["eventLabel"]
        self.parameters = self.data["args"].get("parameters", {})


class PowerLevelNotificationArgsDataType(TypedDict):
    """Represent args for a Power Level CC notification event data dict type."""

    testNodeId: int
    status: int
    acknowledgedFrames: int


class PowerLevelNotificationDataType(BaseNotificationDataType):
    """Represent a Power Level CC notification event data dict type."""

    args: PowerLevelNotificationArgsDataType  # required


@dataclass
class PowerLevelNotification(BaseNotification):
    """Model for a Zwave Node's Power Level CC notification event."""

    data: PowerLevelNotificationDataType = field(repr=False)
    test_node_id: int = field(init=False)
    status: PowerLevelTestStatus = field(init=False)
    acknowledged_frames: int = field(init=False)

    def __post_init__(self) -> None:
        """Post initialize."""
        super().__post_init__()
        self.test_node_id = self.data["args"]["testNodeId"]
        self.status = PowerLevelTestStatus(self.data["args"]["status"])
        self.acknowledged_frames = self.data["args"]["acknowledgedFrames"]


class MultilevelSwitchNotificationArgsDataType(TypedDict, total=False):
    """Represent args for a Multi Level Switch CC notification event data dict type."""

    eventType: int  # required
    eventTypeLabel: str  # required
    direction: str


class MultilevelSwitchNotificationDataType(BaseNotificationDataType):
    """Represent a Multi Level Switch CC notification event data dict type."""

    args: MultilevelSwitchNotificationArgsDataType  # required


@dataclass
class MultilevelSwitchNotification(BaseNotification):
    """Model for a Zwave Node's Multi Level CC notification event."""

    data: MultilevelSwitchNotificationDataType = field(repr=False)
    event_type: MultilevelSwitchCommand = field(init=False)
    event_type_label: str = field(init=False)
    direction: str | None = field(init=False)

    def __post_init__(self) -> None:
        """Post initialize."""
        super().__post_init__()
        self.event_type = MultilevelSwitchCommand(self.data["args"]["eventType"])
        self.event_type_label = self.data["args"]["eventTypeLabel"]
        self.direction = self.data["args"].get("direction")
