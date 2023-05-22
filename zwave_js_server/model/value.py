"""Provide a model for the Z-Wave JS value."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict

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
    min: int | None
    max: int | None
    unit: str
    states: dict[str, str]
    ccSpecific: dict[str, Any]
    valueChangeOptions: list[str]
    allowManualEntry: bool
    valueSize: int
    stateful: bool
    secret: bool


class ValueDataType(TypedDict, total=False):
    """Represent a value data dict type."""

    commandClass: int  # required
    commandClassName: str  # required
    endpoint: int
    property: int | str  # required
    propertyName: str
    propertyKey: int | str
    propertyKeyName: str
    value: Any
    newValue: Any
    prevValue: Any
    metadata: MetaDataType
    ccVersion: int


def _init_value(node: "Node", val: ValueDataType) -> "Value" | "ConfigurationValue":
    """Initialize a Value object from ValueDataType."""
    if val["commandClass"] == CommandClass.CONFIGURATION:
        return ConfigurationValue(node, val)
    return Value(node, val)


def _get_value_id_str_from_dict(node: "Node", val: ValueDataType) -> str:
    """Return string ID of value from ValueDataType dict."""
    return get_value_id_str(
        node,
        val["commandClass"],
        val["property"],
        val.get("endpoint"),
        val.get("propertyKey"),
    )


def get_value_id_str(
    node: "Node",
    command_class: int,
    property_: int | str,
    endpoint: int | None = None,
    property_key: int | str | None = None,
) -> str:
    """Return string ID of value."""
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
    def readable(self) -> bool | None:
        """Return readable."""
        return self.data.get("readable")

    @property
    def writeable(self) -> bool | None:
        """Return writeable."""
        return self.data.get("writeable")

    @property
    def label(self) -> str | None:
        """Return label."""
        return self.data.get("label")

    @property
    def description(self) -> str | None:
        """Return description."""
        return self.data.get("description")

    @property
    def min(self) -> int | None:
        """Return min."""
        return self.data.get("min")

    @property
    def max(self) -> int | None:
        """Return max."""
        return self.data.get("max")

    @property
    def unit(self) -> str | None:
        """Return unit."""
        return self.data.get("unit")

    @property
    def states(self) -> dict:
        """Return (optional) states."""
        return self.data.get("states", {})

    @property
    def cc_specific(self) -> dict[str, Any]:
        """Return ccSpecific."""
        return self.data.get("ccSpecific", {})

    @property
    def value_change_options(self) -> list[str]:
        """Return valueChangeOptions."""
        return self.data.get("valueChangeOptions", [])

    @property
    def allow_manual_entry(self) -> bool | None:
        """Return allowManualEntry."""
        return self.data.get("allowManualEntry")

    @property
    def value_size(self) -> int | None:
        """Return valueSize."""
        return self.data.get("valueSize")

    @property
    def stateful(self) -> bool | None:
        """Return stateful."""
        return self.data.get("stateful")

    @property
    def secret(self) -> bool | None:
        """Return secret."""
        return self.data.get("secret")

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
        return _get_value_id_str_from_dict(self.node, self.data)

    @property
    def metadata(self) -> ValueMetadata:
        """Return value metadata."""
        return self._metadata

    @property
    def value(self) -> Any | None:
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
    def endpoint(self) -> int | None:
        """Return endpoint."""
        return self.data.get("endpoint")

    @property
    def property_(self) -> int | str:
        """Return property.

        Note the underscore in the end of this property name.
        That's there to not confuse Python to think it's a property
        decorator.
        """
        return self.data["property"]

    @property
    def property_key(self) -> int | str | None:
        """Return propertyKey."""
        return self.data.get("propertyKey")

    @property
    def property_name(self) -> str | None:
        """Return propertyName."""
        return self.data.get("propertyName")

    @property
    def property_key_name(self) -> str | None:
        """Return propertyKeyName."""
        return self.data.get("propertyKeyName")

    def receive_event(self, event: Event) -> None:
        """Receive an event."""
        self.update(event.data["args"])

    def update(self, data: ValueDataType) -> None:
        """Update data."""
        self.data.update(data)
        if "newValue" in data:
            self._value = self.data["value"] = data["newValue"]
        elif "value" in data:
            self._value = self.data["value"] = data["value"]
        if "metadata" in data:
            self._metadata.update(data["metadata"])

        self.data.pop("newValue", None)
        self.data.pop("prevValue", None)

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
