"""Provide a model for the Z-Wave JS value."""
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional, TypedDict, Union

from ..event import Event

if TYPE_CHECKING:
    from .node import Node


class MetaDataType(TypedDict, total=False):
    """Represent a metadata data dict type."""

    type: str  # required
    readable: bool  # required
    writeable: bool  # required
    description: str
    label: str
    min: int
    max: int
    unit: str
    states: Dict[int, str]
    ccSpecific: Dict[str, Any]


class ValueDataType(TypedDict, total=False):
    """Represent a value data dict type."""

    commandClass: int  # required
    commandClassName: str  # required
    endpoint: int
    property: Union[str, int]  # required
    propertyName: str
    propertyKey: Union[str, int]
    propertyKeyName: str
    value: Any
    metadata: MetaDataType
    ccVersion: int


def get_value_id(node: "Node", event_data: ValueDataType) -> str:
    """Return ID of value."""
    command_class = event_data["commandClass"]
    endpoint = event_data.get("endpoint") or "00"
    property_ = event_data["property"]
    property_key_name = event_data.get("propertyKeyName") or "00"
    return f"{node.node_id}-{command_class}-{endpoint}-{property_}-{property_key_name}"


class ValueMetadata:
    """Represent metadata on a value instance."""

    def __init__(self, data: MetaDataType) -> None:
        """Initialize metadata."""
        self.data = data

    @property
    def type(self) -> str:
        """Return type."""
        return self.data["type"]

    @property
    def readable(self) -> Optional[bool]:
        """Return readable."""
        return self.data.get("readable")

    @property
    def writeable(self) -> Optional[bool]:
        """Return writeable."""
        return self.data.get("writeable")

    @property
    def label(self) -> Optional[str]:
        """Return label."""
        return self.data.get("label")

    @property
    def min(self) -> Optional[int]:
        """Return min."""
        return self.data.get("min")

    @property
    def max(self) -> Optional[int]:
        """Return max."""
        return self.data.get("max")

    @property
    def unit(self) -> Optional[str]:
        """Return unit."""
        return self.data.get("unit")

    @property
    def states(self) -> Optional[dict]:
        """Return (optional) states."""
        return self.data.get("states")

    @property
    def cc_specific(self) -> Optional[Dict[str, Any]]:
        """Return ccSpecific."""
        return self.data.get("ccSpecific")


class Value:
    """Represent a Z-Wave JS value."""

    def __init__(self, node: "Node", data: ValueDataType) -> None:
        """Initialize value."""
        self.node = node
        self.data = data
        self._value = data.get("value")

    def __repr__(self) -> str:
        """Return the representation."""
        return f"{type(self).__name__}(value_id={self.value_id!r})"

    @property
    def value_id(self) -> str:
        """Return value ID."""
        return get_value_id(self.node, self.data)

    @property
    def metadata(self) -> ValueMetadata:
        """Return value metadata."""
        return ValueMetadata(self.data["metadata"])

    @property
    def value(self) -> Optional[Any]:
        """Return value."""
        return self._value

    @property
    def command_class_name(self) -> str:
        """Return commandClassName."""
        return self.data["commandClassName"]

    @property
    def command_class(self) -> int:
        """Return commandClass."""
        return self.data["commandClass"]

    @property
    def cc_version(self) -> int:
        """Return commandClass version."""
        return self.data["ccVersion"]

    @property
    def endpoint(self) -> Optional[int]:
        """Return endpoint."""
        return self.data.get("endpoint")

    @property
    def property_(self) -> Union[str, int]:
        """Return property.

        Note the underscore in the end of this property name.
        That's there to not confuse Python to think it's a property
        decorator.
        """
        return self.data["property"]

    @property
    def property_key(self) -> Optional[Union[str, int]]:
        """Return propertyKey."""
        return self.data.get("propertyKey")

    @property
    def property_name(self) -> Optional[str]:
        """Return propertyName."""
        return self.data.get("propertyName")

    @property
    def property_key_name(self) -> Optional[str]:
        """Return propertyKeyName."""
        return self.data.get("propertyKeyName")

    def receive_event(self, event: Event) -> None:
        """Receive an event."""
        self.data.update(event.data["args"])
        self._value = event.data["args"].get("newValue")


@dataclass
class ValueNotification:
    """
    Model for a Value Nofification message.

    https://zwave-js.github.io/node-zwave-js/#/api/node?id=quotvalue-notificationquot
    """

    command_class_name: str
    command_class: int
    endpoint: int
    property: str
    value: Any
    property_name: str
    metadata: Optional[ValueMetadata] = None

    @classmethod
    def from_event(cls, event: Event) -> "ValueNotification":
        """Parse event message into ValueNotification."""
        return cls(
            command_class_name=event.data["args"]["commandClassName"],
            command_class=event.data["args"]["commandClass"],
            endpoint=event.data["args"]["endpoint"],
            property=event.data["args"]["property"],
            value=event.data["args"].get("value"),
            property_name=event.data["args"]["propertyName"],
            metadata=ValueMetadata(
                event.data["args"]["metadata"]
                if "metadata" in event.data["args"]
                else None
            ),
        )
