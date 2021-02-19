"""Provide a model for the Z-Wave JS value."""
import json
from typing import TYPE_CHECKING, Any, Dict, Optional, TypedDict, Union

from ..const import ConfigurationValueType
from ..exceptions import UnparseableValue
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
    newValue: Any
    prevValue: Any
    metadata: MetaDataType
    ccVersion: int


def _get_value_id_from_dict(node: "Node", val: ValueDataType) -> str:
    """Return ID of value from ValueDataType dict."""
    return get_value_id(
        node,
        val["commandClass"],
        val["property"],
        val.get("endpoint"),
        val.get("propertyKey"),
        val.get("propertyKeyName"),
    )


def get_value_id(
    node: "Node",
    command_class: int,
    property_: Union[str, int],
    endpoint: Optional[int] = None,
    property_key: Optional[Union[str, int]] = None,
    property_key_name: Optional[str] = None,
) -> str:
    """Return ID of value."""
    endpoint_ = "00" if endpoint is None else endpoint
    if property_key is None:
        property_key = "00"
    property_key_name = property_key_name or "00"
    return (
        f"{node.node_id}-{command_class}-{endpoint_}-"
        f"{property_}-{property_key}-{property_key_name}"
    )


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


class Value:
    """Represent a Z-Wave JS value."""

    def __init__(self, node: "Node", data: ValueDataType) -> None:
        """Initialize value."""
        self.node = node
        self.data = data
        self._value = data.get("newValue", data.get("value"))
        if self.metadata.type == "string" and self._value and self._value[0] == "{":
            try:
                parsed_val = json.loads(self._value)
                if (
                    "type" not in parsed_val
                    or parsed_val["type"] != "Buffer"
                    or "data" not in parsed_val
                ):
                    raise ValueError("JSON string does not match expected schema")
                self._value = "".join([chr(x) for x in parsed_val["data"]])
            except ValueError as err:
                raise UnparseableValue(
                    f"Unparseable value {self}: {self.value}"
                ) from err

    def __repr__(self) -> str:
        """Return the representation."""
        return f"{type(self).__name__}(value_id={self.value_id!r})"

    @property
    def value_id(self) -> str:
        """Return value ID."""
        return _get_value_id_from_dict(self.node, self.data)

    @property
    def metadata(self) -> ValueMetadata:
        """Return value metadata."""
        return ValueMetadata(self.data.get("metadata", {"type": "unknown"}))

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
        self.update(event.data["args"])

    def update(self, data: ValueDataType) -> None:
        """Update data."""
        self.data.update(data)
        if "newValue" in data:
            self._value = data["newValue"]
        if "value" in data:
            self._value = data["value"]


class ValueNotification(Value):
    """
    Model for a Value Nofification message.

    https://zwave-js.github.io/node-zwave-js/#/api/node?id=quotvalue-notificationquot
    """

    # format is the same as a Value message, subclassed for easier identifying and future use


class ConfigurationValue(Value):
    """Model for a Configuration Value."""

    @property
    def configuration_value_type(self) -> ConfigurationValueType:
        """Return configuration value type."""
        if self.metadata.type == "number":
            if self.metadata.states:
                return ConfigurationValueType.ENUMERATED
            if (
                self.metadata.max is not None or self.metadata.min is not None
            ) and not self.metadata.max == self.metadata.min == 0:
                return ConfigurationValueType.RANGE

        return ConfigurationValueType.UNDEFINED
