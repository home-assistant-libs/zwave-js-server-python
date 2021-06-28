"""Provide a model for the Z-Wave JS value."""
from typing import List, TYPE_CHECKING, Any, Dict, Optional, TypedDict, Union

from ..const import VALUE_UNKNOWN, CommandClass, ConfigurationValueType
from ..event import Event
from ..util.helpers import parse_buffer

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
    valueChangeOptions: List[str]
    allowManualEntry: bool
    valueSize: int


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
    newValue: Any
    prevValue: Any
    metadata: MetaDataType
    ccVersion: int


def _init_value(
    node: "Node", val: ValueDataType
) -> Union["Value", "ConfigurationValue"]:
    """Intialize a Value object from ValueDataType."""
    if val["commandClass"] == CommandClass.CONFIGURATION:
        return ConfigurationValue(node, val)
    return Value(node, val)


def _get_value_id_from_dict(node: "Node", val: ValueDataType) -> str:
    """Return ID of value from ValueDataType dict."""
    return get_value_id(
        node,
        val["commandClass"],
        val["property"],
        val.get("endpoint"),
        val.get("propertyKey"),
    )


def get_value_id(
    node: "Node",
    command_class: int,
    property_: Union[str, int],
    endpoint: Optional[int] = None,
    property_key: Optional[Union[str, int]] = None,
) -> str:
    """Return ID of value."""
    # If endpoint is not provided, assume root endpoint
    endpoint_ = endpoint or 0
    value_id = f"{node.node_id}-{command_class}-{endpoint_}-{property_}"
    # Property key is only included when it has a value
    if property_key is not None:
        value_id += f"-{property_key}"
    return value_id


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
    def description(self) -> Optional[str]:
        """Return description."""
        return self.data.get("description")

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
    def states(self) -> dict:
        """Return (optional) states."""
        return self.data.get("states", {})

    @property
    def cc_specific(self) -> Dict[str, Any]:
        """Return ccSpecific."""
        return self.data.get("ccSpecific", {})

    @property
    def value_change_options(self) -> List[str]:
        """Return valueChangeOptions."""
        return self.data.get("valueChangeOptions", [])

    @property
    def allow_manual_entry(self) -> Optional[bool]:
        """Return allowManualEntry."""
        return self.data.get("allowManualEntry")

    @property
    def value_size(self) -> Optional[int]:
        """Return valueSize."""
        return self.data.get("valueSize")

    def update(self, data: MetaDataType) -> None:
        """Update data."""
        self.data.update(data)


class Value:
    """Represent a Z-Wave JS value."""

    def __init__(self, node: "Node", data: ValueDataType) -> None:
        """Initialize value."""
        self.node = node
        self.data: ValueDataType = {}
        self._value: Any = None
        self._metadata = ValueMetadata({"type": "unknown"})
        self.update(data)

    def __repr__(self) -> str:
        """Return the representation."""
        return f"{type(self).__name__}(value_id={self.value_id!r})"

    def __hash__(self) -> int:
        """Return the hash."""
        return hash((self.node, self.value_id))

    def __eq__(self, other: object) -> bool:
        """Return whether this instance equals another."""
        if not isinstance(other, Value):
            return False
        return self.node == other.node and self.value_id == other.value_id

    @property
    def value_id(self) -> str:
        """Return value ID."""
        return _get_value_id_from_dict(self.node, self.data)

    @property
    def metadata(self) -> ValueMetadata:
        """Return value metadata."""
        return self._metadata

    @property
    def value(self) -> Optional[Any]:
        """Return value."""
        # Treat unknown values like they are None
        if self._value == VALUE_UNKNOWN:
            return None
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
        self.update(event.data["args"])

    def update(self, data: ValueDataType) -> None:
        """Update data."""
        self.data.update(data)
        if "newValue" in data:
            self._value = data["newValue"]
        if "value" in data:
            self._value = data["value"]
        if "metadata" in data:
            self._metadata.update(data["metadata"])

        # Handle buffer dict and json string in value.
        if self.metadata.type == "buffer":
            self._value = parse_buffer(self._value)


class ValueNotification(Value):
    """
    Model for a Value Notification message.

    https://zwave-js.github.io/node-zwave-js/#/api/node?id=quotvalue-notificationquot
    """

    # format is the same as a Value message, subclassed for easier identifying and future use


class ConfigurationValue(Value):
    """Model for a Configuration Value."""

    @property
    def configuration_value_type(self) -> ConfigurationValueType:
        """Return configuration value type."""
        if self.metadata.type == "number":
            if (
                self.metadata.allow_manual_entry
                and not self.metadata.max == self.metadata.min == 0
            ):
                return ConfigurationValueType.MANUAL_ENTRY
            if self.metadata.states:
                return ConfigurationValueType.ENUMERATED
            if (
                self.metadata.max is not None or self.metadata.min is not None
            ) and not self.metadata.max == self.metadata.min == 0:
                return ConfigurationValueType.RANGE

        return ConfigurationValueType.UNDEFINED
