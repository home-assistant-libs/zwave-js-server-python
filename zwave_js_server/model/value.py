"""Value model."""


from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .node import Node


def value_id(node: "Node", event: dict) -> str:
    """Return ID of value."""
    command_class = event.get("commandClass")
    endpoint = event.get("endpoint")
    property_key_name = event.get("propertyKeyName")
    return f"{node.node_id}-{command_class}-{endpoint}-{property_key_name}"


class ValueMetadata:
    def __init__(self, data) -> None:
        self.data = data

    @property
    def type(self) -> str:
        """Return type."""
        return self.data.get("type")

    @property
    def readable(self) -> bool:
        """Return readable."""
        return self.data.get("readable")

    @property
    def writeable(self) -> bool:
        """Return writeable."""
        return self.data.get("writeable")

    @property
    def label(self) -> str:
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
    def cc_specific(self) -> Optional[dict]:
        """Return ccSpecific."""
        return self.data.get("ccSpecific")


class Value:
    def __init__(self, node: "Node", data: dict) -> None:
        self.node = node
        self.data = data
        self._value = data.get("value")

    @property
    def value_id(self) -> str:
        """Return value ID."""
        return value_id(self.node, self.data)

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
        return self.data.get("commandClassName")

    @property
    def command_class(self) -> int:
        """Return commandClass."""
        return self.data.get("commandClass")

    @property
    def endpoint(self) -> int:
        """Return endpoint."""
        return self.data.get("endpoint")

    @property
    def property_(self) -> str:
        """Return property."""
        return self.data.get("property")

    @property
    def property_key(self) -> str:
        """Return propertyKey."""
        return self.data.get("propertyKey")

    @property
    def property_name(self) -> str:
        """Return propertyName."""
        return self.data.get("propertyName")

    @property
    def property_key_name(self) -> str:
        """Return propertyKeyName."""
        return self.data.get("propertyKeyName")

    def receive_event(self, event: dict):
        """Receive an event."""
        if event["event"] != "value updated":
            return

        self.data.update(event["args"])
        self._value = event["args"].get("newValue")
